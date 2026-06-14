# 生成创意图片的 Skill

## references — 避免臃肿的 SKILL.md

```
~/.claude/
├── skills/
│   ├── iwen-creative/
│   │   ├── SKILL.md              # 主要说明（必填）
│   │   ├── references/           # 附加文档
│   │   │   ├── box.md            # 包装盒
│   │   │   └── clothes.md        # 工服
│   │   ├── scripts/              # 可从 skill 调用的帮助程序脚本
│   │   └── assets/               # 补充文件
│   └── 技能2/
│       └── SKILL.md
```

---

## SKILL.md 完整示例

```yaml
---
name: iwen-creative
description: 为iwen餐厅生成符合品牌调性的物料设计创意，当用户说要做某种物料(海报、易拉宝、工服、包装盒等)，你需要输出这个物料的设计创意。
---
```

```markdown
# iwen-creative — 为iwen餐厅生成符合品牌视觉规范的各类营销物料，输出创意方案

## 品牌核心元素
- 品牌名: iwen餐厅
- 风格: 年轻、潮流、有网感
- IP形象: 布偶猫
- 主色: 薄荷绿 #5DDEB5
- Slogan: A FRESH, MODERN BITE / 健康轻食主义
- 风格: 3D 卡通、清新时尚、年轻活力

## 你的任务
当用户说要做某种物料(海报、易拉宝、工服、包装盒等)，你需要输出这个物料的设计创意描述或图片。

- 你应当使用 `AskUserQuestion` 来询问用户: 是否需要生成图片？
  - 是 → 把创意转化成生图提示词，调用图片生成流程
  - 否 → 直接输出创意描述
- 用户需要生成图片时，你应当使用 `AskUserQuestion` 询问用户输出路径，如果用户没有指定，则默认路径为 `./images`
- 生成图片时你需要调用 `generate_image.py` 脚本，并且按需求参考将 `assets` 下的图片资源作为参数传入脚本

## 输出格式
请按以下格式输出:

### 创意主题
(一句话概括这个设计的核心概念)

### 视觉风格
(整体氛围、配色方向、质感)

### 画面构成
(主体元素、背景、装饰元素的布局描述)

### 细节建议
(一些能让设计更出彩的小细节)

## 图片生成流程
1. 用户描述需求后，确定物料类型

2. 构建详细的图片描述 prompt
   - 如果存在参考图，需要先分析参考图元素，在新的图片中添加参考图元素

**示例**
- 用户说: "做一张新品海报，主推秋季牛排"
- 提示词: "为秋季牛排制作一张促销海报，突出展示菜品并采用温暖的秋季色调，价格 ￥38，并突出 '新品'(NEW) 标识。"

3. 调用生成脚本:
   python .claude/skills/iwen-creative/generate_image.py "具体需求描述" -t 物料类型 -o 输出路径

### 脚本使用说明
- **基本路径**: 必须使用完整路径 `.claude/skills/iwen-creative/generate_image.py`
- **物料类型**: 必须使用英文参数: hat, tshirt, apron, poster, menu, social, coupon, box, banner
- **输出路径**: 可以是目录或完整文件路径
  - 目录: `-o images` 或 `-o ./images`（会自动生成文件名）
  - 文件: `-o ./images/iwen_<物料类型>.png`（指定完整文件名）
  - 脚本会自动创建不存在的目录
```

---

## 调用 Qwen-Image-2.0-Pro API 生成图片

```python
#!/usr/bin/env python3
"""调用 DashScope Qwen-Image-2.0-Pro API 生成图片，支持参考图输入。"""

import os
import sys
import time
import argparse
import json
import urllib.request
import urllib.error
from pathlib import Path

API_ENDPOINT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
API_KEY = "YOUR_API_KEY"
DEFAULT_SIZE = "1024*1024"

VALID_SIZES = {
    "1024*1024": "1:1 方形",
    "1024*1536": "3:4 海报",
    "1536*1024": "4:3 横幅",
    "768*1344": "9:16 竖版",
    "1344*768": "16:9 横版",
}


def get_api_key() -> str:
    return os.environ.get("DASHSCOPE_API_KEY", API_KEY)


def local_image_to_data_uri(path: str) -> str | None:
    """将本地图片转为 base64 data URI，可直接传给 Qwen-Image API。"""
    try:
        import base64
        import mimetypes

        mime_type = mimetypes.guess_type(path)[0] or "image/png"

        with open(path, "rb") as f:
            file_content = f.read()

        b64 = base64.b64encode(file_content).decode("utf-8")
        data_uri = f"data:{mime_type};base64,{b64}"
        return data_uri
    except Exception as e:
        print(f"读取参考图失败 ({path}): {e}")
    return None


def call_api(prompt: str, api_key: str, size: str, ref_images: list[str] | None = None,
             negative_prompt: str = "", n: int = 1, watermark: bool = False,
             retries: int = 2) -> list[str]:
    """调用 Qwen-Image API，返回图片 URL 列表。"""
    content = []
    if ref_images:
        for img_url in ref_images:
            content.append({"image": img_url})
    content.append({"text": prompt})

    payload = json.dumps({
        "model": "qwen-image-2.0-pro",
        "input": {
            "messages": [
                {"role": "user", "content": content}
            ]
        },
        "parameters": {
            "n": n,
            "negative_prompt": negative_prompt,
            "prompt_extend": True,
            "watermark": watermark,
            "size": size,
        }
    }).encode("utf-8")

    req = urllib.request.Request(API_ENDPOINT, data=payload, method="POST")
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Content-Type", "application/json")

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                body = json.loads(resp.read().decode("utf-8"))
                urls = []
                choices = body.get("output", {}).get("choices", [])
                for choice in choices:
                    for item in choice.get("message", {}).get("content", []):
                        if "image" in item:
                            urls.append(item["image"])
                if not urls:
                    print(f"API 返回异常: {json.dumps(body, ensure_ascii=False)[:500]}", file=sys.stderr)
                    sys.exit(1)
                return urls
        except urllib.error.HTTPError as e:
            if e.code == 401:
                print("错误: API Key 无效，请检查 DASHSCOPE_API_KEY", file=sys.stderr)
                sys.exit(1)
            elif e.code == 429:
                if attempt < retries:
                    print(f"频率限制，等待 5 秒后重试 ({attempt + 1}/{retries})...")
                    time.sleep(5)
                else:
                    print("错误: API 频率限制，请稍后重试", file=sys.stderr)
                    sys.exit(1)
            elif 500 <= e.code < 600:
                if attempt < retries:
                    print(f"服务端错误 {e.code}，等待 3 秒后重试 ({attempt + 1}/{retries})...")
                    time.sleep(3)
                else:
                    print(f"错误: 服务端错误 {e.code}，请稍后重试", file=sys.stderr)
                    sys.exit(1)
            else:
                body = e.read().decode("utf-8") if e.fp else ""
                print(f"错误: HTTP {e.code}\n{body}", file=sys.stderr)
                sys.exit(1)
        except urllib.error.URLError as e:
            print(f"错误: 网络请求失败 - {e.reason}", file=sys.stderr)
            sys.exit(1)

    sys.exit(1)


def download_image(url: str, output_path: str):
    urllib.request.urlretrieve(url, output_path)
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="调用 DashScope Qwen-Image API 生成图片"
    )
    parser.add_argument("prompt", help="图像生成 prompt")
    parser.add_argument(
        "-s", "--size", default=DEFAULT_SIZE,
        help=f"图片尺寸。预设: {', '.join(VALID_SIZES.keys())}"
    )
    parser.add_argument(
        "-o", "--output", default=None,
        help="输出图片路径（默认: 自动命名保存到当前目录）"
    )
    parser.add_argument(
        "-r", "--ref", action="append", default=[],
        help="参考图路径（可多次使用，最多 3 张），支持本地文件或 URL"
    )
    parser.add_argument(
        "-n", "--num", type=int, default=1,
        help="生成图片数量 (1-6)"
    )
    parser.add_argument(
        "--list-sizes", action="store_true",
        help="列出预设尺寸并退出"
    )

    args = parser.parse_args()

    if args.list_sizes:
        print("Qwen-Image 预设尺寸：")
        for size, desc in VALID_SIZES.items():
            print(f"  {size} — {desc}")
        return

    api_key = get_api_key()

    # 处理参考图：本地文件转 base64，URL 直接使用
    ref_urls = []
    for ref_path in args.ref:
        if ref_path.startswith("http://") or ref_path.startswith("https://"):
            ref_urls.append(ref_path)
        elif os.path.isfile(ref_path):
            data_uri = local_image_to_data_uri(ref_path)
            if data_uri:
                ref_urls.append(data_uri)
                print(f"参考图已加载: {ref_path}")
            else:
                print(f"警告: 无法读取参考图 {ref_path}，将继续生成", file=sys.stderr)
        else:
            print(f"警告: 参考图不存在: {ref_path}", file=sys.stderr)

    if args.output:
        base = args.output
    else:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        base = f"iwen_{timestamp}.png"

    print(f"模型: qwen-image-2.0-pro")
    print(f"尺寸: {args.size}")
    print(f"Prompt 长度: {len(args.prompt)} 字符")
    print(f"参考图: {len(ref_urls)} 张")
    print(f"正在生成图片...")

    image_urls = call_api(args.prompt, api_key, args.size, ref_urls)
    print(f"图片已生成: {len(image_urls)} 张")

    # 保存图片
    if len(image_urls) == 1:
        print(f"正在下载...")
        dirpart = os.path.dirname(base)
        if dirpart and not os.path.exists(dirpart):
            os.makedirs(dirpart, exist_ok=True)
        download_image(image_urls[0], base)
        print(f"已保存: {base}")
    else:
        for i, url in enumerate(image_urls):
            stem = os.path.splitext(base)[0]
            ext = os.path.splitext(base)[1]
            out = f"{stem}_{i+1}{ext}"
            dirpart = os.path.dirname(out)
            if dirpart and not os.path.exists(dirpart):
                os.makedirs(dirpart, exist_ok=True)
            print(f"正在下载第 {i+1} 张...")
            download_image(url, out)
            print(f"已保存: {out}")


if __name__ == "__main__":
    main()
```

---

## assets — 提供参考图

为了保持品牌的调性、设计的一致性，还可以增加参考图。
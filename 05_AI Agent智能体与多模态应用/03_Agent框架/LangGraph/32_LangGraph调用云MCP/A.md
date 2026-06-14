# ☁️ LangGraph 调用云端 MCP 服务

## 🎯 学习目标

- ✅ 掌握如何查找和使用现成的 MCP Server
- ✅ 了解云端 MCP 服务的优势与使用场景
- ✅ 学会连接云端 MCP 并调用其工具

---

## 📌 核心概念

MCP 的最大优势之一是**生态共享**。社区已经提供了大量现成的 MCP Server，覆盖文件系统、数据库、GitHub、Slack 等常见服务。**不需要自己写，直接连接就能用。**

### 💡 形象比喻：自建 vs 云端

```
🥬 自建 MCP = 自己种菜
   ├─ 从种子开始
   ├─ 费时费力但自由度高
   └─ 适合核心业务

🛒 云端 MCP = 去超市买菜
   ├─ 现成可用
   ├─ 选择丰富，按需购买
   └─ 适合通用能力

✅ 实际项目：两者混合使用
   ├─ 核心业务 → 自建
   └─ 通用能力 → 云端
```

---

## 🔍 参考资源

### MCP 市场平台

- **魔搭社区**：[https://www.modelscope.cn/mcp](https://www.modelscope.cn/mcp)
- **阿里云百炼**：[https://bailian.console.aliyun.com](https://bailian.console.aliyun.com/cn-beijing/?tab=app#/mcp-market)

很多云服务商已经把常用能力封装成了 MCP 服务并托管在云端，开发者只需连接就能用，**不用自己写代码、不用自己部署服务器**。

---

## 💻 代码示例

### 连接云端小说搜索 MCP

```python
import os
import asyncio

from dotenv import load_dotenv
load_dotenv()

# 通义模型配置
tongyi_key = os.environ.get('QWEN_KEY')
os.environ["DASHSCOPE_API_KEY"] = tongyi_key

from langchain_community.chat_models import ChatTongyi
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage


async def main():
    llm = ChatTongyi()
    
    # 连接云端 MCP Server
    client = MultiServerMCPClient(
        {
            "shuqi-novel": {
                "transport": "http",
                "url": "https://dashscope.aliyuncs.com/api/v1/mcps/market-cmapi00072981/mcp",
                "headers": {
                    "Authorization": f"Bearer {tongyi_key}",
                    "Content-Type": "application/json"
                }
            }
        }
    )

    # 获取所有 Server 的工具
    tools = await client.get_tools()
    print(f"可用工具：{[t.name for t in tools]}")

    app = create_agent(llm, tools)

    # 测试问题
    questions = [
        "好评率最高的男生爱看的玄幻小说"
    ]

    for question in questions:
        result = await app.ainvoke({"messages": [HumanMessage(question)]})
        print(f"用户：{question}")
        print(f"AI：{result['messages'][-1].content}")
        print()

if __name__ == '__main__':
    asyncio.run(main())
```

### 运行结果

```
可用工具：['copyrightBookSearch', 'internetBookSearch']

用户：好评率最高的男生爱看的玄幻小说
AI：以下是好评率最高的男生爱看的玄幻小说推荐：

1. 《一剑独尊》- 作者：青鸾峰上（评分：9.6）
   简介：生死看淡，不服就干。诸天神佛仙，不过一剑间！

2. 《斗破苍穹》- 作者：天蚕土豆（评分：9.2）
   简介：无尽世界，位面交汇，万族林立，群雄荟萃...

3. 《师叔，你的法宝太不正经了》- 作者：李别浪（评分：9.2）
   简介：当了半辈子道士的李寒舟中了彩票，本以为能走上人生巅峰...

这些小说都是广受好评的作品，值得一读！
```

---

## 🔄 工作流程

```
1️⃣ 配置云端 MCP Server
   └─ URL + Headers（认证信息）

2️⃣ MultiServerMCPClient 连接到云端服务
   └─ 通过 HTTP 协议通信

3️⃣ 获取云端工具列表
   └─ copyrightBookSearch, internetBookSearch

4️⃣ 创建 Agent 并绑定工具
   └─ Agent 像使用本地工具一样使用云端工具

5️⃣ 用户提问 → Agent 调用云端 API → 返回结果
```

---

## ⚙️ 配置说明

### 云端 MCP 配置要点

```python
"shuqi-novel": {
    "transport": "http",                      # 使用 HTTP 模式
    "url": "https://...",                     # 云端服务地址
    "headers": {
        "Authorization": f"Bearer {token}",   # 认证令牌
        "Content-Type": "application/json"    # 内容类型
    }
}
```

**关键点：**
- 🔑 **认证信息**：大多数云端 MCP 需要 API Key 或 Token
- 🌐 **HTTP 模式**：云端服务必须使用 HTTP/HTTPS
- 📝 **Headers**：根据服务商要求配置请求头

---

## ⚖️ 自建 vs 云端对比

| 特性 | 自建 MCP | 云端 MCP |
|------|---------|---------|
| **开发成本** | 高（需编写代码） | 低（直接使用） |
| **部署维护** | 需自行维护服务器 | 无需维护 |
| **自定义程度** | 完全可控 | 受限于服务商 |
| **响应速度** | 取决于本地网络 | 取决于云服务 |
| **适用场景** | 核心业务逻辑 | 通用能力集成 |
| **成本** | 服务器成本 | API 调用费用 |

---

## 💡 核心要点

- ☁️ **云端 MCP** 提供即插即用的服务能力
- 🔗 **无需部署**：直接连接云端 API
- 🔑 **认证必要**：大部分云端服务需要 API Key
- 🌐 **HTTP 模式**：云端服务统一使用 HTTP 传输
- 🎯 **混合架构**：核心自建 + 通用云端
- 📚 **丰富生态**：社区和云服务商提供大量现成服务

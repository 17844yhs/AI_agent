# Agent Skills 环境搭建

在正式开始之前，还有准备工作要做，那就安装几个软件，用来生成和编写 Skills：

- **VSCode** — 做编辑器
- **Claude Code** — 做 Agent
- **CC Switch** — 配置模型切换

这些软件大家可以自己去官网下载，如果嫌麻烦，也可以在资料包中找到。

---

## 1. VSCode 下载与安装

- 官方地址：https://code.visualstudio.com/

安装流程比较简单，傻瓜式安装即可。

---

## 2. Claude Code 安装

- 官网地址：https://code.claude.com/docs/zh-CN/overview

运行命令安装：

```powershell
irm https://claude.ai/install.ps1 | iex
```

具体流程，可以参考我之前的视频，需要的私信或者评论区留言获取！

---

## 3. CC Switch 安装与使用

CC-Switch 是一个用于切换 Claude Code 供应商（如官方、GLM、DeepSeek）的工具。

- 下载地址：https://github.com/farion1231/cc-switch/releases/tag/v3.10.1
- 安装：Windows 全程点下一步就行了

### 配置 CC Switch

关键步骤：

1. **必须先添加一个官方供应商**（即使没账号），否则可能出错
2. 添加第三方供应商（如 DeepSeek），输入 API Key
3. 点击「启用」你想要的供应商
4. 回到 VSCode 新建终端，输入 `claude` 回车
5. 如果出现登录提示，说明配置未生效，请回到 Switch 重新切换供应商
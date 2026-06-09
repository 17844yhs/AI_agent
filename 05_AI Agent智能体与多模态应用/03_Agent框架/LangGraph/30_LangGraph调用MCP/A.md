# 🔗 LangGraph 调用 MCP 服务

## 🎯 学习目标

- ✅ 理解 `MultiServerMCPClient` 连接多个 Server 的方式
- ✅ 掌握将 MCP 工具转换为 LangChain 工具的方法
- ✅ 了解 MCP 适配器的工作原理与使用场景

---

## 📌 核心概念

LangGraph Agent **不能直接使用** MCP 工具，需要一个"适配器"来转换。**`langchain-mcp-adapters`** 这个包就是桥梁——它把 MCP Server 的工具自动转换为 LangChain 的 `@tool` 格式，Agent 就能像使用本地工具一样使用 MCP 工具。

### 工作流程

```
MCP Server（工具）
    ↓
langchain-mcp-adapters（转换）
    ↓
LangChain @tool
    ↓
Agent 使用
```

### 💡 形象比喻：万能转换器

```
MCP Server = 日版电器（110V接口）
LangGraph Agent = 中国插座（220V接口）
langchain-mcp-adapters = 电压转换器（让两者兼容）
```

---

## 🛠️ 环境准备

### 安装依赖

```bash
uv add langchain-mcp-adapters==0.2.2 langgraph==1.0.6
```

---

## 💻 代码示例

### 完整实现

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
    
    # 连接多个 MCP Server
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["mcp_server1.py"],
                "transport": "stdio",
            },
            "weather": {
                "url": "http://localhost:8000/mcp",
                "transport": "http",
            }
        }
    )

    # 所有 Server 的工具合并为一个列表
    tools = await client.get_tools()
    print(f"可用工具：{[t.name for t in tools]}")

    app = create_agent(llm, tools)

    # 测试不同类型的问题
    questions = [
        "帮我算一下 2的10次方",
        "北京今天天气怎么样？"
    ]

    for question in questions:
        result = await app.ainvoke({"messages": [HumanMessage(question)]})
        print(f"用户：{question}")
        print(f"AI：{result['messages'][-1].content}")
        print()

asyncio.run(main())
```

### 运行结果

```
可用工具：['add', 'multiply', 'power', 'get_weather', 'get_forecast']

用户：帮我算一下 2的10次方
AI：2的10次方等于1024。

用户：北京今天天气怎么样？
AI：北京今天晴天，15-25度，空气质量良好。
```

---

## 🔄 工作流程详解

```
1️⃣ MultiServerMCPClient 连接到配置的 MCP Server
   ├─ math Server（stdio 模式）
   └─ weather Server（HTTP 模式）

2️⃣ 调用 get_tools() 获取所有 Server 上的工具列表
   └─ 返回：[add, multiply, power, get_weather, get_forecast]

3️⃣ langchain-mcp-adapters 自动将 MCP 工具转换为 LangChain Tool
   └─ 透明转换，对 Agent 无感知

4️⃣ 传给 create_agent，Agent 像使用本地工具一样使用它们
   └─ Agent 不知道这些工具来自 MCP

5️⃣ Agent 调用工具时，MCP Client 通过 MCP 协议与 Server 通信
   └─ 自动处理请求和响应
```

---

## ⚙️ 配置说明

### stdio 模式配置

```python
"math": {
    "command": "python",           # 启动命令
    "args": ["mcp_server1.py"],    # 参数
    "transport": "stdio",          # 传输模式
}
```

**特点：**
- 📍 Client 自动启动 Server 子进程
- 🔄 适合本地开发
- 🚫 不支持远程调用

### HTTP 模式配置

```python
"weather": {
    "url": "http://localhost:8000/mcp",  # Server 地址
    "transport": "http",                 # 传输模式
}
```

**特点：**
- 🌐 通过网络连接已运行的 Server
- ✅ 适合生产环境
- 🔄 支持远程调用

---

## ⚠️ 注意事项

| 场景 | 建议 |
|------|------|
| **Web 服务** | 使用 HTTP 模式，让 Server 独立运行 |
| **本地开发** | 可以使用 stdio 模式，快速测试 |
| **简单场景** | 直接用 `@tool` 更轻量，不需要 MCP |
| **多 Server** | 使用 `MultiServerMCPClient` 统一管理 |

### 重要提示

```
⚠️ MCP 的 stdio 模式会在调用工具时启动新的子进程
   └─ 在 Web 服务中可能导致资源浪费
   └─ 建议使用 HTTP 模式

✅ 对于简单场景，直接用 @tool 更轻量
   └─ 不需要跨框架复用
   └─ 不需要连接外部服务
```

---

## 💡 核心要点

- 🔗 **langchain-mcp-adapters** 是 MCP 与 LangGraph 的桥梁
- 🔄 **自动转换**：MCP 工具 → LangChain @tool
- 🌐 **多 Server 支持**：`MultiServerMCPClient` 统一管理
- 📍 **两种模式**：stdio（本地）、HTTP（远程）
- 🎯 **选择原则**：简单用 @tool，复杂用 MCP
- ⚡ **生产建议**：Web 服务使用 HTTP 模式

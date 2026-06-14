# 🏗️ StateGraph 调用 MCP 服务

## 🎯 学习目标

- ✅ 掌握在自定义 StateGraph 中使用 MCP 工具
- ✅ 了解 MCP 工具在自定义 Graph 中与本地工具的混合使用
- ✅ 理解自定义 Agent 流程的构建方法

---

## 📌 核心概念

除了 `create_react_agent` 一行代码创建 Agent 外，还可以在**自定义的 StateGraph** 中使用 MCP 工具。这样可以在 Agent 流程中加入**自定义节点和逻辑**。

### 优势对比

```
create_react_agent：
├─ ✅ 快速上手，一行代码
└─ ❌ 流程固定，难以定制

自定义 StateGraph：
├─ ✅ 灵活控制每个节点
├─ ✅ 可添加自定义逻辑
└─ ✅ 适合复杂业务场景
```

---

## 💻 代码示例

### 完整实现

```python
import os
import asyncio
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool
from langchain_core.messages import HumanMessage

load_dotenv()

# 1. 定义本地工具（和 MCP 工具混合使用）
@tool
def greet(name: str) -> str:
    """打招呼，输入名字"""
    return f"你好 {name}！很高兴认识你。"


async def main():
    llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # 2. 连接 MCP Server
    client = MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["math_server.py"],
                "transport": "stdio",
            }
        }
    )
    mcp_tools = await client.get_tools()

    # 3. 本地工具 + MCP 工具混合
    all_tools = [greet] + mcp_tools
    print(f"全部工具：{[t.name for t in all_tools]}")

    # 4. 构建自定义 StateGraph
    def call_model(state: MessagesState):
        response = llm.bind_tools(all_tools).invoke(state["messages"])
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(all_tools))

    builder.add_edge(START, "call_model")
    # tools_condition: 自动判断是否需要调用工具
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")

    graph = builder.compile()

    # 5. 测试
    questions = [
        "你好，我叫张三",
        "帮我算一下 (10 + 20) x 3"
    ]

    for question in questions:
        result = await graph.ainvoke({"messages": [HumanMessage(question)]})
        print(f"用户：{question}")
        print(f"AI：{result['messages'][-1].content}")
        print()

asyncio.run(main())
```

### 运行结果

```
全部工具：['greet', 'add', 'multiply', 'power']

用户：你好，我叫张三
AI：你好 张三！很高兴认识你。

用户：帮我算一下 (10 + 20) x 3
AI：(10 + 20) x 3 = 90
```

---

## 🔄 工作流程详解

```
1️⃣ 定义本地工具
   └─ @tool 装饰器创建 greet 函数

2️⃣ 连接 MCP Server
   └─ MultiServerMCPClient 连接 math_server.py
   └─ 获取 MCP 工具列表：[add, multiply, power]

3️⃣ 合并工具列表
   └─ all_tools = [greet] + [add, multiply, power]
   └─ 最终：[greet, add, multiply, power]

4️⃣ 构建 StateGraph
   ├─ call_model 节点：LLM 绑定工具并响应
   ├─ tools 节点：ToolNode 执行工具调用
   ├─ START → call_model
   ├─ call_model → tools_condition（条件路由）
   │   ├─ 需要工具 → tools
   │   └─ 不需要工具 → END
   └─ tools → call_model（循环）

5️⃣ 执行对话
   └─ 用户提问 → LLM 判断 → 调用工具 → 返回结果
```

---

## 🎯 关键组件说明

### 1. 工具混合使用

```python
# 本地工具
@tool
def greet(name: str) -> str:
    return f"你好 {name}！"

# MCP 工具
mcp_tools = await client.get_tools()

# 合并
all_tools = [greet] + mcp_tools
```

**优势：**
- ✅ 本地工具：快速实现简单功能
- ✅ MCP 工具：复用外部服务
- ✅ 统一管理：对 LLM 透明

### 2. 自定义节点

```python
def call_model(state: MessagesState):
    response = llm.bind_tools(all_tools).invoke(state["messages"])
    return {"messages": [response]}
```

**作用：**
- 🔗 绑定所有工具到 LLM
- 📨 处理消息历史
- 🔄 返回模型响应

### 3. 条件路由

```python
builder.add_conditional_edges("call_model", tools_condition)
```

**tools_condition 的作用：**
- 🔍 检查 LLM 响应中是否有工具调用
- ➡️ 有工具调用 → 跳转到 tools 节点
- ➡️ 无工具调用 → 直接结束

---

## ⚖️ 两种方式对比

| 特性 | create_react_agent | 自定义 StateGraph |
|------|-------------------|------------------|
| **代码量** | 少（一行） | 多（需手动构建） |
| **灵活性** | 低（固定流程） | 高（完全自定义） |
| **适用场景** | 快速原型、简单 Agent | 复杂业务逻辑 |
| **学习成本** | 低 | 中 |
| **扩展性** | 有限 | 强 |

---

## 💡 核心要点

- 🏗️ **自定义 StateGraph** 提供更高的灵活性
- 🔧 **工具混合**：本地工具 + MCP 工具统一管理
- 🔄 **条件路由**：`tools_condition` 自动判断工具调用
- 📦 **ToolNode**：自动执行工具调用并返回结果
- 🎯 **选择原则**：简单用 `create_react_agent`，复杂用自定义 Graph
- ⚡ **最佳实践**：先在本地工具上验证，再集成 MCP 工具

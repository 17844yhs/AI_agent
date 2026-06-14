# 🎯 学习目标

- 掌握 LangGraph 内置的 `tools_condition` 函数
- 理解 `tools_condition` 与手写 `should_continue` 的等价关系
- 学会用 `tools_condition` 简化 Agent 构建代码

---

## 📖 介绍

上一节我们手写了 `should_continue` 函数来判断 LLM 是否需要调用工具。LangGraph 内置了 **`tools_condition`** 函数，逻辑完全相同，但不用自己写。

---

## 🗺️ 生活化比喻：导航

| 方式 | 类比 | 特点 |
|------|------|------|
| **手写 should_continue** | 自己查地图判断方向 | 灵活但繁琐 ❌ |
| **tools_condition** | 直接打开 GPS 导航，自动规划路线 | 省事高效 ✅ |

**结果一样，但后者省事得多！**

---

## 💻 代码对比

### ❌ 手写版本（上一节）

```python
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

graph.add_conditional_edges("agent", should_continue, {
    "tools": "tools",
    END: END
})
```

### ✅ tools_condition 版本（本节）

```python
from langgraph.prebuilt import tools_condition

graph.add_conditional_edges("agent", tools_condition, {
    "tools": "tools",
    END: END
})
```

---

## 🔍 tools_condition 的内部逻辑

`tools_condition` 的逻辑非常简单，等效于：

```python
# tools_condition 的源码逻辑（简化版）
def tools_condition(state):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END
```

---

## 💻 完整代码示例

```python
import os
from dotenv import load_dotenv
from typing import Annotated, Sequence, TypedDict
from operator import add
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# 1. 定义工具
@tool
def search(query: str) -> str:
    """搜索互联网信息"""
    return f"关于'{query}'的搜索结果：找到3条相关内容"

@tool
def calculator(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{e}"

tools = [search, calculator]

# 2. 定义 State
class AgentState(TypedDict):
    messages: Annotated[Sequence, add]

# 3. Agent 节点
def agent_node(state: AgentState):
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 4. 构建 Graph（用 tools_condition 替代手写的 should_continue）
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition, {  # 内置条件路由
    "tools": "tools",
    END: END
})
graph.add_edge("tools", "agent")

app = graph.compile()

# 5. 测试
result = app.invoke({"messages": "帮我计算 99*88"})
print(f"回复：{result['messages'][-1].content}")
```

### 📊 运行结果

```
回复：计算结果是8712。
```

---

## 📋 对比总结

| 特性 | 手写 should_continue | tools_condition |
|------|---------------------|-----------------|
| **代码量** | 需要编写函数 | ✅ 一行导入即可 |
| **可读性** | ⚠️ 需要理解逻辑 | ✅ 语义清晰 |
| **维护性** | ⚠️ 自定义逻辑需维护 | ✅ 官方维护，稳定 |
| **灵活性** | ✅ 可添加额外逻辑 | ⚠️ 固定逻辑 |
| **适用场景** | 需要特殊判断 | 标准 Agent 流程 |

---

## 💡 最佳实践

### ✅ 推荐使用 tools_condition

```python
# 标准写法
from langgraph.prebuilt import tools_condition

graph.add_conditional_edges("agent", tools_condition, {
    "tools": "tools",
    END: END
})
```

### ⚠️ 何时手写字义

只有在需要**额外判断逻辑**时才手写：

```python
def custom_should_continue(state: AgentState):
    last_message = state["messages"][-1]
    
    # 额外判断：检查消息长度
    if len(state["messages"]) > 10:
        return END  # 超过10轮对话，强制结束
    
    # 使用 tools_condition 的标准逻辑
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END
```

---

## 🎯 核心要点

- ✅ **tools_condition**：LangGraph 内置的条件路由函数
- ✅ **等价关系**：与手写 `should_continue` 逻辑完全相同
- ✅ **简化代码**：减少样板代码，提高可读性
- ✅ **标准写法**：Agent 构建的标准做法
- ✅ **广泛应用**：`create_react_agent` 等高级 API 内部也使用它
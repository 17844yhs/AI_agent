# 🎯 学习目标

- 理解 **ToolNode** 的作用：自动执行 LLM 输出的 `tool_calls`
- 掌握 ToolNode 与 LLM 的协作模式
- 了解 `MessagesState` 的消息追加机制
- 学会手动实现工具执行节点（替代 ToolNode）

---

## 📖 介绍

LLM 输出了 `tool_calls` 指令，但工具并没有真正执行。**ToolNode** 就是 LangGraph 提供的"工具执行器"——接收 LLM 的 `tool_calls`，自动执行对应工具，并将结果包装为 `ToolMessage` 返回。

---

## 🏭 生活化比喻：自动化工厂

| 角色 | 对应组件 | 职责 |
|------|---------|------|
| **设计师** | LLM | 画好图纸（`tool_calls`） |
| **机器人手臂** | ToolNode | 按图纸自动加工 |
| **产品** | ToolMessage | 加工完成的产品，送回给设计师检查 |

---

## 💻 代码示例：Agent 工具调用

### 方式1：使用 ToolNode（推荐）

```python
import os
from dotenv import load_dotenv
from typing import Annotated, Sequence, TypedDict
from operator import add
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

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

# 2. 定义 State（使用 Annotated[Sequence, add] 自动追加消息）
class AgentState(TypedDict):
    messages: Annotated[Sequence, add]

# 3. Agent 节点
def agent_node(state: AgentState):
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# 4. 条件函数：检查 LLM 是否要求调用工具
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# 5. 构建 Graph
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))  # ToolNode 自动执行工具

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {
    "tools": "tools",
    END: END
})
graph.add_edge("tools", "agent")  # 工具执行后返回 Agent 继续思考

app = graph.compile()

# 6. 测试
tests = [
    ("搜索", "搜索最新的AI新闻"),
    ("计算", "帮我计算 25*4+10"),
    ("对话", "你好")
]

for label, question in tests:
    result = app.invoke({"messages": question})
    print(f"[{label}] {question}")
    print(f"回复：{result['messages'][-1].content}")
    print()
```

#### 📊 运行结果

```
[搜索] 搜索最新的AI新闻
回复：根据搜索结果，最新的AI新闻包括...

[计算] 帮我计算 25*4+10
回复：计算结果是110。

[对话] 你好
回复：你好！有什么我可以帮助你的吗？
```

---

### 方式2：手动实现工具节点（灵活控制）

```python
from langchain_core.messages import ToolMessage

# 创建工具字典，方便查找
tools_dict = {tool.name: tool for tool in tools}

def manual_tool_node(state: AgentState):
    """手动处理工具调用"""
    last_message = state["messages"][-1]
    tool_calls = last_message.tool_calls
    
    if not tool_calls:
        return {"messages": []}
    
    tool_messages = []
    
    for tool_call in tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_call_id = tool_call["id"]
        
        print(f"🔧 手动执行工具: {tool_name}({tool_args})")
        
        # 根据工具名称调用对应函数
        if tool_name in tools_dict:
            try:
                # 调用工具函数
                result = tools_dict[tool_name].invoke(tool_args)
                content = str(result)
            except Exception as e:
                content = f"工具执行错误: {e}"
        else:
            content = f"错误：未找到工具 '{tool_name}'"
        
        # 创建工具响应消息
        tool_message = ToolMessage(
            content=content,
            tool_call_id=tool_call_id
        )
        tool_messages.append(tool_message)
    
    return {"messages": tool_messages}

# 使用手动工具节点
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", manual_tool_node)  # 使用手动实现的节点

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {
    "tools": "tools",
    END: END
})
graph.add_edge("tools", "agent")

app = graph.compile()
```

---

## 🔄 Agent 循环详解

### 示例：用户问"帮我计算 25*4+10"

```
第1轮 agent：
  LLM 分析 → 需要计算器 
  → 输出 tool_calls: [calculator("25*4+10")]
  → should_continue 返回 "tools"
      ↓
第1轮 tools：
  ToolNode 执行 calculator("25*4+10")
  → 返回 "计算结果：110"
  → 回到 agent
      ↓
第2轮 agent：
  LLM 看到工具结果 
  → 不需要再调用工具 
  → 直接回复 "计算结果是110"
  → should_continue 返回 END
      ↓
流程结束
```

---

## 📝 Annotated[Sequence, add] 的作用

```python
class AgentState(TypedDict):
    messages: Annotated[Sequence, add]
    # ↑ 每个节点返回的 messages 会被追加到列表中，而不是覆盖
```

### 📋 消息追加过程

```python
# agent 节点返回
{"messages": [AIMessage(tool_calls=[...])]}
→ 追加后：[HumanMessage, AIMessage(tool_calls=[...])]

# tools 节点返回
{"messages": [ToolMessage(content="110")]}
→ 追加后：[HumanMessage, AIMessage(tool_calls=[...]), ToolMessage(content="110")]

# agent 节点再次返回
{"messages": [AIMessage(content="结果是110")]}
→ 追加后：[HumanMessage, AIMessage(tool_calls=[...]), ToolMessage, AIMessage(content="结果是110")]
```

---

## ⚠️ 重要注意事项

### 🔴 必须使用 `add` Reducer

```python
# ✅ 正确：使用 add，消息会追加
messages: Annotated[Sequence, add]

# ❌ 错误：不用 add，后一个节点会覆盖前一个节点的消息
messages: Sequence  # 导致对话历史丢失！
```

### 📋 原因

- Agent 需要**完整的对话历史**才能做出正确决策
- 如果消息被覆盖，LLM 看不到之前的工具调用和结果
- `add` 确保所有消息都被保留

---

## 🔧 ToolNode vs 手动实现对比

| 特性 | ToolNode | 手动实现 |
|------|----------|---------|
| **开发速度** | ✅ 快速，一行代码 | ⚠️ 需要编写完整逻辑 |
| **灵活性** | ⚠️ 固定行为 | ✅ 完全自定义 |
| **错误处理** | ✅ 内置异常处理 | ⚠️ 需手动处理 |
| **日志调试** | ⚠️ 黑盒 | ✅ 可添加详细日志 |
| **适用场景** | 标准 Agent | 需要特殊逻辑的场景 |

### 💡 选择建议

- **优先使用 ToolNode**：90% 的场景都适用
- **手动实现**：需要自定义错误处理、日志记录、权限控制等特殊需求时

---

## 🎯 核心要点

- ✅ **ToolNode**：自动执行 LLM 的 `tool_calls`，返回 `ToolMessage`
- ✅ **Agent 循环**：LLM → ToolNode → LLM，直到不再需要工具
- ✅ **Annotated[Sequence, add]**：消息追加而非覆盖，保持完整对话历史
- ✅ **should_continue**：判断是否需要继续调用工具
- ✅ **标准模式**：Agent + ToolNode 是 LangGraph Agent 的标准架构
- ✅ **手动实现**：提供更大灵活性，适合特殊需求
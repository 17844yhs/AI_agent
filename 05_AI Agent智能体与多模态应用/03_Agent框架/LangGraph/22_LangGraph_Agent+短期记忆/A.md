# 🤖 LangGraph Agent + 短期记忆

## 🎯 学习目标

- ✅ 掌握在带工具的 Agent 中使用 Checkpointer
- ✅ 理解 Agent 记忆与工具调用的协作方式
- ✅ 了解工具调用记录的保存机制

---

## 📌 核心概念

上一节是纯对话场景的记忆。实际开发中，Agent 通常带有**工具调用**，记忆需要同时保存：

- 💬 对话历史
- 🔧 工具调用记录（`tool_calls`）
- 📊 工具返回结果（`ToolMessage`）

`create_agent` 同样支持 `checkpointer` 参数。

---

## 💻 代码示例

### 完整实现

```python
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# 1. 定义工具
@tool
def search(query: str) -> str:
    """搜索信息"""
    return f"关于'{query}'的搜索结果：找到5条相关内容"

@tool
def calculator(expression: str) -> str:
    """计算数学表达式"""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算错误：{e}"

# 2. 创建带记忆的 Agent
memory = MemorySaver()
app = create_agent(
    llm,
    [search, calculator],
    checkpointer=memory  # 关键：传入 checkpointer
)

config = {"configurable": {"thread_id": "agent-001"}}
```

### 多轮对话测试

```python
# 3. 多轮对话（记忆上下文）
conversations = [
    "我叫张三，是一名Python开发者",
    "帮我算一下 1000 + 2000",
    "刚才的计算结果是多少？",
    "我叫什么名字？做什么工作的？"
]

for question in conversations:
    result = app.invoke({"messages": [HumanMessage(question)]}, config)
    print(f"用户：{question}")
    print(f"AI：{result['messages'][-1].content}")
    print()
```

### 运行结果

```
用户：我叫张三，是一名Python开发者
AI：你好张三！很高兴认识你。Python开发是个很好的方向。

用户：帮我算一下 1000 + 2000
AI：1000 + 2000 = 3000

用户：刚才的计算结果是多少？
AI：刚才的计算结果是3000。

用户：我叫什么名字？做什么工作的？
AI：你叫张三，是一名Python开发者。
```

---

## 🔍 记忆中保存了什么？

Checkpointer 保存的完整 State（`messages` 列表）：

```python
[
    HumanMessage("我叫张三，是一名Python开发者"),
    AIMessage("你好张三！..."),
    
    HumanMessage("帮我算一下 1000 + 2000"),
    AIMessage("", tool_calls=[calculator("1000+2000")]),  # 工具调用也保存
    ToolMessage("3000"),                                   # 工具结果也保存
    AIMessage("1000 + 2000 = 3000"),
    
    HumanMessage("刚才的计算结果是多少？"),
    AIMessage("刚才的计算结果是3000。"),
    
    ...
]
```

### 关键点

- ✅ 每次 `invoke` 时，完整的历史都会被恢复并发送给 LLM
- ✅ **工具调用记录**（`tool_calls`）会被保存
- ✅ **工具返回结果**（`ToolMessage`）会被保存
- ✅ LLM 能看到之前做了什么操作、得到了什么结果

---

## 🎯 工作流程

```
第1轮：用户提问 → Agent 思考 → 调用工具 → 获取结果 → 回复用户
       ↓
   Checkpointer 保存完整 State（含工具调用记录）

第2轮：用户提问 → Checkpointer 恢复历史 → Agent 看到完整上下文
       → 可以引用之前的工具结果 → 回复用户
```

---

## ⚠️ 注意事项

| 特性 | 说明 |
|------|------|
| **保存内容** | 对话历史 + 工具调用 + 工具结果 |
| **适用场景** | 需要记住工具执行结果的 Agent |
| **存储位置** | 内存中（程序重启后数据丢失） |
| **生产环境** | 请使用 `PostgresSaver` 持久化存储 |

---

## 💡 核心要点

- 🔑 **`checkpointer`** 不仅保存对话，还保存工具调用链
- 🔄 相同 `thread_id` 的调用会自动恢复完整上下文
- 🛠️ LLM 可以看到之前的工具执行过程和结果
- 🗄️ 不同 `thread_id` 的会话完全独立

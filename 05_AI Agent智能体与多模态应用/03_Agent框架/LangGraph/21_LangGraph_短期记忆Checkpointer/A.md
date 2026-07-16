# 🧠 LangGraph 短期记忆：Checkpointer

## 🎯 学习目标

- ✅ 掌握 `MemorySaver` 作为 Checkpointer 的基本用法
- ✅ 理解 `thread_id` 实现会话隔离的机制
- ✅ 了解 Checkpointer 的工作原理与适用场景

---

## 📌 核心概念

**短期记忆**是最常用的记忆方式：每次 Graph 执行后自动保存 State，下次通过相同的 `thread_id` 恢复。用户感觉就像 AI "记住"了之前的对话。

### 💡 形象比喻

```
📒 没有记忆的 Agent = 每次对话都从第一页开始看
📖 有记忆的 Agent = 记住上次看到第几页，继续往下看
🔑 thread_id = 不同的笔记本，互不干扰
```

---

## 🔍 有无 Checkpointer 对比

### ❌ 没有 Checkpointer

```python
第1轮：invoke({"messages": ["我叫张三"]}) 
      → AI：你好张三
    
第2轮：invoke({"messages": ["我叫什么？"]}) 
      → AI：不知道（因为 State 未保存）❌
```

### ✅ 有 Checkpointer

```python
第1轮：invoke({"messages": ["我叫张三"]}, thread_id="001")
      → AI：你好张三
      → State自动保存：[Human("我叫张三"), AI("你好张三")]

第2轮：invoke({"messages": ["我叫什么？"]}, thread_id="001")
      → 自动恢复State：[Human("我叫张三"), AI("你好张三"), Human("我叫什么？")]
      → AI：你叫张三 ✅
```

---

## 💻 代码示例

### 完整实现

```python
import os
from dotenv import load_dotenv
from typing import Annotated, Sequence, TypedDict
from operator import add
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# 1. 定义 State
class ChatState(TypedDict):
    messages: Annotated[Sequence, add]

# 2. 定义聊天节点
def chat_node(state: ChatState):
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

# 3. 构建 Graph
graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.set_entry_point("chat")
graph.add_edge("chat", END)

# 4. 关键：添加 Checkpointer
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# 5. 使用 thread_id 区分不同会话
config_a = {"configurable": {"thread_id": "user-alice"}}
config_b = {"configurable": {"thread_id": "user-bob"}}
```

### 多用户会话测试

```python
# === 用户A的对话 ===
print("=== 用户A ===")

result = app.invoke({"messages": [HumanMessage("我叫张三")]}, config_a)
print(f"第1轮 AI：{result['messages'][-1].content}")

result = app.invoke({"messages": [HumanMessage("我25岁，住在北京")]}, config_a)
print(f"第2轮 AI：{result['messages'][-1].content}")

result = app.invoke({"messages": [HumanMessage("我叫什么名字？多大？住哪？")]}, config_a)
print(f"第3轮 AI：{result['messages'][-1].content}")

# === 用户B的对话（独立的会话） ===
print("\n=== 用户B ===")

result = app.invoke({"messages": [HumanMessage("我叫什么名字？")]}, config_b)
print(f"用户B问 AI：{result['messages'][-1].content}")

# === 用户A继续对话（记忆还在） ===
print("\n=== 用户A继续 ===")

result = app.invoke({"messages": [HumanMessage("你还记得我喜欢什么吗？")]}, config_a)
print(f"用户A问 AI：{result['messages'][-1].content}")
```

### 运行结果

```
=== 用户A ===
第1轮 AI：你好张三！很高兴认识你。
第2轮 AI：25岁住在北京，是个好年纪！
第3轮 AI：你叫张三，25岁，住在北京。

=== 用户B ===
用户B问 AI：抱歉，我不知道你的名字。

=== 用户A继续 ===
用户A问 AI：根据我们之前的对话，你提到了住在北京，但我还不清楚你具体喜欢什么。
```

---

## ⚙️ Checkpointer 工作原理

### 第一次调用

```python
invoke({"messages": [HumanMessage("你好")]}, thread_id="001")

步骤：
1️⃣ MemorySaver 检查 thread_id="001" 是否有历史 State
   → 没有历史，从空 State 开始

2️⃣ 执行 Graph 节点（chat_node）
   → State 变为：[HumanMessage("你好"), AIMessage("你好！")]

3️⃣ Graph 执行完毕，MemorySaver 自动保存 State
   → thread_id="001" → [HumanMessage("你好"), AIMessage("你好！")]
```

### 第二次调用

```python
invoke({"messages": [HumanMessage("我叫张三")]}, thread_id="001")

步骤：
1️⃣ MemorySaver 检查 thread_id="001" 的历史 State
   → 恢复：[HumanMessage("你好"), AIMessage("你好！")]

2️⃣ 新消息追加到 State
   → [HumanMessage("你好"), AIMessage("你好！"), HumanMessage("我叫张三")]

3️⃣ 执行 chat_node，LLM 看到完整对话历史
   → AI 知道之前说过"你好"

4️⃣ 保存更新后的 State
```

---

## ⚠️ 注意事项

| 特性               | 说明                               |
| ------------------ | ---------------------------------- |
| **存储位置** | 内存中（程序重启后数据丢失）       |
| **适用场景** | 开发测试阶段                       |
| **生产环境** | 请使用`PostgresSaver` 持久化存储 |

---

## 🎯 关键要点

- 🔑 **`thread_id`** 是会话隔离的核心标识
- 💾 **Checkpointer** 在每次 Graph 执行后自动保存 State
- 🔄 相同 `thread_id` 的调用会自动恢复历史上下文
- 🗄️ 不同 `thread_id` 的会话完全独立，互不干扰

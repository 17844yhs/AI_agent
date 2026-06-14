# 🎯 学习目标

- 理解 `interrupt()` 的作用：暂停 Graph 执行等待人工输入
- 掌握 `Command(resume=...)` 恢复执行的方式
- 了解 interrupt 在审批、确认等场景中的应用

---

## 📖 介绍

有些场景需要在流程中间**暂停**，等人工确认后再继续。例如：

- ✅ 发送邮件前需要人工审核
- ✅ 删除数据前需要确认
- ✅ 重要操作需要审批

LangGraph 的 `interrupt()` 就是为此设计的。

---

## 📦 生活化比喻：快递签收

| 方式 | 行为 | 结果 |
|------|------|------|
| **正常流程** | 快递直接放门口 | 无人确认 ❌ |
| **interrupt** | 快递员敲门等你签字 | 签完后他才离开 ✅ |
| **Command(resume)** | 你签字确认 | 快递员继续送下一单 🎯 |

---

## 💻 代码示例：文案审批流程

```python
import os
import uuid
from dotenv import load_dotenv
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

class ReviewState(TypedDict):
    topic: str
    draft: str
    approved: bool
    final: str

def draft_node(state: ReviewState):
    """起草节点：生成文案"""
    response = llm.invoke(f"请为以下主题写一段简短的产品介绍文案：{state['topic']}")
    return {"draft": response.content}

def review_node(state: ReviewState):
    """审批节点：暂停等待人工确认"""
    # interrupt 会暂停执行，返回值是人工输入的回复
    human_decision = interrupt(
        f"请审核以下文案：\n{state['draft']}\n\n是否通过？（通过/拒绝）"
    )
    approved = human_decision == "通过"
    return {"approved": approved}

def result_node(state: ReviewState):
    """结果节点：根据审批结果输出"""
    if state["approved"]:
        return {"final": f"文案已通过，将发布上线：\n{state['draft']}"}
    else:
        return {"final": "文案未通过，流程结束。"}

# 构建 Graph
graph = StateGraph(ReviewState)
graph.add_node("draft", draft_node)
graph.add_node("review", review_node)
graph.add_node("result", result_node)

graph.set_entry_point("draft")
graph.add_edge("draft", "review")
graph.add_edge("review", "result")
graph.add_edge("result", END)

# 关键：需要 Checkpointer 才能使用 interrupt
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# A. 开启一个新的审批任务
thread_id = str(uuid.uuid4())  # 动态生成 ID
config = {"configurable": {"thread_id": thread_id}}

# 第一次调用：会在 review_node 暂停
print("=== 第一次调用 ===")
result = app.invoke({
    "topic": "智能手表",
    "draft": "",
    "approved": False,
    "final": ""
}, config)
print(f"起草完成，等待审核...")

# 人工审核后，用 Command 恢复执行
print("\n=== 人工审核通过，恢复执行 ===")
result2 = app.invoke(
    Command(resume="通过"),
    config
)
print(result2["final"])
```

### 📊 运行结果

```
=== 第一次调用 ===
起草完成，等待审核...

=== 人工审核通过，恢复执行 ===
文案已通过，将发布上线：
这款智能手表集健康监测、运动追踪...
```

---

## 🔑 工作流程

```
起草文案 → interrupt 暂停 → 人工审核 → Command 恢复 → 输出结果
              ↓                    ↓
          等待输入            通过/拒绝
```

---

## ⚠️ 重要注意事项

### 🔴 必须配合 Checkpointer 使用

```python
# ✅ 正确：使用 MemorySaver 保存状态
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# ❌ 错误：没有 checkpointer，无法使用 interrupt
app = graph.compile()  # 会报错！
```

### 📋 原因

- `interrupt()` 需要保存中间状态
- 恢复执行时需要从检查点读取
- 没有 Checkpointer 无法实现暂停/恢复机制

---

## 🎯 核心要点

- ✅ **interrupt = 暂停执行**：等待人工输入或确认
- ✅ **Command(resume) = 恢复执行**：传入人工决策结果
- ✅ **必须使用 Checkpointer**：保存和恢复中间状态
- ✅ **典型应用**：审批流程、人工审核、敏感操作确认
- ✅ **thread_id**：每个任务需要唯一的线程 ID
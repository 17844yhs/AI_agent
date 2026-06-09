# 🔄 LangGraph 人机协作：反馈模式

## 🎯 学习目标

- ✅ 掌握让人类修改 Agent 输出并重新提交的方法
- ✅ 理解反馈循环的实现方式
- ✅ 学会构建"生成→审核→修改→确认"的工作流

---

## 📌 核心概念

除了审批（批准/拒绝），Human-in-the-Loop 的另一个重要模式是**反馈修正**。Agent 生成内容后暂停，人类可以修改、补充、或要求 Agent 重新生成，直到满意为止。

### 💡 形象比喻：文档审阅

```
📝 Agent 写好报告 → 提交给领导审阅

✍️ 领导批注："第三段数据不对，第五段语气太生硬"

🔄 Agent 根据批注修改 → 再次提交

✅ 领导："可以了" → 定稿
```

---

## 🔄 反馈循环流程

```
┌─────────────┐
│  用户需求    │
└──────┬──────┘
       ↓
┌─────────────┐
│ 生成草稿     │ ←────┐
└──────┬──────┘      │
       ↓             │
┌─────────────┐      │
│ 人类审核     │      │
└──────┬──────┘      │
       ↓             │
   需要修改？         │
   ╱        ╲        │
  是        否       │
   ↓         ↓       │
┌──────┐ ┌──────┐   │
│修改草稿│ │批准发送│   │
└──┬───┘ └──┬───┘   │
   │        ↓       │
   └────────┘       │
       ↓            │
    完成 ✅          │
```

---

## 💻 代码示例：邮件撰写助手

### 1. 定义状态

```python
import os
from dotenv import load_dotenv
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

class EmailState(TypedDict):
    requirement: str      # 用户需求
    draft: str           # 邮件草稿
    feedback: str        # 人类反馈
    final_email: str     # 最终邮件
    status: str          # draft / approved / rejected
```

### 2. 构建工作流节点

#### 生成邮件草稿

```python
def generate_draft(state: EmailState) -> dict:
    """生成邮件草稿"""
    response = llm.invoke([
        SystemMessage(content="你是一个商务邮件撰写助手。根据用户需求写一封专业的邮件。"),
        HumanMessage(content=f"请根据以下需求撰写邮件：\n{state['requirement']}")
    ])
    return {"draft": response.content, "status": "draft"}
```

#### 人类审核

```python
def human_review(state: EmailState) -> dict:
    """人类审核：暂停等待反馈"""
    feedback = interrupt(
        f"📧 邮件草稿已生成，请审核：\n\n"
        f"{'='*40}\n"
        f"{state['draft']}\n"
        f"{'='*40}\n\n"
        f"请提供反馈：\n"
        f"- 输入 'approve' 批准发送\n"
        f"- 输入修改意见，我将修改后重新提交"
    )
    return {"feedback": feedback}
```

#### 处理反馈

```python
def process_feedback(state: EmailState) -> dict:
    """处理人类反馈"""
    if state["feedback"].strip().lower() == "approve":
        return {"status": "approved", "final_email": state["draft"]}

    # 有修改意见，根据反馈修改草稿
    response = llm.invoke([
        SystemMessage(content="你是一个商务邮件撰写助手。根据反馈修改邮件。"),
        HumanMessage(content=f"原始邮件：\n{state['draft']}\n\n修改意见：\n{state['feedback']}")
    ])
    return {"draft": response.content, "status": "draft"}
```

#### 判断是否继续

```python
def should_continue(state: EmailState) -> str:
    """判断是继续修改还是结束"""
    if state["status"] == "approved":
        return "send"
    return "revise"
```

### 3. 构建 Graph

```python
builder = StateGraph(EmailState)

builder.add_node("generate", generate_draft)
builder.add_node("review", human_review)
builder.add_node("revise", process_feedback)
builder.add_node("send", lambda state: {
    "final_email": state["draft"],
    "status": "sent"
})

builder.add_edge(START, "generate")
builder.add_edge("generate", "review")
builder.add_edge("review", "revise")
builder.add_conditional_edges("revise", should_continue, {
    "send": "send",
    "revise": "review"  # 修改后再审，形成循环
})
builder.add_edge("send", END)

app = builder.compile(checkpointer=MemorySaver())
```

### 4. 使用示例

#### 第1步：提交需求

```python
config = {"configurable": {"thread_id": "email-001"}}

result = app.invoke(
    {
        "requirement": "给客户王总发一封项目进度汇报邮件，说明本月完成了用户系统重构，下周开始做支付模块",
        "status": ""
    },
    config
)
# → Agent 生成草稿，触发 interrupt 等待审核
```

#### 第2步：人类审核并给出修改意见

```python
result = app.invoke(
    Command(resume="语气太正式了，加上一句感谢王总上次提出的建议"),
    config
)
# → Agent 根据反馈修改，再次触发 interrupt 等待审核
```

#### 第3步：人类批准

```python
result = app.invoke(
    Command(resume="approve"),
    config
)
print(f"最终邮件：\n{result['final_email']}")
```

---

## 🔄 工作流程详解

```
第1轮：生成草稿
  用户需求 → generate_draft → 生成邮件草稿
  → human_review → interrupt 暂停 ⏸️

第2轮：反馈修改
  人类反馈 → process_feedback → 根据反馈修改
  → human_review → interrupt 暂停 ⏸️
  （可重复多轮）

第3轮：批准发送
  人类输入 "approve" → process_feedback → status = approved
  → should_continue → send → 完成 ✅
```

---

## 🔑 关键要点

### 反馈循环机制

```python
# 核心循环
review → revise → review → revise → ... → approve

# 退出条件
if feedback == "approve":
    status = "approved"
    → 跳出循环，发送邮件
```

### 必要条件

- ✅ **必须启用 checkpointer**：保存中断状态和循环历史
- ✅ **使用 Command(resume=...)**：传递人类反馈
- ✅ **相同 thread_id**：确保恢复到正确的会话
- ✅ **状态管理**：通过 `status` 字段控制流程

---

## 💡 核心要点

- 🔄 **反馈循环**：生成 → 审核 → 修改 → 再审核，直到满意
- ✍️ **人类反馈**：可以是修改意见或直接批准
- ⏸️ **interrupt 暂停**：每次审核后等待人类决策
- 📋 **状态管理**：通过 `status` 字段控制流程走向
- 🎯 **适用场景**：文档撰写、代码审查、内容创作等需要迭代的任务
- 🔁 **循环设计**：`add_conditional_edges` 实现灵活的反馈循环

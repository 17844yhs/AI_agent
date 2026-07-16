# ✅ LangGraph 人机协作：审批模式

## 🎯 学习目标

- ✅ 掌握在工具调用前插入人工审批的方法
- ✅ 实现批准/拒绝的工作流
- ✅ 理解 interrupt 机制的工作原理

---

## 📌 核心概念

最常见的 HITL 场景是**工具执行前审批**。Agent 决定调用某个工具（如退款、删除、发送邮件），但在实际执行前暂停，展示操作详情给人类确认。

### 💡 形象比喻：银行转账

```
🏦 Agent = 网银系统，处理转账请求

❌ 没有 HITL = 输入金额直接转账（危险）

✅ 有 HITL = 显示转账详情 → 弹出确认框 → 人类确认后才执行（安全）
```

---

## 💻 代码示例：退款审批 Agent

### 1. 定义需要审批的工具

```python
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt, Command
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# 查询订单（无需审批）
@tool
def query_order(order_id: str) -> str:
    """查询订单信息。"""
    orders = {
        "ORD001": {"status": "已签收", "amount": "299元", "item": "蓝牙耳机"},
        "ORD002": {"status": "已签收", "amount": "5999元", "item": "笔记本电脑"},
        "ORD003": {"status": "配送中", "amount": "89元", "item": "手机壳"},
    }
    order = orders.get(order_id)
    if order:
        return f"订单{order_id}：{order['item']}，金额{order['amount']}，状态-{order['status']}"
    return f"未找到订单 {order_id}"

# 处理退款（需要审批）
@tool
def process_refund(order_id: str, reason: str) -> str:
    """处理退款。此操作需要人工审批。"""
    # 在工具执行前暂停，等待人类审批
    approval = interrupt(
        f"⚠️ 退款审批请求\n"
        f"订单号：{order_id}\n"
        f"退款原因：{reason}\n"
        f"请确认是否批准退款？"
    )
    # approval 是人类通过 Command(resume=...) 传入的值
    if approval == "approve":
        return f"✅ 订单{order_id}退款已处理，预计1-3个工作日到账"
    else:
        return f"❌ 订单{order_id}退款已被拒绝"

# 搜索商品（无需审批）
@tool
def search_products(keyword: str) -> str:
    """搜索商品。"""
    return f"搜索到3个与'{keyword}'相关的商品：商品A(99元)、商品B(199元)、商品C(299元)"

tools = [query_order, process_refund, search_products]
```

### 2. 构建 Agent

```python
def call_model(state: MessagesState):
    response = llm.bind_tools(tools).invoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "call_model")
builder.add_conditional_edges("call_model", tools_condition)
builder.add_edge("tools", "call_model")

# 必须启用 checkpointer！
app = builder.compile(checkpointer=MemorySaver())
```

### 3. 测试流程

#### 第1轮：查询订单（无需审批）

```python
config = {"configurable": {"thread_id": "refund-001"}}

print("=== 第1轮：查询订单（无需审批）===")
result = app.invoke(
    {"messages": [HumanMessage("帮我查一下ORD002订单")]},
    config
)
print(f"AI：{result['messages'][-1].content}")
```

**输出：**
```
AI：订单ORD002：笔记本电脑，金额5999元，状态-已签收
```

#### 第2轮：申请退款（触发审批）

```python
print("\n=== 第2轮：申请退款（触发审批）===")
result = app.invoke(
    {"messages": [HumanMessage("我要退款ORD002，商品质量有问题")]},
    config
)
```

**此时 Agent 暂停，显示审批请求：**
```
⚠️ 退款审批请求
订单号：ORD002
退款原因：商品质量有问题
请确认是否批准退款？
```

### 4. 人类审批的两种方式

#### 方式1：批准退款

```python
result = app.invoke(
    Command(resume="approve"),  # 传入 "approve" 批准
    config
)
print(f"AI：{result['messages'][-1].content}")
```

**输出：**
```
AI：✅ 订单ORD002退款已处理，预计1-3个工作日到账
```

#### 方式2：拒绝退款

```python
result = app.invoke(
    Command(resume="reject"),  # 传入 "reject" 拒绝
    config
)
print(f"AI：{result['messages'][-1].content}")
```

**输出：**
```
AI：❌ 订单ORD002退款已被拒绝
```

---

## 🔄 完整交互流程

```
人类：帮我查一下ORD002订单
AI：订单ORD002：笔记本电脑，金额5999元，状态-已签收

人类：我要退款ORD002，商品质量有问题
Agent：（调用process_refund工具 → 触发interrupt → 暂停）

     ⚠️ 退款审批请求
     订单号：ORD002
     退款原因：商品质量有问题
     请确认是否批准退款？

人类：approve（通过Command传入）
Agent：✅ 订单ORD002退款已处理，预计1-3个工作日到账
```

---

## 🛡️ 工具分类：哪些需要审批

### 低风险工具（直接执行）✅

```
├── query_order()      — 查询操作，不修改数据
├── search_products()  — 搜索操作，只读
└── calculator()       — 计算，纯本地操作
```

### 高风险工具（需要审批）⚠️

```
├── process_refund()   — 涉及资金变动
├── send_email()       — 对外发送信息
├── delete_data()      — 删除操作不可逆
└── deploy_code()      — 影响生产环境
```

---

## 🔑 关键要点

### interrupt 机制

```python
approval = interrupt("审批提示信息")
# Agent 在此处暂停，等待人类输入
# 人类通过 Command(resume=...) 恢复执行
```

**工作流程：**
1. **触发 interrupt**：工具执行前暂停
2. **显示审批信息**：向人类展示操作详情
3. **等待人类决策**：批准或拒绝
4. **恢复执行**：根据人类决策继续执行

### 必要条件

- ✅ **必须启用 checkpointer**：保存中断状态
- ✅ **使用 Command(resume=...)**：传递人类决策
- ✅ **相同 thread_id**：确保恢复到正确的会话

---

## 💡 核心要点

- ✅ **interrupt** 在工具执行前暂停，等待人工审批
- 🛡️ **Command(resume=...)** 传递人类决策（批准/拒绝）
- 📋 **工具分类**：低风险直接执行，高风险需要审批
- 💾 **checkpointer 必需**：保存中断状态
- 🔄 **审批流程**：触发 → 暂停 → 决策 → 恢复
- ⚖️ **风险控制**：关键操作必须人工确认

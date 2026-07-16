# LangGraph 人机协作 - 智能审批

## 学习目标

- 掌握根据条件决定是否 `interrupt` 的方法
- 理解**"低风险自动执行、高风险人工审批"**的设计模式

---

## 核心概念

不是所有工具调用都需要人工审批。理想的方式是**智能审批**：
- **低风险操作** → 自动执行
- **高风险操作** → 暂停等待人类确认

判断标准：操作类型、金额大小、影响范围等。

### 类比：支付系统

| 场景 | 风险等级 | 处理方式 |
|------|---------|---------|
| 转账 100 元 | 低风险 | 自动通过 |
| 转账 1 万元 | 中风险 | 需要短信验证 |
| 转账 50 万元 | 高风险 | 需要柜台人工确认 |

Agent 同样遵循此原则，根据操作风险等级决定是否需要人类介入。

---

## 代码示例：智能审批 Agent

### 导入依赖

```python
import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.types import interrupt, Command

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### 定义工具（带风险判断）

#### 1. 低风险工具：直接执行

```python
@tool
def query_order(order_id: str) -> str:
    """查询订单信息。"""
    orders = {
        "ORD001": {"amount": 299, "item": "蓝牙耳机", "status": "已签收"},
        "ORD002": {"amount": 5999, "item": "笔记本电脑", "status": "已签收"},
        "ORD003": {"amount": 89, "item": "手机壳", "status": "配送中"},
    }
    order = orders.get(order_id)
    if order:
        return json.dumps(order, ensure_ascii=False)
    return f"未找到订单 {order_id}"
```

#### 2. 高风险工具：条件审批

```python
@tool
def process_refund(order_id: str, reason: str) -> str:
    """处理退款。大额退款需要人工审批。"""
    orders = {
        "ORD001": {"amount": 299, "item": "蓝牙耳机"},
        "ORD002": {"amount": 5999, "item": "笔记本电脑"},
        "ORD003": {"amount": 89, "item": "手机壳"},
    }
    order = orders.get(order_id, {"amount": 0, "item": "未知"})

    # 根据金额决定是否需要审批
    if order["amount"] >= 1000:
        # 大额退款：需要人工审批
        approval = interrupt(
            f"⚠️ 大额退款审批\n"
            f"订单：{order_id} - {order['item']}\n"
            f"金额：{order['amount']}元\n"
            f"原因：{reason}\n"
            f"此笔退款金额较大，需要确认。"
        )
        if approval != "approve":
            return f"❌ 退款被拒绝：{approval}"

    # 小额退款或已批准：直接执行
    return f"✅ 订单{order_id}({order['item']})退款{order['amount']}元已处理"
```

#### 3. 不可逆操作：强制审批

```python
@tool
def cancel_order(order_id: str) -> str:
    """取消订单。此操作不可逆，需要人工确认。"""
    approval = interrupt(
        f"⚠️ 取消订单确认\n"
        f"订单号：{order_id}\n"
        f"此操作不可逆，确认取消？"
    )
    if approval == "approve":
        return f"✅ 订单{order_id}已取消"
    return f"❌ 取消操作已撤回"

tools = [query_order, process_refund, cancel_order]
```

### 构建 Agent

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

app = builder.compile(checkpointer=MemorySaver())
```

### 测试场景

#### 场景1：小额退款（自动通过）

```python
config = {"configurable": {"thread_id": "smart-001"}}
result = app.invoke(
    {"messages": [HumanMessage("退款ORD003，买错了")]},
    config
)
print(f"AI：{result['messages'][-1].content}")
# 输出：✅ 订单ORD003(手机壳)退款89元已处理
# → 没有触发interrupt，直接执行
```

#### 场景2：大额退款（需要审批）

```python
config = {"configurable": {"thread_id": "smart-002"}}
result = app.invoke(
    {"messages": [HumanMessage("退款ORD002，电脑有质量问题")]},
    config
)
# → 触发interrupt，等待人类确认

# 人类批准
result = app.invoke(Command(resume="approve"), config)
print(f"AI：{result['messages'][-1].content}")
# 输出：✅ 订单ORD002(笔记本电脑)退款5999元已处理
```

---

## 风险分级策略

在工具内部根据条件决定是否调用 `interrupt`。

### 分级示例：转账功能

```python
@tool
def transfer_money(to_account: str, amount: float) -> str:
    """转账"""
    if amount >= 50000:
        # 高风险：必须人工审批
        approval = interrupt(f"⚠️ 大额转账 {amount}元 到 {to_account}，需要确认")
    elif amount >= 5000:
        # 中风险：提示但不强制
        approval = interrupt(f"⚠️ 转账 {amount}元 到 {to_account}，请确认")
    # else: 低风险（<5000），直接执行

    if amount >= 5000 and approval != "approve":
        return "转账已取消"

    return f"已转账 {amount}元 到 {to_account}"
```

---

## 风险等级划分参考

```
低风险（自动执行）：
├── 查询操作（query_order, search）
├── 小额退款（< 1000元）
└── 计算、格式化

中风险（提示确认）：
├── 中等金额退款（1000-5000元）
├── 发送内部邮件
└── 修改非关键数据

高风险（强制审批）：
├── 大额退款（> 5000元）
├── 删除/取消操作
├── 发送外部邮件
└── 影响生产环境的操作
```

---

## 关键要点总结

| 要点 | 说明 |
|------|------|
| **interrupt 机制** | 在工具内部调用 `interrupt()` 暂停执行，等待用户确认 |
| **条件判断** | 根据业务规则（金额、操作类型）决定是否触发中断 |
| **用户确认** | 通过 `Command(resume="approve")` 传递审批结果 |
| **状态持久化** | 使用 `MemorySaver` 保存对话状态，支持断点续传 |
| **设计原则** | 低风险自动执行，高风险人工审批，平衡效率与安全 |

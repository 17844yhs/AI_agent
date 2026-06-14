# 多Agent协作介绍 + Supervisor实现

## 学习目标

- 理解多Agent协作的应用场景
- 掌握 **Supervisor（主管）模式** 的设计思路
- 了解如何用 LangGraph 构建多Agent系统

---

## 一、问题场景：单Agent的局限

### 场景示例

**用户需求**：帮我分析一下苹果公司的股票，然后翻译成英文，最后发邮件给老板

**单Agent执行**：
- ✅ 调用股票查询工具
- ❌ 翻译？没有翻译工具
- ❌ 发邮件？没有邮件工具

**问题**：需要一个"全能"Agent，工具越来越多，提示词越来越长

---

## 二、多Agent协作方案

### 场景示例

**用户需求**：帮我分析一下苹果公司的股票，然后翻译成英文，最后发邮件给老板

**多Agent执行（Supervisor模式）**：
- Supervisor：分析股票？交给"金融Agent"
- Supervisor：翻译？交给"翻译Agent"
- Supervisor：发邮件？交给"邮件Agent"
- ✅ 汇总结果

### 核心问题

单个 Agent 难以处理复杂的多领域任务，需要多个专业 Agent 分工协作。

### 类比：公司团队

```
单Agent = 一个人同时做产品、开发、测试、运维（累死）

多Agent = 产品经理提需求、开发写代码、测试找bug、运维部署（各司其职）

Supervisor = 项目经理，决定每个任务交给谁
```

---

## 三、Supervisor 模式架构

```
┌─────────────────────────────────────────────────────────────┐
│                      用户请求                               │
└───────────────────────────┬─────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Supervisor（主管）                        │
│           分析问题 → 决定交给哪个专业Agent处理                │
└───────────────────────────┬─────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ↓                 ↓                 ↓
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   Tech Agent    │ │   CS Agent      │ │   Direct Agent  │
│  (技术支持)     │ │  (客服专员)      │ │  (直接回答)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      返回结果给用户                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 四、代码示例：客服中心多Agent

### 导入依赖

```python
import os
from dotenv import load_dotenv
from typing import Annotated, Sequence, TypedDict
from operator import add
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END, START
from langchain.agents import create_agent

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### 定义专业Agent

#### 1. 技术支持Agent

```python
@tool
def check_system_status(service_name: str) -> str:
    """检查系统服务状态，输入服务名称。"""
    status = {
        "数据库": "正常运行，响应时间50ms",
        "API网关": "正常运行，QPS 1200",
        "缓存服务": "告警：内存使用率85%"
    }
    return status.get(service_name, f"{service_name}：未找到该服务")

@tool
def restart_service(service_name: str) -> str:
    """重启指定服务。"""
    return f"服务 {service_name} 已重启，预计30秒恢复"

tech_tools = [check_system_status, restart_service]
tech_agent = create_agent(
    llm, tech_tools,
    prompt="你是技术支持专家，负责检查系统状态和处理技术问题。回答要专业简洁。"
)
```

#### 2. 客服Agent

```python
@tool
def query_order(order_id: str) -> str:
    """查询订单信息，输入订单号。"""
    orders = {
        "ORD001": {"status": "已发货", "amount": "299元", "delivery": "预计明天到达"},
        "ORD002": {"status": "处理中", "amount": "1599元", "delivery": "预计3天后发货"},
    }
    order = orders.get(order_id)
    if order:
        return f"订单{order_id}：状态-{order['status']}，金额-{order['amount']}，{order['delivery']}"
    return f"未找到订单 {order_id}"

@tool
def process_refund(order_id: str, reason: str) -> str:
    """处理退款申请，输入订单号和退款原因。"""
    return f"订单{order_id}的退款申请已提交（原因：{reason}），预计1-3个工作日到账"

cs_tools = [query_order, process_refund]
cs_agent = create_agent(
    llm, cs_tools,
    prompt="你是客服专员，负责处理订单查询和退款申请。态度友好，耐心解答。"
)
```

### 定义 Supervisor

```python
class SupervisorState(TypedDict):
    messages: Annotated[Sequence, add]
    next_agent: str

def supervisor_node(state: SupervisorState):
    """Supervisor：分析用户问题，决定交给哪个Agent处理"""
    last_message = state["messages"][-1]
    user_text = last_message.content if hasattr(last_message, "content") else str(last_message)

    prompt = f"""根据用户的问题，判断应该交给哪个团队处理：

选项：
- tech：技术支持团队（系统故障、服务状态、技术问题）
- cs：客服团队（订单查询、退款、售后服务）
- direct：直接回答（问候、简单问答）

用户问题：{user_text}

只回复选项名称（tech/cs/direct），不要其他内容。"""

    response = llm.invoke(prompt)
    choice = response.content.strip().lower()

    if choice not in ("tech", "cs"):
        choice = "direct"

    return {"next_agent": choice}
```

### 定义执行节点

```python
def tech_node(state: SupervisorState):
    """调用技术支持Agent"""
    user_msg = state["messages"][-1]
    result = tech_agent.invoke({"messages": [user_msg]})
    return {"messages": [result["messages"][-1]]}

def cs_node(state: SupervisorState):
    """调用客服Agent"""
    user_msg = state["messages"][-1]
    result = cs_agent.invoke({"messages": [user_msg]})
    return {"messages": [result["messages"][-1]]}

def direct_node(state: SupervisorState):
    """直接回答"""
    user_msg = state["messages"][-1]
    response = llm.invoke(f"你是一个友好的客服中心接待员，请回答：{user_msg.content if hasattr(user_msg, 'content') else user_msg}")
    return {"messages": [AIMessage(response.content)]}

def route_to_agent(state: SupervisorState) -> str:
    return state["next_agent"]
```

### 构建 Supervisor Graph

```python
graph = StateGraph(SupervisorState)
graph.add_node("supervisor", supervisor_node)
graph.add_node("tech", tech_node)
graph.add_node("cs", cs_node)
graph.add_node("direct", direct_node)

graph.add_edge(START, "supervisor")
graph.add_conditional_edges("supervisor", route_to_agent, {
    "tech": "tech",
    "cs": "cs",
    "direct": "direct"
})
graph.add_edge("tech", END)
graph.add_edge("cs", END)
graph.add_edge("direct", END)

app = graph.compile()
```

### 测试多Agent

```python
questions = [
    "你好，请问你们的工作时间是什么？",
    "帮我查一下ORD001订单到哪了",
    "缓存服务有告警，帮我看看",
    "我想退款ORD002，商品有质量问题",
]

for question in questions:
    result = app.invoke({"messages": [HumanMessage(question)], "next_agent": ""})
    print(f"用户：{question}")
    print(f"路由：{result['next_agent']}")
    print(f"回复：{result['messages'][-1].content}")
    print()
```

#### 运行结果

```
用户：你好，请问你们的工作时间是什么？
路由：direct
回复：您好！我们的工作时间是周一至周五 9:00-18:00。

用户：帮我查一下ORD001订单到哪了
路由：cs
回复：订单ORD001：状态-已发货，金额-299元，预计明天到达。

用户：缓存服务有告警，帮我看看
路由：tech
回复：缓存服务告警：内存使用率85%，建议扩容或清理缓存。需要我帮您重启服务吗？

用户：我想退款ORD002，商品有质量问题
路由：cs
回复：订单ORD002的退款申请已提交（原因：商品有质量问题），预计1-3个工作日到账。
```

---

## 五、多Agent架构对比

| 架构 | 结构 | 适用场景 |
|------|------|---------|
| **Supervisor** | 主管 → 分发任务给专业Agent | 需要根据任务类型路由 |
| **Pipeline** | Agent1 → Agent2 → Agent3（串行） | 固定流程，前一个的输出是后一个的输入 |
| **Parallel** | 多个Agent同时工作 → 汇总 | 任务互不依赖，需要加速 |

### 核心要点

**Supervisor 模式是最常用的多Agent架构**：
- 像一个项目经理，把用户请求分给最合适的团队成员处理
- 每个专业Agent可以有自己的工具和提示词，互不干扰
- 扩展性好，新增Agent只需注册到Supervisor即可

---

## 六、关键要点总结

| 要点 | 说明 |
|------|------|
| **Supervisor 职责** | 分析问题、决定路由、调用专业Agent |
| **专业Agent** | 专注特定领域，拥有专属工具和prompt |
| **状态管理** | 通过 `SupervisorState` 传递消息和路由信息 |
| **条件路由** | `add_conditional_edges` 实现动态路由 |
| **扩展性** | 新增Agent只需添加节点和路由规则 |

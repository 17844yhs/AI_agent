# LangGraph 集成 A2A Client

> **目标**：在 LangGraph Agent 中集成 A2A Client，实现用户请求 → Agent 判断 → A2A 委托 → 返回结果的完整流程。

---

## 学习目标

- [x] 掌握在 LangGraph Agent 中集成 A2A Client
- [x] 实现完整的用户请求 → Agent 判断 → A2A 委托 → 返回结果流程

---

## 架构图

```text
用户请求
  ↓
LangGraph 客服 Agent
  ├── greet_customer()   → 本地工具，直接回答
  └── call_refund_agent()  → A2A 工具（@tool 封装）
       ↓
  A2ACardResolver → 发现退款 Agent
  ClientFactory   → 创建 A2A Client
  send_message()  → 发送退款请求
       ↓
  退款 Agent Server（refund_agent_server.py，独立进程）
  RefundAgentExecutor → 执行退款逻辑
       ↓
  返回 Artifact → 客服 Agent → 回复用户
```

---

## 完整代码

```python
import os
import asyncio
from uuid import uuid4

import httpx
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain.tools import tool

# A2A Client 相关
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.types.a2a_pb2 import Message as A2AMessage, Part, Role, SendMessageRequest

load_dotenv()


# ===== 1. 定义工具：通过 A2A 调用退款 Agent =====

@tool
async def call_refund_agent(query: str) -> str:
    """调用退款处理Agent处理退款相关请求。
    当用户需要退款、查询退款进度时使用此工具。
    参数 query: 退款请求的具体内容"""
    async with httpx.AsyncClient() as httpx_client:
        # ① 发现退款 Agent
        card = await A2ACardResolver(
            httpx_client=httpx_client,
            base_url="http://localhost:9999"
        ).get_agent_card()
        # ② 创建 Client（非流式）
        client = ClientFactory(config=ClientConfig(streaming=False)).create(card)

        # ③ 发送退款请求
        request = SendMessageRequest(message=A2AMessage(
            role=Role.ROLE_USER,
            parts=[Part(text=query)],
            message_id=uuid4().hex,
        ))

        # ④ 收集结果
        result_text = ""
        async for resp in client.send_message(request):
            if resp.HasField("artifact_update"):
                for part in resp.artifact_update.artifact.parts:
                    if part.text:
                        result_text += part.text
            elif resp.HasField("task"):
                for artifact in resp.task.artifacts:
                    for part in artifact.parts:
                        if part.text:
                            result_text += part.text

        await client.close()
        return result_text or "退款Agent未返回结果"


# ===== 2. 定义客服问候工具（本地工具，不依赖外部服务）=====

@tool
def greet_customer(name: str) -> str:
    """向客户打招呼。当用户只是打招呼时使用。"""
    return f"您好{name}！我是智能客服，可以帮您处理退款、查询订单等问题。请问有什么可以帮您的？"


# ===== 3. 构建 LangGraph Agent =====

async def main():
    llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    tools = [call_refund_agent, greet_customer]

    def call_model(state: MessagesState):
        system_prompt = SystemMessage(content=(
            "你是一个电商客服助手。你可以：\n"
            "1. 和客户打招呼\n"
            "2. 处理退款相关请求（调用退款Agent）\n"
            "请根据用户的需求选择合适的工具。"
        ))
        messages = [system_prompt] + state["messages"]
        response = llm.bind_tools(tools).invoke(messages)
        return {"messages": [response]}

    # LangGraph：Call Model → 选择工具 → 回到 Model
    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_node("tools", ToolNode(tools))
    builder.add_edge(START, "call_model")
    builder.add_conditional_edges("call_model", tools_condition)
    builder.add_edge("tools", "call_model")
    graph = builder.compile()

    # 测试三轮对话
    questions = [
        "你好，我叫张三",
        "我买的商品有质量问题，帮我退款订单ORD001",
        "顺便帮我查一下退款单RF001的进度",
    ]
    for question in questions:
        print(f"\n👤 用户: {question}")
        result = await graph.ainvoke({"messages": [HumanMessage(content=question)]})
        print(f"🤖 客服: {result['messages'][-1].content}")
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 运行步骤

```bash
# 终端1：启动退款 Agent Server
python a2a_simple_server.py

# 终端2：运行客服 Agent
python a2a_langGraph_client.py
```

### 运行结果

```
👤 用户: 你好，我叫张三
🤖 客服: 您好张三！我是智能客服，可以帮您处理退款、查询订单等问题。请问有什么可以帮您的？
--------------------------------------------------

👤 用户: 我买的商品有质量问题，帮我退款订单ORD001
🤖 客服: ✅ 订单ORD001退款成功！金额299元将在1-3个工作日退回原支付方式。
--------------------------------------------------

👤 用户: 顺便帮我查一下退款单RF001的进度
🤖 客服: 📊 退款单RF001正在处理中，预计今天内完成审核。
--------------------------------------------------
```

---

## 架构总结

```text
用户请求
  ↓
LangGraph 客服 Agent（customer_service_agent.py）
  ├── greet_customer()   → 本地工具，直接回答
  └── call_refund_agent()  → A2A 工具（@tool 封装）
     ↓
  A2ACardResolver → 发现退款 Agent
  ClientFactory  → 创建 A2A Client
  send_message()  → 发送退款请求
     ↓
  退款 Agent Server（refund_agent_server.py，独立进程）
  RefundAgentExecutor → 执行退款逻辑
     ↓
  返回 Artifact → 客服 Agent → 回复用户
```

---

## 关键点

> 💡 **核心设计**：客服 Agent 和退款 Agent 是**完全解耦**的。
>
> - A2A 调用被封装在 `@tool` 里，LangGraph Agent **像使用本地工具一样**调用远程 Agent
> - Agent 不需要知道背后是远程服务还是本地函数
> - **未来替换退款 Agent 的实现，客服 Agent 的代码不需要任何修改**
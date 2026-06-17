# LangGraph 包装为 A2A Server

> **目标**：将 LangGraph Agent 包装成 A2A Server，让其他系统可以通过 A2A 协议调用它。

---

## 学习目标

- [x] 掌握将 LangGraph Agent 包装成 A2A Server

---

## 核心思路

```text
在 AgentExecutor.execute() 里调用 LangGraph 的 graph.ainvoke()
把 LangGraph 的输出结果包装成 A2A Artifact 返回
```

> 💡 **通俗理解**：给 LangGraph Agent 穿上一层 A2A 的外衣，让它能接受 A2A 请求并返回 A2A 格式的响应。

---

## 完整代码

```python
import os
import uvicorn
from starlette.applications import Starlette
from dotenv import load_dotenv

# A2A Server 相关
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill, AgentCapabilities, AgentInterface
from a2a.types.a2a_pb2 import (
    Artifact, Part, Task as ProtoTask,
    TaskArtifactUpdateEvent, TaskState, TaskStatus, TaskStatusUpdateEvent,
)

# LangGraph 相关
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, MessagesState, START, END

load_dotenv()


# ===== 1. 构建 LangGraph Agent（和普通 LangGraph 代码完全一样）=====

def create_graph():
    """创建一个简单的客服 LangGraph"""
    llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )

    def call_model(state: MessagesState):
        system_prompt = SystemMessage(content=(
            "你是一个智能客服助手，可以回答用户关于订单、退款、物流等问题。"
            "请用简洁友好的语气回答。"
        ))
        messages = [system_prompt] + state["messages"]
        response = llm.invoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("call_model", call_model)
    builder.add_edge(START, "call_model")
    builder.add_edge("call_model", END)
    return builder.compile()


# ===== 2. 将 LangGraph 包装成 AgentExecutor =====

class LangGraphExecutor(AgentExecutor):
    """在 execute() 中调用 LangGraph graph，把结果包装成 A2A Artifact"""

    def __init__(self):
        self.graph = create_graph()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_input = context.get_user_input()

        # ① 创建任务（SUBMITTED）
        if context.current_task is None:
            await event_queue.enqueue_event(ProtoTask(
                id=context.task_id, context_id=context.context_id,
                status=TaskStatus(state=TaskState.TASK_STATE_SUBMITTED),
            ))

        # ② 处理中（WORKING）
        await event_queue.enqueue_event(TaskStatusUpdateEvent(
            task_id=context.task_id, context_id=context.context_id,
            status=TaskStatus(state=TaskState.TASK_STATE_WORKING),
        ))

        # ③ 核心：调用 LangGraph graph（把 A2A 请求转发给 LangGraph）
        result = await self.graph.ainvoke(
            {"messages": [HumanMessage(content=user_input)]}
        )
        answer = result["messages"][-1].content

        # ④ 返回 Artifact（把 LangGraph 输出包装成 A2A 格式）
        await event_queue.enqueue_event(TaskArtifactUpdateEvent(
            task_id=context.task_id, context_id=context.context_id,
            artifact=Artifact(parts=[Part(text=answer)]),
        ))

        # ⑤ 完成（COMPLETED）
        await event_queue.enqueue_event(TaskStatusUpdateEvent(
            task_id=context.task_id, context_id=context.context_id,
            status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED),
        ))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("不支持取消")


# ===== 3. 启动 A2A Server =====

if __name__ == "__main__":
    # 注意端口用 9998，和退款 Agent 的 9999 不冲突，可以同时运行
    agent_card = AgentCard(
        name="智能客服Agent",
        description="基于LangGraph的智能客服，可回答订单、退款、物流等问题",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[
            AgentInterface(protocol_binding="JSONRPC", url="http://localhost:9998"),
        ],
        skills=[
            AgentSkill(id="customer-service", name="客服咨询",
                       description="回答客户问题",
                       tags=["客服", "咨询"],
                       examples=["我的订单到哪了？"]),
        ],
    )

    handler = DefaultRequestHandler(
        agent_executor=LangGraphExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )
    routes = [*create_agent_card_routes(agent_card),
              *create_jsonrpc_routes(handler, "/")]

    print("🚀 LangGraph A2A Server 启动: http://localhost:9998")
    uvicorn.run(Starlette(routes=routes), host="127.0.0.1", port=9998)
```

---

## 用极简 Client 测试

```python
import asyncio
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.types.a2a_pb2 import Message, Part, Role, SendMessageRequest
from uuid import uuid4


async def main():
    async with httpx.AsyncClient() as c:
        card = await A2ACardResolver(
            httpx_client=c,
            base_url='http://localhost:9998'
        ).get_agent_card()
        print(f'发现 Agent: {card.name}')

        client = ClientFactory(config=ClientConfig(streaming=False)).create(card)
        req = SendMessageRequest(message=Message(
            role=Role.ROLE_USER,
            parts=[Part(text='我的订单ORD001到哪了？')],
            message_id=uuid4().hex,
        ))

        async for resp in client.send_message(req):
            if resp.HasField('task'):
                for a in resp.task.artifacts:
                    for p in a.parts:
                        if p.text:
                            print(f'回复: {p.text}')

        await client.close()


asyncio.run(main())
```

---

## 代码解析

```text
LangGraph 作为 A2A Server 的关键步骤：

第1步：照常写 LangGraph Agent（create_graph）
      └── 和以前完全一样，不需要任何 A2A 相关的代码

第2步：在 AgentExecutor.execute() 中调用 graph.ainvoke()
      └── 这是核心：把 A2A 收到的用户请求传给 LangGraph

第3步：把 LangGraph 的输出包装成 A2A Artifact 返回
      └── answer = result["messages"][-1].content
      └── Artifact(parts=[Part(text=answer)])

第4步：端口用 9998（和退款 Agent 的 9999 不冲突，可以同时运行）
```

---

## 整体架构回顾

```text
┌─────────────────────────────────────────────────┐
│  A2A Client（任意语言/框架）                     │
│  └── A2ACardResolver → ClientFactory → send     │
└────────────────────┬────────────────────────────┘
                     │ A2A JSON-RPC
                     ▼
┌─────────────────────────────────────────────────┐
│  A2A Server（本示例）                            │
│  ┌─────────────────────────────────────────┐   │
│  │  LangGraphExecutor.execute()            │   │
│  │  └── graph.ainvoke(user_input)          │   │
│  │      └── ChatOpenAI → LLM 回答          │   │
│  └─────────────────────────────────────────┘   │
│  端口: 9998                                    │
└─────────────────────────────────────────────────┘
```

> 💡 **一句话总结**：给 LangGraph 包一层 `AgentExecutor`，它就变成了一个 A2A Agent，任何遵守 A2A 协议的 Client 都能调用它。
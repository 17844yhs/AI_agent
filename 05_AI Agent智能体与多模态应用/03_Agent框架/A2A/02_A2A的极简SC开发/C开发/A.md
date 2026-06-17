# A2A 极简 Server → Client 开发

> **目标**：用最少代码跑通 A2A 完整链路，理解通信核心流程。
>
> **思路**：先用最简单的 Echo Agent 跑通骨架，后续再加业务逻辑。

---

## 学习目标

- [x] 用少量代码跑通 A2A 完整链路：Server → Client
- [x] 理解 A2A 通信核心流程：创建任务 → 返回结果

---

## 核心流程概览

```text
Server 端 (EchoExecutor.execute)：
  ① SUBMITTED  → 告诉 Client "我收到请求了"
  ② WORKING    → 告诉 Client "我在处理"
  ③ Artifact   → 告诉 Client "这是结果"
  ④ COMPLETED  → 告诉 Client "处理完毕"

Client 端：
  ① A2ACardResolver  → 读取 Agent Card（发现 Agent）
  ② ClientFactory    → 创建 Client 实例
  ③ send_message()   → 发送请求，接收 StreamResponse
  ④ HasField()       → 判断响应类型（task / artifact_update / status_update）
```

---

## Server 代码

```python
import uvicorn
from starlette.applications import Starlette
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill, AgentCapabilities, AgentInterface
from a2a.types.a2a_pb2 import (
    Artifact, Message, Part, Role, Task as ProtoTask,
    TaskArtifactUpdateEvent, TaskState, TaskStatus, TaskStatusUpdateEvent,
)


class EchoExecutor(AgentExecutor):
    """最简单的 Executor：原样返回用户输入"""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_input = context.get_user_input()

        # ① 创建任务（SUBMITTED）
        if context.current_task is None:
            await event_queue.enqueue_event(ProtoTask(
                id=context.task_id, context_id=context.context_id,
                status=TaskStatus(state=TaskState.TASK_STATE_SUBMITTED),
            ))

        # ② 状态更新：处理中（WORKING）
        await event_queue.enqueue_event(TaskStatusUpdateEvent(
            task_id=context.task_id, context_id=context.context_id,
            status=TaskStatus(state=TaskState.TASK_STATE_WORKING),
        ))

        # ③ 返回结果（Artifact）
        await event_queue.enqueue_event(TaskArtifactUpdateEvent(
            task_id=context.task_id, context_id=context.context_id,
            artifact=Artifact(parts=[Part(text=f"Echo: {user_input}")]),
        ))

        # ④ 状态更新：完成（COMPLETED）
        await event_queue.enqueue_event(TaskStatusUpdateEvent(
            task_id=context.task_id, context_id=context.context_id,
            status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED),
        ))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("不支持取消")


if __name__ == "__main__":
    # 配置 Agent Card（描述 Agent 身份和能力）
    agent_card = AgentCard(
        name="Echo Agent",
        description="原样返回用户输入",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[AgentInterface(
            protocol_binding="JSONRPC", url="http://localhost:9999"
        )],
        skills=[AgentSkill(id="echo", name="回声",
                           description="原样返回输入", tags=["echo"])],
    )

    handler = DefaultRequestHandler(
        agent_executor=EchoExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )

    routes = [*create_agent_card_routes(agent_card),
              *create_jsonrpc_routes(handler, "/")]
    print("🚀 Echo Agent 启动: http://localhost:9999")
    uvicorn.run(Starlette(routes=routes), host="127.0.0.1", port=9999)
```

> 💡 **Server 端要点**：
>
> - `AgentExecutor.execute()` 是核心入口，负责处理请求并发送事件
> - 事件队列（`EventQueue`）按顺序发送状态更新和结果
> - `AgentCard` 相当于 Agent 的名片，Client 通过它发现和调用 Agent

---

## Client 代码

```python
import asyncio
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.types.a2a_pb2 import Message, Part, Role, SendMessageRequest


async def main():
    async with httpx.AsyncClient() as httpx_client:
        # ① 发现 Agent（读取 Agent Card）
        card = await A2ACardResolver(
            httpx_client=httpx_client,
            base_url="http://localhost:9999"
        ).get_agent_card()
        print(f"发现 Agent: {card.name}")

        # ② 创建 Client + 发送消息
        client = ClientFactory(config=ClientConfig(streaming=False)).create(card)
        request = SendMessageRequest(message=Message(
            role=Role.ROLE_USER,
            parts=[Part(text="你好，A2A！")],
            message_id=uuid4().hex,
        ))

        # ③ 接收结果（非流式）
        #     非流式模式下，SDK 聚合为单个 task 响应，artifact 在 task.artifacts 里
        async for resp in client.send_message(request):
            if resp.HasField("task"):
                for artifact in resp.task.artifacts:
                    for part in artifact.parts:
                        if part.text:
                            print(f"结果: {part.text}")
            elif resp.HasField("artifact_update"):
                for part in resp.artifact_update.artifact.parts:
                    if part.text:
                        print(f"结果: {part.text}")

        await client.close()


asyncio.run(main())
```

> 💡 **Client 端要点**：
>
> - `A2ACardResolver` 通过 HTTP 获取 Agent Card（服务发现）
> - `ClientFactory` 根据 Agent Card 自动创建匹配的 Client
> - `send_message()` 返回 `StreamResponse`，用 `HasField()` 判断响应类型
> - 非流式模式下，SDK 会自动聚合所有事件为完整的 Task 对象

---

## 运行步骤

```bash
# 终端1：启动 Server
python a2a_hello_server.py

# 终端2：运行 Client
python a2a_hello_client.py
```

### 运行结果

```
发现 Agent: Echo Agent
状态: TASK_STATE_SUBMITTED
结果: Echo: 你好，A2A！
```

---

## 进度小结

> ✅ **至此已跑通 A2A 完整链路！** 接下来可以在骨架上添加真实的业务逻辑。

### 关键概念回顾

| 步骤 | Server 端 | Client 端 |
|------|-----------|-----------|
| ① | 定义 AgentCard（身份） | A2ACardResolver（发现） |
| ② | 实现 AgentExecutor（业务） | ClientFactory（创建） |
| ③ | 发送事件到 EventQueue | send_message（请求） |
| ④ | 返回 Artifact + 状态 | HasField 判断响应类型 |
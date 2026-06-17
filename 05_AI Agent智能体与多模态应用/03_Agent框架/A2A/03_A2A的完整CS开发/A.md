# A2A 完整 Client/Server 开发

> **目标**：在极简骨架基础上加入真实业务逻辑，掌握多技能 Agent 的定义和两种调用方式。

---

## 学习目标

- [x] 掌握多技能 Agent 的定义（退款 + 查询）
- [x] 理解非流式和流式两种调用方式的差异

---

## 本示例做了三件事

1. **Server 端** 加入真实的退款业务逻辑（关键词匹配模拟）
2. **Agent Card** 定义多个技能（退款处理 + 退款查询）
3. **Client 端** 分别演示非流式和流式调用

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
from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill
from a2a.types.a2a_pb2 import (
    Artifact, Message, Part, Role, Task as ProtoTask,
    TaskArtifactUpdateEvent, TaskState, TaskStatus, TaskStatusUpdateEvent,
)


# ===== 1. 退款业务逻辑 =====

class RefundAgent:
    """退款处理 Agent 的核心逻辑"""

    async def process_refund(self, query: str) -> str:
        """根据用户输入模拟退款处理"""
        query_lower = query.lower()

        if "ord001" in query_lower:
            return "✅ 订单ORD001退款成功！金额299元将在1-3个工作日退回原支付方式。"
        elif "ord002" in query_lower:
            return "✅ 订单ORD002退款成功！金额5999元将在1-3个工作日退回原支付方式。"
        elif "查询" in query or "进度" in query or "状态" in query:
            return "📊 退款单RF001正在处理中，预计今天内完成审核。"
        else:
            return f"📝 已收到退款请求：「{query}」，正在为您处理。退款将在审核通过后1-3个工作日到账。"


# ===== 2. AgentExecutor（和极简版骨架一样，只是业务逻辑不同）=====

class RefundAgentExecutor(AgentExecutor):

    def __init__(self):
        self.agent = RefundAgent()

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        user_input = context.get_user_input()

        # ① 创建任务（SUBMITTED）
        if context.current_task is None:
            await event_queue.enqueue_event(ProtoTask(
                id=context.task_id, context_id=context.context_id,
                status=TaskStatus(state=TaskState.TASK_STATE_SUBMITTED),
            ))

        # ② 处理中（WORKING）——带上消息说明
        await event_queue.enqueue_event(TaskStatusUpdateEvent(
            task_id=context.task_id, context_id=context.context_id,
            status=TaskStatus(
                state=TaskState.TASK_STATE_WORKING,
                message=Message(
                    role=Role.ROLE_AGENT, parts=[Part(text="正在处理退款请求...")],
                    message_id=f"msg-working-{context.task_id}",
                ),
            ),
        ))

        # ③ 执行业务逻辑 + 返回 Artifact
        result = await self.agent.process_refund(user_input)
        await event_queue.enqueue_event(TaskArtifactUpdateEvent(
            task_id=context.task_id, context_id=context.context_id,
            artifact=Artifact(name="退款结果", parts=[Part(text=result)]),
        ))

        # ④ 完成（COMPLETED）
        await event_queue.enqueue_event(TaskStatusUpdateEvent(
            task_id=context.task_id, context_id=context.context_id,
            status=TaskStatus(state=TaskState.TASK_STATE_COMPLETED),
        ))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        raise Exception("退款处理中，暂不支持取消")


# ===== 3. 定义 Agent Card 并启动 =====

if __name__ == "__main__":
    # 定义多个技能（skills），Client 可以按需选择
    agent_card = AgentCard(
        name="退款处理Agent",
        description="处理电商订单退款，支持多种退款方式和进度查询",
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        supported_interfaces=[
            AgentInterface(protocol_binding="JSONRPC", url="http://localhost:9999"),
        ],
        skills=[
            AgentSkill(
                id="process-refund", name="退款处理",
                description="处理电商订单退款，支持全额退款和部分退款",
                tags=["退款", "订单", "支付"],
                examples=["帮我退款订单ORD001"],
            ),
            AgentSkill(
                id="query-refund-status", name="退款查询",
                description="查询退款进度和状态",
                tags=["退款", "查询"],
                examples=["退款单RF001处理到哪了"],
            ),
        ],
    )

    handler = DefaultRequestHandler(
        agent_executor=RefundAgentExecutor(),
        task_store=InMemoryTaskStore(),
        agent_card=agent_card,
    )
    routes = [*create_agent_card_routes(agent_card), *create_jsonrpc_routes(handler, "/")]
    app = Starlette(routes=routes)

    print("🚀 退款Agent服务启动: http://localhost:9999")
    print("📋 Agent Card: http://localhost:9999/.well-known/agent-card.json")
    uvicorn.run(app, host="127.0.0.1", port=9999)
```

> 💡 **与极简版的区别**：
>
> - 新增 `RefundAgent` 业务类，包含真实的退款逻辑
> - `AgentCard.skills` 定义了两个技能：退款处理 + 退款查询
> - WORKING 状态附带了消息文本，Client 可以展示给用户
> - Artifact 加了 `name="退款结果"` 以便区分不同输出

---

## Client 代码（非流式 + 流式）

```python
import asyncio
from uuid import uuid4
import httpx
from a2a.client import A2ACardResolver, ClientFactory, ClientConfig
from a2a.types.a2a_pb2 import Message, Part, Role, SendMessageRequest, TaskState


def state_name(state_num):
    """将数字状态码转为可读名称（如 3 → COMPLETED）"""
    return TaskState.Name(state_num).replace("TASK_STATE_", "")


async def main():
    async with httpx.AsyncClient() as httpx_client:
        # 发现 Agent
        card = await A2ACardResolver(
            httpx_client=httpx_client,
            base_url="http://localhost:9999"
        ).get_agent_card()
        print(f"📋 发现 Agent: {card.name}")
        print(f"  技能: {[s.name for s in card.skills]}")
        print()

        # ===== 非流式调用 =====
        print("===== 非流式调用 =====")
        client = ClientFactory(config=ClientConfig(streaming=False)).create(card)
        request = SendMessageRequest(message=Message(
            role=Role.ROLE_USER,
            parts=[Part(text="帮我退款订单ORD001，商品有质量问题")],
            message_id=uuid4().hex,
        ))

        async for resp in client.send_message(request):
            if resp.HasField("task"):
                print(f"  状态: {state_name(resp.task.status.state)}")
                for artifact in resp.task.artifacts:
                    for part in artifact.parts:
                        if part.text:
                            print(f"  结果: {part.text}")
            elif resp.HasField("status_update"):
                print(f"  状态更新: {state_name(resp.status_update.status.state)}")
            elif resp.HasField("artifact_update"):
                for part in resp.artifact_update.artifact.parts:
                    if part.text:
                        print(f"  结果: {part.text}")

        await client.close()
        print()

        # ===== 流式调用 =====
        print("===== 流式调用 =====")
        streaming_client = ClientFactory(config=ClientConfig(streaming=True)).create(card)
        stream_request = SendMessageRequest(message=Message(
            role=Role.ROLE_USER,
            parts=[Part(text="退款单RF001处理到哪了？")],
            message_id=uuid4().hex,
        ))

        async for resp in streaming_client.send_message(stream_request):
            if resp.HasField("status_update"):
                print(f"  [流式] 状态: {state_name(resp.status_update.status.state)}")
            elif resp.HasField("artifact_update"):
                for part in resp.artifact_update.artifact.parts:
                    if part.text:
                        print(f"  [流式] 结果: {part.text}")
            elif resp.HasField("task"):
                print(f"  [流式] 任务: {state_name(resp.task.status.state)}")

        await streaming_client.close()


asyncio.run(main())
```

---

## 运行步骤

```bash
# 终端1：启动退款 Agent Server（独立终端运行，会阻塞）
python a2a_simple_server.py

# 终端2：运行 Client
python a2a_simple_client
```

### 运行结果

```
📋 发现 Agent: 退款处理Agent
  技能: ['退款处理', '退款查询']

===== 非流式调用 =====
  状态: TASK_STATE_COMPLETED
  结果: ✅ 订单ORD001退款成功！金额299元将在1-3个工作日退回原支付方式。

===== 流式调用 =====
  [流式] 状态: TASK_STATE_WORKING
  [流式] 任务: TASK_STATE_COMPLETED
  [流式] 结果: 📊 退款单RF001正在处理中，预计今天内完成审核。
```

---

## 非流式 vs 流式对比

| 特性 | 非流式（`streaming=False`） | 流式（`streaming=True`） |
|------|---------------------------|-------------------------|
| 返回方式 | 等待任务完成后一次性返回 | 实时推送每次状态变化 |
| 收到的主要响应类型 | `task` 和 `artifact_update` | `status_update` → `artifact_update` |
| 适用场景 | 短任务、简单集成 | 长时间任务、进度监控 |
| 区别 | 只有一个参数不同！ | `ClientConfig(streaming=True/False)` |

> 💡 **核心要点**：两者唯一的区别就是 `ClientConfig(streaming=True/False)`，其他代码（构造请求、解析响应）完全一样。

---

## 注意事项

> ⚠️ `InMemoryTaskStore` 将任务存储在内存中，服务重启后数据会丢失。生产环境可使用 PostgreSQL/SQLite 持久化存储（安装 `a2a-sdk[postgresql]` 或 `a2a-sdk[sqlite]`）。
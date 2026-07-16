# A2A 协议介绍

> **Agent-to-Agent Protocol（A2A）**：Google 于 2025 年 4 月发布，2025 年 6 月捐赠给 Linux 基金会（Apache 2.0），截至 2026 年已有 150+ 组织支持。
>
> 官方文档：[https://a2a-protocol.org/latest/#why-use-the-a2a-protocol](https://a2a-protocol.org/latest/#why-use-the-a2a-protocol)

---

## 为什么需要 A2A？

### 问题场景

```text
# 前面学的多Agent协作（LangGraph内部）
Supervisor Agent → 金融Agent / 翻译Agent / 邮件Agent

# 问题：这些Agent都在同一个进程中，无法跨框架、跨服务器协作 ❌

# 企业级场景：用户请求退款，需要多个系统的Agent协作
客服 Agent（LangGraph 开发）    → 接收请求
订单 Agent（Salesforce 平台）   → 查询订单
支付 Agent（PayPal 服务）       → 处理退款
通知 Agent（企业微信）          → 发送通知

# 这些Agent来自不同供应商、不同框架、不同服务器
# 没有统一协议 → 每两个Agent之间都要写定制接口 ❌
```

### 核心问题

> 不同框架、不同服务器上的 Agent 无法互通。
>
> **A2A 标准化了 Agent 之间的通信方式**，让任何 Agent 都能发现彼此、委托任务、协调工作。

---

## 三大核心对象

| 对象                 | 作用                          | 类比                      |
| -------------------- | ----------------------------- | ------------------------- |
| **Agent Card** | 描述 Agent 的身份、能力、接口 | 🏪 餐厅招牌（菜单+地址）  |
| **Task**       | Agent 之间交换的工作单元      | 📦 一笔订单（有状态追踪） |
| **Artifact**   | Task 执行完成后的输出结果     | 🍜 外卖食物（最终交付物） |

---

## Task 生命周期

```
                    ┌─────────┐
                    │ SUBMITTED│  ← 任务已提交
                    └────┬────┘
                         │
                    ┌────▼────┐
                    │ WORKING │  ← 正在处理
                    └────┬────┘
                         │
              ┌──────────┼──────────┐
              │          │          │
         ┌────▼───┐ ┌───▼────┐ ┌───▼──────┐
         │COMPLETED│ │ FAILED │ │ CANCELED │
         └────────┘ └────────┘ └──────────┘
              ↑ 成功    ↑ 失败    ↑ 取消
         ┌────▼───────┐
         │IN_REQUIRED │  ← 需额外信息（等待中）
         └────────────┘
         ┌──────────┐
         │ REJECTED │  ← 被服务端拒绝
         └──────────┘
```

### 状态枚举

| 状态                          | 枚举值 | 说明                    | 类型     |
| ----------------------------- | ------ | ----------------------- | -------- |
| `TASK_STATE_SUBMITTED`      | 1      | 任务已提交              | 初始状态 |
| `TASK_STATE_WORKING`        | 2      | 正在处理中              | 进行中   |
| `TASK_STATE_INPUT_REQUIRED` | 6      | 需要额外信息            | 等待中   |
| `TASK_STATE_COMPLETED`      | 3      | 成功完成，产出 Artifact | 终态     |
| `TASK_STATE_FAILED`         | 4      | 执行失败                | 终态     |
| `TASK_STATE_CANCELED`       | 5      | 被客户端取消            | 终态     |
| `TASK_STATE_REJECTED`       | 7      | 被服务端拒绝            | 终态     |

> 💡 **注意**：TaskState 是 protobuf 枚举，打印时显示的是数字（1、2、3...）。可以用 `TaskState.Name(state)` 转为可读名称。

---

## 安装 SDK

```bash
# 安装 A2A Python SDK（含 HTTP 服务器支持）
uv add "a2a-sdk[http-server]"

# 还需要 uvicorn 作为 HTTP 服务器
uv add uvicorn
```

> 💡 **说明**：`a2a-sdk` 是官方 A2A Python SDK（GitHub: [a2aproject/a2a-python](https://github.com/a2aproject/a2a-python)）。`[http-server]` extra 包含 Starlette 依赖，用于创建 HTTP 模式的 A2A Server。

---

## 学习目标（回顾）

- [X] 理解 A2A 协议的核心概念和架构
- [X] 掌握 Agent Card / Task / Artifact 三大核心对象
- [X] 了解 Task 的生命周期
- [X] 安装 A2A Python SDK

# 🧠 LangGraph 记忆系统分类

## 🎯 学习目标

- ✅ 理解 LangGraph 中两种记忆类型：**短期记忆**和**长期记忆**
- ✅ 了解新旧 API 的差异与迁移策略
- ✅ 掌握记忆系统的选择原则

---

## 📌 核心概念

在 LangGraph 中，记忆通过两种机制实现：

| 机制 | 作用 | 类比 |
|------|------|------|
| **Checkpointer** | 短期记忆 | 📒 笔记本 - 记录当前对话的所有内容 |
| **Store** | 长期记忆 | 🗄️ 档案柜 - 按标签存放关键信息 |

---

## 🔍 两种记忆类型详解

### 1️⃣ 短期记忆（Checkpointer）

**实现方式：** `MemorySaver` / `PostgresSaver`

**特点：**
- 💾 保存 Graph 的完整 State
- 🔑 通过 `thread_id` 隔离会话
- 💬 适合：多轮对话上下文管理

### 2️⃣ 长期记忆（Store）

**实现方式：** `InMemoryStore` / `PostgresStore`

**特点：**
- 📊 以键值对存储结构化数据
- 🔄 跨会话持久化
- 👤 适合：用户画像、偏好设置、历史经验

---

## ⚖️ 新旧 API 对比

> ⚠️ **注意**：旧版 `RunnableWithMessageHistory`、`ConversationBufferMemory`、`ConversationSummaryMemory` 等类已逐步弃用。**新项目请使用 LangGraph 的 Checkpointer + Store。**

| 特性 | 旧版（已弃用） | 新版（推荐）✨ |
|------|---------------|----------------|
| **短期记忆** | RunnableWithMessageHistory | MemorySaver (Checkpointer) |
| **长期记忆** | 无官方方案 | InMemoryStore / PostgresStore |
| **会话隔离** | session_id | thread_id |
| **依赖库** | langchain-core | langgraph |
| **生产持久化** | 需自己实现 | PostgresSaver / PostgresStore |

---

## 💡 形象比喻

```
📒 短期记忆（Checkpointer）= 笔记本
   └─ 记录当前对话的所有内容
   └─ 翻到哪页就是哪页（基于 thread_id）

🗄️ 长期记忆（Store）= 档案柜
   └─ 按标签存放关键信息（姓名、地址、偏好）
   └─ 随时可查，跨会话共享
```

---

## 🎯 选择原则

| 场景 | 推荐方案 |
|------|---------|
| 多轮对话上下文 | Checkpointer |
| 用户画像/偏好 | Store |
| 两者都需要 | Checkpointer + Store 组合使用 |

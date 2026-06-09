# 🔌 MCP vs @tool：区别与选择

## 🎯 学习目标

- ✅ 理解 MCP 协议的核心概念
- ✅ 掌握 MCP Server / Client 的架构关系
- ✅ 了解 MCP 与 LangChain `@tool` 的区别
- ✅ 掌握两者的适用场景与选择原则

---

## 📌 核心概念

### MCP 是什么？

**MCP（Model Context Protocol）** 是 Anthropic 提出的开放协议，标准化了 AI 模型与外部工具/数据源的通信方式。

```
类比：
HTTP 协议 → 标准化了网页通信
MCP 协议  → 标准化了 AI 工具调用
```

### MCP 架构

```
┌─────────────┐         ┌──────────────┐
│  MCP Client │ ←────→  │ MCP Server   │
│  (Agent)    │  MCP    │ (Tools/Data) │
└─────────────┘  Protocol └──────────────┘
     │                          │
     ├─ LangGraph              ├─ 文件系统
     ├─ Claude                 ├─ 数据库
     └─ OpenAI                 └─ Web API
```

**工作流程：**
1. **MCP Server**：提供工具和服务（独立进程）
2. **MCP Client**：连接并使用工具（Agent 框架）
3. **MCP Protocol**：统一的通信标准

---

## ⚖️ MCP vs @tool 对比

| 对比项 | LangChain `@tool` | MCP Server |
|--------|------------------|------------|
| **定义方式** | Python 函数 + 装饰器 | 独立的 Server 进程 |
| **运行方式** | 和 Agent 同一个进程 | 独立进程，通过网络通信 |
| **跨框架** | ❌ 只能在 LangChain/LangGraph 中用 | ✅ 任何支持 MCP 的客户端都能用 |
| **复用性** | ❌ 需要复制代码 | ✅ 写一次，到处用 |
| **适合场景** | 简单的本地工具 | 需要共享、跨应用、连接外部服务 |

---

## 💡 形象比喻

```
@tool = 自家厨房做菜
├─ 优点：简单直接，无需额外配置
└─ 缺点：只能自己用，别人想吃要重新做

MCP = 外卖平台
├─ 优点：餐厅做一次，所有用户都能点
└─ 缺点：需要接入平台，有额外开销
```

---

## 🎯 如何选择？

### 使用 @tool 的场景 ✅

- 🔧 简单的本地工具（计算、字符串处理等）
- 🚀 快速原型开发
- 📦 不需要跨框架复用
- 👤 单个项目内部使用

```python
@tool
def calculator(expression: str) -> str:
    """简单的数学计算"""
    return str(eval(expression))
```

### 使用 MCP 的场景 ✅

- 🌐 需要跨框架共享（LangGraph + Claude + OpenAI）
- 🔗 连接外部服务（数据库、API、文件系统）
- 🏪 使用社区现成的 MCP Server
- 🔄 需要被多个应用复用

```python
# 示例：使用现有的 MCP Server
# - GitHub MCP Server（代码搜索）
# - PostgreSQL MCP Server（数据库查询）
# - Filesystem MCP Server（文件操作）
```

---

## ⚠️ 重要提示

```
❌ MCP 不是要替代 @tool

✅ 简单工具 → 用 @tool 就够了
✅ 跨框架共享 → 用 MCP
✅ 连接外部服务 → 用 MCP
✅ 使用社区资源 → 用 MCP
```

---

## 💡 核心要点

- 📋 **MCP** 是标准化的工具调用协议
- 🔄 **@tool** 适合简单本地工具，快速开发
- 🌐 **MCP** 适合跨框架复用和外部服务集成
- 🎯 **选择原则**：简单用 @tool，复杂用 MCP
- 🧩 **两者互补**：不是替代关系，而是协作关系

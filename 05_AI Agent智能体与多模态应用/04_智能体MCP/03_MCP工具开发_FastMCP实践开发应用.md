# FastMCP 实践开发应用

## 一、什么是 FastMCP

**FastMCP** 是一个基于 Python 的高级框架，用于构建 **MCP（Model Context Protocol）服务器**。它帮助开发者以最小的代码量创建 MCP 服务器，让 AI 助手能够更好地与本地工具进行交互。

### 核心价值

| 特性 | 说明 |
|------|------|
| **极简 API** | 通过装饰器（如 `@tool`）快速将普通 Python 函数转换为 MCP 工具 |
| **高性能** | 基于异步 I/O（asyncio），能够高效处理并发请求 |
| **内置功能** | 原生支持资源（Resources）管理、提示词模板（Prompts）等 MCP 核心概念 |
| **开发友好** | 提供清晰的类型提示、简单的运行方式和易于调试的结构 |

---

## 二、核心组件

一个典型的 FastMCP 应用包含以下核心组件：

```
┌─────────────────────────────────────────────────────────────┐
│                    FastMCP Server                           │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │  Tools  │  │Resources│  │ Prompts │  │  Tasks  │       │
│  │  (手脚)  │  │  (眼睛)  │  │ (模板)  │  │(长任务) │       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### 1. MCP Server

- **角色**：由 FastMCP 创建的应用实例
- **职责**：负责与 LLM 客户端通信，管理工具注册和调用

### 2. Tools（工具）

- **角色**：服务器向客户端公开的可调用函数
- **类比**：AI 智能体的**手和脚**，执行具体操作
- **示例**：发送邮件、调用 API、运行 SQL 查询

### 3. Resources（资源）

- **角色**：服务器向客户端提供的可读数据源
- **类比**：AI 智能体的**眼睛**，获取信息
- **示例**：文件内容、数据库记录、实时数据

### 4. Prompts（提示词）

- **角色**：服务器预定义的、参数化的文本模板
- **作用**：客户端可以调用它们来快速构建高质量的提示

### 5. Tasks（任务）（FastMCP 3.x 新增）

- **角色**：支持长时间运行的操作
- **状态**：`working`、`input_required`、`completed`、`failed`、`cancelled`
- **适用场景**：批量数据处理、复杂工作流

---

## 三、FastMCP 3.x 最新特性（2026年更新）

### 1. 远程桥接（fastmcp-remote）

```bash
# 将远程服务器桥接到仅支持 stdio 的主机
uvx fastmcp-remote https://example.com/mcp
```

### 2. 轻量级版本（fastmcp-slim）

```bash
# 仅安装客户端，不含服务器依赖
pip install fastmcp-slim
```

### 3. Code Mode（代码模式）

让 LLM 动态搜索和调用工具：
- 按需搜索相关工具
- 检查工具 schema
- 在沙箱中编写 Python 代码调用工具

### 4. 企业级认证支持

| 认证方式 | 说明 |
|---------|------|
| **WorkOS** | 统一身份管理 |
| **AuthKit** | 开发者友好的认证 |
| **GitHub** | GitHub OAuth |
| **Google** | Google OAuth |
| **Azure** | Azure AD / B2C |
| **Keycloak** | 企业级身份管理 |

### 5. 安全增强

- **OAuth Proxy 强化**：防止混淆代理和授权绕过攻击
- **RFC 7662 令牌内省**：支持企业级认证流程
- **安全同意屏幕**：用户明确授权

---

## 四、快速入门示例

### 1. 安装

```bash
# 完整版本（含服务器）
pip install fastmcp

# 轻量级版本（仅客户端）
pip install fastmcp-slim
```

### 2. 基本服务器示例

```python
from fastmcp import FastMCP

mcp = FastMCP("Demo Server 🚀")

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run(transport="http",port=4001)
```

### 3. 运行服务器

```bash
# 开发模式（自动重载）
fastmcp run server.py --reload

# 指定端口
fastmcp run server.py --port 8000
```

---

## 五、CLI 工具

FastMCP 3.x 提供了丰富的 CLI 命令：

| 命令 | 说明 |
|------|------|
| `fastmcp run` | 启动服务器 |
| `fastmcp list` | 列出可用工具 |
| `fastmcp call` | 调用工具 |
| `fastmcp discover` | 发现服务器能力 |
| `fastmcp generate-cli` | 生成 CLI 客户端 |
| `fastmcp install` | 安装到 Claude Desktop/Cursor |

---

## 六、关键要点总结

| 要点 | 说明 |
|------|------|
| **核心价值** | 简化 MCP 服务器开发，让开发者专注于业务逻辑 |
| **架构模式** | 插件化设计，支持 Tools、Resources、Prompts、Tasks |
| **最新特性** | Code Mode、远程桥接、企业级认证、轻量级版本 |
| **部署方式** | stdio（本地）、HTTP（远程）、SSE（流式） |
| **CLI 工具** | 提供开发、调试、部署的完整工具链 |

> **类比**：如果 MCP 是 AI 模型的"USB-C 接口"，那么 FastMCP 就是"接口适配器"——让开发者轻松创建各种"外设"。

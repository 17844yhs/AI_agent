# MCP 客户端开发

## FastMCP Client 概述

**FastMCP Client** 提供类型安全的接口，自动处理连接管理。

**核心特性**：
- 自动传输选择
- 类型安全
- 连接管理（上下文管理器）

---

## 创建客户端

### 1. 连接到 HTTP 服务器

```python
from fastmcp import Client

client = Client("https://api.example.com/mcp")
```

### 2. 连接到本地脚本

```python
from fastmcp import Client

client = Client("my_mcp_server.py")
```

---

## 基本操作

```python
import asyncio
from fastmcp import Client

async def main():
    async with Client("http://localhost:4001/mcp") as client:
        # 列出工具
        tools = await client.list_tools()
        
        # 调用工具
        result = await client.call_tool("add", arguments={"a": 1, "b": 2})
        print(result)

asyncio.run(main())
```

---

## 传输方式

| 传输方式 | 适用场景 |
|---------|---------|
| **In-memory** | 单元测试 |
| **STDIO** | 本地脚本 |
| **HTTP** | 远程服务 |

---

## CLI 客户端

```bash
# 列出工具
fastmcp list server.py

# 调用工具
fastmcp call server.py greet name=World
```

---

## 关键要点

> **类比**：FastMCP Client 就像智能遥控器，统一操作接口，专注于使用工具而不是连接细节。
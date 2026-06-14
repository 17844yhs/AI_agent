# 🚀 MCP 服务：stdio 模式与传输协议

## 🎯 学习目标

- ✅ 掌握 FastMCP 创建 MCP Server 的方法
- ✅ 了解 stdio、SSE、Streamable HTTP 三种传输模式的区别
- ✅ 理解不同传输模式的适用场景与选择原则

---

## 📌 核心概念

**MCP Server** 是一个独立的服务进程，对外提供工具。**LangGraph Agent** 作为 Client 连接到 Server，调用其中的工具。

使用 Python 的 **FastMCP** 库可以快速创建 Server。

### 📚 参考资源

- [FastMCP 中文文档](https://fastmcp.wiki/zh/getting-started/welcome)
- [GoFastMCP 文档](https://gofastmcp.com/getting-started/welcome)

---

## 🔌 三种传输模式

MCP 支持三种传输模式，适用于不同的部署场景：

| 模式 | 通信方式 | 适用场景 |
|------|---------|---------|
| **stdio** | 标准输入/输出 | 本地开发，Client 启动 Server 子进程 |
| **SSE**（旧版） | HTTP 长连接（Server-Sent Events） | 远程 Server，旧版兼容 |
| **Streamable HTTP**（推荐） | HTTP 流式传输 | 远程 Server，2025年推荐方式 |

---

## ⚖️ 传输模式对比

| 特性 | stdio | SSE | Streamable HTTP |
|------|-------|-----|-----------------|
| **通信方向** | 双向（本地） | 单向（服务端→客户端） | 双向（全双工流） |
| **是否依赖网络** | ❌ 否 | ✅ 是 | ✅ 是 |
| **是否支持并发** | ❌ 否 | ⚠️ 有限 | ✅ 是 |
| **是否适合生产环境** | ❌ 否（仅本地） | ❌ 已弃用 | ✅ 是（推荐） |
| **协议基础** | 操作系统 IPC | HTTP + EventStream | 标准 HTTP/1.1 或 HTTP/2 |
| **云原生友好度** | 🔴 低 | 🟡 中 | 🟢 高 |

---

## 💻 代码示例

### 示例1：数学计算 Server（stdio 模式）

```python
# math_server.py — 独立的 MCP Server 进程

from mcp.server.fastmcp import FastMCP

# 创建 MCP Server 实例
mcp = FastMCP("MathTools")

@mcp.tool()
def add(a: int, b: int) -> int:
    """两数相加"""
    return a + b

@mcp.tool()
def multiply(a: int, b: int) -> int:
    """两数相乘"""
    return a * b

@mcp.tool()
def power(base: int, exponent: int) -> int:
    """计算幂运算"""
    return base ** exponent

# 启动 Server（stdio 模式：通过标准输入输出通信）
if __name__ == "__main__":
    mcp.run(transport="stdio")
```

### 示例2：天气查询 Server（Streamable HTTP 模式）

```python
# weather_server.py — 另一个独立的 MCP Server

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WeatherTools")

@mcp.tool()
def get_weather(city: str) -> str:
    """查询指定城市的天气信息"""
    # 模拟天气数据（实际开发中调用真实天气 API）
    weather_data = {
        "北京": "晴天，15-25度，空气质量良好",
        "上海": "多云，18-28度，有轻微雾霾",
        "广州": "阵雨，22-30度，出门带伞",
        "深圳": "阴天，20-29度，可能转雨"
    }
    return weather_data.get(city, f"暂无{city}的天气数据")

@mcp.tool()
def get_forecast(city: str, days: int) -> str:
    """查询城市未来几天的天气预报"""
    return f"{city}未来{days}天：整体天气稳定，温度适宜"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")  # Streamable HTTP 模式
    # 访问地址：http://localhost:8000/mcp
```

---

## 🚀 启动方式

### stdio 模式

```bash
# Client 会自动启动 Server 子进程
mcp.run(transport="stdio")
```

**特点：**
- 📍 本地通信，无需网络
- 🔄 Client 和 Server 在同一台机器
- 🚫 不支持远程调用

### Streamable HTTP 模式

```bash
# Server 独立运行，Client 通过网络连接
mcp.run(transport="streamable-http")
```

**特点：**
- 🌐 基于 HTTP 协议
- 🔄 支持远程调用
- ✅ 生产环境推荐

### SSE 模式（不推荐）

```bash
# 旧版方式，新项目不建议使用
mcp.run(transport="sse")
```

---

## 💡 重要提示

### MCP Server 类型

```
MCP Server 分为两种：

1️⃣ npm 包 → 用 npx 启动
   └─ 例如：npx @modelcontextprotocol/server-filesystem

2️⃣ Python 包 → 用 python 启动
   └─ 例如：python math_server.py
```

### 连接方式

```
✅ 连接方式完全一样，只是 command 不同
   ├─ npm 包：command = ["npx", "-y", "@xxx/server"]
   └─ Python 包：command = ["python", "math_server.py"]
```

---

## 🎯 如何选择传输模式？

### 使用 stdio 的场景 ✅

- 🖥️ 本地开发测试
- 📦 Server 和 Client 在同一台机器
- 🚀 快速原型验证
- 🔒 不需要网络暴露

### 使用 Streamable HTTP 的场景 ✅

- 🌐 生产环境部署
- ☁️ 云原生架构
- 🔄 需要远程调用
- ⚡ 需要高并发支持

### 避免使用 SSE ❌

- ⚠️ 已弃用，不再推荐
- 🔄 建议使用 Streamable HTTP 替代

---

## 💡 核心要点

- 🚀 **FastMCP** 简化了 MCP Server 的开发
- 🔌 **三种传输模式**：stdio（本地）、SSE（旧版）、Streamable HTTP（推荐）
- 📍 **stdio** 适合本地开发，无需网络
- 🌐 **Streamable HTTP** 适合生产环境，支持远程调用
- 🎯 **选择原则**：开发用 stdio，生产用 Streamable HTTP
- 📦 **两种 Server**：npm 包和 Python 包，连接方式相同

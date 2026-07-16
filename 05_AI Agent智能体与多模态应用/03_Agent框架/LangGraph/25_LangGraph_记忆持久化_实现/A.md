# 🗄️⚙️ LangGraph 记忆持久化：环境搭建

## 🎯 学习目标

- ✅ 掌握 PostgreSQL 数据库的初始化方法（安装依赖、建表）
- ✅ 分别掌握 `PostgresSaver`（短期记忆）和 `PostgresStore`（长期记忆）的完整用法
- ✅ 理解从开发环境到生产环境的迁移策略

---

## 📌 核心概念

前面用的 `MemorySaver` 和 `InMemoryStore` 都把数据存在**内存中**，程序一重启就没了。

**生产环境需要持久化存储**——LangGraph 提供了基于 **PostgreSQL** 的实现。

### 开发 vs 生产对比

| 环境           | Checkpointer  | Store         | 数据存储             | 需要初始化         |
| -------------- | ------------- | ------------- | -------------------- | ------------------ |
| **开发** | MemorySaver   | InMemoryStore | 内存（重启丢失）     | ❌ 不需要          |
| **生产** | PostgresSaver | PostgresStore | PostgreSQL（持久化） | ✅ 需要`setup()` |

---

## 🛠️ 环境准备

### 1. 安装 Python 依赖

```bash
pip install langgraph-checkpoint-postgres psycopg[binary]
```

### 2. 启动 PostgreSQL 数据库

#### 方式一：Docker（推荐）

```bash
docker run -d \
  --name langgraph-postgres \
  -e POSTGRES_PASSWORD=langgraph123 \
  -p 5432:5432 \
  postgres:17
```

#### 方式二：本地安装

如果本地已安装 PostgreSQL，直接创建数据库即可：

```sql
CREATE DATABASE memory_db;
CREATE USER langgraph WITH PASSWORD 'langgraph123';
GRANT ALL PRIVILEGES ON DATABASE memory_db TO langgraph;
```

---

## ⚙️ 数据库初始化

`PostgresSaver` 和 `PostgresStore` 都需要调用 `setup()` 方法来创建所需的数据库表。

### 基础初始化

```python
from langgraph.checkpoint.postgres import PostgresSaver
from langgraph.store.postgres import PostgresStore

DB_URI = "postgresql://langgraph:langgraph123@localhost:5432/memory_db"

# 创建 Checkpointer 并初始化表
checkpointer = PostgresSaver.from_conn_string(DB_URI)
checkpointer.setup()  # 创建 checkpoints 相关表

# 创建 Store 并初始化表
store = PostgresStore.from_conn_string(DB_URI)
store.setup()  # 创建 store 相关表

print("数据库初始化完成！")
```

### 💡 重要提示

```
✅ setup() 只需在首次使用时调用一次
✅ 它会自动创建所需的数据库表和索引
✅ 如果表已存在会自动跳过，不会覆盖数据
❌ 不调用 setup() 会报错找不到表
```

---

## 💻 完整的生产环境示例

上一节"Agent + 长期记忆"已经同时使用了短期记忆（`MemorySaver`）和长期记忆（`InMemoryStore`）。切换到生产环境只需**两步**：

1. **换 import**
2. **加 `setup()`**

其他代码完全不变！

### 完整代码

```python
import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.agents import create_agent
# ← 改动1：换 import
from langgraph.checkpoint.postgres import PostgresSaver  # 原来是 MemorySaver
from langgraph.store.postgres import PostgresStore       # 原来是 InMemoryStore
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

DB_URI = os.getenv("DATABASE_URI", "postgresql://langgraph:langgraph123@localhost:5432/memory_db")

# ← 改动2：用 with 创建 + setup()
with PostgresSaver.from_conn_string(DB_URI) as memory, \
     PostgresStore.from_conn_string(DB_URI) as store:
  
    memory.setup()  # ← 必须调用！
    store.setup()   # ← 必须调用！

    # ===== 以下代码与"Agent + 长期记忆"一节完全相同 =====

    # 定义工具：保存用户信息到长期记忆
    @tool
    def save_user_info(user_id: str, info_key: str, info_value: str) -> str:
        """保存用户信息到长期记忆。user_id是用户ID，info_key是信息类别（如name/age/city），info_value是信息内容。"""
        namespace = ("users", user_id)
        existing = store.get(namespace, "profile")
        profile = existing.value if existing else {}
        profile[info_key] = info_value
        store.put(namespace, "profile", profile)
        return f"已保存：{info_key} = {info_value}"

    @tool
    def get_user_info(user_id: str, info_key: str = "") -> str:
        """查询用户信息。user_id是用户ID，info_key可选，指定查询某个信息类别。不填则返回全部。"""
        namespace = ("users", user_id)
        existing = store.get(namespace, "profile")
        if not existing:
            return f"未找到用户 {user_id} 的信息"
        profile = existing.value
        if info_key:
            return profile.get(info_key, f"未找到 {info_key} 信息")
        return json.dumps(profile, ensure_ascii=False)

    # 创建带记忆的 Agent
    app = create_agent(
        llm,
        [save_user_info, get_user_info],
        checkpointer=memory
    )

    SYSTEM_PROMPT = """你是一个友好的AI助手。
当用户提到自己的个人信息时（姓名、年龄、城市、工作等），
请主动调用 save_user_info 工具保存到长期记忆中。
用户ID固定为 "user-001"。
"""

    # === 第一次对话 ===
    print("=== 第一次对话 ===")
    config = {"configurable": {"thread_id": "session-001"}}
    conversations_1 = [
        "我叫张三，25岁，住在北京",
        "我是一名Python开发者"
    ]

    for msg in conversations_1:
        result = app.invoke(
            {"messages": [HumanMessage(SYSTEM_PROMPT + "\n用户：" + msg)]},
            config
        )
        print(f"用户：{msg}")
        print(f"AI：{result['messages'][-1].content}")
        print()

    # === 查看长期记忆 ===
    print("=== 长期记忆中的数据 ===")
    profile = store.get(("users", "user-001"), "profile")
    print(f"用户画像：{profile.value}")

    # === 第二次对话（新会话，但长期记忆还在） ===
    print("\n=== 第二次对话（新会话） ===")
    config2 = {"configurable": {"thread_id": "session-002"}}

    conversations_2 = [
        "你还记得我吗？帮我查一下我的信息",
        "根据我的信息，推荐一个适合我的技术方向"
    ]

    for msg in conversations_2:
        result = app.invoke(
            {"messages": [HumanMessage(SYSTEM_PROMPT + "\n用户：" + msg)]},
            config2
        )
        print(f"用户：{msg}")
        print(f"AI：{result['messages'][-1].content}")
        print()
```

### 运行结果

```
=== 第一次对话 ===
用户：我叫张三，25岁，住在北京
AI：你好张三！我已经记住了你的信息。

用户：我是一名Python开发者
AI：Python开发是个很好的方向！我已经记录了你的职业信息。

=== 长期记忆中的数据 ===
用户画像：{'name': '张三', 'age': '25', 'city': '北京', 'job': 'Python开发者'}

=== 第二次对话（新会话） ===
用户：你还记得我吗？帮我查一下我的信息
AI：让我查一下...你是张三，25岁，住在北京，是一名Python开发者。

用户：根据我的信息，推荐一个适合我的技术方向
AI：你作为25岁的Python开发者，建议可以关注以下方向...
```

---

## 🔄 改动对比

### 开发环境（内存版）→ 生产环境（持久化版）

```python
# Import 改动
from ...memory import MemorySaver      →  from ...postgres import PostgresSaver
from ...memory import InMemoryStore    →  from ...postgres import PostgresStore

# 初始化改动
store = InMemoryStore()                →  store = PostgresStore.from_conn_string(DB_URI)
                                              store.setup()  ← 新增

memory = MemorySaver()                 →  memory = PostgresSaver.from_conn_string(DB_URI)
                                              memory.setup()  ← 新增

# Agent 代码 → 完全不变 ✅
```

---

## ⚠️ 注意事项

| 项目                   | 说明                                                                      |
| ---------------------- | ------------------------------------------------------------------------- |
| **依赖包**       | 需安装`langgraph-checkpoint-postgres` 和 `psycopg`（或 `psycopg2`） |
| **数据库服务**   | 确保 PostgreSQL 服务已启动并可访问                                        |
| **setup() 调用** | 必须在首次使用前调用，否则会报错找不到表                                  |
| **连接管理**     | 推荐使用`with` 语句自动管理连接生命周期                                 |
| **环境变量**     | 建议使用`.env` 文件管理数据库连接字符串                                 |

---

## 💡 核心要点

- 🔄 **平滑迁移**：从内存版到持久化版只需改 import + 加 `setup()`
- ⚙️ **setup()**：首次使用前必须调用，自动创建表和索引
- 🗄️ **PostgreSQL**：生产环境的标准选择，支持高可用和扩展
- 🔒 **连接管理**：使用 `with` 语句确保资源正确释放
- 📦 **代码复用**：Agent 业务逻辑完全不变，只需更换存储后端

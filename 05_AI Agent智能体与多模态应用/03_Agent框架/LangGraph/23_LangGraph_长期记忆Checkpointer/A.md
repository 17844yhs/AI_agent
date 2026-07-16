# 🗄️ LangGraph 长期记忆：Store

## 🎯 学习目标

- ✅ 理解长期记忆与短期记忆的区别
- ✅ 掌握 `InMemoryStore` 的 `put` / `get` / `search` 用法
- ✅ 了解命名空间（`namespace`）的组织方式

---

## 📌 核心概念

### 短期记忆 vs 长期记忆

| 特性               | 短期记忆（Checkpointer） | 长期记忆（Store）                     |
| ------------------ | ------------------------ | ------------------------------------- |
| **保存范围** | 单个会话内               | 跨会话、跨用户                        |
| **数据格式** | 完整的 Graph State       | 键值对（JSON 文档）                   |
| **生命周期** | 程序重启就丢失           | InMemory: 重启丢失 / Postgres: 持久化 |
| **适用场景** | 多轮对话上下文           | 用户画像、偏好、知识库                |

### 💡 形象比喻

```
📒 短期记忆 = 笔记本
   └─ 记今天的对话内容
   └─ 合上本子就翻篇了

🪪 长期记忆 = 身份证
   └─ 不管今天明天，信息一直都在
```

---

## 🔍 为什么需要长期记忆？

**短期记忆（Checkpointer）**只能保存当前会话的 State，会话结束就没了。

但有些信息需要**跨会话持久化**：

- 👤 用户姓名、年龄
- ⚙️ 偏好设置
- 📦 历史订单
- 📚 知识库

**`InMemoryStore`** 就是为了解决这个问题。

---

## 💻 代码示例

### 1. 创建 Store

```python
from langgraph.store.memory import InMemoryStore

# 创建 Store
store = InMemoryStore()
```

### 2. 写入数据（put）

```python
# put(namespace, key, value)

# 用户 user-001 的个人资料
store.put(
    ("users", "user-001"),          # 命名空间：用户 user-001
    "profile",                       # key
    {
        "name": "张三",
        "age": 25,
        "city": "北京",
        "job": "Python开发者"
    }
)

# 用户 user-001 的偏好设置
store.put(
    ("users", "user-001"),
    "preferences",
    {
        "language": "Python",
        "framework": "LangChain",
        "theme": "dark"
    }
)

# 用户 user-002 的个人资料
store.put(
    ("users", "user-002"),
    "profile",
    {
        "name": "李四",
        "age": 30,
        "city": "上海",
        "job": "前端开发"
    }
)
```

### 3. 读取数据（get）

```python
# 读取用户信息
profile = store.get(("users", "user-001"), "profile")
print(f"用户信息：{profile.value}")

# 读取偏好设置
prefs = store.get(("users", "user-001"), "preferences")
print(f"偏好设置：{prefs.value}")
```

### 4. 更新数据（put 相同 key 会覆盖）

```python
# 更新用户信息
store.put(
    ("users", "user-001"),
    "profile",
    {
        "name": "张三",
        "age": 26,
        "city": "北京",
        "job": "全栈开发"
    }
)

profile = store.get(("users", "user-001"), "profile")
print(f"更新后：{profile.value}")
```

### 5. 搜索数据（search）

```python
# 搜索 user-001 的所有记忆
results = store.search(("users", "user-001"))
print(f"\nuser-001 的所有记忆：")
for item in results:
    print(f"  {item.key}: {item.value}")
```

### 运行结果

```
用户信息：{'name': '张三', 'age': 25, 'city': '北京', 'job': 'Python开发者'}
偏好设置：{'language': 'Python', 'framework': 'LangChain', 'theme': 'dark'}
更新后：{'name': '张三', 'age': 26, 'city': '北京', 'job': '全栈开发'}

user-001 的所有记忆：
  profile: {'name': '张三', 'age': 26, 'city': '北京', 'job': '全栈开发'}
  preferences: {'language': 'Python', 'framework': 'LangChain', 'theme': 'dark'}
```

---

## 📋 InMemoryStore API 速查

| 操作           | 方法                                 | 说明                   |
| -------------- | ------------------------------------ | ---------------------- |
| **写入** | `store.put(namespace, key, value)` | 写入或更新数据         |
| **读取** | `store.get(namespace, key)`        | 读取单个数据           |
| **搜索** | `store.search(namespace)`          | 搜索命名空间下所有数据 |
| **删除** | `store.delete(namespace, key)`     | 删除数据               |

---

## 🏷️ 命名空间（Namespace）

命名空间用于组织数据结构，采用**元组**形式：

```python
# 单层命名空间
("users",)

# 双层命名空间
("users", "user-001")

# 三层命名空间
("users", "user-001", "profile")
```

**作用：**

- 📂 类似文件夹结构，便于数据分类
- 🔑 支持层级搜索（搜索父级可找到所有子级数据）

---

## ⚠️ 注意事项

| 特性               | 说明                               |
| ------------------ | ---------------------------------- |
| **存储位置** | 内存中（程序重启后数据丢失）       |
| **适用场景** | 开发测试阶段                       |
| **生产环境** | 请使用`PostgresStore` 持久化存储 |

---

## 🎯 核心要点

- 🗄️ **Store** 用于跨会话持久化结构化数据
- 🏷️ **命名空间** 采用元组形式，支持层级组织
- 📝 使用 `put` / `get` / `search` / `delete` 管理数据
- 🔄 相同 `namespace + key` 的 `put` 会覆盖原有数据
- 🗃️ 生产环境使用 `PostgresStore` 实现持久化

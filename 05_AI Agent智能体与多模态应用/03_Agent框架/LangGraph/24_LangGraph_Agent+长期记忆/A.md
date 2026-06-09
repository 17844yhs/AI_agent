# 🤖🗄️ LangGraph Agent + 长期记忆

## 🎯 学习目标

- ✅ 掌握在 Agent 中同时使用 Checkpointer 和 Store
- ✅ 理解如何让 Agent 自动提取和存储用户信息
- ✅ 了解短期记忆与长期记忆的协作机制

---

## 📌 核心概念

实际应用中，Agent 通常需要**同时使用短期记忆和长期记忆**：

```
用户说话 → Agent 处理
        ├── 短期记忆：保存完整对话历史（Checkpointer）
        └─ 长期记忆：提取关键信息存入 Store（InMemoryStore）

下次对话 → Agent 处理
        ├── 短期记忆：恢复上次对话上下文
        └── 长期记忆：读取用户画像辅助回答
```

### 两种记忆的职责分工

| 记忆类型 | 职责 | 存储内容 |
|---------|------|---------|
| **短期记忆** | 保持当前会话上下文 | 完整对话历史 |
| **长期记忆** | 跨会话持久化关键信息 | 用户画像、偏好设置 |

---

## 💻 代码示例

### 1. 初始化组件

```python
import os
import json
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver
from langgraph.store.memory import InMemoryStore
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# 创建 Store 和 Checkpointer
store = InMemoryStore()
memory = MemorySaver()
```

### 2. 定义工具

#### 保存用户信息到长期记忆

```python
@tool
def save_user_info(user_id: str, info_key: str, info_value: str) -> str:
    """保存用户信息到长期记忆。
    
    Args:
        user_id: 用户ID
        info_key: 信息类别（如 name/age/city）
        info_value: 信息内容
    """
    namespace = ("users", user_id)
    
    # 读取已有信息，合并新信息
    existing = store.get(namespace, "profile")
    if existing:
        profile = existing.value
    else:
        profile = {}
    
    profile[info_key] = info_value
    store.put(namespace, "profile", profile)
    
    return f"已保存：{info_key} = {info_value}"
```

#### 查询用户信息

```python
@tool
def get_user_info(user_id: str, info_key: str = "") -> str:
    """查询用户信息。
    
    Args:
        user_id: 用户ID
        info_key: 可选，指定查询某个信息类别。不填则返回全部。
    """
    namespace = ("users", user_id)
    existing = store.get(namespace, "profile")
    
    if not existing:
        return f"未找到用户 {user_id} 的信息"
    
    profile = existing.value
    if info_key:
        return profile.get(info_key, f"未找到 {info_key} 信息")
    
    return json.dumps(profile, ensure_ascii=False)
```

### 3. 创建带记忆的 Agent

```python
app = create_agent(
    llm,
    [save_user_info, get_user_info],
    checkpointer=memory  # 短期记忆
)

# 系统提示：让 Agent 主动记住用户信息
SYSTEM_PROMPT = """你是一个友好的AI助手。
当用户提到自己的个人信息时（姓名、年龄、城市、工作等），
请主动调用 save_user_info 工具保存到长期记忆中。
用户ID固定为 "user-001"。
"""

config = {"configurable": {"thread_id": "session-001"}}
```

### 4. 第一次对话（保存信息）

```python
print("=== 第一次对话 ===")
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
```

### 5. 查看长期记忆

```python
print("=== 长期记忆中的数据 ===")
profile = store.get(("users", "user-001"), "profile")
print(f"用户画像：{profile.value}")
```

### 6. 第二次对话（新会话，读取信息）

```python
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
已保存：name = 张三

用户：我是一名Python开发者
AI：Python开发是个很好的方向！我已经记录了你的职业信息。
已保存：job = Python开发者

=== 长期记忆中的数据 ===
用户画像：{'name': '张三', 'age': '25', 'city': '北京', 'job': 'Python开发者'}

=== 第二次对话（新会话） ===
用户：你还记得我吗？帮我查一下我的信息
AI：让我查一下...你是张三，25岁，住在北京，是一名Python开发者。

用户：根据我的信息，推荐一个适合我的技术方向
AI：你作为25岁的Python开发者，建议可以关注以下方向...
```

---

## 🔑 关键设计点

### 1️⃣ 系统提示词引导

```
系统提示词告诉 Agent 何时保存信息
→ 用户提到个人信息时，主动调用 save_user_info
```

### 2️⃣ 短期记忆的作用域

```
短期记忆（session-001）只保存当次对话
→ session-002 是新会话，不记得上次对话内容
```

### 3️⃣ 长期记忆的持久化

```
长期记忆（InMemoryStore）跨会话持久化
→ session-002 可以通过 get_user_info 查到 user-001 的信息
```

### 4️⃣ 用户隔离机制

```
用户ID作为命名空间的一部分
→ 不同用户的数据互不干扰
```

---

## 🎯 工作流程

```
第1次会话（session-001）：
  用户说"我叫张三" 
  → Agent 调用 save_user_info 
  → Store 保存 {name: "张三"}
  → Checkpointer 保存完整对话历史

第2次会话（session-002）：
  用户问"你还记得我吗"
  → Checkpointer 无历史（新会话）
  → Agent 调用 get_user_info 
  → Store 读取 {name: "张三"}
  → AI 回复个性化内容
```

---

## ⚠️ 注意事项

| 特性 | 说明 |
|------|------|
| **短期记忆** | `MemorySaver` - 内存存储，重启丢失 |
| **长期记忆** | `InMemoryStore` - 内存存储，重启丢失 |
| **生产环境** | 使用 `PostgresSaver` + `PostgresStore` |
| **用户隔离** | 通过 `namespace` 实现多用户数据隔离 |

---

## 💡 核心要点

- 🔄 **双记忆机制**：短期记忆保上下文，长期记忆保关键信息
- 🛠️ **工具驱动**：通过工具调用实现信息的自动提取和存储
- 🏷️ **命名空间**：使用 `(type, user_id)` 实现用户数据隔离
- 📝 **系统提示**：引导 Agent 主动调用工具保存信息
- 🗄️ **持久化方案**：生产环境使用 Postgres 系列组件

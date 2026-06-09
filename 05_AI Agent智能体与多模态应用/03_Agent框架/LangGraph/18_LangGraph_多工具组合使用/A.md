# 🎯 学习目标

- 理解 **多工具组合** 的工作机制
- 掌握 LLM 如何自动选择和编排多个工具
- 了解复杂问题的多步工具调用流程

---

## 📖 介绍

真实业务中，Agent 通常需要配备**多个工具**。LLM 会根据问题自动选择：
- ✅ 调用哪些工具
- ✅ 以什么顺序调用
- ✅ 是否需要多次调用

一个复杂问题可能需要**多次工具调用**才能解决。

---

## 💻 代码示例：多工具组合

```python
import os
import json
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_agent

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# 模拟数据库
user_database = {
    "张三": {"age": 25, "city": "北京", "balance": 10000},
    "李四": {"age": 30, "city": "上海", "balance": 25000},
    "王五": {"age": 28, "city": "广州", "balance": 8000},
}

# 1. 定义多个工具
@tool
def query_user(name: str) -> str:
    """查询用户信息，输入用户姓名，返回年龄、城市、余额等信息。"""
    user = user_database.get(name)
    if user:
        return json.dumps(user, ensure_ascii=False)
    return f"未找到用户：{name}"

@tool
def calculate(expression: str) -> str:
    """计算数学表达式，输入数学表达式字符串。"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误：{e}"

@tool
def transfer(from_user: str, to_user: str, amount: float) -> str:
    """转账操作，输入转出人、转入人和金额。"""
    from_data = user_database.get(from_user)
    to_data = user_database.get(to_user)
    
    if not from_data or not to_data:
        return "转账失败：用户不存在"
    
    if from_data["balance"] < amount:
        return f"转账失败：{from_user}余额不足（当前{from_data['balance']}元）"
    
    from_data["balance"] -= amount
    to_data["balance"] += amount
    
    return f"转账成功！{from_user}向{to_user}转账{amount}元"

@tool
def get_weather(city: str) -> str:
    """查询城市天气，输入城市名称。"""
    weather = {
        "北京": "晴天 15-25度",
        "上海": "多云 18-28度",
        "广州": "阵雨 22-30度"
    }
    return weather.get(city, f"暂无{city}天气数据")

# 2. 创建 Agent
app = create_agent(llm, [query_user, calculate, transfer, get_weather])

# 3. 测试多工具组合场景
questions = [
    "查询张三的余额",
    "张三向李四转账3000元，转账后各自余额是多少？",
    "北京天气怎么样？张三在那边适合出门吗？",
]

for question in questions:
    print(f"用户：{question}")
    result = app.invoke({"messages": question})
    print(f"AI：{result['messages'][-1].content}")
    print()
```

### 📊 运行结果

```
用户：查询张三的余额
AI：张三的当前余额是10000元。

用户：张三向李四转账3000元，转账后各自余额是多少？
AI：转账成功！张三向李四转账3000元。
转账后余额：张三7000元，李四28000元。

用户：北京天气怎么样？张三在那边适合出门吗？
AI：北京今天晴天，15-25度，非常适合出门。张三在北京，可以放心出行。
```

---

## 🔄 LLM 的工具选择逻辑

### 场景1：单工具调用

```
用户：查询张三的余额
  ↓
LLM 分析：需要查用户信息
  ↓
调用 query_user("张三")
  ↓
返回：{"age": 25, "city": "北京", "balance": 10000}
  ↓
直接回答：张三的当前余额是10000元。
```

---

### 场景2：多工具顺序调用

```
用户：张三向李四转账3000元
  ↓
LLM 分析：需要先查余额确认够不够
  ↓
第1步：调用 query_user("张三")
  → 返回：余额10000元 ✅ 够
  ↓
第2步：调用 transfer("张三", "李四", 3000)
  → 返回：转账成功
  ↓
回答：转账成功！张三7000元，李四28000元。
```

---

### 场景3：多工具并行调用

```
用户：北京天气怎么样？张三在那边适合出门吗？
  ↓
LLM 分析：需要天气信息 + 用户所在城市
  ↓
第1步：调用 query_user("张三")
  → 返回：city="北京"
  ↓
第2步：调用 get_weather("北京")
  → 返回：晴天 15-25度
  ↓
综合两个工具结果回答：
北京晴天，15-25度，非常适合出门。张三在北京，可以放心出行。
```

---

## 📋 工具调用模式总结

| 模式 | 特点 | 示例 |
|------|------|------|
| **单工具** | 只需调用一个工具 | 查询余额、查询天气 |
| **顺序调用** | 先查后改，有依赖关系 | 查余额 → 转账 |
| **并行调用** | 多个独立信息，可同时获取 | 查用户城市 + 查天气 |

---

## 💡 核心优势

### ✅ 开发者只需定义工具

```python
# 只需要：
# 1. 定义工具函数
# 2. 写好工具描述（docstring）
# 3. 传给 create_agent

app = create_agent(llm, [query_user, calculate, transfer, get_weather])

# 不需要写：
# ❌ 工具调用逻辑
# ❌ 条件判断
# ❌ 循环控制
```

### ✅ LLM 自动编排

- **智能选择**：根据问题自动选择合适的工具
- **合理排序**：有依赖关系的工具按顺序调用
- **并行优化**：独立的工具可以同时调用
- **动态决策**：根据中间结果决定下一步

---

## ⚠️ 注意事项

### 1️⃣ 工具描述很重要

```python
# ✅ 好的描述：清晰说明用途和参数
@tool
def transfer(from_user: str, to_user: str, amount: float) -> str:
    """转账操作，输入转出人、转入人和金额。"""

# ❌ 差的描述：模糊不清
@tool
def transfer(a, b, c):
    """转账。"""
```

### 2️⃣ 工具之间不要有副作用冲突

```python
# ✅ 安全：每次调用都基于最新状态
@tool
def query_user(name: str) -> str:
    user = user_database.get(name)  # 实时查询

# ❌ 危险：缓存旧数据可能导致不一致
cached_data = {}  # 不要这样！
```

### 3️⃣ 工具数量不宜过多

- **推荐**：5-10个工具
- **原因**：工具太多会增加 LLM 的选择难度
- **解决方案**：使用子图或分类管理

---

## 🎯 核心要点

- ✅ **多工具组合**：LLM 自动选择和编排多个工具
- ✅ **智能决策**：根据问题复杂度决定调用几个工具
- ✅ **灵活编排**：支持单工具、顺序调用、并行调用
- ✅ **开发简单**：只需定义工具和描述，无需编写调用逻辑
- ✅ **工具描述关键**：清晰的 docstring 帮助 LLM 正确选择
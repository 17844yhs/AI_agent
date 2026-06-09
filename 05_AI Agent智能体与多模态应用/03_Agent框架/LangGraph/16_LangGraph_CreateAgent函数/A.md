# 🎯 学习目标

- 理解 **ReAct 模式**：推理（Reasoning）+ 行动（Acting）的循环
- 掌握 `create_agent` 的一行代码创建 Agent
- 了解手动构建与 `create_agent` 的对应关系

---

## 📖 介绍

我们手动构建了 Agent 的完整 Graph（定义节点、条件边、循环）。LangGraph 提供了 **`create_agent`** 函数，一行代码就能创建一个标准的 ReAct Agent。

---

## 🚗 生活化比喻：买车

| 方式 | 类比 | 特点 |
|------|------|------|
| **手动构建** | 自己买零件组装一辆车（发动机、方向盘、轮胎...） | 灵活但繁琐 ❌ |
| **create_agent** | 直接从4S店提一辆现成的车 | 省事高效 ✅ |

**功能一样，但省去了组装的麻烦！**

---

## 🔄 ReAct 模式原理

```
用户输入 → LLM 思考 → 需要工具？
              ↓ 是
          调用工具 → 获取结果 → 回到 LLM 思考
              ↓ 否
          直接回答 → 结束
```

**核心**：推理（Reasoning）+ 行动（Acting）的循环

---

## 💻 代码示例：一行创建 Agent

```python
import os
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_agent
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# 1. 定义工具
@tool
def search(query: str) -> str:
    """搜索互联网信息，输入搜索关键词"""
    results = {
        "北京": "北京：故宫、长城、颐和园，历史文化深厚",
        "上海": "上海：外滩、东方明珠、迪士尼，现代都市风情",
    }
    for key, value in results.items():
        if key in query:
            return value
    return f"关于'{query}'的搜索结果：找到5条相关内容"

@tool
def calculator(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{e}"

@tool
def get_weather(city: str) -> str:
    """查询城市天气"""
    weather_data = {"北京": "晴天 15-25度", "上海": "多云 18-28度"}
    return weather_data.get(city, f"暂无{city}天气数据")

# 2. 一行代码创建 Agent
app = create_agent(llm, [search, calculator, get_weather])

# 3. 测试
questions = [
    "北京今天天气怎么样？适合出游吗？",
    "帮我算一下，旅行预算5000元，住宿花了2000，吃饭花了800，还剩多少？",
    "你好，你是什么模型？"
]

for question in questions:
    print(f"用户：{question}")
    result = app.invoke({"messages": [HumanMessage(question)]})
    print(f"AI：{result['messages'][-1].content}")
    print()
```

### 📊 运行结果

```
用户：北京今天天气怎么样？适合出游吗？
AI：北京今天晴天，气温15-25度，非常适合出游！推荐去故宫和长城。

用户：帮我算一下，如果旅行预算是5000元，住宿花了2000，吃饭花了800，还剩多少？
AI：5000 - 2000 - 800 = 2200元，还剩2200元。

用户：你好，你是什么模型？
AI：你好！我是一个AI助手，可以帮你搜索信息、计算和查询天气。
```

---

## 📋 手动构建 vs create_agent

| 对比项 | 手动构建 | create_agent |
|--------|---------|--------------|
| **代码量** | ~30行 | ✅ ~3行 |
| **灵活性** | ✅ 完全自定义 | ⚠️ 使用标准 ReAct 模式 |
| **适用场景** | 需要定制 Agent 行为 | ✅ 标准 Agent 快速搭建 |
| **内部结构** | ✅ 可控 | ⚠️ 自动处理（LLM + ToolNode + 循环） |
| **开发速度** | ⚠️ 较慢 | ✅ 快速 |

---

## 🔍 create_agent 内部结构

`create_agent` 内部自动构建了以下 Graph：

```
agent(LLM) ──[需要工具]──→ ToolNode ──→ agent（循环）
  │
  └──[不需要工具]──→ END
  
# 内部使用的就是 tools_condition + ToolNode
```

### 📝 等价的手动构建代码

```python
# create_agent 等效于以下手动构建代码：
graph = StateGraph(AgentState)
graph.add_node("agent", agent_node)
graph.add_node("tools", ToolNode(tools))

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", tools_condition, {
    "tools": "tools",
    END: END
})
graph.add_edge("tools", "agent")

app = graph.compile()
```

---

## 💡 最佳实践

### ✅ 推荐使用 create_agent

```python
# 标准写法：一行创建 Agent
app = create_agent(llm, [search, calculator, get_weather])
```

**适用场景**：
- 90% 的标准 Agent 需求
- 快速原型开发
- 不需要特殊定制

### ⚠️ 何时手动构建

只有在需要**定制 Agent 行为**时才手动构建：

- 添加中间处理节点
- 自定义终止条件
- 特殊的消息处理逻辑
- 复杂的状态管理

---

## 🎯 核心要点

- ✅ **ReAct 模式**：推理 + 行动的循环，Agent 的核心范式
- ✅ **create_agent**：一行代码创建标准 ReAct Agent
- ✅ **内部实现**：自动使用 `tools_condition` + `ToolNode` + 循环
- ✅ **快速开发**：适合大多数标准场景
- ✅ **手动构建**：需要定制时才使用，提供完全控制权
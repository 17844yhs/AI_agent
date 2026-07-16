# LangSmith 检测 LangGraph

## 学习目标

- 使用 LangSmith 追踪 Agent 执行过程
- 学会调试带记忆的 Agent
- 理解在 LangSmith 中查看 Agent 执行流程的方法

---

## 示例1：追踪 Agent 执行过程

```python
import os
import json
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

@tool
def search_weather(city: str) -> str:
    """查询城市天气"""
    # 模拟天气查询
    weather_data = {
        "北京": "晴天，15°C",
        "上海": "多云，18°C",
        "杭州": "小雨，12°C",
    }
    return weather_data.get(city, f"{city}：暂无天气数据")

@tool
def calculate(expression: str) -> str:
    """计算数学表达式"""
    try:
        result = eval(expression)  # 仅用于演示，生产环境不要用 eval
        return f"计算结果：{result}"
    except Exception as e:
        return f"计算错误：{e}"

# 创建 Agent
tools = [search_weather, calculate]
app = create_agent(llm, tools)

# 执行（LangSmith 自动追踪每一步）
result = app.invoke({
    "messages": [HumanMessage("北京天气怎么样？如果出门需要穿几度对应的衣服？")]
})
print(result["messages"][-1].content)
```

**在 LangSmith 中可查看：**
- Agent 的思考过程（是否调用工具、调用哪个工具）
- 工具调用的参数和返回结果
- 最终回答的生成过程

---

## 示例2：追踪带记忆的 Agent

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
app_with_memory = create_agent(llm, tools, checkpointer=memory)

config = {"configurable": {"thread_id": "user-001"}}

# 第一轮对话
print("=== 第一轮 ===")
result1 = app_with_memory.invoke(
    {"messages": [HumanMessage("我叫张三")]},
    config
)
print(result1["messages"][-1].content)

# 第二轮对话（有记忆）
print("=== 第二轮 ===")
result2 = app_with_memory.invoke(
    {"messages": [HumanMessage("我叫什么名字？")]},
    config
)
print(result2["messages"][-1].content)
```

**运行结果：**
```
=== 第一轮 ===
你好张三，很高兴认识你！

=== 第二轮 ===
你叫张三。
```

**在 LangSmith 中可以看到：**
- 第一轮 Trace：Agent 回答 "你好张三"
- 第二轮 Trace：Agent 从记忆中读取上下文，正确回答 "你叫张三"
- 对比两次 Trace 的 `messages` 字段，可以看到记忆是如何注入的

---

## 关键要点总结

| 要点 | 说明 |
|------|------|
| **自动追踪** | LangSmith 自动记录 Agent 的每一步执行 |
| **工具调用** | 可查看调用了哪些工具、参数是什么、返回结果 |
| **记忆机制** | 可查看 `messages` 字段，理解记忆是如何注入的 |
| **多轮对话** | 对比不同轮次的 Trace，分析上下文保持情况 |
| **调试价值** | 定位 Agent 决策错误、工具调用问题、记忆失效等问题 |

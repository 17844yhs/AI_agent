# 🎯 学习目标

- 掌握 `add_conditional_edges` 的用法
- 理解路由函数的设计模式
- 了解如何根据 State 中的字段动态选择执行路径

---

## 📖 介绍

**条件路由**让 Graph 根据运行时的数据动态选择不同的执行路径，类似编程中的 `if-elif-else`。

---

## 📦 生活化比喻：快递分拣

| 方式               | 行为                   | 结果                          |
| ------------------ | ---------------------- | ----------------------------- |
| **普通边**   | 所有快递走同一条传送带 | 无法区分目的地 ❌             |
| **条件边**   | 扫描地址后分流         | 国内件→左边，国际件→右边 ✅ |
| **路由函数** | 扫描快递地址的"扫码枪" | 决定走哪条路 🎯               |

---

## 💻 代码示例：智能问答路由

```python
import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

load_dotenv()

# 1. 定义 State
class RouterState(TypedDict):
    input: str
    category: str
    response: str

# 2. 定义节点
def classify_node(state: RouterState):
    """分类节点：使用LLM判断输入类型"""
    llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    prompt = f"""请判断以下用户输入属于哪个类别，只回复类别名（math/code/general）：
用户输入：{state['input']}"""
    response = llm.invoke(prompt)
    category = response.content.strip().lower()
    # 确保category是有效值
    if category not in ("math", "code", "general"):
        category = "general"
    return {"category": category}

def math_handler(state: RouterState):
    """数学问题处理器"""
    llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    response = llm.invoke(f"请解答这道数学题：{state['input']}")
    return {"response": response.content}

def code_handler(state: RouterState):
    """代码问题处理器"""
    llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    response = llm.invoke(f"请编写代码实现：{state['input']}")
    return {"response": response.content}

def general_handler(state: RouterState):
    """通用问题处理器"""
    llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    response = llm.invoke(f"请回答这个问题：{state['input']}")
    return {"response": response.content}

# 3. 路由函数（返回下一个节点的名称）
def route_function(state: RouterState) -> str:
    """根据分类结果路由到不同处理器"""
    if state["category"] == "math":
        return "math_handler"
    elif state["category"] == "code":
        return "code_handler"
    return "general_handler"

# 4. 构建 Graph
graph = StateGraph(RouterState)
graph.add_node("classify", classify_node)
graph.add_node("math_handler", math_handler)
graph.add_node("code_handler", code_handler)
graph.add_node("general_handler", general_handler)

graph.set_entry_point("classify")

# 关键：条件边，路由函数返回值决定走哪个分支
graph.add_conditional_edges(
    "classify",
    route_function,
    {
        "math_handler": "math_handler",
        "code_handler": "code_handler",
        "general_handler": "general_handler"
    }
)

# 所有分支最终都结束
graph.add_edge("math_handler", END)
graph.add_edge("code_handler", END)
graph.add_edge("general_handler", END)

# 5. 编译并运行
app = graph.compile()

test_inputs = [
    "帮我计算 1+1等于几",
    "用Python写一个冒泡排序",
    "今天天气怎么样"
]

for test_input in test_inputs:
    result = app.invoke({"input": test_input})
    print(f"输入：{test_input}")
    print(f"分类：{result['category']}")
    print(f"输出：{result['response'][:50]}...")
    print()
```

### 📊 运行结果

```
输入：帮我计算 1+1等于几
分类：math
输出：1+1等于2...

输入：用Python写一个冒泡排序
分类：code
输出：以下是Python冒泡排序的实现...

输入：今天天气怎么样
分类：general
输出：作为AI，我无法获取实时天气信息...
```

---

## 🔍 add_conditional_edges 参数解析

```python
graph.add_conditional_edges(
    "classify",              # 参数1：从哪个节点出发
    route_function,          # 参数2：路由函数，返回下一个节点名称
    {                        # 参数3：路由映射表
        "math_handler": "math_handler",      # 返回值 → 目标节点
        "code_handler": "code_handler",
        "general_handler": "general_handler"
    }
)
```

### 📋 参数说明

| 参数               | 类型         | 说明                                   |
| ------------------ | ------------ | -------------------------------------- |
| **source**   | `str`      | 起始节点名称                           |
| **path**     | `Callable` | 路由函数，接收 State，返回目标节点名称 |
| **path_map** | `dict`     | 路由映射表：`{返回值: 目标节点}`     |

---

## ⚠️ 注意事项

1. **路由函数返回值必须与映射表中的 key 匹配**

   - 不匹配会报错 ❌
2. **建议添加默认分支兜底**

   ```python
   def route_function(state: RouterState) -> str:
       if state["category"] == "math":
           return "math_handler"
       elif state["category"] == "code":
           return "code_handler"
       return "general_handler"  # 默认分支 ✅
   ```
3. **映射表的 value 必须是已注册的节点名称**

---

## 🎯 核心要点

- ✅ **条件路由 = 动态分支**：根据 State 内容选择执行路径
- ✅ **路由函数**：接收 State，返回目标节点名称字符串
- ✅ **路由映射表**：将返回值映射到具体节点
- ✅ **默认分支**：防止未匹配的情况导致错误

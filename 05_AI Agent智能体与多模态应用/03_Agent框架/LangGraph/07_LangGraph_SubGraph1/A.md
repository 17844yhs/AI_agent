# 🎯 学习目标

- 理解 **SubGraph** 的设计思想：将复杂 Graph 拆分为可复用的模块
- 掌握子图的创建和嵌入方式
- 了解父子图之间的 State 映射

---

## 📖 介绍

当 Graph 变得复杂时，可以将一部分节点和边封装为**子图**，再嵌入到主图中。就像函数封装一样：把重复逻辑抽成函数，主函数调用它。

### 🔍 对比示例

#### ❌ 没有子图（所有逻辑平铺）
```
主图：classify → translate → summarize → format → output
问题：节点太多，难以管理
```

#### ✅ 有子图（模块化）
```
主图：classify → [翻译子图] → [总结子图] → output
                ↓
            translate → polish
            
                ↓
            summarize
```

---

## 🏢 生活化比喻：公司架构

| 方式 | 结构 | 结果 |
|------|------|------|
| **没有子图** | 所有员工直接向CEO汇报 | 几十个人排队，混乱 ❌ |
| **有子图** | CEO → 部门经理 → 员工 | 层级清晰，各司其职 ✅ |
| **部门经理** | 子图的入口 | CEO不需要知道部门内部怎么运作 🎯 |

---

## 💻 代码示例：翻译模块

### 1️⃣ 子图：翻译模块

```python
import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

# ===== 子图：翻译模块 =====
class TranslateState(TypedDict):
    text: str
    translated: str

def translate_node(state: TranslateState):
    """翻译节点：中译英"""
    response = llm.invoke(f"将以下中文翻译为英文：{state['text']}")
    return {"translated": response.content}

def polish_node(state: TranslateState):
    """润色节点：优化翻译"""
    response = llm.invoke(f"请润色以下英文翻译，使其更地道：\n{state['translated']}")
    return {"translated": response.content}

# 构建子图
sub_graph = StateGraph(TranslateState)
sub_graph.add_node("translate", translate_node)
sub_graph.add_node("polish", polish_node)
sub_graph.add_edge(START, "translate")
sub_graph.add_edge("translate", "polish")
sub_graph.add_edge("polish", END)

translate_app = sub_graph.compile()
```

### 2️⃣ 主图：调用子图

```python
# ===== 主图 =====
class MainState(TypedDict):
    input: str
    category: str
    result: str

def classify_node(state: MainState):
    """分类节点：判断是否需要翻译"""
    if any('\u4e00' <= c <= '\u9fff' for c in state["input"]):
        return {"category": "chinese"}
    return {"category": "other"}

def call_translate(state: MainState):
    """调用翻译子图"""
    # 将主图State映射为子图State，调用子图
    sub_result = translate_app.invoke({
        "text": state["input"],
        "translated": ""
    })
    return {"result": sub_result["translated"]}

def default_handler(state: MainState):
    """非中文内容直接返回"""
    return {"result": f"无需翻译：{state['input']}"}

def route(state: MainState) -> str:
    """路由函数"""
    return "translate" if state["category"] == "chinese" else "default"

# 构建主图
graph = StateGraph(MainState)
graph.add_node("classify", classify_node)
graph.add_node("translate", call_translate)
graph.add_node("default", default_handler)

graph.add_edge(START, "classify")
graph.add_conditional_edges("classify", route, {
    "translate": "translate",
    "default": "default"
})
graph.add_edge("translate", END)
graph.add_edge("default", END)

app = graph.compile()

# 测试
tests = ["今天天气真好", "Hello World"]
for text in tests:
    result = app.invoke({
        "input": text,
        "category": "",
        "result": ""
    })
    print(f"输入：{text}")
    print(f"分类：{result['category']}")
    print(f"结果：{result['result'][:60]}...")
    print()
```

### 📊 运行结果

```
输入：今天天气真好
分类：chinese
结果：The weather is really nice today...

输入：Hello World
分类：other
结果：无需翻译：Hello World
```

---

## 🔑 子图的关键点

| 特性 | 说明 |
|------|------|
| **独立 State** | 子图有自己的 State（`TranslateState` vs `MainState`） |
| **手动映射** | 主图通过 `invoke` 调用子图，需手动做 State 映射 |
| **独立编译** | 子图可以单独编译和测试 |
| **复用性** | 一个子图可以在多个主图中复用 |

---

## 🎯 核心要点

- ✅ **子图 = 模块化**：将复杂逻辑拆分为可管理的模块
- ✅ **独立 State**：父子图使用不同的 State 类型
- ✅ **手动映射**：调用子图时需转换 State 字段
- ✅ **高复用性**：一次编写，多处调用
- ✅ **易测试**：子图可独立测试，降低调试难度
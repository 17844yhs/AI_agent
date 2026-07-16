# 🎯 学习目标

- 理解 `app.stream()` 与 `app.invoke()` 的区别
- 掌握 stream 的不同模式：`values`、`updates`
- 掌握 `get_graph().print_ascii()` 可视化 Graph 结构

---

## 📖 介绍

| 方法               | 行为                               | 用户体验        |
| ------------------ | ---------------------------------- | --------------- |
| **invoke()** | 等整个 Graph 跑完才返回最终结果    | 用户干等 ❌     |
| **stream()** | 每执行完一个节点就实时输出中间结果 | 全程可见进度 ✅ |

### 🔍 对比示例

#### ❌ invoke（一次性返回）

```
用户等待...等待...等待... → 拿到最终结果
```

#### ✅ stream（逐步返回）

```
节点A完成 → 立即展示
节点B完成 → 立即展示
节点C完成 → 立即展示
用户全程能看到进度
```

---

## 🛵 生活化比喻：外卖配送

| 方式             | 行为                                                       | 体验        |
| ---------------- | ---------------------------------------------------------- | ----------- |
| **invoke** | 下单后一直等，直到外卖送到门口才知道状态                   | 焦虑等待 ❌ |
| **stream** | 实时看到：已接单 → 制作中 → 骑手取餐 → 配送中 → 已送达 | 安心追踪 ✅ |

---

## 💻 代码示例：流式输出

```python
from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, END

class StreamState(TypedDict):
    text: str
    steps: Annotated[list, add]  # 使用 add reducer 自动合并 steps

def step1_node(state: StreamState):
    """步骤1：大写转换"""
    return {
        "text": state["text"].upper(),
        "steps": ["大写转换"]
    }

def step2_node(state: StreamState):
    """步骤2：添加标记"""
    return {
        "text": f"[{state['text']}]",
        "steps": ["添加标记"]
    }

def step3_node(state: StreamState):
    """步骤3：添加序号"""
    return {
        "text": f"1. {state['text']}",
        "steps": ["添加序号"]
    }

# 构建 Graph
graph = StateGraph(StreamState)
graph.add_node("step1", step1_node)
graph.add_node("step2", step2_node)
graph.add_node("step3", step3_node)

graph.set_entry_point("step1")
graph.add_edge("step1", "step2")
graph.add_edge("step2", "step3")
graph.add_edge("step3", END)

app = graph.compile()
```

### 1️⃣ values 模式：输出完整 State

```python
# 方式1：values 模式（输出每一步的完整 State）
print("=== stream_mode='values' ===")
for state in app.stream(
    {"text": "hello langgraph", "steps": []},
    stream_mode="values"
):
    print(f"  State: {state}")
```

#### 📊 运行结果

```
=== stream_mode='values' ===
  State: {'text': 'hello langgraph', 'steps': []}
  State: {'text': 'HELLO LANGGRAPH', 'steps': ['大写转换']}
  State: {'text': '[HELLO LANGGRAPH]', 'steps': ['大写转换', '添加标记']}
  State: {'text': '1. [HELLO LANGGRAPH]', 'steps': ['大写转换', '添加标记', '添加序号']}
```

### 2️⃣ updates 模式：输出增量更新

```python
# 方式2：updates 模式（只输出每一步的增量更新）
print("=== stream_mode='updates' ===")
for update in app.stream(
    {"text": "hello langgraph", "steps": []},
    stream_mode="updates"
):
    print(f"  节点更新: {update}")
```

#### 📊 运行结果

```
=== stream_mode='updates' ===
  节点更新: {'step1': {'text': 'HELLO LANGGRAPH', 'steps': ['大写转换']}}
  节点更新: {'step2': {'text': '[HELLO LANGGRAPH]', 'steps': ['添加标记']}}
  节点更新: {'step3': {'text': '1. [HELLO LANGGRAPH]', 'steps': ['添加序号']}}
```

---

## 📋 两种模式对比

| 模式              | 输出内容         | 适用场景                       |
| ----------------- | ---------------- | ------------------------------ |
| **values**  | 每步的完整 State | 需要跟踪完整状态变化（调试）   |
| **updates** | 每步的增量更新   | 只关心当前节点做了什么（生产） |

---

## 🗺️ Graph 可视化

### ASCII 可视化

```python
# 查看 Graph 结构
print(app.get_graph().print_ascii())
```

#### 📊 运行结果

```
    +-----------+
    |  __start__|
    +-----------+
     |
     v
   +-------+
   | step1 |
   +-------+
     |
     v
   +-------+
   | step2 |
   +-------+
     |
     v
   +-------+
   | step3 |
   +-------+
     |
     v
    +---------+
    | __end__ |
    +---------+
```

---

## 🎯 核心要点

- ✅ **invoke vs stream**：一次性返回 vs 实时流式输出
- ✅ **values 模式**：输出完整 State，适合调试
- ✅ **updates 模式**：输出增量更新，适合生产环境
- ✅ **可视化**：`get_graph().print_ascii()` 快速查看 Graph 结构
- ✅ **用户体验**：stream 让用户实时看到进度，减少等待焦虑

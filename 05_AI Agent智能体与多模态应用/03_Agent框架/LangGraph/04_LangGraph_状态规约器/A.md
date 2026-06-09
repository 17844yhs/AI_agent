# 🎯 学习目标

- 理解 **Reducer** 的作用：控制 State 字段的更新方式
- 掌握常用 Reducer：`operator.add`、自定义 Reducer 函数
- 了解不同 Reducer 对 State 更新的影响

---

## 📖 介绍

前面在线性 Graph 中看到，节点返回的字典会**覆盖**同名字段。但有些场景需要**累加**而不是覆盖——比如多个节点各自添加一条消息，最终合并为消息列表。

**Reducer** 决定了当多个节点更新同一个 State 字段时，如何合并这些更新。

### 🔍 对比示例

#### ❌ 没有 Reducer（默认行为）
```
节点A返回 {"score": 10}
节点B返回 {"score": 20}
→ 最终 State：score = 20（后写覆盖前写）
```

#### ✅ 有 Reducer（如 `operator.add`）
```
节点A返回 {"score": 10}
节点B返回 {"score": 20}
→ 最终 State：score = 30（累加）
```

---

## 💰 生活化比喻：银行账户

| 方式 | 行为 | 结果 |
|------|------|------|
| **没有 Reducer** | 每次交易直接设置余额 | 第2笔交易覆盖第1笔 ❌ |
| **有 Reducer (add)** | 每次交易在余额上累加 | 存100 + 存50 = 余额150 ✅ |

---

## 🔧 常用 Reducer

```python
from typing import Annotated
from operator import add

# 1. add（累加）：适合列表、数字
messages: Annotated[list, add]      # 多个节点的消息自动合并
total: Annotated[int, add]          # 多个节点的数值自动累加

# 2. 默认（覆盖）：不写 Annotated 就是覆盖
result: str                         # 后写的值覆盖前写的值
```

---

## 💻 代码示例：评委打分系统

```python
from typing import Annotated, TypedDict
from operator import add
from langgraph.graph import StateGraph, END

# 1. 定义 State，不同字段使用不同 Reducer
class ScoreState(TypedDict):
    # add Reducer：多个节点的值会累加
    total_score: Annotated[int, add]
    # add Reducer：多个节点的消息会合并为一个列表
    comments: Annotated[list, add]
    # 无 Reducer：后写的值覆盖前写的值
    winner: str

# 2. 定义节点
def judge_a(state: ScoreState):
    """评委A打分"""
    return {
        "total_score": 85,
        "comments": ["评委A：表现优秀，逻辑清晰"],
    }

def judge_b(state: ScoreState):
    """评委B打分"""
    return {
        "total_score": 90,
        "comments": ["评委B：创意不错，可以改进"],
    }

def judge_c(state: ScoreState):
    """评委C打分"""
    return {
        "total_score": 78,
        "comments": ["评委C：整体不错，细节待完善"],
    }

def summarize(state: ScoreState):
    """汇总节点：根据总分判断胜负"""
    avg = state["total_score"] / 3
    if avg >= 85:
        winner = "通过"
    else:
        winner = "未通过"
    return {"winner": f"平均分{avg:.1f}，{winner}"}

# 3. 构建 Graph
graph = StateGraph(ScoreState)
graph.add_node("judge_a", judge_a)
graph.add_node("judge_b", judge_b)
graph.add_node("judge_c", judge_c)
graph.add_node("summarize", summarize)

graph.set_entry_point("judge_a")
graph.add_edge("judge_a", "judge_b")
graph.add_edge("judge_b", "judge_c")
graph.add_edge("judge_c", "summarize")
graph.add_edge("summarize", END)

app = graph.compile()
result = app.invoke({"total_score": 0, "comments": [], "winner": ""})

print(f"总分：{result['total_score']}")       # 85 + 90 + 78 = 253
print(f"评论数：{len(result['comments'])}")   # 3条评论自动合并
for comment in result["comments"]:
    print(f"  {comment}")
print(f"结论：{result['winner']}")
```

### 📊 运行结果

```
总分：253
评论数：3
  评委A：表现优秀，逻辑清晰
  评委B：创意不错，可以改进
  评委C：整体不错，细节待完善
结论：平均分84.3，未通过
```

---

## 📋 Reducer 对比总结

| 方式 | 语法 | 行为 | 适用场景 |
|------|------|------|----------|
| **默认覆盖** | `name: str` | 后写覆盖前写 | 单一结果字段 |
| **add 累加** | `Annotated[int, add]` | 数值累加 | 计数、求和 |
| **add 合并** | `Annotated[list, add]` | 列表合并 | 消息列表、评论列表 |

---

## 🎯 核心要点

- ✅ **Reducer 控制字段更新策略**：覆盖 vs 累加 vs 合并
- ✅ **`Annotated[type, reducer]`**：声明式指定 Reducer
- ✅ **`operator.add`**：最常用的 Reducer，支持数字累加和列表合并
- ✅ **默认行为**：不写 `Annotated` 就是覆盖
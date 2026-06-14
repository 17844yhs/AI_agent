# 🎯 学习目标

- 理解 LangGraph 中并行执行的概念
- 掌握使用条件边实现"扇出-汇聚"模式
- 了解并行执行对性能的提升

---

## 📖 介绍

默认情况下，Graph 的节点是**串行执行**的（A → B → C）。但有些场景中多个节点之间没有依赖关系，可以**同时执行**，最后汇聚结果。

---

## 👨‍🍳 生活化比喻：厨房做菜

| 方式 | 行为 | 耗时 |
|------|------|------|
| **串行** | 一个人先洗菜、再切菜、再炒菜、再装盘 | 慢 ❌ |
| **并行** | 一人洗菜 + 一人切菜 + 一人热锅（同时进行） | 快 ✅ |

**关键**：三件事互不依赖，同时做更快！

---

## 💻 代码示例：并行任务处理

```python
import time
from typing import TypedDict
from langgraph.graph import StateGraph, END, START

# 1. 定义状态结构
class ParallelState(TypedDict):
    text: str
    translation: str
    summary: str
    keywords: str
    final: str

# 2. 定义各个节点（业务逻辑）
def translate_node(state: ParallelState):
    """翻译节点：耗时 0.5s"""
    time.sleep(0.5)
    print("--- 完成翻译 (0.5s) ---")
    return {"translation": f"[翻译] {state['text']}"}

def summary_node(state: ParallelState):
    """总结节点：耗时 0.3s"""
    time.sleep(0.3)
    print("--- 完成总结 (0.3s) ---")
    return {"summary": "[总结] 这是一段关于 LangGraph 并行机制的演示。"}

def keywords_node(state: ParallelState):
    """关键词提取节点：耗时 0.2s"""
    time.sleep(0.2)
    print("--- 完成关键词提取 (0.2s) ---")
    return {"keywords": "[关键词] AI, LangGraph, 并行计算"}

def merge_node(state: ParallelState):
    """汇聚节点：只有当上述三个节点都完成后，该节点才会被触发一次"""
    print("--- 正在合并结果 ---")
    parts = [
        state["translation"],
        state["summary"],
        state["keywords"]
    ]
    return {"final": "\n".join(parts)}

# 3. 构建图
workflow = StateGraph(ParallelState)

# 添加节点
workflow.add_node("translate", translate_node)
workflow.add_node("summary", summary_node)
workflow.add_node("keywords", keywords_node)
workflow.add_node("merge", merge_node)

# --- 关键：并行逻辑设计 ---

# 从 START 同时指向三个任务节点，实现 Fan-out（扇出）
workflow.add_edge(START, "translate")
workflow.add_edge(START, "summary")
workflow.add_edge(START, "keywords")

# 三个任务节点都指向 merge 节点，实现 Fan-in（扇入/汇聚）
workflow.add_edge("translate", "merge")
workflow.add_edge("summary", "merge")
workflow.add_edge("keywords", "merge")

# 最后从汇聚点结束
workflow.add_edge("merge", END)

# 编译
app = workflow.compile()

# 4. 运行并计时
print("开始并行任务...\n")
start_time = time.time()

inputs = {
    "text": "LangGraph is a powerful framework for building stateful multi-agent systems.",
    "translation": "",
    "summary": "",
    "keywords": "",
    "final": ""
}

# 使用 invoke 调用
result = app.invoke(inputs)

elapsed = time.time() - start_time

print("-" * 30)
print(result["final"])
print("-" * 30)
print(f"实际总耗时：{elapsed:.2f} 秒")
print("理论预期：接近最慢的单任务耗时（0.5s）")
```

### 📊 运行结果

```
开始并行任务...

--- 完成关键词提取 (0.2s) ---
--- 完成总结 (0.3s) ---
--- 完成翻译 (0.5s) ---
--- 正在合并结果 ---
------------------------------
[翻译] LangGraph is a powerful framework for building stateful multi-agent systems.
[总结] 这是一段关于 LangGraph 并行机制的演示。
[关键词] AI, LangGraph, 并行计算
------------------------------
实际总耗时：0.50 秒
理论预期：接近最慢的单任务耗时（0.5s）
```

---

## 🔄 并行模式：扇出-汇聚

```
         ┌→ translate (0.5s) ─┐
START ───┼→ summary   (0.3s) ─┼→ merge → END
         └→ keywords  (0.2s) ─┘
         
    Fan-out (扇出)      Fan-in (汇聚)
```

### 🔑 关键设计

| 步骤 | 操作 | 说明 |
|------|------|------|
| **Fan-out** | `START` → 多个节点 | 同时启动多个独立任务 |
| **并行执行** | 三个节点同时运行 | 互不依赖，并发处理 |
| **Fan-in** | 多个节点 → `merge` | 等待所有任务完成后汇聚 |

---

## ⚡ 性能对比

| 执行方式 | 总耗时 | 说明 |
|---------|--------|------|
| **串行执行** | 0.5 + 0.3 + 0.2 = 1.0s | 依次执行，累加耗时 ❌ |
| **并行执行** | max(0.5, 0.3, 0.2) ≈ 0.5s | 同时执行，取最大值 ✅ |

**提升**：节省约 **50%** 的时间！

---

## 🎯 核心要点

- ✅ **并行执行**：多个无依赖节点可同时运行
- ✅ **Fan-out**：从起点分发到多个节点
- ✅ **Fan-in**：多个节点汇聚到一个节点
- ✅ **性能提升**：总耗时 ≈ 最慢任务的耗时
- ✅ **适用场景**：独立任务（翻译、总结、关键词提取等）
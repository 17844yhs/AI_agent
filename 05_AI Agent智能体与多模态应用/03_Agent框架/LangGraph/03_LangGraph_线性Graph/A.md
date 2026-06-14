# 🎯 学习目标

- 掌握 `StateGraph` 的基本用法
- 理解 State 在节点间的传递方式
- 了解 `set_entry_point` 和 `END` 的作用

---

## 📖 介绍

最简单的 Graph 结构，节点按顺序依次执行，与 LCEL 的 `|` 管道类似，但使用 Graph 结构为后续扩展（添加分支、循环）打下基础。

```
输入 → process → format → 输出
```

---

## 💻 代码示例：线性 Graph

```python
import os
from dotenv import load_dotenv
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI

load_dotenv()

# 1. 定义 State
class SimpleState(TypedDict):
    input: str
    processed: str
    output: str

# 2. 定义节点（每个节点接收State，返回更新后的State）
def process_node(state: SimpleState):
    """处理节点：调用LLM"""
    llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    response = llm.invoke(state["input"])
    return {"processed": response.content}

def format_node(state: SimpleState):
    """格式化节点：添加格式"""
    formatted = f"处理结果：\n{state['processed']}"
    return {"output": formatted}

# 3. 构建 Graph
graph = StateGraph(SimpleState)
graph.add_node("process", process_node)
graph.add_node("format", format_node)

# 4. 添加边
graph.set_entry_point("process")      # 入口节点
graph.add_edge("process", "format")   # process → format
graph.add_edge("format", END)         # format → 结束

# 5. 编译并运行
app = graph.compile()
result = app.invoke({"input": "简单介绍一下Python"})
print(f"最终输出：\n{result['output']}")
```

### 📊 运行结果

```
最终输出：
处理结果：
Python是一种高级编程语言...
```

---

## 🔄 State 传递规则

### 🔑 关键规则

**节点返回的字典会与当前 State 合并（覆盖同名字段）**

### 📋 传递过程示例

```python
# 初始 State
{"input": "hello", "processed": "", "output": ""}

# process 节点返回
{"processed": "处理后的文本"}

# ↓ 合并后
{"input": "hello", "processed": "处理后的文本", "output": ""}

# format 节点返回
{"output": "处理结果：处理后的文本"}

# ↓ 合并后
{"input": "hello", "processed": "处理后的文本", "output": "处理结果：处理后的文本"}
```

---

## ⚠️ 重要注意事项

### ✅ 最佳实践

- **只需返回要更新的字段**，不需要返回完整的 State
- LangGraph 会**自动合并**节点返回值和当前 State
- 同名键会被**覆盖**，其他字段保持不变

### ❌ 常见错误

```python
# ❌ 错误：返回完整 State（冗余）
def process_node(state: SimpleState):
    return {
        "input": state["input"],      # 不需要重复返回
        "processed": "处理后的文本",
        "output": state["output"]     # 不需要重复返回
    }

# ✅ 正确：只返回更新的字段
def process_node(state: SimpleState):
    return {"processed": "处理后的文本"}
```

---

## 🎯 核心要点

- ✅ **StateGraph**：LangGraph 的核心构建块
- ✅ **TypedDict**：定义 State 结构，类型安全
- ✅ **节点函数**：接收 State，返回更新的字段字典
- ✅ **自动合并**：LangGraph 自动合并节点返回值和当前 State
- ✅ **set_entry_point**：指定 Graph 的入口节点
- ✅ **END**：标记 Graph 的结束点
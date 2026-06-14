# 🎯 学习目标

- 理解如何通过条件边实现循环
- 掌握循环终止条件的设置方式

---

## 📖 介绍

**循环**是 LangGraph 区别于 LCEL 的核心能力之一。通过条件边将执行路径指回之前的节点，可以实现：

- ✅ 失败重试
- ✅ 反复优化
- ✅ 自我修正

---

## 🎓 生活化比喻：考试补考

| 方式 | 行为 | 结果 |
|------|------|------|
| **线性流程** | 只有一次考试机会 | 不及格就淘汰 ❌ |
| **循环流程** | 不及格可以补考 | 最多补考3次 ✅ |
| **条件函数** | 判断"及格了吗？补考次数超了吗？" | 决定继续或结束 🎯 |

---

## 💻 代码示例：重试机制

```python
import os
import random
from typing import TypedDict
from langgraph.graph import StateGraph, END

class RetryState(TypedDict):
    input: str
    attempts: int
    max_attempts: int
    success: bool
    result: str

def attempt_node(state: RetryState):
    """尝试节点：模拟可能失败的操作"""
    attempts = state["attempts"] + 1
    print(f"第{attempts}次尝试...")
    
    # 模拟：50%概率成功
    success = random.choice([True, False])

    if success:
        return {
            "attempts": attempts,
            "success": True,
            "result": "操作成功完成！"
        }
    else:
        return {
            "attempts": attempts,
            "success": False,
            "result": "操作失败，需要重试"
        }

def should_retry(state: RetryState) -> str:
    """判断下一步：成功、重试、还是放弃"""
    if state["success"]:
        return "succeed"
    elif state["attempts"] < state["max_attempts"]:
        return "retry"
    return "failed"

def succeed_node(state: RetryState):
    """成功处理节点"""
    return {"result": f"操作成功完成！（尝试{state['attempts']}次）"}

def failed_node(state: RetryState):
    """失败处理节点"""
    return {"result": f"达到最大重试次数（{state['attempts']}次），操作失败"}

# 构建 Graph
graph = StateGraph(RetryState)
graph.add_node("attempt", attempt_node)
graph.add_node("succeed", succeed_node)
graph.add_node("failed", failed_node)

graph.set_entry_point("attempt")

# 关键：条件边实现循环
graph.add_conditional_edges(
    "attempt",
    should_retry,
    {
        "retry": "attempt",     # 循环：回到 attempt
        "succeed": "succeed",   # 成功
        "failed": "failed"      # 放弃
    }
)

graph.add_edge("succeed", END)
graph.add_edge("failed", END)

app = graph.compile()

# 运行多次观察不同结果
for i in range(3):
    print(f"--- 第{i+1}次运行 ---")
    result = app.invoke({
        "input": "执行操作",
        "attempts": 0,
        "max_attempts": 5,
        "success": False,
        "result": ""
    })
    print(result["result"])
    print()
```

### 📊 运行结果

```
--- 第1次运行 ---
第1次尝试...
第2次尝试...
操作成功完成！（尝试2次）

--- 第2次运行 ---
第1次尝试...
第2次尝试...
第3次尝试...
操作成功完成！（尝试3次）

--- 第3次运行 ---
第1次尝试...
第2次尝试...
第3次尝试...
第4次尝试...
第5次尝试...
达到最大重试次数（5次），操作失败
```

---

## 🔄 实际应用场景：LLM 输出验证

```python
# 场景：让LLM生成JSON，验证格式是否正确，不正确就重试

def generate_node(state):
    """让LLM生成JSON格式输出"""
    llm = ChatOpenAI(
        base_url=os.getenv("OPENAI_API_BASE"),
        api_key=os.getenv("OPENAI_API_KEY")
    )
    prompt = f"请以JSON格式输出：{state['input']}\n只输出JSON，不要其他内容。"
    response = llm.invoke(prompt)
    return {
        "result": response.content,
        "attempts": state["attempts"] + 1
    }

def validate_node(state):
    """验证输出是否为合法JSON"""
    import json
    try:
        json.loads(state["result"])
        return {"success": True}
    except json.JSONDecodeError:
        return {"success": False}
```

### 🎯 工作流程

```
生成JSON → 验证格式 → 成功? → 结束
              ↓ 失败
          次数超限? → 是 → 失败
              ↓ 否
          重新生成 (循环)
```

---

## ⚠️ 重要注意事项

### 🔴 必须设置终止条件

```python
def should_retry(state: RetryState) -> str:
    # ✅ 正确：有明确的退出条件
    if state["success"]:
        return "succeed"
    elif state["attempts"] < state["max_attempts"]:  # 最大重试次数
        return "retry"
    return "failed"  # 超过次数，强制退出
```

### ❌ 避免无限循环

- 不设终止条件 → 可能造成无限循环
- 消耗大量 Token 和 API 调用次数 💸
- 建议始终设置 `max_attempts` 限制

---

## 🎯 核心要点

- ✅ **循环 = 条件边指向之前节点**：实现重试和优化
- ✅ **路由函数控制循环**：判断是否继续或退出
- ✅ **必须设置终止条件**：防止无限循环
- ✅ **典型应用**：LLM 输出验证、自我修正、迭代优化
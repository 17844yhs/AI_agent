# 🎯 学习目标

- 理解 LangGraph 的三大核心概念：**State**、**Node**、**Edge**
- 掌握 LangGraph 与 LCEL 的适用场景区别
- 了解 LangGraph 的构建和运行流程

---

## 💡 核心概念

**LangGraph**：用于构建**有状态、多步骤应用**的框架，特别适合 Agent 开发。

### 🔑 三个核心概念

| 概念 | 说明 | 特点 |
|------|------|------|
| **State（状态）** | Graph 中共享的数据容器 | • 使用 `TypedDict` 定义<br>• 节点可以读取 State<br>• 节点可以更新 State |
| **Node（节点）** | 处理逻辑单元 | • 接收当前 State<br>• 执行处理逻辑<br>• 返回更新的 State |
| **Edge（边）** | 连接节点的路径 | • **普通边**：A → B（无条件）<br>• **条件边**：A → [判断] → B/C（根据条件选择） |

---

## 🏭 形象比喻：流水线 vs 智能车间

### 🔹 LCEL：直流水线
```text
原料 → 工位1 → 工位2 → 工位3 → 成品
```
- ✅ 单向流动，没有回头路
- ✅ 适合简单固定的流程

### 🔸 LangGraph：智能车间
```text
     ↗ 返工 ↖
原料 → 工位1 → 质检 → 成品
     ↓         ↓
   工位2 ← 特殊通道
```
- ✅ 产品可在不同工位间来回传递
- ✅ 质检不合格就退回重做
- ✅ 遇到特殊订单就走专用通道

---

## 📊 LangGraph vs LCEL 对比

| 特性 | LCEL | LangGraph |
|------|------|-----------|
| **适用场景** | 简单线性流程 | 复杂循环/分支流程 |
| **状态管理** | ❌ 无 | ✅ 有（TypedDict） |
| **循环控制** | ❌ 不支持 | ✅ 支持 |
| **条件分支** | ⚠️ RunnableBranch | ✅ 更强大的条件边 |
| **人工介入** | ❌ 不支持 | ✅ interrupt 机制 |
| **持久化** | ⚠️ 需要手动实现 | ✅ Checkpointer |
| **可视化** | ❌ 无 | ✅ get_graph() |

---

## 🛠️ 构建流程（5步法）

```python
# 第1步：定义 State
class MyState(TypedDict):
    messages: list
    current_step: str

# 第2步：定义 Node
def my_node(state: MyState) -> MyState:
    # 处理逻辑
    return updated_state

# 第3步：构建 Graph
graph = StateGraph(MyState)

# 第4步：添加边
graph.add_edge("node_a", "node_b")  # 普通边
graph.add_conditional_edges(        # 条件边
    "decision_node",
    {"option1": "node_b", "option2": "node_c"}
)

# 第5步：编译运行
app = graph.compile()
result = app.invoke(initial_state)
```

---

## 🎯 总结

**LCEL** → 快速搭建简单链式任务  
**LangGraph** → 构建复杂、有状态、可循环的智能体工作流
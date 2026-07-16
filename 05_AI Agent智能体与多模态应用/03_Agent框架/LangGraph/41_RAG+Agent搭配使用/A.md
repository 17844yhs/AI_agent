# RAG + Agent 搭配使用

## 学习目标

- 理解 RAG + Agent 的组合方式
- 了解 RAG Agent 与传统 RAG Pipeline 的区别

---

## 一、问题场景对比

### 传统 RAG Pipeline（固定流程）

```
用户提问 → 检索文档 → 生成回答
```

**问题分析**：

- ❌ 不管用户问什么，都会去检索，浪费 Token
- ❌ 检索结果可能不相关，但无法自我修正

### RAG Agent（自主决策）

```
用户提问 → Agent 判断 → 决定是否检索
```

**智能决策示例**：

- ✅ 用户："你好" → Agent 判断：不需要检索 → 直接回答
- ✅ 用户："公司的请假制度是什么？" → Agent 判断：需要检索 → 调用检索工具 → 回答
- ✅ 用户："上次检索的内容不对" → Agent 判断：重新检索 → 换个关键词搜索 → 回答

### 核心问题

**传统 RAG** 是固定流水线，无法根据问题动态调整检索策略。

**Agent 化的 RAG** 让 LLM 自主决定：

- 是否需要检索
- 用什么关键词检索
- 检索结果是否满意

### 类比：图书馆

```
传统RAG = 每次都去书架上翻一遍，不管问题需不需要查书

RAG Agent = 先思考"这个问题需要查书吗？"，需要才去查，查到不满意的还知道换本书再查
```

---

## 二、代码示例：公司知识库助手

### 导入依赖

```python
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.agents import create_agent
from langchain_core.messages import HumanMessage

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)
```

### 模拟文档库

```python
documents = [
    {"id": 1, "title": "请假制度", "content": "员工每年享有15天年假。请提前3天在OA系统提交申请，直属领导审批后生效。病假需提供医院证明。"},
    {"id": 2, "title": "报销流程", "content": "差旅报销：出差结束后7日内提交，附发票和行程单。餐饮报销：每月汇总一次，限额500元/月。"},
    {"id": 3, "title": "考勤规定", "content": "上班时间9:00-18:00，弹性30分钟。迟到3次以内口头警告，超过3次扣绩效。"},
    {"id": 4, "title": "技术栈规范", "content": "后端使用Python/FastAPI，前端使用React/TypeScript。代码必须通过Code Review才能合并。"},
    {"id": 5, "title": "新人入职", "content": "入职第一天由HR引导办理工牌、开通账号。第二天由导师安排技术培训。试用期为3个月。"},
]
```

### 定义检索工具

```python
@tool
def search_documents(query: str) -> str:
    """搜索公司内部文档，输入搜索关键词。当用户问到公司制度、流程、规定时使用此工具。"""
    results = []
    query_lower = query.lower()
    for doc in documents:
        if (query_lower in doc["title"].lower() or
            query_lower in doc["content"].lower() or
            any(c in doc["title"] or c in doc["content"] for c in query if '\u4e00' <= c <= '\u9fff')):
            results.append(f"【{doc['title']}】{doc['content']}")

    if not results:
        return f"未找到与'{query}'相关的文档。建议尝试其他关键词。"
    return "\n---\n".join(results)

@tool
def list_all_documents() -> str:
    """列出所有可用的文档标题列表。"""
    return "可用文档：" + "、".join([f"《{doc['title']}》" for doc in documents])
```

### 创建 RAG Agent

```python
SYSTEM_PROMPT = """你是一个公司内部知识库助手。你的职责是回答员工关于公司制度、流程、规定的问题。

工作方式：
1. 先判断用户的问题是否需要查询文档
2. 如果需要，调用 search_documents 搜索相关文档
3. 根据搜索结果回答用户问题
4. 如果搜索结果不够，尝试换关键词重新搜索

不需要查询文档的情况：
- 简单问候（你好、谢谢等）
- 通用知识问题
- 你已经能确定答案的问题
"""

app = create_agent(
    llm,
    [search_documents, list_all_documents],
    prompt=SYSTEM_PROMPT
)
```

### 测试

```python
questions = [
    "你好，你是做什么的？",
    "公司年假有多少天？怎么请假？",
    "出差报销流程是什么？",
    "公司用什么技术栈？",
    "帮我看看公司有哪些文档",
    "我想迟到10分钟，有问题吗？"
]

for question in questions:
    result = app.invoke({"messages": [HumanMessage(question)]})
    print(f"用户：{question}")
    print(f"AI：{result['messages'][-1].content}")
    print()
```

#### 运行结果

```
用户：你好，你是做什么的？
AI：你好！我是公司内部知识库助手，可以帮你查询公司制度、流程和规定。有什么可以帮你的？

用户：公司年假有多少天？怎么请假？
AI：根据公司制度，员工每年享有15天年假。请提前3天在OA系统提交申请，直属领导审批后生效。

用户：出差报销流程是什么？
AI：出差报销流程：出差结束后7日内提交，附发票和行程单。餐饮报销每月汇总一次，限额500元/月。

用户：公司用什么技术栈？
AI：公司技术栈：后端使用Python/FastAPI，前端使用React/TypeScript。代码必须通过Code Review才能合并。

用户：帮我看看公司有哪些文档
AI：可用文档：《请假制度》、《报销流程》、《考勤规定》、《技术栈规范》、《新人入职》

用户：我想迟到10分钟，有问题吗？
AI：公司有30分钟弹性时间，迟到10分钟在弹性范围内，不会有问题。但建议尽量准时。
```

---

## 三、RAG Agent vs 传统 RAG Pipeline

| 对比项               | 传统 RAG Pipeline | RAG Agent              |
| -------------------- | ----------------- | ---------------------- |
| **检索决策**   | 总是检索          | LLM 判断是否需要检索   |
| **关键词**     | 固定/用户输入     | LLM 自动生成检索关键词 |
| **结果不满意** | 直接用            | 可换关键词重新检索     |
| **简单问题**   | 也走检索流程      | 直接回答，省 Token     |
| **灵活性**     | 低                | 高                     |
| **实现复杂度** | 简单              | 中等                   |

### 流程图对比

#### 传统 RAG Pipeline（固定流程）

```
用户问题 → 检索 → 拼接 prompt → LLM 生成回答
```

#### RAG Agent（自主决策）

```
用户问题 → Agent 思考
        ├── 不需要检索 → 直接回答
        ├── 需要检索 → search("关键词1")
        │   ├── 结果满意 → 回答
        │   └── 结果不满意 → search("关键词2") → 回答
        └── 不确定 → list_all_documents() → 决定下一步
```

---

## 四、关键要点总结

| 要点                  | 说明                                 |
| --------------------- | ------------------------------------ |
| **核心优势**    | Agent 自主决定是否检索、如何检索     |
| **Token 节省**  | 简单问题直接回答，无需检索           |
| **自我修正**    | 检索结果不满意可重新检索             |
| **工具设计**    | 定义检索工具和列表工具，支持灵活查询 |
| **Prompt 引导** | 通过系统提示词指导 Agent 的决策逻辑  |

# 🎯 学习目标

理解 LangChain 早期的设计思想。这些内容虽已逐步被现代 LCEL（LangChain Expression Language）范式取代，但它们揭示了**"为何要引入链"**以及**"链解决了什么问题"**，是掌握现代实践的重要认知基础。

> ⚠️ **注意**：本部分内容主要用于理解演进逻辑。在新项目中，优先使用 LCEL 构建工作流。

---

## 🔗 基础链：LLMChain

在 LangChain 最初的版本中，最核心的问题是：**如何将用户输入、提示模板和语言模型有序结合起来**。

直接调用模型时，开发者需要：
- ❌ 手动拼接字符串
- ❌ 处理变量替换
- ❌ 管理输出格式

这既繁琐又容易出错。

### 💡 解决方案

**LLMChain** 的出现，正是为了解决这一痛点。它的设计非常简洁：

| 组成部分 | 说明 |
|---------|------|
| **输入** | 一组变量（如 `{"question": "什么是量子计算？"}`） |
| **中间** | 一个 PromptTemplate（定义如何组织输入） |
| **输出** | 调用 LLM 并返回原始文本 |

本质上，LLMChain 就是一个 **"提示 + 模型"的封装体**，它把两个最常用的组件绑定在一起，形成一个可复用的单元。

> 🧠 **设计思想**：将"上下文构建"与"模型调用"视为一个原子操作。

---

### 💻 代码示例

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.chains import LLMChain

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "你是一位精通各领域知识的知名教授"),
        ("human", "请你尽可能详细的解释一下：{knowledge}"),
    ]
)

# 1. 创建 LLMChain
llm_chain = LLMChain(
    llm=chat_model,
    prompt=prompt
)

# 2. 调用 LLMChain，返回结果
result = llm_chain.run({"knowledge": "Agent"})
print(result)
```

---

### ⚠️ 问题分析

如果输出不理想，**难以定位问题根源**：

- ❓ 是提示模板问题？
- ❓ 是模型调用问题？
- ❓ 是输入处理问题？

**痛点**：调试困难，缺乏清晰的错误追踪机制。

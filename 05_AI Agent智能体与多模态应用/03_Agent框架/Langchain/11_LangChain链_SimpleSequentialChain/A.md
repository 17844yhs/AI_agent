# 📖 介绍

**SimpleSequentialChain** 是 LangChain 中最简单的链式结构，它顺序执行一系列子链：

- 每个子链的输出是下一个子链的输入
- 整个链只有一个输入和一个输出

---

## ✨ 特点

| 特性 | 说明 |
|------|------|
| **线性流程** | 子链按顺序执行，一步接一步 |
| **单一输入/输出** | 整个链接收一个输入，产生一个输出。中间过程对外透明（只能看到最终结果） |
| **自动传递** | 前一个链的输出会自动作为后一个链的输入，开发者无需手动处理数据传递 |

---

## 🎯 适用场景

非常适用于那些步骤之间有**明确、简单依赖关系**的线性任务：

```
📝 文本生成 → 📋 文本摘要
📊 原始数据 → 🧹 数据清洗 → 📐 数据格式化
✍️ 创意写作 → ✨ 内容润色
```

---

## 💻 代码示例

> ⚠️ **注意**：因版本更新，以下代码只能作为伪代码来理解链的使用方式。

```python
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain, SimpleSequentialChain
from langchain.prompts import ChatPromptTemplate

# 初始化模型
llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

# ---------------------------------------------------------
# 第一步：写文章
# ---------------------------------------------------------
# 这里的输入变量必须叫 {input}，SimpleSequentialChain 固定规则
prompt_template1 = ChatPromptTemplate.from_template(
    "你是一个科技博主。请根据主题：'{input}'，写一篇约 200 字的简短科普文章。"
)

chain_one = LLMChain(llm=llm, prompt=prompt_template1)

# ---------------------------------------------------------
# 第二步：写摘要
# ---------------------------------------------------------
# 这里的 {input} 会自动接收上一步 chain_one 输出的文章内容
prompt_template2 = ChatPromptTemplate.from_template(
    "请将下面的文章总结为一句话的核心观点：\n\n{input}"
)

chain_two = LLMChain(llm=llm, prompt=prompt_template2)

# ---------------------------------------------------------
# 组合并执行
# ---------------------------------------------------------
overall_chain = SimpleSequentialChain(
    chains=[chain_one, chain_two],
    verbose=True
)

# 执行：只需要传入一个字符串
topic = "量子计算的基本原理"
final_summary = overall_chain.run(topic)

print("\n=== 最终摘要结果 ===")
print(final_summary)
```

---

## ⚠️ 问题分析

### 痛点：缺乏灵活性

突发需求场景：
- 🔸 有时只需要 `chain1`
- 🔸 有时需要 `chain1 → chain2`
- 🔸 有时需要 `chain2 → chain1`

**问题**：无法动态调整！必须创建多个不同的 Chain 实例，导致代码冗余和维护困难。

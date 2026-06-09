# 📖 介绍

**SequentialChain** 是 [SimpleSequentialChain](file://d:\Agent_study\AI-agent_produce\05_AI%20Agent智能体与多模态应用\03_Agent框架\11_LangChain链_SimpleSequentialChain\A) 的更强大、更灵活的版本。它同样顺序执行一系列子链，但支持：

- ✅ 多个输入变量
- ✅ 多个输出变量
- ✅ 精细控制数据流向

---

## ✨ 特点

| 特性 | 说明 |
|------|------|
| **多输入/输出** | 可以定义整个链的多个输入和多个输出，也可以指定每个子链的输入和输出键名 |
| **灵活的数据路由** | 精确指定每个子链的输入来源（上一个链的输出或初始输入） |
| **保留中间结果** | 可选择性地输出中间链的结果，而不仅仅是最终结果 |

---

## 🎯 适用场景

适用于**更复杂、多步骤**的任务，特别是需要合并多个信息源或生成多种输出的场景：

### 📝 剧本创作
```
输入：标题 + 体裁 → 生成剧本 → 根据剧本生成剧评
输出：剧本 + 剧评
```

### 📊 市场分析
```
输入：产品描述 → 生成营销文案 → 翻译成多语言 → 分析不同版本的语气
输出：文案 + 各语言版本
```

---

## 💻 代码示例

> ⚠️ **注意**：因版本更新，以下代码只能作为伪代码来理解链的使用方式。

```python
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import ChatPromptTemplate

# 初始化模型 (确保你已配置好 OPENAI_API_KEY)
llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

# ---------------------------------------------------------
# 第一步：剧本创作链
# ---------------------------------------------------------
# 定义提示词模板，输入变量为 "title" 和 "genre"
prompt_template1 = ChatPromptTemplate.from_template(
    "你是一个剧作家。请根据标题 '{title}' 和题材 '{genre}' 写一个简短的剧本。"
)

# 创建第一个 Chain
chain_one = LLMChain(
    llm=llm,
    prompt=prompt_template1,
    output_key="script"  # 关键：将输出的剧本保存到 "script" 变量中
)

# ---------------------------------------------------------
# 第二步：剧评撰写链
# ---------------------------------------------------------
# 定义提示词模板，输入变量为第一步的输出 "script"
prompt_template2 = ChatPromptTemplate.from_template(
    "你是一个著名的剧评人。请对下面的剧本写一段简短的点评：\n\n{script}"
)

# 创建第二个 Chain
chain_two = LLMChain(
    llm=llm,
    prompt=prompt_template2,
    output_key="review"  # 最终点评结果保存到 "review"
)

# ---------------------------------------------------------
# 组合成顺序链
# ---------------------------------------------------------
# 这里定义执行顺序和最终输出的变量
overall_chain = SequentialChain(
    chains=[chain_one, chain_two],
    input_variables=["title", "genre"],      # 初始输入
    output_variables=["script", "review"],   # 我们想看到的最终输出
    verbose=True                              # 打印中间过程
)

# ---------------------------------------------------------
# 执行链
# ---------------------------------------------------------
result = overall_chain({
    "title": "午夜咖啡馆",
    "genre": "悬疑"
})

print("\n=== 最终剧本 ===")
print(result['script'])

print("\n=== 最终剧评 ===")
print(result['review'])
```

---

## 🔗 其它链的问题

### ❌ 混乱的接口示例

```python
from langchain.chains import LLMChain, LLMMathChain, ConversationChain

# 三种不同的调用方式！
chain1 = LLMChain(...)
result1 = chain1.run({"product": "手机"})           # 方式1：.run() 接受字典

chain2 = LLMMathChain(...)
result2 = chain2.run("2 + 2等于多少？")             # 方式2：.run() 接受字符串

chain3 = ConversationChain(...)
result3 = chain3.predict(input="你好！")            # 方式3：.predict() 方法

# 还有更多变体：
# chain.apply()  - 用于批量处理
# chain()        - 直接调用实例
# chain.arun()   - 异步版本
```

### 😫 开发者痛点

**必须记住每种 Chain 的特殊调用方式**，导致：
- 🔸 学习成本高
- 🔸 容易混淆
- 🔸 代码不一致

这正是 **LCEL（LangChain Expression Language）** 要解决的核心问题！

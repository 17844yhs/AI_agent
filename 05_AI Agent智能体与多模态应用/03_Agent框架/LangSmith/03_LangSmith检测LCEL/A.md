# LangSmith 检测 LCEL

## 学习目标

- 使用 LangSmith 调试简单的 LCEL 链式调用
- 学会定位 Pydantic 解析错误
- 掌握在 LangSmith 中排查问题的步骤

---

## 示例1：调试简单链

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

prompt = ChatPromptTemplate.from_template(
    "你是一个{role}，请回答：{question}"
)
chain = prompt | llm | StrOutputParser()

# LangSmith 自动记录这次调用的完整链路
result = chain.invoke({
    "role": "Python 专家",
    "question": "装饰器是什么？"
})
print(result)
```

**执行效果**：
- LangSmith 自动记录完整调用链：`prompt → llm → parser`
- 可查看每一步的输入输出、耗时、Token 消耗

---

## 示例2：调试 Pydantic 解析错误

```python
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class MovieReview(BaseModel):
    """电影评价"""
    title: str = Field(description="电影名称")
    score: float = Field(description="评分 0-10")
    review: str = Field(description="一句话评价")

parser = PydanticOutputParser(pydantic_object=MovieReview)

prompt = ChatPromptTemplate.from_template(
    "评价这部电影：{movie}\n{format_instructions}",
    partial_variables={"format_instructions": parser.get_format_instructions()}
)

chain = prompt | llm | parser

try:
    # 如果 LLM 输出格式不对，parser 会报错
    # 在 LangSmith 中可以看到 LLM 的原始输出，定位是 LLM 问题还是 parser 问题
    result = chain.invoke({"movie": "盗梦空间"})
    print(result)
except Exception as e:
    print(f"错误：{e}")
    # 打开 LangSmith → 查看 Trace → 找到 ChatOpenAI 步骤
    # 看 LLM 的原始输出是什么 → 判断是 prompt 需要优化还是 parser 需要调整
```

---

## 在 LangSmith 中定位错误的步骤

```
1. Trace 列表中，失败的 Trace 会标记红色 ❌
2. 点击进入，看到具体哪一步 Run 失败
3. 查看失败 Run 的输入输出：
   ├── 如果 LLM 输出的格式就错了 → 优化 prompt，强调输出格式
   └── 如果 LLM 输出正确但 parser 解析失败 → 检查 parser 配置
```

### 错误定位流程图

```
链执行失败 → 打开 LangSmith → 查看失败 Trace
                           │
              ┌────────────┴────────────┐
              ↓                         ↓
      LLM 输出格式错误            Parser 配置问题
              │                         │
              ↓                         ↓
      优化 Prompt                   检查 Parser
    （强调输出格式）              （字段定义/类型）
```

---

## 关键要点总结

| 要点 | 说明 |
|------|------|
| **自动追踪** | LCEL 链式调用自动记录到 LangSmith |
| **失败标记** | 失败的 Trace 会显示红色 ❌ |
| **问题定位** | 查看失败步骤的输入输出，判断问题来源 |
| **常见错误** | LLM 输出格式错误 → 优化 prompt；Parser 配置问题 → 检查字段定义 |
| **调试流程** | Trace 列表 → 失败 Trace → 查看具体步骤 → 定位问题 → 修复 |

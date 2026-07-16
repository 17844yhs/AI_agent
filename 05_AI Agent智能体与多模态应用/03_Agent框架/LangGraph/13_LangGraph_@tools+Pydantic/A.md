# 🎯 学习目标

- 掌握简单工具与复杂工具的定义选择
- 学会使用 `args_schema` + Pydantic 定义带约束的工具参数
- 理解 Pydantic 验证在 LangGraph 工具调用中的工作流程

---

## 🔧 两种工具定义方式

我们用 `@tool` + 类型注解定义工具。对于简单场景这已经够用，但当参数需要约束（范围、枚举、必填/可选）时，就需要 Pydantic 的 `args_schema`。

---

## 📝 生活化比喻：签合同

| 方式                  | 类比                           | 特点                            |
| --------------------- | ------------------------------ | ------------------------------- |
| **简单工具**    | 签字确认，一个签名就行         | `query: str` ✅               |
| **复杂工具**    | 填合同表格，多个字段有格式要求 | 金额范围、日期格式、枚举选项 ✅ |
| **args_schema** | "合同模板"                     | 规定每个字段怎么填 📋           |

---

## 💻 代码对比

### 1️⃣ 方式1：简单工具 - 类型注解即可

```python
import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

@tool
def search(query: str) -> str:
    """搜索互联网信息，输入搜索关键词。"""
    return f"关于'{query}'的搜索结果：找到5条相关内容"
```

### 2️⃣ 方式2：复杂工具 - 使用 args_schema + Pydantic

```python
from typing import Optional
from pydantic import BaseModel, Field

class ProductSearchInput(BaseModel):
    """商品搜索参数"""
    keyword: str = Field(description="搜索关键词")
    min_price: float = Field(default=0, ge=0, description="最低价格")
    max_price: float = Field(default=99999, ge=0, description="最高价格")
    category: Optional[str] = Field(
        default=None,
        description="商品分类",
        # 注意：enum 约束通过描述让 LLM 理解
    )
    limit: int = Field(default=10, ge=1, le=50, description="返回数量")

@tool(args_schema=ProductSearchInput)
def search_products(
    keyword: str,
    min_price: float = 0,
    max_price: float = 99999,
    category: str = None,
    limit: int = 10
) -> str:
    """搜索商品，支持按价格范围和分类筛选。"""
    # 模拟商品搜索
    return f"搜索'{keyword}'，价格{min_price}-{max_price}元，分类：{category}，返回{limit}条结果"
```

### 3️⃣ 测试：LLM 自动提取参数

```python
# 绑定工具到 LLM
tools = [search, search_products]
llm_with_tools = llm.bind_tools(tools)

# 简单场景：只需类型注解
response1 = llm_with_tools.invoke("搜索AI新闻")
print("简单工具：")
if response1.tool_calls:
    print(f"  调用：{response1.tool_calls[0]}")

# 复杂场景：Pydantic 约束生效
response2 = llm_with_tools.invoke("帮我找200到500元之间的电子产品，只要前5个")
print("\n复杂工具：")
if response2.tool_calls:
    print(f"  调用：{response2.tool_calls[0]}")
```

#### 📊 运行结果

```
简单工具：
 调用：{'name': 'search', 'args': {'query': 'AI新闻'}, 'id': 'call_5b77...', 'type': 'tool_call'}

复杂工具：
 调用：{'name': 'search_products', 'args': {'category': '电子产品', 'keyword': '电子产品', 'limit': 5, 'max_price': 500, 'min_price': 200}, 'id': 'call_cff9...', 'type': 'tool_call'}
```

---

## 🔄 工作流程

```
用户输入："帮我找200到500元之间的电子产品，只要前5个"
  ↓
LLM 看到工具描述 + args_schema（Pydantic 生成的 JSON Schema）
  ↓
LLM 自动提取参数：
  keyword="电子产品"
  min_price=200
  max_price=500
  limit=5
  ↓
LangGraph 执行工具时，Pydantic 自动验证参数：
  ✓ min_price=200 >= 0
  ✓ limit=5, 1 <= 5 <= 50
  ↓
验证通过 → 执行工具
```

---

## 📋 选择指南

| 场景                                | 方式                       | 示例                               |
| ----------------------------------- | -------------------------- | ---------------------------------- |
| **参数简单**（1-2个基础类型） | `@tool` + 类型注解       | `search(query: str)`             |
| **参数有约束**（范围、枚举）  | `@tool(args_schema=...)` | `min_price: float = Field(ge=0)` |
| **参数嵌套复杂**              | `@tool(args_schema=...)` | 嵌套`BaseModel`                  |

---

## 💡 经验法则

> **先从简单的 `@tool` 开始**，当发现 LLM 传错参数或参数需要约束时，再加 `args_schema`。

---

## 🎯 核心要点

- ✅ **简单工具**：`@tool` + 类型注解，适合快速开发
- ✅ **复杂工具**：`@tool(args_schema=...)` + Pydantic，提供参数验证
- ✅ **Pydantic 优势**：
  - 范围约束（`ge`, `le`）
  - 默认值设置
  - 可选参数（`Optional`）
  - 自动生成 JSON Schema
- ✅ **工作流程**：LLM 提取参数 → Pydantic 验证 → 执行工具

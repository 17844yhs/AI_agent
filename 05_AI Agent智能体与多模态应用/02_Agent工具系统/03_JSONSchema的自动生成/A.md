# 🤖 JSON Schema 自动生成

## 🎯 课程目标

- ✅ 掌握使用Pydantic等现代工具自动生成JSON Schema的方法
- ✅ 理解类型驱动的开发方式

---

## 1️⃣ 为什么需要自动生成?

### ⚠️ 传统方式的局限性

| 问题 | 说明 | 影响 |
|------|------|------|
| **手动编写易错** | 手写JSON Schema容易遗漏或写错 | 运行时错误 |
| **维护困难** | 代码和Schema分离,需要同步修改 | 不一致风险 |
| **类型不一致** | Python类型与Schema可能不匹配 | 验证失效 |
| **效率低下** | 每次修改都要手动更新Schema | 开发缓慢 |

### ✨ 现代化方案的优势

```
┌─────────────────┐
│  Python类型注解  │
└────────┬────────┘
         ↓ 自动转换
┌─────────────────┐
│  Pydantic模型   │
└────────┬────────┘
         ↓ 自动生成
┌─────────────────┐
│  JSON Schema    │
└─────────────────┘
```

| 优势 | 说明 |
|------|------|
| **类型安全** | 从Python类型注解自动生成 |
| **代码即文档** | 类型定义同时提供验证和文档 |
| **维护简单** | 修改类型自动更新Schema |
| **错误减少** | 编译时类型检查 |

---

## 2️⃣ Pydantic基础回顾

### 📚 官方文档

🔗 [Pydantic v2 Documentation](https://docs.pydantic.dev/2.12/)

### ⭐ Pydantic的核心特性

| 特性 | 说明 |
|------|------|
| **数据验证** | 基于类型注解的自动验证 |
| **类型转换** | 自动进行合理的类型转换 |
| **验证器支持** | 丰富的自定义验证器 |
| **Schema生成** | 自动生成JSON Schema |

---

## 3️⃣ 实战示例

### 📝 基础用法

```python
from pydantic import BaseModel, Field

class WeatherQuery(BaseModel):
    """天气查询参数"""
    city: str = Field(description="城市名称")
    unit: str = Field(
        default="celsius",
        description="温度单位",
        enum=["celsius", "fahrenheit"]
    )

# 自动生成JSON Schema
schema = WeatherQuery.model_json_schema()
print(schema)
```

### 🔧 高级用法

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

class SearchParams(BaseModel):
    """搜索参数"""
    keyword: str = Field(
        min_length=1,
        max_length=100,
        description="搜索关键词"
    )
    category: Optional[str] = Field(
        default=None,
        description="分类过滤"
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="返回数量"
    )
    tags: List[str] = Field(
        default_factory=list,
        description="标签列表"
    )

    @field_validator('keyword')
    @classmethod
    def validate_keyword(cls, v):
        """自定义验证器"""
        if not v.strip():
            raise ValueError("关键词不能为空")
        return v.strip()

# 生成Schema
schema = SearchParams.model_json_schema()
```

### 🎯 嵌套对象

```python
from pydantic import BaseModel, Field

class Address(BaseModel):
    """地址信息"""
    street: str = Field(description="街道")
    city: str = Field(description="城市")
    zipcode: str = Field(pattern=r"^\d{6}$", description="邮编")

class UserProfile(BaseModel):
    """用户资料"""
    name: str = Field(description="姓名")
    age: int = Field(ge=0, le=150, description="年龄")
    address: Address = Field(description="地址信息")

# 生成包含嵌套结构的Schema
schema = UserProfile.model_json_schema()
```

---

## 4️⃣ 与Tool Calling结合

### 🔗 LangChain集成

```python
from langchain.tools import tool
from pydantic import BaseModel, Field

class CalculatorInput(BaseModel):
    """计算器输入参数"""
    expression: str = Field(
        description="数学表达式,如 '2 + 3 * 4'"
    )

@tool(args_schema=CalculatorInput)
def calculator(expression: str) -> str:
    """执行数学计算"""
    try:
        result = eval(expression)
        return f"结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"

# LangChain会自动从Pydantic模型生成JSON Schema
```

### 💡 OpenAI API集成

```python
from pydantic import BaseModel, Field
import json

class WeatherParams(BaseModel):
    city: str = Field(description="城市名称")
    unit: str = Field(default="celsius", description="温度单位")

# 生成OpenAI兼容的Schema
schema = WeatherParams.model_json_schema()

tools = [{
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取天气信息",
        "parameters": schema
    }
}]
```

---

## 5️⃣ 最佳实践和注意事项

### ✅ 类型设计原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **具体类型** | 使用具体的类型而不是Any | `str` 而非 `Any` |
| **添加描述** | 为所有字段添加description | `Field(description="...")` |
| **合理约束** | 设置min/max、pattern等 | `Field(ge=0, le=100)` |
| **单一职责** | 保持模型的单一职责 | 一个模型只做一件事 |

### 📊 完整示例对比

#### ❌ 手动编写(易错)

```json
{
  "type": "object",
  "properties": {
    "city": {"type": "string"},
    "limit": {"type": "integer"}
  },
  "required": ["city"]
}
```

#### ✅ Pydantic自动生成(推荐)

```python
class QueryParams(BaseModel):
    city: str = Field(description="城市名称")
    limit: int = Field(default=10, ge=1, le=100, description="限制数量")

# 一行代码生成,保证一致性
schema = QueryParams.model_json_schema()
```

### 🔍 常见陷阱

```python
# ❌ 错误: 使用Any类型
from typing import Any
data: Any  # 无法生成有效的Schema

# ✅ 正确: 使用具体类型
data: dict[str, str]  # 清晰的类型定义

# ❌ 错误: 缺少description
name: str

# ✅ 正确: 添加描述
name: str = Field(description="用户姓名")
```

---

## 📝 总结

> 💡 **核心洞察**: 类型驱动开发让代码、验证、文档三位一体,大幅提升开发效率和可靠性

### 🎯 关键要点

- **自动化**: Pydantic从类型注解自动生成Schema
- **一致性**: 代码与Schema始终保持同步
- **类型安全**: 编译时检查 + 运行时验证
- **易用性**: 简洁的API,强大的功能

### 🚀 工作流

```
定义Pydantic模型 
    ↓
自动验证数据 
    ↓
自动生成Schema 
    ↓
用于Tool Calling
```

# 📋 参数验证策略 - Schema参数验证

## 🎯 课程目标

- ✅ 理解参数验证的重要性
- ✅ 如何选择合适的验证策略

---

## 1️⃣ AI平台的验证机制

### 🔍 理解AI平台的角色

| 特性 | 说明 |
|------|------|
| **内置验证** | OpenAI/Claude等平台内置JSON Schema验证 |
| **自动重试** | 参数格式错误时,AI会收到反馈并重新生成 |
| **简化开发** | 大多数简单场景下不需要额外验证 |

### 💡 AI平台工作流程

```python
# 工作流程:
# 1. 用户请求 → AI生成参数 → 平台验证Schema → 调用工具
# 2. 如果验证失败 → AI收到错误 → 重新生成参数
```

### 👨‍💻 开发者视角

```python
def get_weather(city: str, unit: str = "celsius"):
    """
    大多数情况下可以直接使用参数
    AI平台已经完成了基本的格式验证
    """
    return call_weather_api(city, unit)
```

---

## 2️⃣ 选择验证策略

### 📊 何时需要验证?

#### ✅ 需要验证的场景

| 场景 | 原因 |
|------|------|
| **关键业务系统** | 金融、医疗、交易系统需要严格验证 |
| **外部API调用** | 参数需要符合第三方API规范 |
| **复杂业务逻辑** | 涉及多重依赖的参数关系 |
| **用户输入处理** | 直接来自用户的未经验证数据 |

#### ❌ 不需要验证的场景

| 场景 | 原因 |
|------|------|
| **简单工具调用** | 参数格式简单,相信AI生成 |
| **内部服务** | 参数来自可信的内部系统 |
| **原型开发** | 快速验证功能为主 |

### 🛠️ 验证策略选择

#### 策略1: 信任AI(最常见)

```python
def simple_tool(params):
    """直接使用参数,不做额外验证"""
    return my_function(**params)
```

#### 策略2: 基本类型检查

```python
def basic_validation(params):
    """进行基本的类型检查"""
    if not isinstance(params.get('city'), str):
        raise ValueError("city必须是字符串")
    return my_function(**params)
```

#### 策略3: 使用Pydantic(⭐推荐)

```python
from pydantic import BaseModel, Field

class ToolParams(BaseModel):
    city: str
    limit: int = Field(ge=1, le=100)

def pydantic_validation(params_dict):
    """利用Pydantic自动验证"""
    params = ToolParams(**params_dict)
    return my_function(params.city, params.limit)
```

#### 策略4: 完整验证(关键系统)

```python
def full_validation(params_dict):
    """多层次验证 + 业务规则 + 安全检查"""
    validated = comprehensive_validator(params_dict)
    return my_function(**validated)
```

---

## 3️⃣ 现代工具与框架

### 🔧 Pydantic集成

```python
from pydantic import BaseModel, Field, ValidationError
from typing import Optional

class DatabaseQuery(BaseModel):
    table: str = Field(description="表名")
    limit: int = Field(default=10, ge=1, le=1000)
    filters: Optional[dict] = None

    def execute(self):
        """参数已自动验证,直接执行查询"""
        return db.query(self.table, self.limit, self.filters)

# 使用示例
try:
    query = DatabaseQuery(table="users", limit=50)
    result = query.execute()
except ValidationError as e:
    print(f"参数错误: {e}")
```

### 🦜 LangChain工具装饰器

```python
from langchain.tools import tool
from langchain_core.tools import ToolException

@tool
def search_database(query: str, limit: int = 10) -> str:
    """
    搜索数据库
    
    Args:
        query: 搜索关键词
        limit: 返回数量 (1-100)
    """
    # LangChain会自动验证参数类型和范围
    if len(query) < 2:
        raise ToolException("搜索关键词太短")
    
    return db.search(query, limit)
```

---

## 4️⃣ 实际项目案例

### 🛒 案例1: 电商搜索工具

**场景**: 简单场景,相信AI参数

```python
@tool
def search_products(query: str, category: str = None) -> str:
    """搜索产品"""
    # AI通常会生成合理参数,直接使用
    return product_db.search(query, category)
```

---

### 💰 案例2: 金融交易工具

**场景**: 关键场景,全方位验证

```python
from pydantic import BaseModel, Field, model_validator
from decimal import Decimal

class TransferParams(BaseModel):
    from_account: str = Field(pattern=r'^\d{10}$')
    to_account: str = Field(pattern=r'^\d{10}$')
    amount: Decimal = Field(ge=0.01, le=1000000)
    description: str = Field(max_length=100)

    @model_validator(mode='after')  # 在字段验证之后执行
    def validate_accounts(self):
        """验证转出和转入账户不能相同"""
        if self.from_account == self.to_account:
            raise ValueError("转出和转入账户不能相同")
        return self

@tool
def transfer_money(params: TransferParams) -> str:
    """转账功能"""
    # 所有验证已完成,直接执行业务逻辑
    return banking_system.transfer(
        params.from_account,
        params.to_account,
        params.amount,
        params.description
    )
```

**等价写法**:

```python
@tool(args_schema=TransferParams)
def transfer_money(
    from_account: str,   # ← 注意:参数是展开的
    to_account: str,
    amount: Decimal,
    description: str
) -> str:
    """转账功能"""
    return banking_system.transfer(
        from_account, 
        to_account, 
        amount, 
        description
    )
```

---

### 🌐 案例3: API代理工具

**场景**: 中等场景,适度验证

```python
def call_external_api(endpoint: str, params: dict) -> dict:
    """调用外部API"""
    
    # 基本验证
    if not endpoint.startswith('/api/'):
        raise ValueError("无效的API端点")
    
    # 转换参数格式(如果需要)
    api_params = convert_params_for_external_api(params)
    
    # 调用外部API
    return requests.post(
        f"https://api.example.com{endpoint}", 
        json=api_params
    )
```

---

## 🏆 最佳实践

| 原则 | 说明 |
|------|------|
| **从简单开始** | 先假设参数正确,逐步添加必要验证 |
| **选择合适工具** | Pydantic > 手动验证 > 无验证 |
| **分层验证** | 输入验证 → 业务验证 → 安全验证 |
| **性能考虑** | 避免过度验证影响响应速度 |
| **错误友好** | 提供清晰、可操作的错误信息 |

---

## 📝 总结

> 💡 **核心思想**: 根据业务场景选择合适的验证策略,平衡安全性与开发效率

- **简单场景**: 信任AI平台的内置验证
- **中等场景**: 使用Pydantic进行类型和范围验证
- **关键场景**: 多层次验证 + 业务规则 + 安全检查

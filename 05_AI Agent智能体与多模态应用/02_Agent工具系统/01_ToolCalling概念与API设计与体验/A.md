# 🔧 Tool Calling 概念与API设计

## 🎯 课程目标

- ✅ 理解Tool Calling的基本概念
- ✅ 掌握API设计原则
- ✅ 了解应用场景

---

## 1️⃣ Tool Calling 基本概念

### 📖 定义

**Tool Calling**(原名Function Calling)是指大语言模型(LLM)能够理解用户意图并调用外部函数或工具的能力。这种能力让LLM从单纯的文本生成工具转变为可以执行实际任务的智能代理。

### 🔄 概念演变

| 阶段           | 名称             | 特点                            |
| -------------- | ---------------- | ------------------------------- |
| **初期** | Function Calling | OpenAI最初命名,专注于函数调用   |
| **现在** | Tools            | 扩展为更通用的概念,涵盖更多功能 |

### ⭐ 核心特点

```
┌─────────────┐
│  意图识别   │ → LLM能理解用户的工具使用需求
└─────────────┘
       ↓
┌─────────────┐
│  参数提取   │ → 自动从对话中提取函数参数
└─────────────┘
       ↓
┌─────────────┐
│  函数执行   │ → 调用实际的代码函数
└─────────────┘
       ↓
┌─────────────┐
│  结果整合   │ → 将函数结果整合到回复中
└─────────────┘
```

---

## 2️⃣ API设计模式

### 📝 OpenAI Tool Calling API设计

#### 工具定义格式

```json
{
  "type": "function",
  "function": {
    "name": "get_weather",
    "description": "获取指定城市的天气信息",
    "parameters": {
      "type": "object",
      "properties": {
        "city": {
          "type": "string",
          "description": "城市名称"
        },
        "unit": {
          "type": "string",
          "enum": ["celsius", "fahrenheit"],
          "description": "温度单位"
        }
      },
      "required": ["city"]
    }
  }
}
```

### 🔑 核心API组件

| 组件                  | 说明             | 示例值                               |
| --------------------- | ---------------- | ------------------------------------ |
| **tools**       | 工具定义列表     | `[tool1, tool2, ...]`              |
| **tool_choice** | 指定要调用的工具 | `"auto"` / `"none"` / 具体工具名 |
| **messages**    | 对话历史         | `[{role: "user", content: "..."}]` |

> 💡 **提示**: OpenAI只是举例,目的是讲清楚概念和模式。OpenAI是最早系统化提出并推广Function Calling范式的主流大模型厂商。

---

## 3️⃣ 应用场景分析

### 🚀 典型应用场景

| 场景类型           | 具体应用                   | 示例               |
| ------------------ | -------------------------- | ------------------ |
| **信息查询** | 天气、股票、新闻等实时数据 | 查询北京今天的天气 |
| **数据操作** | 数据库查询、文件处理       | 搜索用户记录       |
| **外部服务** | API接口、第三方服务        | 调用支付接口       |
| **计算任务** | 数学计算、数据分析         | 计算统计数据       |

### 💼 实际应用案例

```python
# 案例1: 天气查询
@tool
def get_weather(city: str, unit: str = "celsius"):
    """获取天气信息"""
    return weather_api.query(city, unit)

# 案例2: 数据库查询
@tool
def search_users(keyword: str, limit: int = 10):
    """搜索用户"""
    return db.search("users", keyword, limit)

# 案例3: 数学计算
@tool
def calculate(expression: str):
    """计算数学表达式"""
    return eval(expression)
```

---

## 📝 总结

> 💡 **核心洞察**: Tool Calling让LLM具备了"行动能力",从被动回答问题转向主动执行任务

- **本质**: LLM + 外部工具的桥梁
- **关键**: 清晰的API设计和参数定义
- **价值**: 扩展LLM的实际应用能力

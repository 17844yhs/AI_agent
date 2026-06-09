# 📐 JSON Schema 设计基础

## 🎯 课程目标

- ✅ 掌握JSON Schema的设计原则
- ✅ 学会参数结构化方法

---

## 1️⃣ JSON Schema 基础概念

### 📖 定义

**JSON Schema**是用于定义JSON数据结构的规范,它描述了数据的格式、类型和约束条件。在Tool Calling中,JSON Schema用于定义工具参数的结构。

```
┌──────────────────┐
│   JSON Schema    │
├──────────────────┤
│ • 数据格式定义   │
│ • 类型约束       │
│ • 验证规则       │
└──────────────────┘
         ↓
   工具参数结构
```

---

## 2️⃣ 核心数据类型

### 🔢 基本类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **string** | 字符串 | `"hello"` |
| **number** | 数字(整数或浮点数) | `3.14`, `42` |
| **integer** | 整数 | `42`, `-7` |
| **boolean** | 布尔值 | `true`, `false` |
| **object** | 对象 | `{"key": "value"}` |
| **array** | 数组 | `[1, 2, 3]` |
| **null** | 空值 | `null` |

---

## 3️⃣ 参数定义结构

### 📝 完整的参数Schema结构

```json
{
  "type": "object",
  "properties": {
    "参数名": {
      "type": "数据类型",
      "description": "参数描述",
      "其他约束": "约束值"
    }
  },
  "required": ["必需参数列表"]
}
```

### 💡 实际示例

```json
{
  "type": "object",
  "properties": {
    "city": {
      "type": "string",
      "description": "城市名称"
    },
    "unit": {
      "type": "string",
      "description": "温度单位",
      "enum": ["celsius", "fahrenheit"]
    }
  },
  "required": ["city"]
}
```

---

## 4️⃣ 约束条件详解

### 🔤 字符串约束

```json
{
  "type": "string",
  "minLength": 1,           // 最小长度
  "maxLength": 100,         // 最大长度
  "pattern": "^[a-zA-Z]+$", // 正则表达式
  "enum": ["选项1", "选项2", "选项3"] // 枚举值
}
```

### 🔢 数值约束

```json
{
  "type": "number",
  "minimum": 0,        // 最小值
  "maximum": 100,      // 最大值
  "multipleOf": 0.5    // 必须是0.5的倍数
}
```

### 📊 数组约束

```json
{
  "type": "array",
  "items": {
    "type": "string"
  },
  "minItems": 1,          // 最少元素数
  "maxItems": 10,         // 最多元素数
  "uniqueItems": true     // 元素必须唯一
}
```

---

## 5️⃣ 嵌套对象设计

### 🏗️ 复杂结构示例

```json
{
  "type": "object",
  "properties": {
    "user": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "用户姓名"
        },
        "age": {
          "type": "integer",
          "minimum": 0,
          "description": "用户年龄"
        },
        "email": {
          "type": "string",
          "format": "email",
          "description": "邮箱地址"
        }
      },
      "required": ["name", "email"]
    },
    "preferences": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["sports", "music", "reading"]
      },
      "description": "用户偏好"
    }
  },
  "required": ["user"]
}
```

### 📊 结构层次图

```
root (object)
├── user (object) ⭐ required
│   ├── name (string) ⭐ required
│   ├── age (integer, min: 0)
│   └── email (string, format: email) ⭐ required
└── preferences (array)
    └── items: string (enum: sports/music/reading)
```

---

## 🏆 最佳实践

### ✅ 设计原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **清晰的描述** | 每个字段都要有description | `"description": "城市名称"` |
| **合理的约束** | 设置min/max限制范围 | `"minimum": 0, "maximum": 100` |
| **必需的标记** | 明确标注required字段 | `"required": ["city"]` |
| **类型准确** | 使用最具体的类型 | 用`integer`而非`number` |
| **枚举优先** | 有限选项使用enum | `"enum": ["celsius", "fahrenheit"]` |

### ❌ 常见错误

```json
// ❌ 错误: 缺少description
{
  "city": {
    "type": "string"
  }
}

// ✅ 正确: 包含完整信息
{
  "city": {
    "type": "string",
    "description": "城市名称,如'北京'、'上海'",
    "minLength": 1,
    "maxLength": 50
  }
}
```

---

## 📝 总结

> 💡 **核心洞察**: JSON Schema是Tool Calling的参数契约,清晰的结构定义是成功的关键

- **基础**: 7种基本数据类型
- **关键**: 合理使用约束条件
- **技巧**: 嵌套对象支持复杂数据结构
- **原则**: 描述清晰、约束合理、类型准确

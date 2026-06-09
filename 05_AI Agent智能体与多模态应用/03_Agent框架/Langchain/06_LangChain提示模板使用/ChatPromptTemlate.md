# 💬 ChatPromptTemplate

## 🎯 学习目标
掌握如何使用ChatPromptTemplate

---

## 1️⃣ 介绍

**ChatPromptTemplate** 是用于构建聊天消息序列的提示模板，特别适用于包含多角色（如系统、用户、AI）和多轮交互的对话场景。

相比普通的 PromptTemplate，它能更自然地模拟真实对话结构。

---

## 2️⃣ 核心特点

- ✅ 支持多种角色的消息定义：**system**（系统指令）、**human**（用户输入）、**ai**（模型回复）等
- ✅ 可有效组织和维护对话上下文与历史

---

## 3️⃣ 参数格式

模板通过一个消息列表进行定义，列表中的每一项通常是一个二元组：

```python
(role: str, content: str)
```

| 参数 | 说明 |
|------|------|
| **role** | 指定消息发送者的角色，常用值为 "system"、"human" 或 "ai" |
| **content** | 消息内容，可以是字符串，也可以是结构化数据（如工具调用、多模态输入等） |

```python
messages = [
    ("system", "你是一位专业的翻译助手。"),
    ("human", "翻译成中文：Hello, how are you?"),
    ("ai", "你好，你怎么样？")
]
```

通过这种方式，ChatPromptTemplate 能够灵活构建符合对话逻辑的输入，为大模型提供更清晰的上下文指引。
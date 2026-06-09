# LangSmith 初步体验

## 学习目标

- 完成 LangSmith 注册和配置
- 跑通第一个 Trace
- 学会在面板中查看调用详情

---

## 第一步：注册和获取 API Key

1. **访问官网**：https://smith.langchain.com
2. **注册账号**：支持 GitHub / Google 登录
3. **创建 API Key**：进入 `Settings` → `API Keys` → `Create API Key`
4. **复制 Key**：格式为 `lsv2_pt_xxx...`

---

## 第二步：配置环境变量

### 方式一：使用 .env 文件（推荐）

```env
# .env 文件内容
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your-key-here
LANGCHAIN_PROJECT=my-first-project
```

### 方式二：代码中设置（不推荐，仅用于测试）

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "lsv2_pt_your-key-here"
os.environ["LANGCHAIN_PROJECT"] = "my-first-project"
```

### ⚠️ 安全注意事项

- API Key 是敏感信息，**不要提交到 Git 仓库**
- 确保 `.env` 文件在 `.gitignore` 中
- `LANGCHAIN_TRACING_V2=true` 是开启追踪的开关，设置后所有 LangChain 调用都会自动上报到 LangSmith

---

## 第三步：跑通第一个 Trace

```python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

# LangSmith 会自动追踪，无需额外代码
llm = ChatOpenAI(
    base_url=os.getenv("OPENAI_API_BASE"),
    api_key=os.getenv("OPENAI_API_KEY")
)

prompt = ChatPromptTemplate.from_template("用一句话介绍：{topic}")
chain = prompt | llm | StrOutputParser()

# 执行后，打开 LangSmith 面板查看 Trace
result = chain.invoke({"topic": "人工智能"})
print(result)
```

#### 运行结果

```
人工智能是计算机科学的一个分支，致力于创建能够模拟人类智能的系统，包括学习、推理和自我纠错等能力。
```

---

## 第四步：查看 Trace 面板

1. **打开 LangSmith**：https://smith.langchain.com
2. **选择项目**：点击 `my-first-project`
3. **查看 Trace**：看到刚才的调用记录
4. **展开详情**：查看 `prompt → LLM → parser` 三步的详细信息

### Trace 面板解读

```
Trace: ChatPromptTemplate | ChatOpenAI | StrOutputParser
├── Run 1: ChatPromptTemplate（耗时 <1ms）
│   ├── 输入：{"topic": "人工智能"}
│   └── 输出：[HumanMessage(content="用一句话介绍：人工智能")]
│
├── Run 2: ChatOpenAI（耗时 1.2s）     ← 最耗时的一步
│   ├── 输入：[HumanMessage(...)]
│   ├── 输出：AIMessage(content="人工智能是...")
│   └── Token：输入 12 + 输出 45 = 57   ← Token 消耗
│
└── Run 3: StrOutputParser（耗时 <1ms）
    ├── 输入：AIMessage(content="人工智能是...")
    └── 输出："人工智能是..."

总耗时：1.21s   总 Token：57
```

### 关键信息解读

| 信息类型 | 说明 |
|---------|------|
| **执行步骤** | 链式调用的每一步（prompt → llm → parser） |
| **耗时分析** | 每步的执行时间，可定位性能瓶颈 |
| **Token 消耗** | 输入/输出 Token 数量，帮助成本估算 |
| **输入输出** | 每步的具体输入输出内容 |

---

## 关键要点总结

| 要点 | 说明 |
|------|------|
| **开启方式** | 设置环境变量 `LANGCHAIN_TRACING_V2=true` |
| **自动追踪** | 配置后所有 LangChain 调用自动上报 |
| **查看位置** | https://smith.langchain.com → 选择项目 |
| **安全规范** | API Key 不要提交到 Git，使用 .env 文件 |

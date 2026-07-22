1.学习目标
    了解什么是Langchain 

2.资料
    github地址：https://github.com/langchain-ai/langchain
    官网地址：https://www.langchain.com/langchain
    官网文档：https://docs.langchain.com/oss/python/langchain/overview
    中文文档：https://www.langchain.com.cn/

3.介绍
LangChain 是一个开源框架，简单来说，它帮开发者更方便地构建基于大语言模型（LLM）的智能应用

    提示:它不是 Agent 本身，而是让 Agent 开发更顺手的工具集合

    为什么使用LangChain?
    程序员完全可以直接调用大语言模型（LLM）的 API来构建自己的 Agent 应用， 为什么还要使用LangChain ？
        简化开发难度：更简单、更高效、效果更好， 不用花大量时间和精力 处理底层技术细节

        学习成本更低：不同模型的 API不同，调用方式也有区别，切换模型时学习成本高

        现成的链式组装：LangChain提供了一些现成的 链式组装，让复杂的逻辑变得 结构化、易组合、易扩展

4.Langchain 与Agent关系
LangChain 很像 Agent 的“万能工具箱”，但没那么“万能”。它提供了很多现成的模块，比如：
    链（Chains）：把多个操作串起来，比如先理解用户意图，再查数据，最后生成回答
    工具（Tools）：让 Agent 能用外部功能，比如搜索、计算、翻译
    记忆（Memory）：存对话历史或用户数据
    检索（RAG）：从知识库或网上抓最新信息

局限:
    不是开箱即用：得开发者自己搭配合适的模块和 LLM
    性能依赖 LLM：如果底层的 LLM 不够强，LangChain 再好也有限
    复杂场景还得定制：比如超复杂的任务流，可能还得自己写代码

核心优势
    无需重造轮子，标准化开发流程
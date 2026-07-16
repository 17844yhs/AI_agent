# LangChain 环境搭建

## 1. 学习目标
- 了解如何配置 LangChain 环境
- 了解接入通义大模型的基本流程

## 2. 环境配置
1. 创建虚拟环境
```bash
conda create -n agent_env python=3.12
```

或者：
```bash
uv venv -p 3.12
uv init
```

2. 激活虚拟环境
```bash
conda activate agent_env
```

## 3. 安装依赖
```bash
pip install langchain-community==0.4.1
pip install dashscope==1.25.9
```

## 4. 注册 API Key
不同的运营商有不同的注册方式。

例如，百炼大模型服务平台：
- 控制台地址：https://bailian.console.aliyun.com/#/home
- 创建 Key 地址：https://bailian.console.aliyun.com/?tab=model#/api-key

## 5. 注意事项
- 请将获取到的 Key 设置到环境变量中
- 运行前确认 Python 版本为 3.12
- 若使用其他模型平台，依赖包和环境变量名称可能不同

import json
import os

import openai   # uv add openai==2.14.0  pip install openai==2.14.0
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


# 初始化OpenAI客户端
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_API_BASE")

client = openai.OpenAI(api_key=api_key,base_url=base_url)

def get_weather(city: str, unit: str = "celsius") -> dict:
    """模拟天气查询函数"""
    # 这里应该是实际的天气API调用
    return {"temperature": 22, "condition": "sunny", "city": city}

# 工具定义（新版Tool格式）
weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "获取指定城市的天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {"type": "string", "description": "城市名称"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["city"]
        }
    }
}

def call_function_with_llm(user_query: str):
    """使用LLM进行函数调用的完整流程"""
    response = client.chat.completions.create(
        model="GLM-4.6V-Flash",
        messages=[{"role": "user", "content": user_query}],
        tools=[weather_tool],
        tool_choice="auto"
    )

    # 检查是否需要调用工具
    if response.choices[0].finish_reason == "tool_calls":
        tool_calls = response.choices[0].message.tool_calls

        tool_call_results = []
        for tool_call in tool_calls:
            tool_name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            # 执行工具
            if tool_name == "get_weather":
                result = get_weather(**arguments)

            tool_call_results.append({
                "tool_call_id": tool_call.id,
                "role": "tool",
                "name": tool_name,
                "content": json.dumps(result)
            })

        # 将结果发送回LLM生成最终回复
        final_response = client.chat.completions.create(
            model="GLM-4.6V-Flash",
            messages=[
                {"role": "user", "content": user_query},
                response.choices[0].message,
                *tool_call_results
            ]
        )
        return final_response.choices[0].message.content

    return response.choices[0].message.content

if __name__ == "__main__":
    user_query = "北京今天的天气怎么样？"
    result = call_function_with_llm(user_query)
    print(result)
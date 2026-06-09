from openai import OpenAI

client = OpenAI(
    api_key="710bd138fe244abd8eb15853f4391ea2.lHFnfZkkLm3TMFpw",
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)

completion = client.chat.completions.create(
    model="glm-4.6v-flash",
    messages=[
        {"role": "system", "content": "你是一个聪明客服人员"},
        {"role": "user", "content": "你好，你的职责是什么？"}
    ],
    top_p=0.7,
    temperature=0.9
)

print(completion.choices[0].message.content)
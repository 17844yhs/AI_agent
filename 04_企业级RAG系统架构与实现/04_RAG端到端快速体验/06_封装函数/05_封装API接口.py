from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer

'''
    api_key="710bd138fe244abd8eb15853f4391ea2.lHFnfZkkLm3TMFpw",
    base_url="https://open.bigmodel.cn/api/paas/v4/"
    glm-4.6v-flash
'''
def call_llm(prompt:str,model:str,max_tokens:int = 1024,temperature:float = 0.9,api_key:str = None,api_base_url:str = None):
    '''
    调用LLM
     -  GLM模型 url:  https://open.bigmodel.cn/api/paas/v4/
     -  TONGYI模型 url:  https://dashscope.aliyuncs.com/compatible-mode/v1
    '''
    client = OpenAI(api_key=api_key,base_url=api_base_url)

    completion = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return completion.choices[0].message.content

def format_context(docs:list,max_chars:int = 1500):
    '''
    格式化上下文: 去重，控制长度
    '''
    seen = set()    # 创建一个集合，用于去重
    parts = []      # 创建一个列表，用于存储上下文
    total = 0       # 创建一个变量，用于记录总长度

    for doc in docs:   # 遍历文档
        if not doc:     # 如果文档为空，跳过
            continue
        doc = doc.strip()       # 去除首尾空格
        if not doc or doc in seen:  # 如果文档为空或者已经出现过，跳过
            continue

        next_total = total + len(doc)  + (2 if parts else 0)   # 计算出新总长度
        if next_total > max_chars:  # 如果总长度超过最大长度，跳过
            break
        # 添加文档到列表中
        seen.add(doc)
        parts.append(doc)
        total = next_total
 
    return '\n\n'.join(parts)
def build_prompt(context:str,question:str):
    '''
    构建LLM上下文
    '''
    instruction = (
        "你是一个基于文档的问答助手，请严格依据上下文回答问题；"
        "如果上下文缺失相关信息，直接回答“我不知道”。"
    )

    return (
        f"{instruction}\n\n"
        f"[上下文]：\n{context}\n\n"
        f"[问题]\n问：{question}\n答案："
        )

def generate_answer(
        question:str,
        top_k:int = 3,
        max_tokens:int=1024,
        temperature:float = 0.9,
        model:str = "glm-4.5-flash",
        api_key:str = None,
        api_base_url:str = None
):
    # 获取api_key 如果没有值，返回空
    # 加载模型
    emb_model = SentenceTransformer('BAAI/bge-small-zh')  # 加载模型
    q_emb = emb_model.encode([question], normalize_embeddings=True)
    client = chromadb.PersistentClient(path='chroma_db')   # 初始化数据库
    collection = client.get_or_create_collection('demo')   # 创建集合
    #　在数据库查询数据
    result = collection.query(
        query_embeddings=q_emb,
        n_results=top_k
    )
    docs = result.get('documents',[[]])[0]
    if not docs:
        return {'answer': '我不知道','prompt':'','context':''}

    context = format_context(docs,max_chars=1500)   # 格式化上下文

    prompt = build_prompt(context, question)   # 构建LLM上下文

    # 调用LLM
    answer = call_llm(
        prompt= prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        api_key=api_key,
        api_base_url=api_base_url
    )

    # 返回结果
    return {'answer': answer,'question':question,'context':context}


if __name__ == '__main__':
    # print(call_llm(
    #     "请写一个关于机器学习的小故事",
    #     model="glm-4.5-flash",
    #     api_key="710bd138fe244abd8eb15853f4391ea2.lHFnfZkkLm3TMFpw",
    #     api_base_url="https://open.bigmodel.cn/api/paas/v4/"
    #     ))

    print(generate_answer(
        question="养老保险要交几年?",
        # api_key="710bd138fe244abd8eb15853f4391ea2.lHFnfZkkLm3TMFpw",
        api_key="sk-603a6266260a4504bb27f4adafbd80f0",
        api_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model="qwen-plus"
    ))
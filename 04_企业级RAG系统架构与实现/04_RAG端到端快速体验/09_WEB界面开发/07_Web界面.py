import os

import chromadb
import pdfplumber
def load_txt(path):
    # 加载txt文件
    with open(path,'r',encoding='utf-8') as f:
        # 读取文件
        info = f.read()
    return info

def load_pdf(path):
    # 加载pdf文件
    with pdfplumber.open(path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
    return "\n".join(pages)


def chunk_text(text, chunk_size=500, overlap=100):
    # 分块
    chunks = []
    start = 0    # 块的开始位置
    while start < len(text):
        end = start + chunk_size  # 块的结束位置
        chunks.append(text[start:end])  # 添加块
        start = end - overlap   # 更新块的开始位置
    return chunks

import chromadb
from sentence_transformers import SentenceTransformer
def init_db(doc_paths:list,chunk_size:int = 500,overlap:int = 100):
    '''
    构建向量数据库
    '''
    all_chunks = []
    metas =[]

    for path in doc_paths:
        if path.endswith('.txt'):
            text = load_txt(path)
        elif path.endswith('.pdf'):
            text = load_pdf(path)
        else:
            raise ValueError('不支持的文件格式')
        chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
        all_chunks.extend(chunks)
        metas.extend([{'source': os.path.basename(path), 'idx': i} for i in range(len(chunks))])

    client = chromadb.PersistentClient(path='chroma_db')   # 初始化数据库
    collection = client.get_or_create_collection('demo')   # 创建集合

    model = SentenceTransformer('BAAI/bge-small-zh')  # 加载模型
    embs = model.encode(all_chunks, normalize_embeddings=True)   #　对文本进行向量化，normalize_embeddings=True表示对向量进行归一化
    #　构建数据
    ids = [f'doc-{i}' for i in range(len(all_chunks))]

    collection.upsert(
        ids =ids,
        documents=all_chunks,
        embeddings=embs,
        metadatas=metas
    )
    print('向量库写入完成, 当前向量数量:', collection.count())

def search(query:str,top_k:int =1):
    model = SentenceTransformer('BAAI/bge-small-zh')  # 加载模型
    q_emb = model.encode([query], normalize_embeddings=True)

    client = chromadb.PersistentClient(path='chroma_db')   # 初始化数据库
    collection = client.get_or_create_collection('demo')   # 创建集合

    # 查询数据
    result = collection.query(
        query_embeddings=q_emb,
        n_results=top_k
    )

    if not result.get('documents'):
        return None
    
    docs = result['documents'][0]
    metas = result.get('metadatas', [[]])[0]
    ids = result.get('ids', [[]])[0]

    return {
        'id': ids[0] if ids else None,
        'document': docs[0] if docs else None,
        'metadata': metas[0] if metas else None,
    }


from openai import OpenAI
import chromadb
from sentence_transformers import SentenceTransformer

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
        hits:list,
        **llm_kwargs
):
    # 获取api_key 如果没有值，返回空
    if not hits:
        return {'answer': '我不知道','prompt':'','context':''}
    context = format_context([hits.get('document')],max_chars=1500)   # 格式化上下文
    prompt = build_prompt(context, question)   # 构建LLM上下文

    # 调用LLM
    answer = call_llm(
        prompt= prompt,
        **llm_kwargs
    )

    # 返回结果
    return {'answer': answer,'question':question,'context':context}

def rag_pipeline(query:str,top_k:int = 3,**llm_kwargs):
    '''
        端到端 RAG：输入 query，输出 (answer, hits)。
        自动初始化向量库（如果为空），然后检索 + 生成。
        llm_kwargs 会透传给 generate_answer（如 model, api_key, api_base 等）。
    '''
    hits = search(query,top_k)
    if not hits:
        return "未检索到相关内容，请换个问法。", []
    result = generate_answer(query,hits,**llm_kwargs)
    return result["answer"], hits

if __name__ == '__main__':
    import streamlit as st

    st.title("RAG Demo")
    q = st.text_input("请输入问题：")

    if st.button("提问"):
        if not q.strip():
            st.warning("请输入问题！")
        else:
            with st.spinner("请稍等..."):
                ans,hit = rag_pipeline(
                    query="养老保险要交几年?",
                    api_key="sk-603a6266260a4504bb27f4adafbd80f0",
                    api_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    model="qwen-plus"
                )
                st.subheader("回答:")
                st.write(ans)
                st.subheader("相关文档:")
                st.markdown(f'- **{hit.get("metadata", {})}**  | id: {hit.get("id")}')
                doc = hit.get('document')
                st.write(doc[:300] + "..." if len(doc)>300 else  '')
def load_txt(path):
    # 加载txt文件
    with open(path,'r',encoding='utf-8') as f:
        # 读取文件
        info = f.read()
    return info

import chromadb
from colorama import init
import pdfplumber
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
def init_db(chunks):
    client = chromadb.PersistentClient(path='chroma_db')   # 初始化数据库
    collection = client.get_or_create_collection('demo')   # 创建集合

    model = SentenceTransformer('BAAI/bge-small-zh')  # 加载模型
    embs = model.encode(chunks, normalize_embeddings=True)   #　对文本进行向量化，normalize_embeddings=True表示对向量进行归一化

    #　构建数据
    ids = [f'doc-{i}' for i in range(len(chunks))]
    metas = [{'source': 'faq.pdf', 'idx': i} for i in range(len(chunks))]

    collection.upsert(
        ids =ids,
        documents=chunks,
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

if __name__ == '__main__':
    pdf_path = './data/faq.pdf'
    pdf_info = load_pdf(pdf_path)
    pdf_chunks = chunk_text(pdf_info)
    # init_db(pdf_chunks)
    hit = search('养老保险交几年?')
    print(hit)

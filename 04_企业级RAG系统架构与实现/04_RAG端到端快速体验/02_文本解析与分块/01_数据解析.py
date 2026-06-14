def load_txt(path):
    # 加载txt文件
    with open(path,'r',encoding='utf-8') as f:
        # 读取文件
        info = f.read()
    return info

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


if __name__ == '__main__':
    # 文件路径
    text_path = './data/faq.txt'
    text_info = load_txt(text_path)
    text_chunks = chunk_text(text_info)
    print(f'chucks_numbers: {len(text_chunks)},  第一块内容:',text_chunks[0][:200])

    print('-'*20,'pdf文件内容','-'*20)
    
    pdf_path = './data/faq.pdf'
    pdf_info = load_pdf(pdf_path)
    pdf_chunks = chunk_text(pdf_info)
    print(f'chucks_numbers: {len(pdf_chunks)},  第一块内容:',pdf_chunks[0][:200])
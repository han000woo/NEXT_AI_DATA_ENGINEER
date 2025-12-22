import chromadb
# API 키를 환경변수로 관리하기 위한 설정 파일
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma

# API 키 정보 로드
load_dotenv()

import json
from langchain.docstore.document import Document

# db/db.py
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
BIBLE_PATH = BASE_DIR / "data" / "bible.json"

def load_bible_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        bible_data = json.load(f)
    
    docs = []
    
    for ref, content in bible_data.items():
        # 1. 정규표현식으로 "창1:1" 분리 (창 / 1 / 1)
        import re
        match = re.match(r"([ㄱ-ㅎ가-힣]+)(\d+):(\d+)", ref)
        
        if match:
            book_abbr = match.group(1) # 창
            chapter = match.group(2)   # 1
            verse = match.group(3)     # 1
            
            # 2. 문서 객체 생성
            doc = Document(
                page_content=f"[{ref}] {content.strip()}",
                metadata={
                    "book_abbr": book_abbr,
                    "chapter": int(chapter),
                    "verse": int(verse),
                    "reference": ref
                }
            )
            docs.append(doc)
            
    return docs

# 사용 예시
docs = load_bible_json(BIBLE_PATH)
print("load bible json")
# 2. 텍스트 분할 (이미 절 단위지만, 문맥을 위해 2~3절씩 묶는 것을 권장)
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300, 
    chunk_overlap=50
)
split_docs = text_splitter.split_documents(docs)
print("text split")

# 3. 벡터 DB 저장
vectorstore = Chroma.from_documents(
    documents=split_docs,
    embedding=OpenAIEmbeddings(),
    persist_directory="./bible_vector_db",
    collection_name="bible"
)
print("store vectordb")
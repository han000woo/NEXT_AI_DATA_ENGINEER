from pathlib import Path
import json
from langchain.docstore.document import Document
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

def preprocess_bible(file_path, persist_directory) :
    documents = (load_bible_json(file_path))

    text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1500, 
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""] # 문단 단위로 먼저 자르도록 유도
    )

    split_docs = text_splitter.split_documents(documents)
    print(f"\n✂️ 총 {len(documents)}개의 말씀을 {len(split_docs)}개의 청크(조각)로 분할했습니다.")

    if split_docs:
        print("💾 ChromaDB에 저장 중...")

        # 임베딩 모델 명시 (검색 때와 동일하게!)
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

        vectorstore = Chroma.from_documents(
            documents=split_docs,
            embedding=embeddings,
            persist_directory=persist_directory,
            collection_name="bible" # "pastor_sermons"
        )
        print("✅ 저장 완료! DB가 업데이트되었습니다.")
    else:
        print("❌ 저장할 문서가 없습니다.")


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

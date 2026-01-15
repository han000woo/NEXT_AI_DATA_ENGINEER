from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from pathlib import Path 

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / ".env"

load_dotenv(CONFIG_PATH)

DB_PATH = BASE_DIR / "chroma_vector_db" # 또는 "final_db" 등 실제 폴더명

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

vectorstore = Chroma(
    persist_directory=DB_PATH, 
    embedding_function=embeddings,
    collection_name='yujin_works' # ingest할 때 쓴 이름 확인!
)

retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 3, # 문맥을 좀 더 풍부하게 하기 위해 2 -> 3으로 증가 추천
        }
    )

user_input = ""
while user_input != "stop" :
    user_input = input("\n\n\n질문을 입력하세요 or stop\n\n")    
    docs = retriever.invoke(user_input)
    print(docs,"\n\n\n")
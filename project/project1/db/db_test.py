from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

embeddings = OpenAIEmbeddings()
vectorstore = Chroma(
    persist_directory="bible_vector_db", # DB 저장 경로
    embedding_function=embeddings,
    collection_name='bible'
)

retriever = vectorstore.as_retriever(search_kwargs={"k": 1})
print(vectorstore._collection.count())

docs = retriever.invoke("진실로 진실로 네게")
print(docs)

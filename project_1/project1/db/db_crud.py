from pathlib import Path
import chromadb
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = str(BASE_DIR / "chroma_vector_db")
CONFIG_PATH = BASE_DIR / "config" / ".env"

load_dotenv(CONFIG_PATH)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

client = chromadb.PersistentClient(
    path=DB_PATH
)

def check_tables() : 
    collections = client.list_collections()
    for c in collections:
        print(c.name)

def select_tables(collection_name) : 
    collection = client.get_collection(collection_name)

    rows = collection.get()

    for i in range(len(rows["ids"])):
        print("──────────────")
        print(f"🆔 id        : {rows['ids'][i]}")
        print(f"📄 document  : {rows['documents'][i][:200]}...")  # 앞부분만
        print(f"🧾 metadata  : {rows['metadatas'][i]}")

def select_by_bible_ref(collection_name, pref):
    collection = client.get_collection(collection_name)

    # rows = collection.get(
    #     where={"bible_ref": bible_ref}
    # )
    rows = collection.get()

    for i in range(len(rows["ids"])):
        bible_ref = rows["metadatas"][i].get("bible_ref", "")
        if bible_ref.startswith(pref):
            print("──────────────")
            print(f"🆔 id        : {rows['ids'][i]}")
            print(f"📄 document  : {rows['documents'][i][:200]}...")
            print(f"🧾 metadata  : {rows['metadatas'][i]}")

def delete_tables(collection_name) : 
    client.delete_collection(collection_name)
    print(f"🗑️ 컬렉션 삭제 완료: {collection_name}")

# delete_tables("bubryune_works")
check_tables()
# select_by_bible_ref("woonsung_works","마")

import os
import openai
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from enums.target import TARGET_CONFIG, AnswerTarget, SermonState
from dotenv import load_dotenv

load_dotenv()

# 0. 설교 DB 로드 (나중에 설교집 DB가 완성되면 이 경로를 사용하세요)
embeddings = OpenAIEmbeddings()
# 목사님/철학자 통합 DB 또는 페이지별 DB를 로드합니다.
# collection_name을 'sermons' 등으로 설정했다고 가정합니다.
vectorstore = Chroma(
    persist_directory="./sermon_vector_db", 
    embedding_function=embeddings,
    collection_name='sermons'
)

def get_response(user_input, chat_history, target: AnswerTarget):
    """
    return: (답변 텍스트, 출처 정보 문자열)
    """

    # 1. 설교 DB에서 관련 내용 검색
    # 특정 목사님(target)의 데이터만 가져오도록 필터를 걸 수 있습니다.
    config = TARGET_CONFIG[target]
    author_name = config.get("name", "") # TARGET_CONFIG에 성함이 있다고 가정
    
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 2, 
            "filter": {"author": author_name} # 해당 목사님 설교만 검색
        }
    )
    
    docs = retriever.invoke(user_input)
    
    # 2. 검색 결과 및 출처 정리
    if docs:
        print("here")
        context_text = "\n".join([doc.page_content for doc in docs])
        # 메타데이터에 'title'이나 'date'가 있다면 활용합니다.
        sources = [doc.metadata.get('title', '알 수 없는 설교') for doc in docs]
        source_info = (SermonState.FOUND, f"{author_name} 목사님 설교: " + ", ".join(set(sources)))
    else:
        print("not here")
        context_text = ""
        source_info = (SermonState.NOT_FOUND,-1)

    # 3. 최근 대화 정리
    formatted_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in chat_history[-10:]
    ]

    # 4. 프롬프트 구성
    # 검색된 내용이 있을 때와 없을 때의 지침을 다르게 줍니다.
    if context_text:
        rag_prompt = f"다음은 {author_name} 목사님의 실제 설교 내용입니다:\n{context_text}\n\n위 내용을 바탕으로 답변하세요."
    else:
        rag_prompt = "관련된 설교 내용을 찾지 못했습니다. 평소 목사님의 철학과 따뜻한 마음을 담아 성도님을 위로해 주세요."

    system_message = {
        "role": "system",
        "content": f"{config['system_prompt']}\n\n{rag_prompt}"
    }

    # 5. 메시지 구성 및 API 호출
    messages_to_send = [system_message] + formatted_history + [{"role": "user", "content": user_input}]

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages_to_send,
        temperature=0.7
    )

    return response.choices[0].message.content, source_info
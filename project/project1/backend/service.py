import os
from pathlib import Path
import openai
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from enums.target import TARGET_CONFIG, AnswerTarget, SermonState
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / ".env"

load_dotenv(CONFIG_PATH)

# --- 1. 임베딩 설정 (DB 만들 때와 동일한 모델 필수!) ---
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# --- 2. DB 로드 (전역 변수로 한 번만 로드) ---
# 경로가 실제 존재하는지 확인하는 로직이 있으면 더 안전합니다.
DB_PATH = "chroma_vector_db" # 또는 "final_db" 등 실제 폴더명

woonsung_vectorstore = Chroma(
    persist_directory=DB_PATH,
    embedding_function=embeddings,
    collection_name='woonsung_works'
)

yujin_vectorstore = Chroma(
    persist_directory=DB_PATH, 
    embedding_function=embeddings,
    collection_name='yujin_works' # ingest할 때 쓴 이름 확인!
)

nietzsche_vectorstore = Chroma(
    persist_directory=DB_PATH, 
    embedding_function=embeddings,
    collection_name='nietzsche_works' # ingest할 때 쓴 이름 확인!
)

def get_response(user_input, chat_history, target: AnswerTarget):
    """
    return: (답변 텍스트, (상태, 출처_텍스트))
    """
    
    # --- 3. 타겟별 DB 및 설정 분기 ---
    if target == AnswerTarget.PASTOR_A:
        vectorstore = yujin_vectorstore
        author_title = "김유진 목사"
        # 설교 DB에서 제목을 찾는 키 (ingest.py 확인 필요)
        meta_key = 'title' 

    elif target == AnswerTarget.PASTOR_B:
        vectorstore = woonsung_vectorstore
        author_title = "정운성 목사"
        # 설교 DB에서 제목을 찾는 키 (ingest.py 확인 필요)
        meta_key = 'title' 
    
    elif target == AnswerTarget.NIETZSCHE: # PHILOSOPHER_A 대신 구체적 명칭 권장
        vectorstore = nietzsche_vectorstore
        author_title = "철학자"
        # 니체 DB에서 제목을 찾는 키 (아까 full_ref로 저장함)
        meta_key = 'full_ref' 

    else:
        # 예외 처리: 알 수 없는 타겟이면 기본값 설정
        vectorstore = yujin_vectorstore
        author_title = "AI"
        meta_key = 'source'

    config = TARGET_CONFIG[target]
    author_name = config.get("name", "상담가")

    # --- 4. 검색 (Filter 제거 및 k값 조정) ---
    # 컬렉션이 이미 분리되어 있으므로 filter 불필요
    retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 3, # 문맥을 좀 더 풍부하게 하기 위해 2 -> 3으로 증가 추천
        }
    )
    
    docs = retriever.invoke(user_input)
    
    # --- 5. 검색 결과 및 출처 정리 ---
    if docs:
        context_text = "\n\n".join([doc.page_content for doc in docs])
        
        # 메타데이터에서 출처 가져오기 (없으면 '출처 미상')
        sources = [doc.metadata.get(meta_key, '출처 미상') for doc in docs]
        unique_sources = list(set(sources)) # 중복 제거
        
        # 출처 문구 생성 (페르소나에 맞게)
        if target == AnswerTarget.NIETZSCHE:
             source_str = f"📜 니체 저서 인용: {', '.join(unique_sources)}"
        else:
             source_str = f"📖 {author_name} {author_title} 설교: {', '.join(unique_sources)}"

        source_info = (SermonState.FOUND, source_str)
        
        # 검색된 내용이 있을 때 프롬프트
        rag_prompt = (
            f"다음은 당신이 참고해야 할 지식 베이스(Context)입니다:\n"
            f"---------------------\n"
            f"{context_text}\n"
            f"---------------------\n"
            f"위 지식 베이스의 내용과 당신의 사상을 연결하여 답변하세요."
            f"지식 베이스에 없는 내용은 지어내지 말고 당신의 철학적 관점에서 해석하세요."
        )

    else:
        context_text = ""
        source_info = (SermonState.NOT_FOUND, "") # -1 대신 빈 문자열 권장
        
        # 검색된 내용이 없을 때 프롬프트
        rag_prompt = "관련된 문헌을 찾지 못했습니다. 당신의 평소 사상과 통찰력에 의존하여 답변하세요."

    # --- 6. 최근 대화 정리 ---
    formatted_history = [
        {"role": msg["role"], "content": msg["content"]}
        for msg in chat_history[-6:] # 토큰 절약을 위해 10 -> 6 정도로 조절 (선택사항)
    ]
    print(rag_prompt)

    # --- 7. 최종 메시지 구성 ---
    system_message = {
        "role": "system",
        "content": f"{config['system_prompt']}\n\n[RAG 지침]\n{rag_prompt}"
    }

    messages_to_send = [system_message] + formatted_history + [{"role": "user", "content": user_input}]

    # --- 8. API 호출 ---
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=messages_to_send,
        temperature=0.7 
        # 니체의 경우 창의성을 위해 temperature를 0.8~0.9로 높이는 것도 방법입니다.
    )

    return response.choices[0].message.content, source_info
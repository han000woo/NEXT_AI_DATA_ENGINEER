import os
from pathlib import Path
import openai
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from enums.target import TARGET_CONFIG, AnswerTarget, SermonState
from dotenv import load_dotenv

from utils.util import parse_list

BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / ".env"

load_dotenv(CONFIG_PATH)

# --- 1. 임베딩 설정 (DB 만들 때와 동일한 모델 필수!) ---
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# --- 2. DB 로드 (전역 변수로 한 번만 로드) ---
DB_PATH = "chroma_vector_db" # 또는 "final_db" 등 실제 폴더명

simple_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0) # 비용 절감을 위해 mini 모델 권장

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
    print("get_response")

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

    bible_refs =  expect_query_bible_refs(user_input)
    docs_meta = vectorstore.similarity_search(
    user_input,
    k=3,
    filter={"bible_ref": {"$in": bible_refs}}
    )
    docs_all = vectorstore.similarity_search(
    user_input,
    k=3
    )
    
    docs = get_refined_docs(user_input, docs_meta, docs_all, simple_llm)
    
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

def extract_bible_ref_with_simple_llm(filename: str):
    print("extract_bible_ref_with_simple_llm")

    """
    simple_LLM을 사용하여 파일명에서 '성경:장' 형태의 메타데이터를 추출합니다.
    예: '마가복음 14장' -> '마:14장'
    """
    
    prompt = ChatPromptTemplate.from_template("""
    너는 문자열 변환기다.
    아래 파일명에서 성경 권 이름과 장만 추출하여
    아래 규격의 문자열만 출력하라.
    
    규격:
    - 형식: [성경 한글 줄임표]:[장]
    - 예시:
      "마가복음 14장" → 마:14장
      "창세기 1장" → 창:1장
      "요한복음 3장 16절" → 요:3장
      추출 불가 → unknown
    
    ⚠️ 규칙:
    - 설명하지 마라
    - 따옴표, 별표(**), 줄바꿈 없이
    - 결과 문자열 하나만 출력하라
    
    파일명: {filename}
    """)

    
    chain = prompt | simple_llm | StrOutputParser()
    
    try:
        # 파일명에서 괄호 안의 텍스트가 핵심이므로 이 부분을 강조해서 전달
        bible_ref = chain.invoke({"filename": filename})
        return bible_ref.strip()
    except Exception as e:
        print(f"simple_LLM 추출 오류: {e}")
        return "unknown"

def expect_query_bible_refs(simple_llm, question: str) -> list[str]:
    print("expect_query_bible_refs")

    prompt = f"""
    다음 질문과 관련된 성경 권과 장을 JSON 배열로만 출력해라.
    설명하지 마라.

    예:
    ["마:14장", "시:23편"]
    또는
    []

    질문: {question}
    """
    result = simple_llm.invoke(prompt)
    return parse_list(result)  # 문자열 → 리스트


def get_refined_docs(user_input, docs_meta, docs_all, simple_llm):
    print("get_refined_docs")
    # 1. 문서 합치기 및 중복 제거
    all_candidates = docs_meta + docs_all
    unique_docs = {doc.page_content: doc for doc in all_candidates}.values()
    
    # 2. simple_LLM에게 적합성 판단 요청
    context_text = "\n\n".join([f"[{i+1}] {d.page_content[:500]}..." for i, d in enumerate(unique_docs)])
    
    prompt = f"""
    당신은 설교 데이터 전문가입니다. 아래 질문과 검색된 문서 후보들을 보고, 
    질문에 답하는 데 정말로 도움이 되는 문서의 번호만 골라주세요.
    관련이 없는 문서는 과감히 제외하세요.
    
    질문: {user_input}
    
    후보 문서:
    {context_text}
    
    응답 형식: 관련 있는 문서의 번호만 쉼표로 구분해서 적어주세요 (예: 1, 3). 
    만약 모든 문서가 관련이 없다면 'None'이라고 적어주세요.
    """
    
    selected_indices = simple_llm.invoke(prompt).content.strip()
    
    if "None" in selected_indices or not selected_indices:
        return list(unique_docs)[:2] # 아무것도 없으면 기본 유사도 상위 2개 반환
    
    # 3. 선택된 문서만 필터링해서 반환
    refined_docs = []
    try:
        indices = [int(i.strip()) - 1 for i in selected_indices.split(",")]
        for idx in indices:
            if 0 <= idx < len(unique_docs):
                refined_docs.append(list(unique_docs)[idx])
    except:
        return list(unique_docs)[:2]

    print(refined_docs)
    return refined_docs

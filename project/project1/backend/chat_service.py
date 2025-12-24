import os
from pathlib import Path
from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

import openai
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# 사용자 정의 모듈 (가정)
from enums.target import TARGET_CONFIG, AnswerTarget, SermonState
from utils.util import parse_list

# --- 환경 설정 ---
BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / ".env"
load_dotenv(CONFIG_PATH)

# --- 전역 설정 (싱글톤처럼 사용) ---
# 임베딩 모델은 메모리에 한 번만 로드하는 것이 좋습니다.
EMBEDDINGS = OpenAIEmbeddings(model="text-embedding-3-small")
DB_PATH = "chroma_vector_db"

# ==========================================
# [부모 클래스] 기본 채팅 서비스
# ==========================================
class BaseChatService(ABC):
    def __init__(self, target: AnswerTarget):
        self.target = target
        self.config = TARGET_CONFIG[target]
        self.author_name = self.config.get("name", "AI")
        
        # LLM 모델 설정
        self.main_llm = openai  # OpenAI Client directly
        self.simple_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        
        # VectorStore 설정 (자식에서 구체화)
        self.vectorstore = self._load_vectorstore()
        self.meta_key = self._get_meta_key()

    @abstractmethod
    def _load_vectorstore(self) -> Chroma:
        """자식 클래스에서 사용할 VectorDB를 정의해야 함"""
        pass

    @abstractmethod
    def _get_meta_key(self) -> str:
        """출처 표시를 위한 메타데이터 키 (title, source, full_ref 등)"""
        pass

    def _retrieve_documents(self, user_input: str) -> Tuple[List, List]:
        """
        기본 검색 로직. 
        필요시 자식 클래스에서 오버라이딩(덮어쓰기)하여 필터링 로직 추가.
        반환: (docs_meta, docs_all)
        """
        
        print("_retrieve_documents")
        # 기본은 필터 없이 전체 검색
        docs_all = self.vectorstore.similarity_search(user_input, k=3)
        return [], docs_all

    def _refine_documents(self, user_input: str, docs_candidates: List) -> List:
        """LLM을 이용해 문서 재순위화 (공통 로직)"""

        print("_refine_documents")

        if not docs_candidates:
            return []

        # 중복 제거
        unique_docs = {doc.page_content: doc for doc in docs_candidates}.values()
        
        context_text = "\n\n".join([f"[{i+1}] {d.page_content[:500]}..." for i, d in enumerate(unique_docs)])
        
        prompt = f"""
        당신은 데이터 전문가입니다. 질문에 답하는 데 정말로 도움이 되는 문서 번호만 골라주세요.
        질문: {user_input}
        후보 문서:
        {context_text}
        응답 형식: 번호만 쉼표로 구분 (예: 1, 3). 없으면 'None'.
        """
        
        try:
            selected_indices = self.simple_llm.invoke(prompt).content.strip()
            if "None" in selected_indices or not selected_indices:
                return list(unique_docs)[:2]
            
            indices = [int(i.strip()) - 1 for i in selected_indices.split(",")]
            refined = [list(unique_docs)[idx] for idx in indices if 0 <= idx < len(unique_docs)]
            return refined if refined else list(unique_docs)[:2]
        except Exception as e:
            print(f"Refine Error: {e}")
            return list(unique_docs)[:2]

    def _format_source(self, docs) -> str:
        """출처 포맷팅 (자식에서 커스텀 가능)"""
        sources = [doc.metadata.get(self.meta_key, '출처 미상') for doc in docs]
        unique_sources = list(set(sources))
        return f"📖 {self.author_name} 인용: {', '.join(unique_sources)}"

    def get_response(self, user_input: str, chat_history: list) -> Tuple[str, Tuple[SermonState, str]]:
        print(f"[{self.author_name}] get_response 시작")
        
        # 1. 문서 검색 (자식 클래스 로직에 따라 다름)
        docs_meta, docs_all = self._retrieve_documents(user_input)
        
        # 2. 문서 정제 (Reranking)
        all_candidates = docs_meta + docs_all
        refined_docs = self._refine_documents(user_input, all_candidates)

        # 3. 프롬프트 구성
        if refined_docs and docs_meta:
            context_text = "\n\n".join([doc.page_content for doc in refined_docs])
            source_str = self._format_source(refined_docs)
            source_info = (SermonState.FOUND, source_str)
            
            rag_prompt = (
                f"다음 지식 베이스(Context)를 바탕으로 답변하세요:\n"
                f"---\n{context_text}\n---\n"
                f"지식 베이스 내용을 당신의 사상과 연결하여 해석하세요."
            )
        else:
            context_text = ""
            source_info = (SermonState.NOT_FOUND, "")
            rag_prompt = "관련 문헌을 찾지 못했습니다. 당신의 평소 통찰력에 의존해 답변하세요."

        # 4. LLM 호출
        formatted_history = [
            {"role": msg["role"], "content": msg["content"]} 
            for msg in chat_history[-6:]
        ]
        
        system_message = {
            "role": "system",
            "content": f"{self.config['system_prompt']}\n\n[RAG 지침]\n{rag_prompt}"
        }

        response = self.main_llm.chat.completions.create(
            model="gpt-4o",
            messages=[system_message] + formatted_history + [{"role": "user", "content": user_input}],
            temperature=0.7
        )
        
        return response.choices[0].message.content, source_info


# ==========================================
# [자식 클래스 1] 목회자 서비스 (성경 필터링 포함)
# ==========================================
class PastorService(BaseChatService):
    def __init__(self, target: AnswerTarget, collection_name: str):
        self.collection_name = collection_name
        super().__init__(target)

    def _load_vectorstore(self) -> Chroma:
        return Chroma(
            persist_directory=DB_PATH,
            embedding_function=EMBEDDINGS,
            collection_name=self.collection_name
        )

    def _get_meta_key(self) -> str:
        return 'title' # 설교 제목 키

    def _expect_query_bible_refs(self, question: str) -> list[str]:
        """목회자 특화 기능: 질문에서 성경 구절 추출"""
        prompt = f"""
        질문과 관련된 성경 권과 장을 JSON 배열로 출력. 예: ["마:14장"] 또는 [].
        질문: {question}
        """
        result = self.simple_llm.invoke(prompt).content
        return parse_list(result)

    def _retrieve_documents(self, user_input: str) -> Tuple[List, List]:
        # 1. 성경 구절 추출
        bible_refs = self._expect_query_bible_refs(user_input)

        print(f"_retrieve_documents {bible_refs}")
        docs_meta = []
        if bible_refs:
            print(f"🔍 성경 필터 적용: {bible_refs}")
            docs_meta = self.vectorstore.similarity_search(
                user_input, k=3, filter={"bible_ref": {"$in": bible_refs}}
            )
            
        docs_all = self.vectorstore.similarity_search(user_input, k=3)
        return docs_meta, docs_all
    
    def _format_source(self, docs) -> str:
        # 부모 메서드 오버라이드하여 목사님 전용 문구 사용
        sources = [doc.metadata.get(self.meta_key, '제목 미상') for doc in docs]
        unique_sources = list(set(sources))
        return f"📖 {self.author_name} 설교: {', '.join(unique_sources)}"


# ==========================================
# [자식 클래스 2] 니체 서비스 (철학적 접근)
# ==========================================
class NietzscheService(BaseChatService):
    def _load_vectorstore(self) -> Chroma:
        return Chroma(
            persist_directory=DB_PATH,
            embedding_function=EMBEDDINGS,
            collection_name='nietzsche_works'
        )

    def _get_meta_key(self) -> str:
        return 'full_ref' # 니체 저서 인용 키

    def _retrieve_documents(self, user_input: str) -> Tuple[List, List]:
        # 니체는 성경 필터링이 필요 없으므로 단순 검색만 수행
        # (필요하다면 여기서 철학 용어 필터링 등을 추가 가능)
        return [], self.vectorstore.similarity_search(user_input, k=4) # k를 조금 늘림

    def _format_source(self, docs) -> str:
        sources = [doc.metadata.get(self.meta_key, '출처 미상') for doc in docs]
        unique_sources = list(set(sources))
        return f"📜 니체 저서 인용: {', '.join(unique_sources)}"


# ==========================================
# [팩토리] 서비스 생성기
# ==========================================
def get_chat_service(target: AnswerTarget) -> BaseChatService:
    if target == AnswerTarget.PASTOR_A:
        return PastorService(target, collection_name='yujin_works')
    
    elif target == AnswerTarget.PASTOR_B:
        return PastorService(target, collection_name='woonsung_works')
    
    elif target == AnswerTarget.NIETZSCHE:
        return NietzscheService(target)
    
    else:
        # 기본값 (예외 처리)
        return PastorService(AnswerTarget.PASTOR_A, collection_name='yujin_works')


# ==========================================
# [메인 실행부] 기존 함수 대체
# ==========================================
def get_response(user_input, chat_history, target: AnswerTarget):
    # 1. 타겟에 맞는 서비스 객체 생성 (팩토리 패턴)
    service = get_chat_service(target)
    
    # 2. 객체의 메서드 실행
    return service.get_response(user_input, chat_history)
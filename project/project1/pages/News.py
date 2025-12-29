from pathlib import Path
from dotenv import load_dotenv
import streamlit as st
import asyncio
import os
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession
from enums.target import AnswerTarget
from backend.chat_service import get_chat_service

# --- 환경 설정 ---
BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / ".env"
load_dotenv(CONFIG_PATH)
# 2. 설정: MCP 서버 주소 & OpenAI 모델

MCP_SERVER_URL = os.getenv("MCP_NEWS_URL", "http://localhost:8000/sse")

st.set_page_config(page_title="Wisdom AI", page_icon="🦉")
st.title("뉴스 평론")
st.caption("종교 및 철학가들이 최신 뉴스에 대한 인사이트를 제공합니다.")

targets = list(AnswerTarget)
reviewers = [get_chat_service(e) for e in targets]


# ---------------------------------------------------------
# [기능 1] MCP 서버에서 뉴스 가져오기 (도구 사용)
# ---------------------------------------------------------
async def get_news_from_mcp(search_keyword):
    """MCP 서버에 접속해서 get_latest_news 도구를 실행함"""
    try:
        async with sse_client(MCP_SERVER_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                await session.initialize()
                
                # 도구 실행 요청
                result = await session.call_tool(
                    "get_latest_news",
                    arguments={"keyword": search_keyword, "limit": 2}
                )
                # 결과 텍스트 반환
                return result.content[0].text
            
    except Exception as e:
        return f"Error: MCP 서버 연결 실패 ({str(e)})"


# ---------------------------------------------------------
# [UI] 화면 구성
# ---------------------------------------------------------
keyword = st.text_input("궁금한 뉴스 키워드는?", "인공지능")

if st.button("뉴스 검색 및 멘토 분석 시작"):
    
    # 1단계: 뉴스 가져오기 (MCP)
    with st.spinner(f"📡 MCP 서버에게 '{keyword}' 뉴스를 요청하는 중..."):
        # 비동기 함수 실행
        news_content = asyncio.run(get_news_from_mcp(keyword))
    
    # 뉴스를 못 가져왔거나 에러인 경우 처리
    if "Error" in news_content or "뉴스를 찾을 수 없습니다" in news_content:
        st.error(news_content)
    else:
        # 뉴스 원문 보여주기 (접을 수 있게)
        with st.expander("🔎 수집된 뉴스 원문 보기"):
            st.code(news_content)

        # 2단계: AI 분석 (GPT-4o)
        for target, rev in zip(targets, reviewers):
        
            # 스타일 가져오기 (없으면 기본값)
    
            with st.spinner(f"{target.getAvatar()} {target.value} : 생각을 정리 중입니다..."):
                # AI 응답 받기
                ai_response = rev.review_news(news_content, keyword)
    
                # ---------------------------------------------------
                # [데이터 파싱] 튜플 구조 분해 (Text, Metadata)
                # 구조: (Text, (Enum, Reference))
                # ---------------------------------------------------
                main_text = ""
                reference_text = None
    
                if isinstance(ai_response, tuple):
                    main_text = ai_response[0]  # 메인 답변 텍스트
    
                    # 메타데이터가 있는 경우 (SermonState, Reference)
                    if len(ai_response) > 1 and isinstance(ai_response[1], tuple):
                        # ai_response[1][1]이 실제 참고 문구 (예: '📖 AI 설교: ...')
                        reference_text = ai_response[1][1]
                else:
                    # 튜플이 아니라 그냥 문자열만 온 경우 방어 코드
                    main_text = str(ai_response)
    
                # ---------------------------------------------------
                # [UI 출력] 카드 형태로 예쁘게 출력
                # ---------------------------------------------------
                with st.container(border=True): # 테두리가 있는 컨테이너
                    # 1. 헤더 (아이콘 + 이름)
                    st.subheader(f"{target.getAvatar()} {target.value}")
    
                    # 2. 본문 (가독성을 위해 줄바꿈 처리 등)
                    st.markdown(main_text)
    
                    # 3. 구분선 및 참고자료 (있을 경우에만 표시)
                    if reference_text:
                        st.divider()
                        # 출처/참고 문헌은 눈에 띄게 표시 (info 박스 또는 caption)
                        st.caption(f"📚 **참고 문헌 / 근거**")
                        st.info(reference_text, icon="🔖")
    
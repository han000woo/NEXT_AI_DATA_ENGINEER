import streamlit as st
import time
import random

from utils.chat_util import stream_data

# --- 1. 페이지 설정 ---
st.set_page_config(
    page_title="AI 목사님 상담소",
    page_icon="🙏",
    layout="wide"
)

st.title("🙏 AI 목사님 상담소")
st.caption("목사님의 지난 설교 말씀을 기반으로 성도님의 고민에 답해드립니다.")

# --- 2. 사이드바 설정 ---
with st.sidebar:
    st.header("설정 및 안내")
    st.info("이 챗봇은 목사님의 설교 데이터베이스(10GB)를 기반으로 답변합니다.")
    
    # 대화 초기화 버튼
    if st.button("🗑️ 대화 내용 지우기"):
        st.session_state.messages = []
        st.rerun()
        
    st.divider()
    st.markdown("### 💡 상담 팁")
    st.markdown("- 구체적인 상황을 말씀해 주세요.")
    st.markdown("- 마음의 어려움이나 궁금한 성경 구절을 물어보세요.")

# --- 3. 세션 상태 관리 (대화 기록 저장) ---
# 메시지가 없으면 초기화하고 환영 인사 추가
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "성도님, 평안하셨습니까? 어떤 고민이 있으신가요? 목사님이 설교하셨던 말씀들 속에서 지혜를 찾아드리겠습니다."}
    ]

# --- 4. 채팅 화면 그리기 ---
# 저장된 메시지들을 화면에 표시
for message in st.session_state.messages:
    # 사용자(human)와 AI(assistant) 아이콘 구분
    avatar = "👤" if message["role"] == "user" else "✝️"
    
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        
        # 만약 이전 답변에 '참고 설교' 정보가 있었다면 같이 표시 (구조 예시)
        if "source" in message:
            with st.expander("📖 참고한 설교 말씀 보기"):
                st.caption(f"출처: {message['source']}")

# --- 5. 백엔드 시뮬레이션 함수 (나중에 실제 RAG 로직으로 교체될 부분) ---
def get_pastor_response(user_input):
    """
    실제로는 여기서 벡터 DB를 검색하고 LLM이 답변을 생성해야 합니다.
    지금은 UI 테스트를 위해 가짜 응답을 반환합니다.
    """
    # 흉내내기 위한 지연 시간 (검색하는 척)
    time.sleep(1.5) 
    
    responses = [
        "성도님, 그 문제로 마음이 많이 힘드셨겠습니다. 제가 예전에 **'광야를 지나는 인내'**라는 설교에서 이런 말씀을 드린 적이 있습니다. 하나님은 침묵하시는 것이 아니라 우리를 빚고 계신 것입니다.",
        "참 좋은 질문입니다. 성경은 우리에게 두려워하지 말라고 합니다. **'믿음의 눈'** 설교(2023.05.12)를 보면, 베드로가 물 위를 걸을 때 시선을 주님께 두었음을 기억해 봅시다.",
        "가정의 문제로 고민이 깊으시군요. 우리는 때로 내려놓음이 필요합니다. 주님께 모든 것을 맡기는 기도를 먼저 드려보시는 건 어떨까요?"
    ]
    
    # 랜덤으로 하나 선택 + 가짜 출처 데이터
    return random.choice(responses), "2023년 5월 12일 주일예배 설교 '광야를 지나는 인내'"

if prompt := st.chat_input("여기에 고민을 입력하세요..."):
    # 사용자 메시지 저장
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    # 🔹 빈 assistant 컨테이너 먼저 확보
    assistant_container = st.chat_message("assistant", avatar="✝️")

    # 🔹 spinner는 chat_message 밖에서
    with st.spinner("목사님의 설교록을 찾아보고 있습니다..."):
        response_text, source_info = get_pastor_response(prompt)

    # 🔹 실제 출력은 spinner 종료 후
    with assistant_container:
        st.write_stream(stream_data(response_text))

    # 🔹 session_state에 저장
    st.session_state.messages.append({
        "role": "assistant",
        "content": response_text,
        "source": source_info
    })

import streamlit as st
import time

from backend.chat_service import get_chat_service
from enums.target import AnswerTarget
from utils.util import stream_data
import streamlit as st
from backend.chat_service import get_chat_service
from enums.target import AnswerTarget
from utils.util import stream_data

# --- [1] 페이지 설정 및 CSS 스타일링 ---
st.set_page_config(page_title="사상 토론", page_icon="⚔️", layout="wide")

# 🎨 [핵심] 우측(User 역할) 말풍선을 오른쪽 정렬하는 CSS
st.markdown("""
<style>
    /* user(우측 선수) 메시지 스타일 커스텀 */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        flex-direction: row-reverse; /* 아이콘과 말풍선 위치 반전 */
        background-color: rgba(255, 255, 255, 0.05); /* 배경색 살짝 */
    }
    /* 말풍선 내부 텍스트 우측 정렬 */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) .stMarkdown {
        text-align: right; 
    }
</style>
""", unsafe_allow_html=True)

# --- [2] 도우미 함수 ---
def build_context_string(dialogue_history):
    context_text = ""
    for turn in dialogue_history:
        context_text += f"{turn['speaker']}: {turn['content']}\n"
    return context_text

def reset_conversation():
    # 세션 스테이트의 대화 기록을 비웁니다.
    st.session_state.conversation_log = []
    # 문맥이나 다른 저장소도 필요하다면 여기서 같이 비웁니다.
    st.session_state.full_dialogue_context = []
    
# --- [3] 세션 상태 초기화 (통합된 로그 하나만 사용) ---
if "conversation_log" not in st.session_state:
    st.session_state.conversation_log = [] # 전체 대화 기록 (화면 표시용)

# --- [4] UI: 선수 선택 영역 ---
st.title("사상 토론")
st.caption("두 거인의 사상이 충돌하는 현장을 목격하세요.")

col_left, col_mid, col_right = st.columns([1, 0.1, 1])

player_display_map = {
    AnswerTarget.PASTOR_A: "✝️ 김유진 목사님",
    AnswerTarget.PASTOR_B: "✝️ 정운성 목사님",
    AnswerTarget.BUBRYUNE: "🪷 법륜스님",
    AnswerTarget.NIETZSCHE: "🧔🏻‍♂️ 니체",
}

with col_left:
    left_player = st.selectbox(
        "좌측 선수",
        options=[AnswerTarget.PASTOR_A, AnswerTarget.PASTOR_B, AnswerTarget.BUBRYUNE, AnswerTarget.NIETZSCHE],
        format_func=lambda x: player_display_map[x], 
        key="left_select"
    )

with col_right:
    right_player = st.selectbox(
        "우측 선수",
        options=[AnswerTarget.PASTOR_A, AnswerTarget.PASTOR_B, AnswerTarget.BUBRYUNE, AnswerTarget.NIETZSCHE],
        index=2, 
        format_func=lambda x: player_display_map[x], 
        key="right_select"
    )

# --- [5] 채팅창 디스플레이 (하나의 컨테이너 사용) ---
# 높이를 지정하여 스크롤이 생기게 함
chat_container = st.container(height=500, border=True)

# 기존 대화 기록 출력
with chat_container:
    for msg in st.session_state.conversation_log:
        # role이 'assistant'면 좌측(Left Player), 'user'면 우측(Right Player)로 표시됨
        avatar_icon = left_player.getAvatar() if msg["role"] == "assistant" else right_player.getAvatar()
        
        with st.chat_message(msg["role"], avatar=avatar_icon):
            st.write(msg["content"])

# --- [6] 입력창 및 시작 버튼 ---
col_input, col_btn = st.columns([5, 1], vertical_alignment="bottom")

with col_input:
    initial_topic = st.text_input("토론 주제", placeholder="예: 돈이 많으면 행복한가?", label_visibility="collapsed")

with col_btn:
    start_btn = st.button("대화 시작", type="primary", use_container_width=True, disabled=not initial_topic,on_click=reset_conversation)

conversation_rounds = st.sidebar.slider(
        "대화 턴 수 설정",
        min_value=1,
        max_value=10,
        value=2  # 기본값
    )

# --- [7] 토론 로직 실행 ---
if start_btn:
    # 1. 초기화
    st.session_state.conversation_log = [] # 화면 초기화
    full_dialogue_context = [] # AI에게 줄 문맥용 리스트 (이름, 내용)
    
    # 서비스 로드
    left_service = get_chat_service(left_player)
    right_service = get_chat_service(right_player)

    # ----------------------------------------------------
    # [Round 0] Left Player 선공
    # ----------------------------------------------------
    with chat_container:
        # Left Player는 항상 'assistant' 역할 (왼쪽 배치)
        with st.chat_message("assistant", avatar=left_player.getAvatar()):
            with st.spinner(f"{player_display_map[left_player]} 발언 준비 중..."):
                msg_p1 = left_service.talk_arena(initial_topic, "") # 첫 턴이라 문맥 없음
                st.write_stream(stream_data(msg_p1))
    
    # 기록 저장
    st.session_state.conversation_log.append({"role": "assistant", "content": msg_p1})
    full_dialogue_context.append({"speaker": left_player.value, "content": msg_p1})

    # ----------------------------------------------------
    # [Loop] 티키타카 시작
    # ----------------------------------------------------
    # 슬라이더로 값 받기
    
    for i in range(conversation_rounds):
        
        # === Right Player 턴 (우측) ===
        # Streamlit에서 'user' role을 사용하면 아이콘이 오른쪽에 뜹니다.
        context_str = build_context_string(full_dialogue_context)
        last_msg = full_dialogue_context[-1]["content"]

        with chat_container:
            with st.chat_message("user", avatar=right_player.getAvatar()):
                with st.spinner(f"{player_display_map[right_player]} 반박 준비 중..."):
                    
                    msg_p2 = right_service.talk_arena(
                        topic_or_last_message=last_msg,
                        full_dialogue_context=context_str
                    )
                    st.write_stream(stream_data(msg_p2))
        
        # 기록 저장 ('user' role로 저장)
        st.session_state.conversation_log.append({"role": "user", "content": msg_p2})
        full_dialogue_context.append({"speaker": right_player.value, "content": msg_p2})


        # === Left Player 턴 (좌측) ===
        context_str = build_context_string(full_dialogue_context)
        last_msg = full_dialogue_context[-1]["content"]

        with chat_container:
            with st.chat_message("assistant", avatar=left_player.getAvatar()):
                with st.spinner(f"{player_display_map[left_player]} 재반박 준비 중..."):
                    
                    msg_p1 = left_service.talk_arena(
                        topic_or_last_message=last_msg,
                        full_dialogue_context=context_str
                    )
                    st.write_stream(stream_data(msg_p1))
        
        # 기록 저장 ('assistant' role로 저장)
        st.session_state.conversation_log.append({"role": "assistant", "content": msg_p1})
        full_dialogue_context.append({"speaker": left_player.value, "content": msg_p1})

    st.success("토론이 종료되었습니다.")
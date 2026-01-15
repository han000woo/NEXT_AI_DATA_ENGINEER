import streamlit as st 
from backend.chat_service import get_chat_service
from utils.util import stream_data
from enums.target import TARGET_COLLECTION, AnswerTarget, SermonState

# --- 1. 페이지 설정 및 대상 정의 ---
# 이 페이지의 타겟을 설정합니다. (페이지마다 이 부분을 다르게 설정)
CURRENT_TARGET = AnswerTarget.BUBRYUNE 
# 페이지별 독립된 메시지 저장을 위한 키 생성
SESSION_KEY = f"messages_{CURRENT_TARGET.value}" 

monk = get_chat_service(CURRENT_TARGET)

st.set_page_config(
    page_title="법륜 스님 즉문 즉설",
    page_icon="🧘‍♂️",  # 스님/명상 느낌 아이콘
    layout="wide"
)

st.title("🧘‍♂️ 법륜 스님 즉문즉설")
st.caption(
    "법륜 스님의 지난 유튜브 강의 즉문즉설을 기반으로 사용자의 고민과 마음에 답해드립니다."
)

# --- 2. 사이드바 설정 ---
with st.sidebar:
    st.header("안내")
    st.info(f"{CURRENT_TARGET.value}님의 유튜브 강의 즉문즉설 데이터를 기반으로 답변합니다.")
    
    if st.button("🗑️ 대화 내용 지우기"):
        st.session_state[SESSION_KEY] = [] # 해당 페이지 세션만 삭제
        st.rerun()
        
    st.divider()
    st.markdown("### 💡 상담 팁")
    st.markdown("- 구체적인 상황을 말씀해 주세요.")

# --- 3. 세션 상태 관리 (페이지별 독립 키 사용) ---
if SESSION_KEY not in st.session_state:
    st.session_state[SESSION_KEY] = [
        {
            "role": "assistant",
            "content": (
                f"안녕하세요, {CURRENT_TARGET.value}입니다.\n"
                "오늘도 마음 편안히 하루를 시작하시길 바랍니다.\n"
                "마음속 고민이 있으시면 편하게 말씀해 주세요."
            )
        }
    ]

# --- 4. 채팅 화면 그리기 (공통 루프) ---
for message in st.session_state[SESSION_KEY]:
    avatar = "👤" if message["role"] == "user" else CURRENT_TARGET.getAvatar() #🧘‍♂️
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])
        # 과거 기록에 소스가 있다면 출력
        if "source" in message and message["source"]:
            with st.expander("📖 참고한 설교 말씀 보기"):
                st.caption(f"출처: {message['source']}")

# --- 5. 사용자 입력 처리 ---
if prompt := st.chat_input("여기에 고민을 입력하세요..."):

    # 1) 사용자 메시지 저장 및 즉시 표시
    st.session_state[SESSION_KEY].append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    # 2) AI 답변 생성
    with st.chat_message("assistant", avatar="🪷"):
        with st.spinner("스님의 법문을 찾아보고 있습니다..."):
            # RAG 로직 호출
            response_text, (state, source_text) = monk.get_response(prompt, st.session_state[SESSION_KEY])
            
            # 3) 스트리밍 출력
            st.write_stream(stream_data(response_text))
            
            # 4) 출처 표시 (즉시 보여주기용)
            # print(state)
            if state == SermonState.FOUND:
                # st.success("조건 통과: FOUND 상태입니다.") # 디버깅 완료 후 주석 처리
                with st.expander("참조한 법문 보기"):
                    st.caption(f"출처: {source_text}")
            
            elif state == SermonState.NOT_FOUND:
                # st.error("조건 통과: NOT_FOUND 상태입니다.") # 디버깅 완료 후 주석 처리
                pass

    # 5) AI 메시지 최종 저장 (핵심 수정 부분! 🛠️)
    # 일단 기본 메시지 객체 생성
    message_to_save = {
        "role": "assistant", 
        "content": response_text
    }
    
    # 🚨 중요: state가 FOUND일 때만 'source' 정보를 추가함
    if state == SermonState.FOUND:
        message_to_save["source"] = source_text

    # 저장
    st.session_state[SESSION_KEY].append(message_to_save)
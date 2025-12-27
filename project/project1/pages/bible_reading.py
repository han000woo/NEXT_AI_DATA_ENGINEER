import streamlit as st
from enum import Enum
import time

from enums.target import AnswerTarget

# 실제로는 만드신 get_chat_service를 임포트하세요
# from my_services import get_chat_service 

# (테스트용) 더미 서비스 객체
class MockPastorService:
    def answer(self, question, context):
        time.sleep(1) # 생각하는 척
        return f"성도님, '{context[:10]}...' 말씀에 대해 질문하셨군요. \n\n{question}에 대한 제 생각은 이렇습니다. (RAG 검색 결과)"

def get_chat_service(target):
    return MockPastorService()

# --- [2] 사용자 설정 코드 적용 ---
CURRENT_TARGET = AnswerTarget.PASTOR_B 
SESSION_KEY = f"messages_{CURRENT_TARGET.value}" 
pastor = get_chat_service(CURRENT_TARGET)

st.set_page_config(
    page_title=f"AI {CURRENT_TARGET.value}님 상담소",
    page_icon="🙏",
    layout="wide"
)

st.title(f"🙏{CURRENT_TARGET.value} 성경 읽기")
st.caption(f"{CURRENT_TARGET.value}님의 지난 설교 말씀을 기반으로 성도님의 고민에 답해드립니다.")

st.divider()

# --- [3] 성경 데이터 (실제로는 DB 연동) ---
bible_verses = [
    {"ref": "마태복음 28:18", "text": "예수께서 나아와 말씀하여 이르시되 하늘과 땅의 모든 권세를 내게 주셨으니"},
    {"ref": "마태복음 28:19", "text": "그러므로 너희는 가서 모든 민족을 제자로 삼아 아버지와 아들과 성령의 이름으로 세례를 베풀고"},
    {"ref": "마태복음 28:20", "text": "내가 너희에게 분부한 모든 것을 가르쳐 지키게 하라 볼지어다 내가 세상 끝날까지 너희와 항상 함께 있으리라 하시니라"},
]

# --- [4] 핵심 기능: 팝업 대화창 (@st.dialog) ---
@st.dialog(f"💬 {CURRENT_TARGET.value}님께 여쭤보기")
def open_pastor_chat(verse_ref, verse_text):
    # 팝업 헤더
    st.markdown(f"### 📖 {verse_ref}")
    st.info(f"\"{verse_text}\"")
    st.markdown("---")

    # 이 팝업창 전용 세션 키 생성 (구절마다 채팅 기록 분리 원할 시)
    # 여기서는 팝업을 닫으면 초기화되는 간단한 구조를 사용합니다.
    if "dialog_messages" not in st.session_state:
        st.session_state.dialog_messages = [
            {"role": "assistant", "content": f"반갑습니다. 이 말씀({verse_ref})을 읽으시면서 어떤 점이 마음에 와닿으셨나요?"}
        ]

    # 채팅 기록 출력
    for msg in st.session_state.dialog_messages:
        with st.chat_message(msg["role"], avatar="🧑‍💻" if msg["role"]=="user" else "🙏"):
            st.write(msg["content"])

    # 사용자 입력
    if prompt := st.chat_input("질문을 입력하세요..."):
        # 1. 사용자 메시지 추가
        st.session_state.dialog_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑‍💻"):
            st.write(prompt)

        # 2. AI(목사님) 응답 생성
        with st.chat_message("assistant", avatar="🙏"):
            with st.spinner(f"{CURRENT_TARGET.value}님이 묵상 중입니다..."):
                # 실제 서비스 호출 (컨텍스트로 성경 구절을 함께 넘김)
                response = pastor.answer(question=prompt, context=verse_text)
                st.write(response)
        
        # 3. 응답 저장
        st.session_state.dialog_messages.append({"role": "assistant", "content": response})


# --- [5] 메인 UI: 성경 읽기 리스트 ---
st.subheader("📜 오늘의 말씀 읽기")

for verse in bible_verses:
    # 레이아웃: [본문 텍스트 (넓게)] --- [버튼 (좁게)]
    col_text, col_btn = st.columns([0.85, 0.15])
    
    with col_text:
        st.markdown(f"**[{verse['ref']}]**")
        st.write(verse['text'])
    
    with col_btn:
        # 버튼 수직 중앙 정렬을 위한 빈 공간 (선택사항)
        st.write("") 
        if st.button("목사님께 질문", key=f"btn_{verse['ref']}"):
            # 🚨 중요: 버튼 클릭 시 다이얼로그 함수 호출
            # 클릭할 때마다 채팅 상태 초기화 (새로운 대화 시작)
            if "dialog_messages" in st.session_state:
                del st.session_state.dialog_messages
            open_pastor_chat(verse['ref'], verse['text'])
            
    st.divider() # 구절 사이 구분선
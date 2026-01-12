import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000/generate-by-prompt"

st.set_page_config(page_title="AI Data Generator", layout="wide")
st.title("🤖 AI Log Generator")
st.markdown("데이터 엔지니어링 포트폴리오: **LLM Tool Calling**을 활용한 동적 로그 생성기")

# 채팅 히스토리 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 내용 표시
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# 사용자 입력 받기
if prompt := st.chat_input("어떤 데이터가 필요하신가요? (예: 주식 거래 로그 5개 만들어줘, IoT 센서 데이터 10개 생성해줘)"):
    # 사용자 메시지 표시
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 봇(Backend) 응답 처리
    with st.chat_message("assistant"):
        with st.spinner("LLM이 스키마를 분석하고 데이터를 생성 중입니다..."):
            try:
                response = requests.post(API_URL, json={"prompt": prompt})
                
                if response.status_code == 200:
                    result = response.json()
                    table_name = result.get("table_name", "generated_data")
                    data = result.get("data", [])
                    
                    st.success(f"✅ '{table_name}' 데이터 {len(data)}건 생성 완료!")
                    
                    # 데이터프레임 변환 및 표시
                    df = pd.DataFrame(data)
                    st.dataframe(df, use_container_width=True)
                    
                    # 세션에 기록 (심플하게 텍스트로만)
                    # st.session_state.messages.append({"role": "assistant", "content": f"'{table_name}' 데이터를 생성했습니다."})
                else:
                    st.error(f"Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Failed: {e}")
import streamlit as st 

st.header("3. 시스템 데이터 흐름도")
st.info("사용자의 질문이 MCP 서버와 LLM을 거쳐 어떻게 처리되는지를 보여주는 아키텍처입니다.")

# [1, 2, 1] 비율로 화면을 나눕니다 (좌측여백 : 이미지공간 : 우측여백)
# 이미지가 크다면 [1, 10, 1] 처럼 가운데 비율을 키우세요.
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    st.image("data/project1.png", caption="System Architecture")
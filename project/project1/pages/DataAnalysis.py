import asyncio
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import json
import pandas as pd  # 👈 데이터 처리를 위해 Pandas 추가
from backend.mcp_service import mcp_query_db
from config.mcp_tool import tools_schema
from datetime import datetime
import plotly.express as px  # 👈 Plotly 임포트 추가!

# ... (경로 및 환경변수 설정 기존 동일) ...
BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / ".env"
load_dotenv(CONFIG_PATH)

client = OpenAI()


st.set_page_config(
    page_title="AI 상담 로그 분석",
    layout="wide"  # 차트를 넓게 보기 위해 wide 모드 설정
)

# ==========================================
# [Header] 대시보드 소개 및 요약
# ==========================================
st.title("AI 상담 로그 분석")

st.markdown("""
> **"데이터로 마음을 읽다"** > 이 대시보드는 **MCP(Model Context Protocol)** 기반의 AI 에이전트가 상담 DB를 실시간으로 분석합니다.  
> 복잡한 SQL 쿼리 없이, **자연어**로 질문하면 상담 트렌드, 감정 상태, 키워드 등을 **시각화**하여 보여줍니다.
""")


st.divider() # 구분선

# ==========================================
# [Helper] 차트 그리기 함수
# JSON 데이터를 받아서 적절한 차트를 그립니다.
# ==========================================

def draw_chart(json_data):
    # 1. 데이터 유효성 검사
    if not json_data:
        return

    try:
        # 문자열이면 JSON 파싱
        if isinstance(json_data, str):
            # 디버깅: print(f"[DEBUG] raw: {json_data}")
            data = json.loads(json_data)
        else:
            data = json_data

        # 에러 메시지 처리
        if isinstance(data, dict) and "error" in data:
            st.error(f"서버 에러: {data['error']}")
            return

        # 2. 데이터프레임 변환 및 차트 그리기
        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data)
            
            fig = None # 차트 객체 초기화

            # (1) 감정 분석 (Pie Chart)
            if "emotion" in df.columns:
                st.caption("📊 감정 분포 비율")
                # 도넛 차트 스타일 (hole=0.4)
                fig = px.pie(df, values='count', names='emotion', hole=0.4)
                fig.update_traces(textposition='inside', textinfo='percent+label')
            
            # (2) 멘토 빈도 (Pie Chart)
            elif "mento" in df.columns:
                st.caption("🧑‍🏫 멘토 상담 점유율")
                fig = px.pie(df, values='count', names='mento')
                fig.update_traces(textposition='inside', textinfo='percent+label')
            
            # (3) 키워드 순위 (Pie Chart)
            elif "keyword" in df.columns:
                st.caption("🔑 고민 키워드 비율 (Top 10)")
                # 키워드가 너무 많으면 보기 흉하므로 상위 10개만 자름
                df_top10 = df.head(10) 
                fig = px.pie(df_top10, values='count', names='keyword', hole=0.3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
                # 키워드는 표도 같이 보여주는 게 좋음
                with st.expander("상세 데이터 표 보기"):
                    st.dataframe(df)

            # 3. Streamlit에 차트 출력
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    except json.JSONDecodeError:
        st.warning("데이터 형식이 올바르지 않습니다.")
    except Exception as e:
        st.error(f"차트 그리기 오류: {e}")

# ==========================================
# [FIX 1] 세션 상태 초기화
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []


# ==========================================
# [Main] 채팅 로직
# ==========================================
if user_input := st.chat_input("질문하세요 (예: 이번 달 고민 키워드 차트로 보여줘)"):
    
    # 1. 사용자 메시지 저장 및 표시
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. LLM 호출 준비
    today = datetime.now().strftime("%Y-%m-%d")
    system_msg = {"role": "system", "content": f"당신은 상담 데이터 분석가입니다. 오늘 날짜는 {today}입니다."}
    
    messages_to_send = [system_msg] + st.session_state.messages

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages_to_send,
        tools=tools_schema,
        tool_choice="auto"
    )
    
    response_msg = response.choices[0].message


    # 3. 도구 호출 확인
    if response_msg.tool_calls:
        tool_call = response_msg.tool_calls[0]
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        
        # (1) AI의 의도 저장
        st.session_state.messages.append(response_msg)

        with st.chat_message("assistant"):
            # 진행 상황 표시
            with st.status(f"🛠️ 데이터 분석 중... ({func_name})", expanded=True) as status:
                st.write(f"요청 인자: {func_args}")
                
                # (2) MCP 서버 호출 -> 이제 JSON 문자열이 옴
                tool_result = asyncio.run(mcp_query_db(func_name, func_args))
                
                status.write("✅ 데이터 조회 완료!")
                status.update(label="분석 완료", state="complete", expanded=False)
            
            # 🔥 [핵심] 데이터를 받자마자 차트로 시각화!

            draw_chart(tool_result)

        # (3) 도구 결과(JSON 문자열)를 history에 저장 (LLM 참고용 + 나중에 다시 그리기용)
        st.session_state.messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result
        })

        # (4) 최종 답변 생성 (LLM은 JSON을 보고 요약 멘트를 작성)
        final_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[system_msg] + st.session_state.messages
        )
        final_answer = final_response.choices[0].message.content
        
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        with st.chat_message("assistant"):
            st.write(final_answer)

    else:
        # 일반 대화
        final_answer = response_msg.content
        st.session_state.messages.append({"role": "assistant", "content": final_answer})
        with st.chat_message("assistant"):
            st.write(final_answer)
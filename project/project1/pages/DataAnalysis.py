import asyncio
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st
import json
import pandas as pd
from backend.chat_service import get_chat_service
from backend.mcp_service import mcp_query_db
from config.mcp_tool import tools_schema
from datetime import datetime
import plotly.express as px

from enums.target import AnswerTarget

# -------------------------------------------------------------------------
# 1. 설정 및 초기화
# -------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = BASE_DIR / "config" / ".env"
load_dotenv(CONFIG_PATH)

client = OpenAI()

st.set_page_config(
    page_title="AI 상담 로그 분석",
    layout="wide"
)

# 세션 상태 초기화 (가장 먼저 실행)
if "messages" not in st.session_state:
    st.session_state.messages = []

targets = list(AnswerTarget)
mentors = [get_chat_service(e) for e in targets]
mentor_map = {mentor.author_name: mentor for mentor in mentors}

# -------------------------------------------------------------------------
# 2. Helper 함수: 차트 그리기
# -------------------------------------------------------------------------
def draw_chart(json_data):
    """JSON 데이터를 받아 Pandas DF로 변환 후 Plotly 차트 출력"""
    if not json_data:
        return

    try:
        # 문자열이면 JSON 파싱, 딕셔너리면 그대로 사용
        data = json.loads(json_data) if isinstance(json_data, str) else json_data

        # 에러 메시지 처리
        if isinstance(data, dict) and "error" in data:
            st.error(f"서버 에러: {data['error']}")
            return

        # 리스트 형태의 데이터인 경우 차트 생성
        if isinstance(data, list) and len(data) > 0:
            df = pd.DataFrame(data)
            fig = None 

            # (1) 감정 분석
            if "emotion" in df.columns:
                st.caption("📊 감정 분포 비율")
                fig = px.pie(df, values='count', names='emotion', hole=0.4)
                fig.update_traces(textposition='inside', textinfo='percent+label')
            
            # (2) 멘토 빈도
            elif "mento" in df.columns:
                st.caption("🧑‍🏫 멘토 상담 점유율")
                fig = px.pie(df, values='count', names='mento')
                fig.update_traces(textposition='inside', textinfo='percent+label')
            
            # (3) 키워드 순위
            elif "keyword" in df.columns:
                st.caption("🔑 고민 키워드 비율 (Top 10)")
                df_top10 = df.head(10) 
                fig = px.pie(df_top10, values='count', names='keyword', hole=0.3)
                fig.update_traces(textposition='inside', textinfo='percent+label')
                
                with st.expander("상세 데이터 표 보기"):
                    st.dataframe(df)

            if fig:
                st.plotly_chart(fig, use_container_width=True)

    except (json.JSONDecodeError, TypeError):
        # JSON이 아닌 일반 텍스트가 tool output으로 올 경우 무시하거나 로깅
        pass
    except Exception as e:
        st.error(f"차트 그리기 오류: {e}")

# -------------------------------------------------------------------------
# 3. UI: 헤더 및 멘토 컨트롤
# -------------------------------------------------------------------------
st.markdown(
    """
    <style>
        /* 토스트 컨테이너 크기 조절 */
        div[data-testid="stToast"] {
            width: 50% !important;       /* 가로 너비를 화면의 50%로 설정 (기본값은 고정 픽셀) */
            max-width: 800px !important; /* 최대 너비 제한 */
            padding: 20px !important;    /* 내부 여백을 늘려 시원하게 */
            font-size: 16px !important;  /* 글자 크기도 약간 키움 */
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("AI 상담 로그 분석")
st.markdown("""
    > **"데이터로 마음을 읽다"** > MCP 기반 AI 에이전트가 상담 DB를 실시간 분석합니다. 질문을 던지면 트렌드와 감정을 시각화합니다.
    """)

with st.sidebar:
    selected_mentors = st.multiselect(
        "논평",
        options=list(mentor_map.keys()),
        placeholder="멘토를 선택하세요",
        label_visibility="collapsed"
    )

    if st.button("✨ 멘토 통찰 실행", type="primary", use_container_width=True):
        if selected_mentors:
            target_data = "현재 특별한 데이터가 없습니다. 일반적인 인생 조언을 해주세요."
            
            # 대화 기록 역순 탐색하여 분석 대상 추출
            found_data = False
            for msg in reversed(st.session_state.messages):
                if msg["role"] == "tool":
                    target_data = f"최근 상담 데이터 분석 결과: {msg['content']}"
                    found_data = True
                    break
                elif msg["role"] == "user":
                    target_data = f"사용자 질문: {msg['content']}"
                    found_data = True
                    break
            
            if not found_data:
                st.toast("분석할 대화 내역이 없습니다.", icon="ℹ️")
            
            else:
                with st.spinner("데이터 분석 중..."):
                    for mentor_name in selected_mentors:
                        advice, _ = mentor_map[mentor_name].analysis_data(target_data)
    
                        # 토스트 대신 확장형 박스 사용
                        with st.expander(f"📩 {mentor_name}의 메세지 도착", expanded=True):
                            st.write(advice)
                    # for mentor_name in selected_mentors:
                    #     advice, _ = mentor_map[mentor_name].analysis_data(target_data)
                        
                    #     # [변경 사항]
                    #     # 1. 채팅 기록(session_state)에 저장하는 코드 삭제
                    #     # 2. st.toast로 결과 출력 (icon 옵션 추가로 시각적 효과)
                    #     st.toast(f"{advice}", icon=mentor_map[mentor_name]._get_avartar())
                    #     # show_advice_modal(mentor_name, advice)

st.divider()
for msg in st.session_state.messages:
    # (1) 딕셔너리가 아닌 객체가 섞여있을 경우를 대비한 안전장치 (선택사항이나 권장)
    if not isinstance(msg, dict):
        try:
            msg = msg.model_dump()
        except:
            continue # 변환 안 되면 건너뜀

    # (2) 역할별 출력
    if msg["role"] == "tool":
        with st.chat_message("assistant"):
            draw_chart(msg["content"])
            with st.expander("데이터 원본 보기"):
                st.code(msg["content"], language="json")
    
    elif msg["role"] != "system":
        # ⚠️ 중요: Tool Call 메시지는 content가 None일 수 있음 -> 출력하지 않음
        if msg.get("content"): 
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

# -------------------------------------------------------------------------
# 5. 채팅 로직 (새로운 입력 처리)
# -------------------------------------------------------------------------
if user_input := st.chat_input("질문하세요 (예: 이번 달 고민 키워드 차트로 보여줘)"):
    
    # (1) 사용자 메시지 처리
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # (2) LLM 호출
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

    # (3) 도구 호출 확인
    if response_msg.tool_calls:
        tool_call = response_msg.tool_calls[0]
        func_name = tool_call.function.name
        func_args = json.loads(tool_call.function.arguments)
        
        # 의도 저장 (assistant의 tool call 메시지)
        st.session_state.messages.append(response_msg)

        with st.chat_message("assistant"):
            # 상태 표시
            with st.status(f"데이터 분석 중... ({func_name})", expanded=True) as status:
                st.write(f"요청 인자: {func_args}")
                tool_result = asyncio.run(mcp_query_db(func_name, func_args))
                status.write("✅ 데이터 조회 완료!")
                status.update(label="분석 완료", state="complete", expanded=False)
            
            # 🔥 [즉시 렌더링] 현재 턴의 차트 그리기
            draw_chart(tool_result)

        # 도구 결과 저장
        st.session_state.messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result
        })

        # 최종 답변 생성
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
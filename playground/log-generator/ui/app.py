import streamlit as st
import requests
import pandas as pd

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(page_title="DE Log Builder", layout="wide")

st.title("Log Generator")
st.markdown("데이터 엔지니어링 포트폴리오: **LLM Tool Calling**을 활용한 동적 로그 생성기")


tab1, tab2 =  st.tabs(["스키마 빌더","AI 생성"])

# ui/app.py - TAB 1 Code Update

with tab1:
    # 세션 초기화
    if "custom_columns" not in st.session_state:
        st.session_state.custom_columns = [
            {"name": "created_at", "type": "date", "min_value": "2024-01-01", "max_value": "2024-12-31", "options": []}
        ]

    # [Section 1] 설정 영역 (Configuration)
    st.subheader("Configuration")
    
    col_form, col_list = st.columns([1, 2], gap="large")

    # ---------------------------------------------------------
    # 1-1. 왼쪽: 컬럼 추가 폼 (Input Form)
    # ---------------------------------------------------------
    with col_form:
        with st.container(border=True):
            st.markdown("**Add New Column**")
            
            new_name = st.text_input("Column Name", placeholder="e.g. price, user_id")
            new_type = st.selectbox("Data Type", ["int", "float", "date", "category", "uuid", "string"])

            input_min = None
            input_max = None
            input_options = []

            if new_type in ["int", "float"]:
                c1, c2 = st.columns(2)
                input_min = c1.number_input("Min Value", value=0)
                input_max = c2.number_input("Max Value", value=1000)
                
            elif new_type == "date":
                c1, c2 = st.columns(2)
                d_min = c1.date_input("Start Date", value=pd.to_datetime("2024-01-01"))
                d_max = c2.date_input("End Date", value=pd.to_datetime("2024-12-31"))
                input_min = str(d_min)
                input_max = str(d_max)
                
            elif new_type == "category":
                raw_opts = st.text_area("Options (comma separated)", placeholder="Seoul, Busan, Jeju")
                if raw_opts:
                    input_options = [x.strip() for x in raw_opts.split(",")]

            st.write("")
            if st.button("Add Column", use_container_width=True):
                if not new_name:
                    st.error("Please enter a column name.")
                else:
                    new_col_data = {
                        "name": new_name,
                        "type": new_type,
                        "min_value": input_min,
                        "max_value": input_max,
                        "options": input_options
                    }
                    st.session_state.custom_columns.append(new_col_data)
                    st.rerun()

    # ---------------------------------------------------------
    # 1-2. 오른쪽: 스키마 관리 및 목록 (Load & List)
    # ---------------------------------------------------------
    with col_list:
        # [추가됨] 불러오기 영역
        with st.container(border=True):
            st.markdown("**Load Saved Schema**")
            col_load_sel, col_load_btn = st.columns([3, 1], gap="small")
            
            # API에서 저장된 스키마 목록 가져오기
            try:
                res = requests.get(f"{API_BASE}/schema/list")
                saved_schemas = res.json() if res.status_code == 200 else []
            except:
                saved_schemas = []

            selected_schema_name = None
            with col_load_sel:
                if saved_schemas:
                    schema_options = {s['schema_name']: s for s in saved_schemas}
                    selected_schema_name = st.selectbox(
                        "Select Schema", 
                        list(schema_options.keys()), 
                        label_visibility="collapsed"
                    )
                else:
                    st.selectbox("Select Schema", ["No saved schemas"], disabled=True, label_visibility="collapsed")
            
            with col_load_btn:
                if st.button("Load", use_container_width=True):
                    if selected_schema_name and saved_schemas:
                        # 선택된 스키마 데이터로 세션 덮어쓰기
                        target_schema = schema_options[selected_schema_name]
                        st.session_state.custom_columns = target_schema['columns']
                        st.toast(f"Schema '{selected_schema_name}' loaded successfully.")
                        st.rerun()

        # 현재 스키마 목록 표시 영역
        with st.container(border=True):
            col_header, col_delete = st.columns([4, 1])
            with col_header:
                st.markdown("**Current Schema**")
            with col_delete:
                if st.button("Delete Last", use_container_width=True):
                    if st.session_state.custom_columns:
                        st.session_state.custom_columns.pop()
                        st.rerun()

            if len(st.session_state.custom_columns) > 0:
                display_df = pd.DataFrame(st.session_state.custom_columns)
                
                display_df = display_df.astype(str)
                
                st.dataframe(
                    display_df, 
                    use_container_width=True, 
                    hide_index=True,
                    height=200,
                    column_config={
                        "name": "Name",
                        "type": "Type",
                        "min_value": "Min / Start",
                        "max_value": "Max / End",
                        "options": "Options"
                    }
                )
            else:
                st.markdown("*No columns defined.*")

    st.divider()

    # [Section 2] 실행 및 관리 영역 (Actions)
    st.subheader("Actions")
    
    # 3개의 영역으로 분리: 저장 관리 / 1회성 생성 / 지속 생성(Placeholder)
    col_save, col_batch, col_stream = st.columns([1, 1, 1], gap="medium")

    # 2-1. 스키마 저장 (Save)
    with col_save:
        with st.container(border=True):
            st.markdown("**Save Schema**")
            schema_name_input = st.text_input("Schema Name", value="custom_log_v1")
            if st.button("Save", use_container_width=True):
                payload = {
                    "schema_name": schema_name_input,
                    "columns": st.session_state.custom_columns
                }
                try:
                    res = requests.post(f"{API_BASE}/schema/save", json=payload)
                    if res.status_code == 200:
                        st.toast("Schema saved successfully.")
                    else:
                        st.error(f"Failed: {res.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    # 2-2. 1회성 생성 (Batch Generation)
    with col_batch:
        with st.container(border=True):
            st.markdown("**Batch Generation**")
            gen_count = st.number_input("Batch Count", min_value=1, value=10)
            if st.button("Generate Once", use_container_width=True, type="primary"):
                payload = {
                    "count": gen_count,
                    "config": {
                        "schema_name": schema_name_input,
                        "columns": st.session_state.custom_columns
                    }
                }
                try:
                    res = requests.post(f"{API_BASE}/generate-custom", json=payload)
                    if res.status_code == 200:
                        result = res.json()
                        st.session_state.generated_data = result["data"]
                        st.toast("Data generated successfully.")
                    else:
                        st.error(res.text)
                except Exception as e:
                    st.error(f"Error: {e}")

    # 2-3. [NEW] 지속 생성 (Continuous Stream - Placeholder)
    with col_stream:
        with st.container(border=True):
            st.markdown("**Continuous Generation**")
            interval = st.number_input("Interval (seconds)", min_value=1.0, value=3.0, step=0.5)
            # 아직 구현되지 않았으므로 버튼만 둠
            if st.button("Start Stream", use_container_width=True):
                st.info("Continuous generation feature is currently under development.")

    # [Section 3] 결과 출력 영역
    if "generated_data" in st.session_state:
        st.write("")
        st.markdown("**Generated Results**")
        st.dataframe(
            pd.DataFrame(st.session_state.generated_data),
            use_container_width=True
        )

# ==========================================
# TAB 2: (기존 LLM 기능)
# ==========================================
with tab2:
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
                    response = requests.post(API_BASE + "/generate-by-prompt", json={"prompt": prompt})

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
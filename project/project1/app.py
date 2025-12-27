import streamlit as st

# 페이지 설정
st.set_page_config(page_title="AI Multiverse Counsel", page_icon="🌌", layout="wide")

# --- 내부 페이지 함수 정의 ---

# def login_screen():
#     """로그인 전 보여질 화면"""
#     st.title("🌌 AI Multiverse Counsel")
#     st.write("시공간을 초월한 멘토들과의 대화에 오신 것을 환영합니다.")
#     st.write("현재 인식된 secrets 목록:")

#     try:
#         # 비밀번호가 화면에 노출되니 확인 후 바로 지우세요!
#         print(st.secrets)
#         # st.write(st.secrets["client_id"])
#     except FileNotFoundError:
#         st.error("secrets.toml 파일을 찾을 수 없습니다! 위치를 확인하세요.")
#     except Exception as e:
#         st.error(f"파일은 찾았으나 형식이 잘못되었습니다: {e}")

#     col1, col2 = st.columns([1, 1])
#     with col1:
#         st.header("This app is private.")
#         st.subheader("Please log in to continue.")

#         # Streamlit Native Login (배포 시 작동)
#         if st.button("Log in with Google", icon="🔒", type="primary"):
#             st.login("google")

# def logout_screen():
#     """로그아웃 화면"""
#     st.title("🚪 로그아웃")
#     st.write("상담을 마치시겠습니까?")
#     if st.button("Log out", icon="🔓"):
# st.logout()


def home_dashboard():
    """로그인 후 보여질 메인 로비 (대시보드)"""
    # 사용자 이름 가져오기 (없으면 게스트)
    user_name = st.user.name if st.user.get("name") else "Guest"

    st.title(f"환영합니다, {user_name}님!")
    st.markdown("---")
    st.markdown(
        """
    ### 🌌 상담소 이용 안내
    왼쪽 사이드바에서 원하는 멘토를 선택하여 대화를 시작하세요.
    
    | 카테고리 | 멘토 / 기능 | 특징 |
    | :--- | :--- | :--- |
    | **✝️ Christian** | **정운성 목사님** | 따뜻한 위로와 목회적 조언 |
    | | **김유진 목사님** | 깊이 있는 성경 해석과 통찰 |
    | **☸️ Buddhism** | **법륜스님** | 즉문즉설, 현실적인 깨달음 |
    | **🔥 Philosophy** | **Nietzsche** | 단호하고 본질적인 철학적 질문 |
    | **⚔️ Contents** | **Arena** | 사상과 사상이 부딪히는 토론장 |
    """
    )
    st.info("👈 왼쪽 메뉴를 열어 멘토를 소환하세요!")


# 1. 로그인/로그아웃/홈 (내부 함수 연결)
# login_page = st.Page(login_screen, title="Log in", icon=":material/login:")
# logout_page = st.Page(logout_screen, title="Log out", icon=":material/logout:")
home_page = st.Page(home_dashboard, title="Home", icon=":material/home:", default=True)


pastor_jung = st.Page(
    "pages/PastorJung.py",
    title="정운성 목사님",
    icon=":material/volunteer_activism:",
)
pastor_kim = st.Page(
    "pages/PastorKim.py",
    title="김유진 목사님",
    icon=":material/volunteer_activism:",
)
Nietzsche = st.Page(
    "pages/Nietzsche.py",
    title="Nietzsche",
    icon=":material/psychology:",
)
Bubryune = st.Page(
    "pages/Bubryune.py",
    title="Bubryune",
    icon=":material/temple_buddhist:",
)
Arena = st.Page(
    "pages/Arena.py",
    title="Arena",
    icon=":material/sports_martial_arts:",
)


# is_logged_in = st.user.get("is_logged_in", False)

# if is_logged_in:
#     # [로그인 후]: 메인 대시보드와 각 메뉴 접근 가능
#     pg = st.navigation(
#     {
#         # "Account": [logout_page],
#         "Christian": [pastor_jung, pastor_kim],
#         "Buddhism": [Bubryune],
#         "Philosophy": [Nietzsche],
#         "Contents": [Arena],
#     }
#     )
# else:
#     # [로그인 전]: 로그인 화면만 접근 가능
#     pg = st.navigation([login_page])

pg = st.navigation(
    {
        "Home": [home_page],
        "Christian": [pastor_jung, pastor_kim],
        "Buddhism": [Bubryune],
        "Philosophy": [Nietzsche],
        "Contents": [Arena],
    }
)

pg.run()

import streamlit as st

# 페이지 설정
st.set_page_config(page_title="AI Multiverse Counsel", page_icon="🌌", layout="wide")


# --- (이하 네비게이션 설정 코드는 기존과 동일하게 유지) ---
home_page = st.Page("pages/Home.py", title="Home", icon=":material/home:", default=True)
pastor_jung = st.Page("pages/PastorJung.py", title="정운성 목사님", icon=":material/volunteer_activism:")
pastor_kim = st.Page("pages/PastorKim.py", title="김유진 목사님", icon=":material/volunteer_activism:")
Nietzsche = st.Page("pages/Nietzsche.py", title="Nietzsche", icon=":material/psychology:")
Bubryune = st.Page("pages/Bubryune.py", title="Bubryune", icon=":material/temple_buddhist:")
Arena = st.Page("pages/Arena.py", title="Arena", icon=":material/sports_martial_arts:")
News = st.Page("pages/News.py", title="News", icon=":material/news:")
DataAnalysis = st.Page("pages/DataAnalysis.py", title="데이터 분석", icon=":material/dataset:")
manual1 = st.Page("pages/mannual1.py", title="가상환경구축 메뉴얼", icon=":material/settings:")
manual2 = st.Page("pages/mannual2.py", title="Streamlit 메뉴얼", icon=":material/settings:")
manual3 = st.Page("pages/mannual3.py", title="Diagram", icon=":material/settings:")

pg = st.navigation(
    {
        "Home": [home_page],
        "Christian": [pastor_jung, pastor_kim],
        "Buddhism": [Bubryune],
        "Philosophy": [Nietzsche],
        "Contents": [Arena, News, DataAnalysis],
        "Settings" : [manual1,manual2,manual3]
    }
)

pg.run()
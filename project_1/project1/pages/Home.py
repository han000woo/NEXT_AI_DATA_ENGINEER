import streamlit as st 
# --- 1. CSS 스타일 정의 (Hero + Card 디자인) ---
st.html(
"""
<style>
/* Hero Section Styles */
.hero-wrapper {
    max-width: 900px;
    margin: 0 auto;
    padding: 240px 24px 40px;
    text-align: center;
}
.hero-title {
    font-size: 3.2rem;
    font-weight: 800;
    line-height: 1.2;
    margin-bottom: 48px;
    letter-spacing: -0.02em;
}
.hero-title span {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-subtitle {
    font-size: 1.25rem;
    color: #6b7280;
    line-height: 1.7;
    margin-bottom: 36px;
}
/* Mentor Card Custom Styling */
/* Streamlit의 st.container(border=True)를 타겟팅하여 호버 효과 추가 */
div[data-testid="stVerticalBlockBorderWrapper"] {
    transition: all 0.3s ease;
    border-radius: 16px;
    border: 1px solid #e5e7eb;
    background-color: white; /* 다크모드 대응 필요 시 조정 */
}

/* 마우스 올렸을 때 효과 */
div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    border-color: #6366f1;
}
.mentor-tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 700;
    margin-bottom: 12px;
}

.mentor-quote {
    font-style: italic;
    color: #6b7280;
    font-size: 0.9rem;
    margin-bottom: 16px;
}

@media (max-width: 768px) {
    .hero-title { font-size: 2.4rem; }
    .hero-subtitle { font-size: 1.1rem; }
}
</style>
<div class="hero-wrapper">
    <h1 class="hero-title">
        같은 질문,<br>
        <span>다른 지혜</span>
    </h1>
    <p class="hero-subtitle">
        누구의 관점으로 답을 듣고 싶으신가요?<br>
        오늘 당신의 고민을 들어줄 멘토를 선택하세요.
    </p>
</div>
"""
)
# st.markdown("### 🏛️ 멘토를 선택하세요")
# st.write("") # 간격
# # --- 2. 멘토 카드 섹션 (Grid Layout) ---

# # 첫 번째 줄: 종교 멘토
# col1, col2, col3 = st.columns(3)
# # 1. 정운성 목사님
# with col1:
#     with st.container(border=True):
#         st.markdown('<div class="mentor-tag" style="background:#eff6ff; color:#2563eb;">✝️ 기독교</div>', unsafe_allow_html=True)
#         st.subheader("정운성 목사님")
#         st.markdown('<p class="mentor-quote">"말씀 안에서 길을 찾고, 기도 안에서 위로를 얻으세요."</p>', unsafe_allow_html=True)
#         st.caption("전통적인 성경 해석과 따뜻한 목회적 돌봄을 제공합니다.")
#         st.page_link("pages/PastorJung.py", label="상담 시작하기", icon="🙏", use_container_width=True)
# # 2. 김유진 목사님
# with col2:
#     with st.container(border=True):
#         st.markdown('<div class="mentor-tag" style="background:#eff6ff; color:#2563eb;">✝️ 기독교</div>', unsafe_allow_html=True)
#         st.subheader("김유진 목사님")
#         st.markdown('<p class="mentor-quote">"젊은 날의 고민, 신앙 안에서 새로운 시각으로."</p>', unsafe_allow_html=True)
#         st.caption("현대적인 시각과 청년의 눈높이에서 공감하는 멘토링.")
#         st.page_link("pages/PastorKim.py", label="상담 시작하기", icon="🕊️", use_container_width=True)
# # 3. 법륜스님 (Bubryune)
# with col3:
#     with st.container(border=True):
#         st.markdown('<div class="mentor-tag" style="background:#fff7ed; color:#ea580c;">☸️ 불교</div>', unsafe_allow_html=True)
#         st.subheader("법륜 스님")
#         st.markdown('<p class="mentor-quote">"괴로움은 내 마음이 만드는 것입니다. 지금, 깨어있으세요."</p>', unsafe_allow_html=True)
#         st.caption("즉문즉설의 지혜로 집착을 내려놓고 행복을 찾습니다.")
#         st.page_link("pages/Bubryune.py", label="상담 시작하기", icon="🪷", use_container_width=True)
# st.write("") # 줄 간격
# # 두 번째 줄: 철학 & 시사
# col4, col5, col6 = st.columns(3)
# # 4. 니체 (Nietzsche)
# with col4:
#     with st.container(border=True):
#         st.markdown('<div class="mentor-tag" style="background:#faf5ff; color:#7e22ce;">🔥 철학</div>', unsafe_allow_html=True)
#         st.subheader("Friedrich Nietzsche")
#         st.markdown('<p class="mentor-quote">"신은 죽었다. 이제 당신이 초인(Übermensch)이 될 차례다."</p>', unsafe_allow_html=True)
#         st.caption("기존의 가치에 도전하고 스스로 삶을 창조하는 철학.")
#         st.page_link("pages/Nietzsche.py", label="철학하기", icon="🧠", use_container_width=True)
# # 5. 아레나 (Arena) - 토론장
# with col5:
#     with st.container(border=True):
#         st.markdown('<div class="mentor-tag" style="background:#f3f4f6; color:#374151;">⚔️ 토론</div>', unsafe_allow_html=True)
#         st.subheader("지혜의 아레나")
#         st.markdown('<p class="mentor-quote">"모든 관점이 충돌하며 더 큰 진리를 만듭니다."</p>', unsafe_allow_html=True)
#         st.caption("모든 멘토들이 한 자리에 모여 당신의 질문을 토론합니다.")
#         st.page_link("pages/Arena.py", label="입장하기", icon="🛡️", use_container_width=True)
# # 6. 뉴스 (News)
# with col6:
#     with st.container(border=True):
#         st.markdown('<div class="mentor-tag" style="background:#f0fdf4; color:#16a34a;">📰 시사</div>', unsafe_allow_html=True)
#         st.subheader("뉴스 브리핑")
#         st.markdown('<p class="mentor-quote">"세상의 흐름을 읽고 멘토들의 시선을 더합니다."</p>', unsafe_allow_html=True)
#         st.caption("최신 뉴스를 멘토들의 철학적 관점으로 해석해드립니다.")
#         st.page_link("pages/News.py", label="뉴스 보기", icon="🗞️", use_container_width=True)
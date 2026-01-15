import streamlit as st

st.set_page_config(
    page_title="DevStore",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 1. CSS 커스텀 (개발자 폰트 & 터미널 스타일 적용)
st.markdown("""
    <style>
    /* 폰트: 구글 폰트 Fira Code 적용 */
    @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Fira Code', monospace;
    }
    
    /* 터미널 스타일 박스 */
    .terminal-box {
        background-color: #1E1E1E;
        color: #00FF41; /* 해커 그린 */
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #333;
        font-family: 'Fira Code', monospace;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        margin-bottom: 20px;
    }
    
    /* 카드 스타일 */
    .feature-card {
        background-color: #2D2D2D;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #6C63FF;
        margin-bottom: 10px;
    }
    
    .feature-title {
        font-size: 1.2em;
        font-weight: bold;
        color: #FFFFFF;
    }
    
    /* 깜빡이는 커서 애니메이션 */
    .cursor {
        animation: blink 1s step-end infinite;
    }
    @keyframes blink { 50% { opacity: 0; } }
    </style>
""", unsafe_allow_html=True)

# 2. 헤더 섹션 (IDE 느낌)
col1, col2 = st.columns([3, 1])

with col1:
    st.title("💻 DevStore_")
    st.caption("sudo apt-get install happiness --yes")

with col2:
    # 우측 상단 상태 표시
    st.success("🟢 System Status: Online")

st.divider()

# 3. 터미널 환영 메시지 (HTML/CSS 활용)
st.markdown("""
    <div class="terminal-box">
        <p>$ ssh guest@devstore.com</p>
        <p>$ initializing session... [OK]</p>
        <p>$ load_inventory.py... [OK]</p>
        <br>
        <p>> Hello World! <strong>개발자를 위한 굿즈 샵</strong>에 오신 것을 환영합니다.</p>
        <p>> 버그 없는 하루 되세요! <span class="cursor">_</span></p>
    </div>
""", unsafe_allow_html=True)

# 4. 메뉴 안내 (카드 스타일)
st.subheader("🚀 Quick Navigation")

c1, c2, c3 = st.columns(3)

with c1:
    st.markdown("""
    <div class="feature-card" style="border-left-color: #FFD700;">
        <div class="feature-title">📦 Products</div>
        <p style="color: #ccc; font-size: 0.9em;">
            ./browse_items.sh<br>
            키보드, 후드티, 카페인 등<br>
            코딩 효율을 높여줄 아이템
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Products ➡️"):
        st.switch_page("pages/01_Products.py")

with c2:
    st.markdown("""
    <div class="feature-card" style="border-left-color: #FF5555;">
        <div class="feature-title">🧺 Cart (Buffer)</div>
        <p style="color: #ccc; font-size: 0.9em;">
            ./view_buffer.sh<br>
            임시 저장된 굿즈 확인<br>
            메모리 누수 없이 안전 결제
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Cart ➡️"):
        st.switch_page("pages/02_Cart.py")

with c3:
    st.markdown("""
    <div class="feature-card" style="border-left-color: #4AF626;">
        <div class="feature-title">🔧 Admin (Root)</div>
        <p style="color: #ccc; font-size: 0.9em;">
            sudo ./admin_panel<br>
            새로운 굿즈 등록 및 관리<br>
            (접근 권한 필요)
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Admin ➡️"):
        st.switch_page("pages/03_Admin.py")

st.markdown("---")
st.caption("© 2024 DevStore Inc. All commits reserved. | Powered by Python & Caffeine ☕")
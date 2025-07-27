import streamlit as st
import requests

# Page config
st.set_page_config(
    page_title="YouTube Transcript Summarizer",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

body, .stApp {
    background-color: #ffffff;
    font-family: 'Inter', sans-serif;
    color: #1f2937;
}

.header-container {
    text-align: center;
    padding-top: 2rem;
    padding-bottom: 2rem;
    background: linear-gradient(to bottom, #ffffff 0%, #ffffff 100%);
    border-radius: 20px;
    margin-bottom: 1rem;
}

.header-icon {
    width: 120px;
    height: 120px;
    background: linear-gradient(145deg, #ff0000, #cc0000);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto ;
    box-shadow: 0 8px 20px rgba(255, 0, 0, 0.25);
}

.header-icon svg {
    fill: white;
}

h1 {
    font-size: 2.8rem;
    font-weight: 800;
    margin: 0;
    line-height: 1;
}

.title-black {
    color: #111827;
}

.title-red {
    color: #ef4444;
    margin-top: -0.2rem;
}

.description {
    color: #374151;
    font-size: 1.1rem;
    margin-top: 1rem;
}

.stTextInput > div > div > input {
    background-color: #ffffff !important;
    border: 1.5px solid #e5e7eb !important;
    padding: 0.75rem 1rem;
    font-size: 1rem;
    border-radius: 12px;
    color: #111827 !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
}

/* Fix for placeholder text visibility */
input::placeholder {
    color: #6b7280 !important;
    opacity: 1 !important;
}

/* Button */
.stButton > button {
    background-color: #ef4444 !important;
    color: white !important;
    padding: 0.75rem 1.25rem;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1rem;
    border: none;
    margin-top: 1rem;
}

.stButton > button:hover {
    background-color: #dc2626 !important;
}

/* Success Box */
.success-container {
    background: #f0fdf4;
    border-left: 5px solid #10b981;
    padding: 1rem;
    border-radius: 10px;
    margin-top: 1.5rem;
    color: #065f46;
}

/* Summary Box */
.summary-container {
    background-color: #f9fafb;
    border: 1px solid #e5e7eb;
    padding: 1.5rem;
    border-radius: 16px;
    margin-top: 1.5rem;
    color: #111827;
}

.topic-title {
    font-weight: 600;
    font-size: 1.25rem;
    color: #ef4444;
    margin-bottom: 1rem;
}

.summary-text {
    font-size: 1rem;
    line-height: 1.6;
}

/* Footer */
.footer {
    margin-top: 3rem;
    text-align: center;
    color: #6b7280;
    font-size: 0.85rem;
}

/* Hide branding */
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ✅ HEADER SECTION

st.markdown("""
<div class="header-container">
    <div class="header-icon">
        <svg width="70" height="70" viewBox="0 0 24 24" fill="white">
            <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
        </svg>
    </div>
    <h1 style="
        margin: 0;
        font-size: 4rem;
        font-weight: 800;
        color: #111827;
        line-height: 1.1;
    ">YouTube Transcript</h1>
    <h1 style="
        margin: -2.4rem 0 0;
        font-size: 4rem;
        font-weight: 800;
        color: #ef4444;
        line-height: 1;
    ">Summarizer</h1>
    <p style="font-size: 1.5rem;color: #000000; "class="description">Transform any YouTube video into a concise, intelligent summary </p>
</div>
""", unsafe_allow_html=True)
# ✅ INPUT SECTION
st.markdown("#### YouTube Video URL")
youtube_url = st.text_input("YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...", label_visibility="collapsed")

# ✅ BUTTON & LOGIC
if st.button("✨ Summarize Video"):
    if not youtube_url:
        st.warning("⚠️ Please enter a valid YouTube URL.")
    else:
        with st.spinner("🔄 Analyzing video content..."):
            try:
                response = requests.get("https://youtubesummarizer-backend.onrender.com/summarize", params={"url": youtube_url})
                if response.status_code == 200:
                    data = response.json()
                    st.markdown("""<div class="success-container">✅ <strong>Summary Generated Successfully!</strong></div>""", unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="summary-container">
                        <div class="topic-title">📌 Topic: {data.get('topic_name', 'Unknown')}</div>
                        <div class="summary-text">{data.get('topic_summary', '').replace(chr(10), '<br>')}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error(f"❌ Error: {response.json().get('error', 'Unknown error occurred')}")
            except requests.exceptions.ConnectionError:
                st.error("🚨 Backend server not reachable at `localhost:8000`.")
            except Exception as e:
                st.error(f"🚨 Unexpected error: {str(e)}")

# ✅ FOOTER
st.markdown("""<div class="footer">© 2025 • Streamlit App by Kalam</div>""", unsafe_allow_html=True)

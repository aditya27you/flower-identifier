import streamlit as st
from utils import analyze_flower
from PIL import Image
import io
import datetime

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌸 Flower AI Identifier",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=DM+Sans:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Playfair Display', serif !important;
    }

    .stApp {
        background: linear-gradient(135deg, #0d1117 0%, #1a1f2e 50%, #0d1117 100%);
        color: #e8e3d5;
    }

    .main-title {
        text-align: center;
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #f9c784, #e8845a, #c95b8a);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        text-align: center;
        color: #8a8a9a;
        font-size: 0.95rem;
        margin-bottom: 2rem;
        font-weight: 300;
        letter-spacing: 0.05em;
    }

    .result-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border: 1px solid rgba(249, 199, 132, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 0.8rem 0;
        backdrop-filter: blur(10px);
    }

    .flower-name {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        color: #f9c784;
        margin: 0;
    }

    .scientific-name {
        font-style: italic;
        color: #8a8a9a;
        font-size: 1rem;
        margin-top: 0.2rem;
    }

    .section-label {
        font-size: 0.75rem;
        font-weight: 500;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        color: #c95b8a;
        margin-bottom: 0.4rem;
    }

    .section-content {
        color: #d4cfc4;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    .pred-bar-container {
        margin: 0.4rem 0;
    }

    .pred-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.85rem;
        color: #d4cfc4;
        margin-bottom: 0.2rem;
    }

    .history-item {
        background: rgba(255,255,255,0.03);
        border-left: 3px solid #c95b8a;
        padding: 0.6rem 0.8rem;
        margin: 0.4rem 0;
        border-radius: 0 8px 8px 0;
        font-size: 0.85rem;
        color: #a0a0b0;
    }

    div[data-testid="stButton"] > button {
        background: linear-gradient(135deg, #e8845a, #c95b8a);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 2rem;
        font-family: 'DM Sans', sans-serif;
        font-weight: 500;
        font-size: 1rem;
        width: 100%;
        transition: all 0.3s ease;
        cursor: pointer;
    }

    div[data-testid="stButton"] > button:hover {
        opacity: 0.9;
        transform: translateY(-1px);
    }

    .stProgress > div > div {
        background: linear-gradient(90deg, #f9c784, #c95b8a) !important;
    }

    .stDownloadButton > button {
        background: rgba(255,255,255,0.06) !important;
        color: #d4cfc4 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 8px !important;
        width: 100% !important;
    }

    div[data-testid="stCameraInput"] label {
        color: #8a8a9a !important;
    }

    .feedback-btn > button {
        width: 48%;
    }

    hr {
        border-color: rgba(255,255,255,0.08);
        margin: 1.5rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─── Session State Init ──────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ─── Header ─────────────────────────────────────────────────────────────────
st.markdown('<div class="main-title">🌸 Flower AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Point your camera at any flower — AI identifies it instantly</div>',
    unsafe_allow_html=True,
)

# ─── Input: Camera OR Upload ─────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📷 Live Camera", "📁 Upload Image"])

img_bytes = None
img_display = None

with tab1:
    cam_img = st.camera_input("Take a photo of a flower")
    if cam_img:
        img_bytes = cam_img.read()
        img_display = cam_img

with tab2:
    upload = st.file_uploader("Upload a flower image", type=["jpg", "jpeg", "png", "webp"])
    if upload:
        img_bytes = upload.read()
        img_display = upload

# ─── Identify Button ─────────────────────────────────────────────────────────
if img_bytes:
    st.image(img_display, caption="Your flower image", use_container_width=True)

    if st.button("🔍 Identify Flower"):
        with st.spinner("Analyzing with AI... 🌼"):
            result = analyze_flower(img_bytes)
            st.session_state.last_result = result

            # Add to history
            if result["name"] not in ["Error", "Unknown"]:
                st.session_state.history.append(
                    {
                        "name": result["name"],
                        "scientific": result["scientific_name"],
                        "time": datetime.datetime.now().strftime("%H:%M"),
                    }
                )

# ─── Results ─────────────────────────────────────────────────────────────────
if st.session_state.last_result:
    r = st.session_state.last_result

    if r["error"]:
        st.error(f"❌ {r['error']}")
    else:
        st.success("✅ Flower Identified!")

        # Flower Name Card
        st.markdown(
            f"""
            <div class="result-card">
                <div class="flower-name">{r['name']}</div>
                <div class="scientific-name">{r['scientific_name']}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Top Predictions
        st.markdown("---")
        st.markdown('<div class="section-label">🎯 Top Predictions</div>', unsafe_allow_html=True)
        for pred in r["predictions"][:3]:
            conf = pred["confidence"] / 100
            st.markdown(
                f'<div class="pred-label"><span>{pred["name"]}</span><span><b>{pred["confidence"]}%</b></span></div>',
                unsafe_allow_html=True,
            )
            st.progress(conf)

        st.markdown("---")

        # Details in 2 columns
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-label">🌱 Soil Requirements</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="section-content">{r["soil"]}</div>', unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-label">🌿 Uses</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="section-content">{r["uses"]}</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="section-label">✂️ Care Tips</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="section-content">{r["care_tips"]}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # AI Explanation
        st.markdown('<div class="section-label">🤖 AI Explanation</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="result-card"><div class="section-content">{r["explanation"]}</div></div>',
            unsafe_allow_html=True,
        )

        # Feedback
        st.markdown("---")
        st.markdown('<div class="section-label">👍 Was this correct?</div>', unsafe_allow_html=True)
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            if st.button("✅ Yes, correct!"):
                st.toast("Thanks for the feedback! 🌸")
        with fcol2:
            if st.button("❌ No, wrong"):
                st.toast("Sorry! Try a clearer photo 📷")

        # Download
        st.markdown("---")
        report = f"""🌸 FLOWER AI REPORT
========================
Name: {r['name']}
Scientific Name: {r['scientific_name']}

TOP PREDICTIONS:
{chr(10).join([f"  {i+1}. {p['name']} - {p['confidence']}%" for i, p in enumerate(r['predictions'][:3])])}

SOIL: {r['soil']}

USES: {r['uses']}

CARE TIPS: {r['care_tips']}

AI EXPLANATION:
{r['explanation']}

========================
Generated by Flower AI | {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
"""
        st.download_button("⬇️ Download Full Report", report, file_name="flower_report.txt")

# ─── History Sidebar ──────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("---")
    st.markdown('<div class="section-label">🕘 Recent Identifications</div>', unsafe_allow_html=True)
    for item in reversed(st.session_state.history[-5:]):
        st.markdown(
            f'<div class="history-item">🌸 <b>{item["name"]}</b> <i style="color:#666">({item["scientific"]})</i> — {item["time"]}</div>',
            unsafe_allow_html=True,
        )

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center; margin-top:3rem; color:#444; font-size:0.8rem;">
        Powered by Google Gemini Vision API &nbsp;|&nbsp; Built with Streamlit
    </div>
    """,
    unsafe_allow_html=True,
)

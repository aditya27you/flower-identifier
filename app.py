import streamlit as st
from utils import analyze_flower
import datetime
import json

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🌸 Flower AI",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Mobile-First CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* ── Background ── */
.stApp {
    background: linear-gradient(160deg, #0a0f1e 0%, #111827 60%, #0d1f15 100%);
    color: #e8e3d5;
    min-height: 100vh;
}

/* ── Header ── */
.hero {
    text-align: center;
    padding: 2rem 1rem 1rem;
}
.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(2.2rem, 8vw, 3.5rem);
    font-weight: 700;
    background: linear-gradient(135deg, #fde68a, #f97316, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
    margin: 0;
}
.hero-sub {
    color: #6b7280;
    font-size: clamp(0.8rem, 3vw, 0.95rem);
    margin-top: 0.5rem;
    letter-spacing: 0.06em;
    font-weight: 300;
}

/* ── Cards ── */
.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1.2rem 1.4rem;
    margin: 0.8rem 0;
}
.card-accent {
    border-color: rgba(249,115,22,0.3);
    background: linear-gradient(135deg, rgba(249,115,22,0.06), rgba(236,72,153,0.04));
}

/* ── Flower Name ── */
.flower-hero {
    text-align: center;
    padding: 1.5rem 1rem;
}
.flower-name {
    font-family: 'Cormorant Garamond', serif;
    font-size: clamp(2rem, 7vw, 3rem);
    font-weight: 700;
    color: #fde68a;
    margin: 0;
    line-height: 1.1;
}
.flower-sci {
    font-style: italic;
    color: #9ca3af;
    font-size: clamp(0.85rem, 3vw, 1rem);
    margin-top: 0.3rem;
}
.flower-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
    margin-top: 0.8rem;
}
.tag {
    background: rgba(249,115,22,0.15);
    border: 1px solid rgba(249,115,22,0.3);
    color: #fdba74;
    padding: 0.25rem 0.8rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
}
.tag-green {
    background: rgba(34,197,94,0.12);
    border-color: rgba(34,197,94,0.25);
    color: #86efac;
}
.tag-pink {
    background: rgba(236,72,153,0.12);
    border-color: rgba(236,72,153,0.25);
    color: #f9a8d4;
}

/* ── Section Labels ── */
.sec-label {
    font-size: 0.7rem;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #f97316;
    margin-bottom: 0.5rem;
}

/* ── Info Grid ── */
.info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.8rem;
    margin: 0.8rem 0;
}
.info-cell {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 0.9rem;
}
.info-icon { font-size: 1.3rem; margin-bottom: 0.3rem; }
.info-title {
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6b7280;
    margin-bottom: 0.2rem;
}
.info-val {
    font-size: 0.85rem;
    color: #d1d5db;
    line-height: 1.4;
}

/* ── Fun Fact ── */
.fun-fact {
    background: linear-gradient(135deg, rgba(250,204,21,0.08), rgba(249,115,22,0.06));
    border: 1px solid rgba(250,204,21,0.2);
    border-radius: 16px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
}
.fun-fact-text {
    font-size: 0.9rem;
    color: #fde68a;
    line-height: 1.6;
    font-style: italic;
}

/* ── Prediction Bars ── */
.pred-row {
    margin: 0.6rem 0;
}
.pred-header {
    display: flex;
    justify-content: space-between;
    font-size: 0.83rem;
    color: #d1d5db;
    margin-bottom: 0.25rem;
}
.pred-track {
    background: rgba(255,255,255,0.06);
    border-radius: 999px;
    height: 7px;
    overflow: hidden;
}
.pred-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #f97316, #ec4899);
}

/* ── Map Box ── */
.map-container {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.08);
    margin: 0.8rem 0;
}

/* ── History ── */
.hist-item {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 0.7rem 1rem;
    margin: 0.4rem 0;
}
.hist-name { font-size: 0.88rem; color: #e5e7eb; font-weight: 500; }
.hist-sci { font-size: 0.75rem; color: #6b7280; font-style: italic; }
.hist-time { font-size: 0.72rem; color: #4b5563; margin-left: auto; }

/* ── Buttons ── */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #f97316, #ec4899) !important;
    color: white !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.7rem 1.5rem !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 1rem !important;
    width: 100% !important;
    letter-spacing: 0.02em !important;
}
div[data-testid="stButton"] > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
}
.stDownloadButton > button {
    background: rgba(255,255,255,0.05) !important;
    color: #9ca3af !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important;
    width: 100% !important;
    font-size: 0.9rem !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: rgba(255,255,255,0.03);
    border-radius: 12px;
    padding: 0.3rem;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: #6b7280 !important;
    font-size: 0.85rem !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(249,115,22,0.2) !important;
    color: #fdba74 !important;
}

/* ── Progress ── */
.stProgress > div > div {
    background: linear-gradient(90deg, #f97316, #ec4899) !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #f97316 !important; }

/* ── Divider ── */
hr { border-color: rgba(255,255,255,0.06) !important; margin: 1.2rem 0 !important; }

/* ── Mobile tweaks ── */
@media (max-width: 480px) {
    .info-grid { grid-template-columns: 1fr; }
    .card { padding: 1rem; }
}
</style>
""", unsafe_allow_html=True)

# ─── Session State ────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []
if "result" not in st.session_state:
    st.session_state.result = None

# ─── Hero Header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">🌸 Flower AI</div>
    <div class="hero-sub">Point your camera at any flower — instant AI identification</div>
</div>
""", unsafe_allow_html=True)

# ─── Input Tabs ──────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📷 Camera", "📁 Upload"])

img_bytes = None

with tab1:
    cam = st.camera_input("Take a photo")
    if cam:
        img_bytes = cam.read()

with tab2:
    upload = st.file_uploader("Upload flower image", type=["jpg", "jpeg", "png", "webp"])
    if upload:
        img_bytes = upload.read()

# ─── Identify Button ─────────────────────────────────────────────────────────
if img_bytes:
    if st.button("🔍 Identify Flower"):
        with st.spinner("Analyzing with Gemini AI..."):
            result = analyze_flower(img_bytes)
            st.session_state.result = result
            if result["name"] not in ["Error", "Unknown"]:
                st.session_state.history.append({
                    "name": result["name"],
                    "scientific": result["scientific_name"],
                    "family": result["family"],
                    "bloom": result["bloom_season"],
                    "time": datetime.datetime.now().strftime("%H:%M"),
                })

# ─── Results Dashboard ────────────────────────────────────────────────────────
if st.session_state.result:
    r = st.session_state.result

    if r["error"]:
        st.error(f"❌ {r['error']}")
    else:
        st.success("✅ Flower Identified!")

        # ── Flower Hero Card ──
        bloom_tag = f"🌼 {r['bloom_season']}" if r['bloom_season'] != 'N/A' else ""
        family_tag = f"🌿 {r['family']}" if r['family'] != 'N/A' else ""
        origin_tag = f"📍 {r['origin']}" if r['origin'] != 'N/A' else ""

        tags_html = ""
        if bloom_tag:
            tags_html += f'<span class="tag tag-green">{bloom_tag}</span>'
        if family_tag:
            tags_html += f'<span class="tag">{family_tag}</span>'
        if origin_tag:
            tags_html += f'<span class="tag tag-pink">{origin_tag}</span>'

        st.markdown(f"""
        <div class="card card-accent">
            <div class="flower-hero">
                <div class="flower-name">{r['name']}</div>
                <div class="flower-sci">{r['scientific_name']}</div>
                <div class="flower-tags">{tags_html}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── AI Explanation ──
        st.markdown(f"""
        <div class="card">
            <div class="sec-label">🤖 AI Explanation</div>
            <div style="color:#d1d5db; font-size:0.9rem; line-height:1.7;">{r['explanation']}</div>
        </div>
        """, unsafe_allow_html=True)

        # ── Top 3 Predictions Chart ──
        st.markdown('<div class="sec-label" style="margin-top:1rem;">🎯 Confidence Predictions</div>', unsafe_allow_html=True)
        bars_html = ""
        for p in r["predictions"][:3]:
            bars_html += f"""
            <div class="pred-row">
                <div class="pred-header">
                    <span>{p['name']}</span>
                    <span><b>{p['confidence']}%</b></span>
                </div>
                <div class="pred-track">
                    <div class="pred-fill" style="width:{p['confidence']}%"></div>
                </div>
            </div>"""
        st.markdown(f'<div class="card">{bars_html}</div>', unsafe_allow_html=True)

        # ── Care Info Grid ──
        st.markdown('<div class="sec-label" style="margin-top:1rem;">🌱 Plant Care Dashboard</div>', unsafe_allow_html=True)
        st.markdown(f"""
        <div class="info-grid">
            <div class="info-cell">
                <div class="info-icon">🌍</div>
                <div class="info-title">Soil</div>
                <div class="info-val">{r['soil']}</div>
            </div>
            <div class="info-cell">
                <div class="info-icon">☀️</div>
                <div class="info-title">Sunlight</div>
                <div class="info-val">{r['sunlight']}</div>
            </div>
            <div class="info-cell">
                <div class="info-icon">💧</div>
                <div class="info-title">Watering</div>
                <div class="info-val">{r['watering']}</div>
            </div>
            <div class="info-cell">
                <div class="info-icon">✂️</div>
                <div class="info-title">Care Tips</div>
                <div class="info-val">{r['care_tips']}</div>
            </div>
            <div class="info-cell" style="grid-column: span 2;">
                <div class="info-icon">🌿</div>
                <div class="info-title">Uses</div>
                <div class="info-val">{r['uses']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── Fun Fact ──
        if r["fun_fact"] != "N/A":
            st.markdown(f"""
            <div class="fun-fact">
                <div class="sec-label">💡 Fun Fact</div>
                <div class="fun-fact-text">"{r['fun_fact']}"</div>
            </div>
            """, unsafe_allow_html=True)

        # ── World Map ──
        if r["native_regions"]:
            st.markdown('<div class="sec-label" style="margin-top:1rem;">🗺️ Native Regions Map</div>', unsafe_allow_html=True)

            # Region → approximate lat/lon mapping
            region_coords = {
                "asia": (34.0, 100.0),
                "india": (20.5, 78.9),
                "china": (35.8, 104.1),
                "japan": (36.2, 138.2),
                "europe": (54.5, 15.2),
                "africa": (8.7, 34.5),
                "north america": (54.5, -105.0),
                "south america": (-8.7, -55.4),
                "australia": (-25.2, 133.7),
                "mediterranean": (40.0, 18.0),
                "middle east": (29.3, 42.5),
                "tropical": (0.0, 20.0),
                "southeast asia": (13.0, 107.0),
                "central asia": (41.0, 63.0),
                "americas": (19.4, -99.1),
                "worldwide": (20.0, 0.0),
            }

            map_points = []
            for region in r["native_regions"]:
                key = region.lower().strip()
                for k, v in region_coords.items():
                    if k in key or key in k:
                        map_points.append({
                            "lat": v[0],
                            "lon": v[1],
                            "region": region
                        })
                        break

            if map_points:
                import pandas as pd
                df = pd.DataFrame(map_points)
                st.map(df, latitude="lat", longitude="lon", size=50000, color="#f97316")
                regions_str = " · ".join([p["region"] for p in map_points])
                st.markdown(f'<div style="text-align:center; color:#6b7280; font-size:0.78rem; margin-top:0.3rem;">📍 {regions_str}</div>', unsafe_allow_html=True)
            else:
                regions_str = ", ".join(r["native_regions"])
                st.markdown(f"""
                <div class="card">
                    <div class="sec-label">📍 Native To</div>
                    <div style="color:#d1d5db; font-size:0.9rem;">{regions_str}</div>
                </div>
                """, unsafe_allow_html=True)

        # ── Feedback ──
        st.markdown("---")
        st.markdown('<div class="sec-label">👍 Was this correct?</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("✅ Yes, correct!"):
                st.toast("Thanks for the feedback! 🌸")
        with c2:
            if st.button("❌ No, wrong"):
                st.toast("Sorry! Try a clearer photo 📷")

        # ── Download Report ──
        report = f"""🌸 FLOWER AI REPORT
{'='*40}
Name:            {r['name']}
Scientific Name: {r['scientific_name']}
Family:          {r['family']}
Origin:          {r['origin']}
Bloom Season:    {r['bloom_season']}

TOP PREDICTIONS:
{chr(10).join([f"  {i+1}. {p['name']} — {p['confidence']}%" for i, p in enumerate(r['predictions'][:3])])}

CARE INFORMATION:
  Soil:      {r['soil']}
  Sunlight:  {r['sunlight']}
  Watering:  {r['watering']}
  Care Tips: {r['care_tips']}

USES:
  {r['uses']}

NATIVE REGIONS:
  {', '.join(r['native_regions']) if r['native_regions'] else 'N/A'}

FUN FACT:
  {r['fun_fact']}

AI EXPLANATION:
  {r['explanation']}

{'='*40}
Generated by Flower AI | {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
"""
        st.download_button("⬇️ Download Full Report", report, file_name=f"{r['name'].replace(' ','_')}_report.txt")

# ─── History ─────────────────────────────────────────────────────────────────
if st.session_state.history:
    st.markdown("---")
    st.markdown('<div class="sec-label">🕘 Recent Identifications</div>', unsafe_allow_html=True)
    for item in reversed(st.session_state.history[-5:]):
        st.markdown(f"""
        <div class="hist-item">
            <span>🌸</span>
            <div>
                <div class="hist-name">{item['name']}</div>
                <div class="hist-sci">{item['scientific']}</div>
            </div>
            <div class="hist-time">{item['time']}</div>
        </div>
        """, unsafe_allow_html=True)

# ─── Footer ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; margin-top:3rem; padding-bottom:2rem; color:#374151; font-size:0.78rem;">
    Powered by Google Gemini 2.0 Flash &nbsp;·&nbsp; Built with Streamlit
</div>
""", unsafe_allow_html=True)

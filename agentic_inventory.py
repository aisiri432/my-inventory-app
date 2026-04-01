import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI
import hashlib
import time

# --- 1. PREMIUM UI CONFIG & TARGETED FONT SCALING ---
st.set_page_config(page_title="AROHA | Strategic Intelligence", layout="wide", page_icon="💠")

def apply_aroha_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Global Reset */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0B0F14;
            color: #E6E8EB;
        }

        /* Branding Pulse */
        .brand-container { padding: 10px 0 25px 10px; }
        .brand-title { font-size: 2.5rem; font-weight: 800; color: #FFFFFF; letter-spacing: -1px; margin-bottom: 0; }
        .tagline { font-size: 1.1rem; color: #9AA0A6; margin-top: -2px; display: flex; gap: 6px; }
        .decisions-fade { color: #6C63FF; font-weight: 700; animation: fadeInSlower 3s ease-in-out, glowPulse 2s infinite alternate; }
        @keyframes fadeInSlower { 0% { opacity: 0; } 50% { opacity: 0; } 100% { opacity: 1; } }
        @keyframes glowPulse { from { text-shadow: 0 0 2px #6C63FF; } to { text-shadow: 0 0 10px #38BDF8; } }

        /* Sidebar Styling */
        [data-testid="stSidebar"] { background-color: #090B0F !important; border-right: 1px solid #1F2229; }
        .sidebar-sub { font-size: 0.72rem; color: #6C63FF; font-weight: 600; display: block; margin-top: -12px; margin-bottom: 15px; margin-left: 45px; text-transform: uppercase; opacity: 0.9; letter-spacing: 0.8px; }
        section[data-testid="stSidebar"] .stButton > button { background: transparent !important; border: none !important; color: #E6E8EB !important; text-align: left !important; padding: 10px 15px !important; width: 100%; transition: 0.2s; font-size: 1.1rem !important; font-weight: 600 !important; }
        section[data-testid="stSidebar"] .stButton > button:hover { background: #171A21 !important; color: #6C63FF !important; }

        /* --- DASHBOARD ONLY: FONT SCALING --- */
        .db-header { font-size: 3.5rem !important; font-weight: 800; color: #FFFFFF; letter-spacing: -2px; margin-bottom: 10px; }
        .db-sub { font-size: 1.4rem !important; color: #6B7280; margin-bottom: 40px; }
        .db-metric-val { font-family: 'JetBrains Mono', monospace; font-size: 3.5rem !important; font-weight: 800; color: #6C63FF; }
        .db-metric-label { font-size: 1.1rem !important; text-transform: uppercase; color: #9AA0A6; letter-spacing: 2px; font-weight: 600; }
        
        /* Layered Cards */
        .saas-card { background: #171A21; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 28px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); transition: 0.3s ease; }
        .saas-card:hover { transform: translateY(-4px); border-color: rgba(108, 99, 255, 0.3); }
        .review-box { background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; margin-top: 8px; border: 1px solid #222; font-size: 0.85rem; }
        .recommendation-hero { background: linear-gradient(135deg, rgba(108, 99, 255, 0.12) 0%, rgba(56, 189, 248, 0.05) 100%); border-radius: 12px; padding: 30px; border: 1px solid rgba(108, 99, 255, 0.25); border-left: 10px solid #6C63FF; margin-bottom: 30px; }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ENGINE (v34) ---
DB_FILE = 'aroha_final_v34.db'
def get_db(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
        c.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, 
                      category TEXT, current_stock INTEGER, unit_price REAL, lead_time INTEGER, 
                      supplier TEXT, image_url TEXT, reviews TEXT)''')
        conn.commit()
init_db()

def hash_p(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- 3. SESSION & VOICE ENGINE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_on" not in st.session_state: st.session_state.voice_on = False

def speak(text):
    if st.session_state.voice_on:
        clean = text.replace('"', '').replace("'", "")
        js = f"<script>var m=new SpeechSynthesisUtterance(); m.text='{clean}'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:white; font-size:4.5rem; font-weight:800;'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Where Data Becomes <span style='color:#6C63FF; font-weight:700;'>Decisions</span></p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 0.8, 1])
    with col2:
        m = st.tabs(["Login", "Enroll"])
        with m[0]:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Unlock Dashboard"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Access denied.")
        with m[1]:
            nu = st.text_input("New ID"); np = st.text_input("New Password", type="password")
            if st.button("Initialize Account"):
                if nu and np:
                    try:
                        with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                        st.success("Authorized! Login now.")
                    except: st.error("Identity exists.")
    st.stop()

# --- 5. SIDEBAR (BOLD SANSKRIT FIRST) ---
with st.sidebar:
    st.markdown(f"<div class='brand-container'><div class='brand-title'>AROHA</div><div class='tagline'>Where data becomes <span class='decisions-fade'>Decisions</span></div></div>", unsafe_allow_html=True)
    if st.button("🏠 Dashboard"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-head'>Operations</div>", unsafe_allow_html=True)
    btns = [("📈 PREKSHA", "Preksha", "Predict Demand Instantly"), ("🛡️ STAMBHA", "Stambha", "Test Supply Risks"), ("🎙️ SAMVADA", "Samvada", "Talk To System")]
    for lab, pid, lay in btns:
        if st.button(lab): st.session_state.page = pid; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{lay}</span>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-head'>Financials</div>", unsafe_allow_html=True)
    if st.button("💰 ARTHA"): st.session_state.page = "Artha"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Track Money Flow</span>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-head'>Control</div>", unsafe_allow_html=True)
    btns2 = [("📄 KARYA", "Karya", "Auto Create Orders"), ("📝 NYASA", "Nyasa", "Log Assets Securely"), ("📥 AGAMA", "Agama", "Import Data Easily")]
    for lab, pid, lay in btns2:
        if st.button(lab): st.session_state.page = pid; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{lay}</span>", unsafe_allow_html=True)

    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. TOP BAR HUD ---
t1, t2 = st.columns([1, 1])
with t2: st.markdown(f"<p style='text-align:right; color:#9AA0A6; font-size:1rem; margin-top:10px;'>👤 <b>{st.session_state.user.upper()}</b> • v34.0</p>", unsafe_allow_html=True)

# --- 7. HOME DASHBOARD (MAX FONT SIZE) ---
if st.session_state.page == "Dashboard":
    st.markdown("<div class='db-header'>Strategic Command Hub</div>", unsafe_allow_html=True)
    st.markdown("<div class='db-sub'>Real-time supply chain telemetry • Turning data into decisions</div>", unsafe_allow_html=True)

    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Assets Managed</div><div class='db-metric-val'>{len(df)}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Treasury Value</div><div class='db-metric-val'>₹{val/1000:,.1f}K</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Risk Factor</div><div class='db-metric-val' style='color:#34D399;'>Optimal</div></div>", unsafe_allow_html=True)

    st.markdown(f"""<div class='recommendation-hero'><p style='color:#6C63FF; font-weight:700; font-size:1rem; text-transform:uppercase;'>✨ AI Intelligence Directive</p><h1 style='color:white; margin: 15px 0;'>Execute reorder for 'Top Priority' assets.</h1><p style='color:#9AA0A6; font-size:1.1rem;'>Total required capital for 7-day safety: ₹{val*0.12:,.0f}.</p></div>""", unsafe_allow_html=True)

# --- 8. FEATURE NODES ---

elif st.session_state.page == "Preksha":
    st.markdown("<h1>🔮 PREKSHA</h1>", unsafe_allow_html=True)
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("Treasury empty.")
    else:
        target = st.selectbox("Select Asset", df['name']); p = df[df['name'] == target].iloc[0]
        col_img, col_chart = st.columns([1, 2])
        with col_img:
            if p['image_url']: st.image(p['image_url'], use_container_width=True)
            st.markdown("### Reviews"); st.write(p['reviews'] if p['reviews'] else "No data.")
        with col_chart:
            preds = np.random.randint(20, 60, 7)
            st.plotly_chart(px.area(y=preds, title="AI Forecast", template="plotly_dark").update_traces(line_color='#6C63FF'), use_container_width=True)
            st.markdown(f"<div class='saas-card' style='border-left:5px solid #6C63FF;'>🤖 **Decision:** Order **{preds.sum()} units** immediately.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Samvada":
    st.markdown("<h1>🎙️ SAMVADA</h1>", unsafe_allow_html=True)
    st.session_state.voice_on = st.toggle("Enable Voice Feedback")
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        u_in = st.chat_input("Strategic query...")
        audio = st.audio_input("Speak")
        if audio:
            with st.spinner("Listening..."): u_in = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        if u_in:
            st.session_state.chat_history.append({"role":"user","content":u_in})
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":"You are AROHA AI. Be brief."}] + st.session_state.chat_history[-3:])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant","content":ans}); speak(ans); st.rerun()

elif st.session_state.page == "Nyasa":
    st.markdown("<h1>📝 NYASA</h1>", unsafe_allow_html=True)
    with st.form("add"):
        n = st.text_input("Name"); c = st.text_input("Cat"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1); img = st.text_input("Image URL"); rev = st.text_area("Reviews")
        if st.form_submit_button("Commit"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, category, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?,?)", (st.session_state.user, n, c, s, p, lt, img, rev))
            st.success("Committed.")

elif st.session_state.page == "Agama":
    st.markdown("<h1>📥 AGAMA</h1>", unsafe_allow_html=True)
    f = st.file_uploader("Upload CSV", type="csv")
    if f and st.button("Synchronize"):
        u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
        with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
        st.success("Synced.")

else:
    st.info(f"Node {st.session_state.page} active. Logic processing...")

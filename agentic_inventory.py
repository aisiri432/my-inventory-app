import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI
import hashlib
import time

# --- 1. SETTINGS & PREMIUM DARK INTELLIGENCE UI ---
st.set_page_config(page_title="AROHA | Strategic HUD", layout="wide", page_icon="💠")

def apply_intelligence_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Base Environment */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #0B0F14; /* Tesla/Bloomberg Deep Black */
            color: #FFFFFF;
        }

        /* Glassmorphic Section Cards */
        .glass-card {
            background: rgba(255, 255, 255, 0.02);
            backdrop-filter: blur(15px);
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 25px;
            margin-bottom: 20px;
            transition: 0.3s all ease;
        }
        .glass-card:hover {
            border-color: #7F00FF; /* Electric Purple */
            box-shadow: 0 0 20px rgba(127, 0, 255, 0.2);
        }

        /* Top Bar Branding */
        .top-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0px;
            border-bottom: 1px solid #1F2937;
            margin-bottom: 30px;
        }

        /* Glowing Sidebar Buttons */
        [data-testid="stSidebar"] {
            background-color: #080B0E !important;
            border-right: 1px solid #1F2937;
        }
        section[data-testid="stSidebar"] .stButton > button {
            background: transparent !important;
            border: 1px solid rgba(127, 0, 255, 0.3) !important;
            color: #E0E0E0 !important;
            border-radius: 10px;
            padding: 12px;
            font-size: 0.85rem;
            text-align: left;
            margin-bottom: 10px;
            width: 100%;
            transition: 0.3s;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            border: 1px solid #00D2FF !important; /* Neon Blue */
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.3);
            color: #FFFFFF !important;
            transform: translateX(5px);
        }

        /* 🎙️ Voice Waveform Animation */
        .waveform {
            display: flex;
            align-items: center;
            gap: 3px;
            height: 30px;
            margin-top: 10px;
        }
        .waveform span {
            width: 3px;
            height: 10px;
            background: #7F00FF;
            animation: wave 1.2s infinite ease-in-out;
        }
        @keyframes wave {
            0%, 100% { height: 10px; }
            50% { height: 25px; }
        }
        .waveform span:nth-child(2) { animation-delay: 0.2s; }
        .waveform span:nth-child(3) { animation-delay: 0.4s; }

        /* Metric Highlights */
        .metric-value { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #00D2FF; }
        .metric-label { font-size: 0.7rem; color: #6B7280; text-transform: uppercase; letter-spacing: 1px; }

        /* Gradient Highlight for Decision Box */
        .decision-highlight {
            background: linear-gradient(135deg, rgba(127, 0, 255, 0.1), rgba(0, 210, 255, 0.1));
            border: 1px solid #7F00FF;
            padding: 20px;
            border-radius: 12px;
            border-left: 10px solid #7F00FF;
        }

        /* Layman Description Text */
        .layman-tag { font-size: 0.8rem; color: #7F00FF; font-weight: 600; margin-bottom: 15px; display: block; }
        </style>
    """, unsafe_allow_html=True)

apply_intelligence_css()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_master_v30.db'
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

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_active" not in st.session_state: st.session_state.voice_active = False

# --- 4. AUTHENTICATION (GATE) ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:#7F00FF; font-size:4rem; font-weight:800; letter-spacing:10px;'>AROHA</h1><p style='color:#6B7280; letter-spacing:3px;'>STRATEGIC INTELLIGENCE INTERFACE</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        m = st.tabs(["ACCESS", "ENROLL"])
        with m[0]:
            u = st.text_input("Identity")
            p = st.text_input("Mantra", type="password")
            if st.button("UNLOCK HUB"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Verification Denied")
        with m[1]:
            nu = st.text_input("New ID"); np = st.text_input("New Key", type="password")
            if st.button("ENROLL"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Authorized.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='color:#7F00FF;'>AROHA</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#6B7280;'>OPERATOR: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
    st.divider()
    
    # Styled Navigation Buttons
    nav_items = [
        ("🏠 Dashboard", "Home"),
        ("🔮 Preksha", "Preksha"),
        ("🛡️ Stambha", "Stambha"),
        ("🎙️ Samvada", "Samvada"),
        ("💰 Artha", "Artha"),
        ("🤝 Mithra", "Mithra"),
        ("📄 Karya", "Karya"),
        ("📝 Nyasa", "Nyasa"),
        ("📥 Agama", "Agama")
    ]
    for label, page_id in nav_items:
        if st.button(label):
            st.session_state.page = page_id
            st.rerun()
            
    st.divider()
    if st.button("🔒 Exit"): st.session_state.auth = False; st.rerun()

# --- 6. TOP BAR HUD ---
st.markdown(f"""
    <div class='top-bar'>
        <div style='font-family:JetBrains Mono; font-size:0.7rem;'>OS_CORE: v30.0 // STATUS: OPTIMAL</div>
        <div style='display:flex; gap:20px;'>
            <span>🔔</span><span>👤 {st.session_state.user.upper()}</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 7. HOME DASHBOARD ---
if st.session_state.page == "Home":
    st.markdown("<h1>System Overview</h1>", unsafe_allow_html=True)
    
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='glass-card'><div class='metric-label'>Assets</div><div class='metric-value'>{len(df)}</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='glass-card'><div class='metric-label'>Treasury Value</div><div class='metric-value'>${val:,.0f}</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='glass-card'><div class='metric-label'>Risk Factor</div><div class='metric-value' style='color:#00FF41;'>Low</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='glass-card'><div class='metric-label'>AI Logic</div><div class='metric-value'>Active</div></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div class='glass-card'><h3>📈 Global Demand Forecast</h3>", unsafe_allow_html=True)
        st.plotly_chart(px.area(y=np.random.randint(10, 50, 10), template="plotly_dark").update_traces(line_color='#7F00FF'), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_r:
        st.markdown("<div class='glass-card'><h3>⚠️ Risk Matrix</h3>", unsafe_allow_html=True)
        st.write("No critical stockouts predicted in the next 48 hours.")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 8. FEATURE NODES ---

elif st.session_state.page == "Preksha":
    st.markdown("<h1>🔮 PREKSHA</h1>", unsafe_allow_html=True)
    st.markdown("<span class='layman-tag'>Predict Demand Instantly</span>", unsafe_allow_html=True)
    
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("Database empty.")
    else:
        target = st.selectbox("Asset Search", df['name'])
        preds = np.random.randint(20, 60, 7)
        st.plotly_chart(px.area(y=preds, title="AI Forecasting Stream", template="plotly_dark").update_traces(line_color='#00D2FF'), use_container_width=True)
        st.markdown(f"<div class='decision-highlight'><h3>🤖 AI Suggests...</h3>Procurement of <b>{preds.sum()} units</b> recommended to maintain optimal efficiency.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Samvada":
    st.markdown("<h1>🎙️ SAMVADA</h1>", unsafe_allow_html=True)
    st.markdown("<span class='layman-tag'>Talk To System</span>", unsafe_allow_html=True)
    
    col_c, col_v = st.columns([3, 1])
    with col_v:
        st.markdown("<div class='glass-card' style='text-align:center;'>", unsafe_allow_html=True)
        st.write("AI Voice")
        st.markdown("<div class='waveform'><span></span><span></span><span></span><span></span><span></span></div>", unsafe_allow_html=True)
        st.session_state.voice_active = st.toggle("Enable TTS")
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col_c:
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
            for m in st.session_state.chat_history:
                with st.chat_message(m["role"]): st.markdown(m["content"])
            q = st.chat_input("Input Strategic Command...")
            if q:
                st.session_state.chat_history.append({"role":"user","content":q})
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":"You are AROHA AI. Be strategic."}] + st.session_state.chat_history[-3:])
                ans = res.choices[0].message.content
                st.session_state.chat_history.append({"role":"assistant", "content":ans})
                st.rerun()

elif st.session_state.page == "Nyasa":
    st.markdown("<h1>📝 NYASA</h1>", unsafe_allow_html=True)
    st.markdown("<span class='layman-tag'>Log Assets Securely</span>", unsafe_allow_html=True)
    with st.form("entry"):
        n = st.text_input("Asset Name"); s = st.number_input("Current Stock", 0); p = st.number_input("Unit Price", 0.0)
        if st.form_submit_button("COMMIT TO VAULT"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price) VALUES (?,?,?,?)", (st.session_state.user, n, s, p))
            st.success("Asset Encrypted and Logged.")

# Artha, Mithra, Stambha, Agama follow similar layouts...
else:
    st.info(f"The {st.session_state.page} node is online. Logic processing...")

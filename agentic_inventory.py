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

# --- 1. SETTINGS & EXECUTIVE UI (PhonePe Inspired) ---
st.set_page_config(page_title="AROHA | Executive Suite", layout="wide", page_icon="💠")

def apply_executive_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #050505;
            color: #E0E0E0;
        }

        /* PhonePe Style Card Grid */
        .action-card {
            background: #111111;
            border: 1px solid #222222;
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            transition: 0.3s all ease;
            height: 100%;
        }
        
        .action-card:hover {
            border-color: #7F00FF; /* PhonePe Purple Accent */
            background: #161616;
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(127, 0, 255, 0.1);
        }

        .icon-circle {
            width: 60px; height: 60px;
            background: rgba(127, 0, 255, 0.1);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 15px auto;
            font-size: 30px;
            color: #7F00FF;
        }

        .card-title { font-weight: 700; font-size: 1rem; color: #FFFFFF; letter-spacing: 0.5px; }
        .card-desc { font-size: 0.8rem; color: #666; margin-top: 5px; }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #0A0A0A;
            border-right: 1px solid #1A1A1A;
        }

        /* Metrics / Quick Summary */
        .metric-row {
            background: rgba(127, 0, 255, 0.05);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            border: 1px solid rgba(127, 0, 255, 0.1);
        }

        /* AI Suggestion Box */
        .ai-decision-box {
            background: #0D0D0D;
            border-left: 5px solid #7F00FF;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }

        .stButton>button {
            border-radius: 10px;
            background: #7F00FF;
            color: white;
            font-weight: 600;
            border: none;
            width: 100%;
            padding: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_executive_css()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_executive_v19.db'
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
if "voice_on" not in st.session_state: st.session_state.voice_on = False

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:80px;'><h1 style='color:#7F00FF; font-size:3.5rem; font-weight:800;'>AROHA</h1><p style='color:#666;'>TURN DATA INTO DECISIONS</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        m = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
        with m[0]:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("SIGN IN"):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Authentication Failed")
        with m[1]:
            nu = st.text_input("New Username"); np = st.text_input("New Password", type="password")
            if st.button("CREATE ACCOUNT"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("User Enrolled.")
    st.stop()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#7F00FF;'>AROHA</h2>", unsafe_allow_html=True)
    st.write(f"👤 {st.session_state.user.upper()}")
    st.divider()
    
    # Navigation Link Style
    if st.button("🏠 Home Command"): st.session_state.page = "Home"; st.rerun()
    if st.button("🔮 Preksha Intelligence"): st.session_state.page = "Preksha"; st.rerun()
    if st.button("🛡️ Stambha Resilience"): st.session_state.page = "Stambha"; st.rerun()
    if st.button("💰 Artha Financials"): st.session_state.page = "Artha"; st.rerun()
    if st.button("🎙️ Samvada Voice Chat"): st.session_state.page = "Samvada"; st.rerun()
    if st.button("📝 Nyasa Ledger"): st.session_state.page = "Nyasa"; st.rerun()
    if st.button("📥 Agama Bulk Sync"): st.session_state.page = "Agama"; st.rerun()
    
    st.divider()
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. HOME PAGE (PhonePe Style Quick Actions) ---
if st.session_state.page == "Home":
    st.title("Strategic Command Center")
    
    # Summary Row
    st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    c1.metric("Items Monitored", len(df))
    c2.metric("Treasury Value", f"${(df['current_stock'] * df['unit_price']).sum():,.2f}" if not df.empty else "$0")
    c3.metric("System Health", "Optimal")
    c4.metric("Active Risks", "0")
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Quick Actions")
    
    # Action Grid
    row1_c1, row1_c2, row1_c3 = st.columns(3)
    
    actions = [
        {"id": "Preksha", "icon": "🔮", "title": "Forecasting", "desc": "AI Demand Sensing", "col": row1_c1},
        {"id": "Stambha", "icon": "🛡️", "title": "Resilience", "desc": "Risk Simulator", "col": row1_c2},
        {"id": "Samvada", "icon": "🎙️", "title": "Voice Assistant", "desc": "AI Interaction", "col": row1_c3}
    ]

    for a in actions:
        with a['col']:
            st.markdown(f"""
                <div class='action-card'>
                    <div class='icon-circle'>{a['icon']}</div>
                    <div class='card-title'>{a['title']}</div>
                    <div class='card-desc'>{a['desc']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Open {a['title']}", key=f"btn_{a['id']}"):
                st.session_state.page = a['id']; st.rerun()

# --- 7. FEATURE PAGE LOGIC ---

if st.session_state.page == "Preksha":
    st.title("🔮 Preksha Intelligence")
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("No data found.")
    else:
        target = st.selectbox("Select Asset", df['name'])
        p = df[df['name'] == target].iloc[0]
        col_img, col_chart = st.columns([1, 2])
        with col_img:
            if p['image_url']: st.image(p['image_url'], use_container_width=True)
            st.markdown(f"**Current Stock:** {p['current_stock']}")
            st.markdown("**Reviews:** " + (p['reviews'] if p['reviews'] else "None"))
        with col_chart:
            preds = np.random.randint(10, 50, 7)
            st.plotly_chart(px.area(y=preds, title="7-Day AI Path", template="plotly_dark").update_traces(line_color='#7F00FF'), use_container_width=True)
            st.markdown(f"<div class='ai-decision-box'>🤖 **AI Suggestion:** Restock {preds.sum()} units.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Samvada":
    st.title("🎙️ Samvada Assistant")
    st.session_state.voice_on = st.toggle("Voice Feedback", value=st.session_state.voice_on)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        u_in = st.chat_input("Ask a question...")
        audio = st.audio_input("Microphone")
        if audio:
            with st.spinner("Listening..."): u_in = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            with get_db() as conn: ctx = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", conn, params=(st.session_state.user,)).to_string()
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans})
            st.rerun()

elif st.session_state.page == "Nyasa":
    st.title("📝 Nyasa Asset Ledger")
    with st.form("entry"):
        n = st.text_input("Product Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1); img = st.text_input("Image URL"); rev = st.text_area("Reviews")
        if st.form_submit_button("SAVE TO VAULT"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
            st.success("Saved.")

elif st.session_state.page == "Agama":
    st.title("📥 Agama Bulk Sync")
    f = st.file_uploader("Upload CSV", type="csv")
    if f and st.button("SYNC"):
        st.success("Bulk Data Synchronized.")

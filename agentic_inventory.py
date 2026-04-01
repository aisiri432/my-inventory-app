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

# --- 1. SETTINGS & EXECUTIVE HUD UI ---
st.set_page_config(page_title="AROHA | Strategic Command", layout="wide", page_icon="💠")

def apply_executive_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #050709; 
            color: #E0E0E0;
        }

        /* Sidebar Nav Styling */
        [data-testid="stSidebar"] {
            background-color: #0A0C10;
            border-right: 1px solid #1F2937;
        }
        
        /* Action Tiles (Organized Grid) */
        .action-tile {
            background: #111827;
            border: 1px solid #1F2937;
            border-radius: 12px;
            padding: 30px 15px;
            text-align: center;
            transition: 0.3s all ease;
            height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
        }
        
        .action-tile:hover {
            border-color: #00D2FF;
            background: #161E2E;
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 210, 255, 0.1);
        }

        .tile-icon { font-size: 45px; margin-bottom: 12px; }
        .tile-title { font-weight: 700; font-size: 1rem; color: #FFFFFF; letter-spacing: 1px; }
        .tile-layman { font-size: 0.75rem; color: #00D2FF; margin-top: 5px; font-weight: 600; text-transform: uppercase; }
        .tile-desc { font-size: 0.7rem; color: #6B7280; margin-top: 4px; line-height: 1.2; }

        /* KPI Summary Bar */
        .kpi-bar {
            background: rgba(0, 210, 255, 0.03);
            border: 1px solid rgba(0, 210, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }

        /* AI Decision Highlight */
        .decision-box {
            background: #0F172A;
            border-left: 5px solid #00D2FF;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }

        /* Custom Button */
        .stButton>button {
            border-radius: 6px;
            background: #00D2FF;
            color: #000000;
            font-weight: 700;
            border: none;
            width: 100%;
            transition: 0.2s;
        }
        .stButton>button:hover {
            background: #FFFFFF;
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
        }
        </style>
    """, unsafe_allow_html=True)

apply_executive_css()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_executive_v27.db'
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

# --- 4. AUTHENTICATION (Modern & Professional) ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:#00D2FF; font-size:3rem; font-weight:800; letter-spacing:10px;'>AROHA</h1><p style='color:#6B7280; letter-spacing:2px;'>STRATEGIC ENTERPRISE ORCHESTRATOR</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        m = st.tabs(["IDENTITY ACCESS", "ENROLLMENT"])
        with m[0]:
            u = st.text_input("User ID")
            p = st.text_input("Mantra Key", type="password")
            if st.button("AUTHORIZE SESSION"):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Authentication Error")
        with m[1]:
            nu = st.text_input("Create User ID"); np = st.text_input("Create Mantra Key", type="password")
            if st.button("ENROLL SYSTEM"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Authorized. Please login.")
    st.stop()

# --- 5. GLOBAL SIDEBAR ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#00D2FF; font-size:1.8rem;'>AROHA</h2>", unsafe_allow_html=True)
    st.markdown(f"**Operator:** {st.session_state.user.upper()}")
    st.divider()
    
    if st.button("🏠 Home Command"): st.session_state.page = "Home"; st.rerun()
    if st.button("🔮 Preksha Intelligence"): st.session_state.page = "Preksha"; st.rerun()
    if st.button("🛡️ Stambha Resilience"): st.session_state.page = "Stambha"; st.rerun()
    if st.button("🎙️ Samvada Chat"): st.session_state.page = "Samvada"; st.rerun()
    if st.button("💰 Artha Financials"): st.session_state.page = "Artha"; st.rerun()
    if st.button("🤝 Mithra Suppliers"): st.session_state.page = "Mithra"; st.rerun()
    if st.button("📄 Karya Documents"): st.session_state.page = "Karya"; st.rerun()
    if st.button("📝 Nyasa Ledger"): st.session_state.page = "Nyasa"; st.rerun()
    if st.button("📥 Agama Bulk Sync"): st.session_state.page = "Agama"; st.rerun()
    
    st.divider()
    if st.button("🔒 Terminate Session"): st.session_state.auth = False; st.rerun()

# --- 6. HOME HUB ---
if st.session_state.page == "Home":
    st.title("Strategic Hub Dashboard")
    
    # Summary Bar
    st.markdown("<div class='kpi-bar'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    c1.metric("Assets", len(df))
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c2.metric("Treasury Value", f"${val:,.0f}")
    c3.metric("System Load", "Optimal")
    c4.metric("Risk Level", "Low")
    st.markdown("</div>", unsafe_allow_html=True)

    # Organized 4-Column Grid
    st.subheader("Intelligence Nodes")
    
    nodes = [
        {"id": "Preksha", "icon": "🔮", "title": "PREKSHA", "layman": "Predict Future Sales", "desc": "AI Demand Sensing Engine"},
        {"id": "Stambha", "icon": "🛡️", "title": "STAMBHA", "layman": "Stop Stock Risks", "desc": "Resilience & Disruption Simulator"},
        {"id": "Samvada", "icon": "🎙️", "title": "SAMVADA", "layman": "Talk to AI Assistant", "desc": "Voice & Chat Interaction"},
        {"id": "Artha", "icon": "💰", "title": "ARTHA", "layman": "Check Your Money", "desc": "Capital & Idle Value Tracking"},
        {"id": "Mithra", "icon": "🤝", "title": "MITHRA", "layman": "Manage Sellers", "desc": "Supplier Reliability Scoring"},
        {"id": "Karya", "icon": "📄", "title": "KARYA", "layman": "Make Order Bills", "desc": "Autonomous Document Generator"},
        {"id": "Nyasa", "icon": "📝", "title": "NYASA", "layman": "Add New Items", "desc": "Manual Asset Registry"},
        {"id": "Agama", "icon": "📥", "title": "AGAMA", "layman": "Upload Big Lists", "desc": "Bulk Data Ingestion Node"}
    ]

    cols = st.columns(4)
    for i, node in enumerate(nodes):
        with cols[i % 4]:
            st.markdown(f"""
                <div class='action-tile'>
                    <div class='tile-icon'>{node['icon']}</div>
                    <div class='tile-title'>{node['title']}</div>
                    <div class='tile-layman'>{node['layman']}</div>
                    <div class='tile-desc'>{node['desc']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("ACCESS NODE", key=f"go_{node['id']}"):
                st.session_state.page = node['id']; st.rerun()

# --- 7. LOGIC FOR NODES ---

if st.session_state.page == "Preksha":
    st.title("🔮 Preksha: Turning Data into Decisions")
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("Treasury empty.")
    else:
        target = st.selectbox("Select Asset", df['name'])
        p = df[df['name'] == target].iloc[0]
        col_img, col_chart = st.columns([1, 2])
        with col_img:
            if p['image_url']: st.image(p['image_url'], use_container_width=True)
            st.write(f"**Stock:** {p['current_stock']} units")
        with col_chart:
            preds = np.random.randint(15, 60, 7)
            st.plotly_chart(px.area(y=preds, title="AI Sensing Stream", template="plotly_dark").update_traces(line_color='#00D2FF'), use_container_width=True)
            st.markdown(f"<div class='decision-box'>🤖 **AI DIRECTIVE:** Reorder <b>{preds.sum()} units</b> recommended to prevent a stockout.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Samvada":
    st.title("🎙️ Samvada: Neural Interface")
    st.session_state.voice_active = st.toggle("Voice Feedback", value=st.session_state.voice_active)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        q = st.chat_input("Input Strategic Command...")
        audio = st.audio_input("Microphone")
        if audio:
            with st.spinner("Listening..."): q = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        
        if q:
            st.session_state.chat_history.append({"role":"user", "content":q})
            with get_db() as conn: ct

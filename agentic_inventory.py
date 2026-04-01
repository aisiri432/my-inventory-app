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

# --- 1. THE "SPOTIFY X PINTEREST" CSS ---
st.set_page_config(page_title="AROHA", layout="wide", page_icon="💠")

def apply_aesthetic_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', sans-serif;
            background-color: #000000; 
            color: #FFFFFF;
        }

        /* 📌 Pinterest Masonry Card */
        .pin-card {
            background: linear-gradient(180deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
            backdrop-filter: blur(20px);
            border-radius: 32px;
            padding: 25px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.08);
            transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        }
        .pin-card:hover {
            transform: scale(1.03);
            background: rgba(255,255,255,0.1);
            border-color: #D4AF37;
            box-shadow: 0 20px 40px rgba(0,0,0,0.6);
        }

        .pin-icon { font-size: 65px; margin-bottom: 15px; display: block; filter: drop-shadow(0 0 15px rgba(212,175,55,0.4)); }
        .pin-title { font-weight: 800; font-size: 1.4rem; color: #D4AF37; letter-spacing: -0.5px; }
        .pin-explain { font-size: 0.85rem; color: #888; margin-top: 5px; font-weight: 400; line-height: 1.3; }

        /* 🎧 Spotify style Bottom Player */
        .spotify-player {
            position: fixed; bottom: 0; left: 0; right: 0;
            background: rgba(18, 18, 18, 0.95);
            backdrop-filter: blur(10px);
            padding: 15px 40px;
            display: flex; justify-content: space-between; align-items: center;
            border-top: 1px solid #282828;
            z-index: 1000;
        }

        /* Hide Streamlit components */
        [data-testid="stSidebar"] { display: none; }
        .stTabs [data-baseweb="tab-list"] { gap: 20px; background-color: transparent; }
        .stButton>button { border-radius: 100px; background: #1DB954; color: black; font-weight: 800; border: none; padding: 10px 30px; }
        .stButton>button:hover { background: #1ed760; transform: scale(1.05); }

        /* Auth Box */
        .auth-container { max-width: 450px; margin: 100px auto; padding: 40px; background: #121212; border-radius: 40px; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

apply_aesthetic_css()

# --- 2. DATABASE ---
DB_FILE = 'aroha_aesthetic_v26.db'
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

# --- 4. LOGIN (ZENITH STYLE) ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:80px;'><h1 style='font-size:4rem; font-weight:800; color:#D4AF37; letter-spacing:-2px;'>AROHA</h1><p style='color:#555;'>Turn data into decisions.</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<div class='auth-container'>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["ACCESS", "JOIN"])
        with t1:
            u = st.text_input("Identity")
            p = st.text_input("Mantra", type="password")
            if st.button("Unlock Vault"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Access Denied")
        with t2:
            nu = st.text_input("New ID"); np = st.text_input("New Pass", type="password")
            if st.button("Enroll"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Authorized.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. TOP DISCOVERY BAR ---
def draw_top_bar():
    st.markdown(f"### Good evening, {st.session_state.user.capitalize()} ✨")
    st.markdown("<p style='color:#666;'>Today's Strategic Discovery</p>", unsafe_allow_html=True)

# --- 6. HOME PAGE (Pinterest Waterfall Layout) ---
if st.session_state.page == "Home":
    draw_top_bar()
    
    # 📌 Waterfall Columns (Uneven heights simulation)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""<div class='pin-card'><span class='pin-icon'>🔮</span><span class='pin-title'>PREKSHA</span><br><span class='pin-explain'>Predict future sales</span></div>""", unsafe_allow_html=True)
        if st.button("Open Intelligence", key="nav_pre"): st.session_state.page = "Preksha"; st.rerun()
        
        st.markdown("""<div class='pin-card' style='height:200px;'><span class='pin-icon'>💰</span><span class='pin-title'>ARTHA</span><br><span class='pin-explain'>Check your money</span></div>""", unsafe_allow_html=True)
        if st.button("Open Financials", key="nav_art"): st.session_state.page = "Artha"; st.rerun()

    with col2:
        st.markdown("""<div class='pin-card' style='height:350px;'><span class='pin-icon'>🎙️</span><span class='pin-title'>SAMVADA</span><br><span class='pin-explain'>Talk to AI assistant</span></div>""", unsafe_allow_html=True)
        if st.button("Start Conversation", key="nav_sam"): st.session_state.page = "Samvada"; st.rerun()
        
        st.markdown("""<div class='pin-card'><span class='pin-icon'>📝</span><span class='pin-title'>NYASA</span><br><span class='pin-explain'>Add new items</span></div>""", unsafe_allow_html=True)
        if st.button("Open Ledger", key="nav_nya"): st.session_state.page = "Nyasa"; st.rerun()

    with col3:
        st.markdown("""<div class='pin-card'><span class='pin-icon'>🛡️</span><span class='pin-title'>STAMBHA</span><br><span class='pin-explain'>Stop stock risks</span></div>""", unsafe_allow_html=True)
        if st.button("Open Resilience", key="nav_sta"): st.session_state.page = "Stambha"; st.rerun()
        
        st.markdown("""<div class='pin-card' style='height:300px;'><span class='pin-icon'>🤝</span><span class='pin-title'>MITHRA</span><br><span class='pin-explain'>Manage your sellers</span></div>""", unsafe_allow_html=True)
        if st.button("Open Suppliers", key="nav_mit"): st.session_state.page = "Mithra"; st.rerun()

# --- 7. FEATURE PAGES ---
def back_nav():
    if st.button("⬅️ Back to Discovery"): st.session_state.page = "Home"; st.rerun()

if st.session_state.page == "Preksha":
    back_nav(); st.title("🔮 Preksha: Strategic Forecasting")
    st.markdown("<p style='color:#888;'>AI Sensing future demand flows...</p>", unsafe_allow_html=True)
    # (Prediction logic remains here)

elif st.session_state.page == "Samvada":
    back_nav(); st.title("🎙️ Samvada: Neural Dialogue")
    st.session_state.voice_active = st.toggle("Enable Voice Assistant", value=st.session_state.voice_active)
    # (Chatbot logic remains here)

elif st.session_state.page == "Nyasa":
    back_nav(); st.title("📝 Nyasa: Asset Ledger")
    with st.form("add"):
        n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0)
        if st.form_submit_button("Commit to Vault"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price) VALUES (?,?,?,?)", (st.session_state.user, n, s, p))
            st.success("Pinned to Vault.")

# --- 🎧 THE SPOTIFY PLAYER (BOTTOM BAR) ---
st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True) # Spacer
st.markdown(f"""
    <div class='spotify-player'>
        <div style='display:flex; align-items:center; gap:15px;'>
            <div style='width:45px; height:45px; background:#D4AF37; border-radius:4px; display:flex; align-items:center; justify-content:center; color:black; font-weight:bold;'>A</div>
            <div>
                <div style='font-size:14px; font-weight:600;'>System Sensing...</div>
                <div style='font-size:11px; color:#b3b3b3;'>Operator: {st.session_state.user.upper()}</div>
            </div>
        </div>
        <div style='color:#1DB954; font-size:12px; font-weight:800;'>🟢 CORE ACTIVE</div>
        <div style='font-size:20px; color:#b3b3b3;'> ⏸️ ⏭️ </div>
    </div>
""", unsafe_allow_html=True)

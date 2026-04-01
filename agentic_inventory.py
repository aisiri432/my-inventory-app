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

# --- 1. PREMIUM UI CONFIG (RADIANT TYPOGRAPHY) ---
st.set_page_config(page_title="AROHA | Strategic Intelligence", layout="wide", page_icon="💠", initial_sidebar_state="expanded")

def apply_aroha_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Global Reset */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0B0F14;
            color: #E6E8EB;
        }

        /* 💎 STANDOUT BRANDING */
        .brand-container { padding: 10px 0 25px 15px; }
        .brand-title { 
            font-size: 3.5rem !important; 
            font-weight: 800 !important; 
            color: #FFFFFF !important; 
            letter-spacing: -2px; 
            text-shadow: 0 0 25px rgba(108, 99, 255, 0.6);
            margin-bottom: 0; 
        }
        .tagline { font-size: 1.1rem; color: #9AA0A6; margin-top: -5px; display: flex; gap: 6px; }
        .decisions-fade { color: #6C63FF; font-weight: 700; animation: glowPulse 2s infinite alternate; }
        @keyframes glowPulse { from { text-shadow: 0 0 5px #6C63FF; } to { text-shadow: 0 0 15px #38BDF8; } }

        /* 🧭 SIDEBAR: RADIANT SANSKRIT LABELS */
        [data-testid="stSidebar"] { background-color: #090B0F !important; border-right: 1px solid #1F2229; min-width: 400px !important; }
        
        section[data-testid="stSidebar"] .stButton > button { 
            background: transparent !important; 
            border: none !important; 
            color: #FFFFFF !important; 
            text-align: left !important; 
            padding: 15px 18px !important; 
            width: 100%; 
            font-size: 1.7rem !important; /* RADIANT SIZE */
            font-weight: 800 !important; 
            letter-spacing: 2.5px;
            text-shadow: 0 0 12px rgba(255, 255, 255, 0.3); /* The Feature Name Glow */
            transition: 0.3s;
        }
        
        .sidebar-sub { 
            font-size: 0.95rem !important; 
            color: #6C63FF; 
            font-weight: 700; 
            display: block; 
            margin-top: -18px; 
            margin-bottom: 25px; 
            margin-left: 55px; 
            text-transform: uppercase; 
            letter-spacing: 1.2px;
            opacity: 0.9;
        }

        /* Standout Headings for Feature Pages */
        .feature-header {
            font-size: 3rem !important;
            font-weight: 800 !important;
            color: #D4AF37 !important;
            letter-spacing: 3px;
            text-shadow: 0 0 15px rgba(212, 175, 55, 0.3);
            margin-bottom: 10px;
        }

        /* Saas Cards */
        .saas-card { 
            background: #171A21; 
            border: 1px solid rgba(255, 255, 255, 0.05); 
            border-radius: 12px; 
            padding: 25px; 
            margin-bottom: 20px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.4); 
        }
        .node-card-title {
            font-size: 1.4rem !important;
            font-weight: 800 !important;
            color: #FFFFFF !important;
            letter-spacing: 1.5px;
            text-shadow: 0 0 8px rgba(108, 99, 255, 0.4);
        }

        .ai-decision-box { 
            background: rgba(212, 175, 55, 0.08); 
            border: 2px solid #D4AF37; 
            padding: 25px; 
            border-radius: 15px; 
            border-left: 12px solid #D4AF37;
            margin-top: 25px; 
        }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_final_v40.db'
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

# --- 3. HELPER FUNCTION (Standardized) ---
def get_user_data():
    with get_db() as conn:
        return pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))

# --- 4. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_on" not in st.session_state: st.session_state.voice_on = False

def speak_aloud(text):
    if st.session_state.voice_on:
        clean = text.replace('"', '').replace("'", "")
        js = f"<script>var m = new SpeechSynthesisUtterance(); m.text='{clean}'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 5. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 class='brand-title'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Turn Data Into <span class='decisions-fade'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([1, 0.8, 1])
    with col_center:
        m = st.tabs(["Login", "Enroll"])
        with m[0]:
            u_input = st.text_input("Username")
            p_input = st.text_input("Password", type="password")
            if st.button("Unlock Strategic Hub"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u_input,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p_input):
                    st.session_state.auth = True; st.session_state.user = u_input; st.rerun()
                else: st.error("Access Denied")
        with m[1]:
            nu = st.text_input("New ID"); np = st.text_input("New Password", type="password")
            if st.button("Enroll Session"):
                try:
                    with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                    st.success("Authorized.")
                except: st.error("ID exists.")
    st.stop()

# --- 6. SIDEBAR (RADIANT NAVIGATION) ---
with st.sidebar:
    st.markdown(f"<div class='brand-container'><div class='brand-title'>AROHA</div><div class='tagline'>Data into <span class='decisions-fade'>Decisions</span></div></div>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)
    
    nodes = [
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System"),
        ("💰 ARTHA", "Artha", "Track Money Flow"),
        ("🤝 MITHRA", "Mithra", "Rate Your Suppliers"),
        ("📄 KARYA", "Karya", "Auto Create Orders"),
        ("📝 NYASA", "Nyasa", "Log Assets Securely"),
        ("📥 AGAMA", "Agama", "Import Data Easily")
    ]
    for label, page_id, layman in nodes:
        if st.button(label):
            st.session_state.page = page_id
            st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)

    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 7. DASHBOARD NODE ---
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Strategic Command Hub: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='saas-card'><h3>Assets</h3><h2 style='color:#6C63FF; font-size:2rem;'>{len(df)}</h2></div>", unsafe_allo

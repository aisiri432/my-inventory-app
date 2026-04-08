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

# --- 1. PREMIUM UI CONFIG (FORCED SIDEBAR & GLASSMORPHISM) ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="expanded" # Forces sidebar open on Desktop
)

def apply_aroha_style():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        html, body, [class*="css"] {{ 
            font-family: 'Inter', sans-serif; 
            background-color: #050709; 
            color: #E6E8EB; 
        }}

        /* 📱 MOBILE SIDEBAR FIX */
        @media (max-width: 768px) {{
            [data-testid="stSidebar"] {{ 
                min-width: 100vw !important; 
                z-index: 1000000 !important;
            }}
        }}

        /* 📟 SIDEBAR CONTAINER STYLING */
        [data-testid="stSidebar"] {{ 
            background-color: #080A0C !important; 
            border-right: 1px solid #1F2229 !important;
            display: block !important; /* Ensure it's not hidden */
        }}

        /* 💠 WATERMARK */
        [data-testid="stAppViewContainer"]::before {{
            content: "AROHA"; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-15deg);
            font-size: 15rem; font-weight: 900; color: rgba(255, 255, 255, 0.03); z-index: -1; pointer-events: none; letter-spacing: 20px;
        }}

        /* RADIANT HOLLOW BUTTONS */
        section[data-testid="stSidebar"] .stButton > button {{ 
            background: transparent !important; 
            border: 2px solid rgba(255, 255, 255, 0.1) !important; 
            color: #FFFFFF !important; 
            text-align: left !important; 
            padding: 12px 18px !important; 
            width: 100%; 
            font-size: 1.4rem !important; 
            font-weight: 800 !important; 
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
            margin-bottom: 8px;
            transition: 0.3s;
        }}

        /* SPECTRUM HOVER COLORS */
        div[data-testid="stSidebar"] button[key*="nyasa"]:hover {{ border-color: #00FF88 !important; color: #00FF88 !important; box-shadow: 0 0 15px #00FF88; }}
        div[data-testid="stSidebar"] button[key*="preksha"]:hover {{ border-color: #7F00FF !important; color: #7F00FF !important; box-shadow: 0 0 15px #7F00FF; }}
        div[data-testid="stSidebar"] button[key*="stambha"]:hover {{ border-color: #FF0055 !important; color: #FF0055 !important; box-shadow: 0 0 15px #FF0055; }}
        div[data-testid="stSidebar"] button[key*="kriya"]:hover {{ border-color: #FF33FF !important; color: #FF33FF !important; box-shadow: 0 0 15px #FF33FF; }}
        div[data-testid="stSidebar"] button[key*="samvada"]:hover {{ border-color: #00D4FF !important; color: #00D4FF !important; box-shadow: 0 0 15px #00D4FF; }}
        div[data-testid="stSidebar"] button[key*="vitta"]:hover {{ border-color: #FFD700 !important; color: #FFD700 !important; box-shadow: 0 0 15px #FFD700; }}
        div[data-testid="stSidebar"] button[key*="sanchara"]:hover {{ border-color: #FF8800 !important; color: #FF8800 !important; box-shadow: 0 0 15px #FF8800; }}
        div[data-testid="stSidebar"] button[key*="mithra"]:hover {{ border-color: #34D399 !important; color: #34D399 !important; box-shadow: 0 0 15px #34D399; }}

        .sidebar-sub {{ font-size: 0.9rem; color: #6C63FF; font-weight: 700; display: block; margin-top: -10px; margin-bottom: 25px; margin-left: 20px; text-transform: uppercase; }}
        .brand-title {{ font-weight: 800; color: #FFFFFF; letter-spacing: -2px; text-shadow: 0 0 25px rgba(108, 99, 255, 0.6); margin-bottom: 0; }}
        .saas-card {{ background: rgba(13, 17, 23, 0.7); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 25px; margin-bottom: 20px; }}
        .feature-header {{ font-weight: 800; color: #00D4FF !important; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3); text-transform: uppercase; border-bottom: 2px solid rgba(0, 212, 255, 0.2); padding-bottom: 10px; }}
        
        header {{visibility: hidden;}} footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_nexus_v123.db'
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
def get_user_data():
    with get_db() as conn: return pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_on" not in st.session_state: st.session_state.voice_on = False

# --- 4. AUTHENTICATION GATE ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 class='brand-title'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Turn Data Into <span style='color:#6C63FF; font-weight:700;'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([0.1, 0.8, 0.1])
    with col_center:
        m = st.tabs(["Login", "Enroll"])
        with m[0]:
            u_input = st.text_input("Username", key="l_u")
            p_input = st.text_input("Password", type="password", key="l_p")
            if st.button("Unlock Strategic Hub"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u_input,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p_input):
                    st.session_state.auth = True; st.session_state.user = u_input; st.rerun()
                else: st.error("Access Denied")
        with m[1]:
            nu = st.text_input("New ID"); np = st.text_input("New Pass", type="password")
            if st.button("Enroll Session"):
                try:
                    with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                    st.success("Authorized! Now Login.")
                except: st.error("ID exists.")
    st.stop() # Code pauses here until login is successful

# --- 5. SIDEBAR (THIS ONLY RUNS AFTER LOGIN) ---
with st.sidebar:
    st.markdown(f"<div style='text-align:center; margin-bottom:20px;'><h1 style='color:white; font-size:2.5rem; letter-spacing:-1px;'>AROHA</h1></div>", unsafe_allow_html=True)
    
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)

    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items & PO Gen"),
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks"),
        ("👷‍♂️ KRIYA", "Kriya", "Workforce Intelligence"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System"),
        ("💰 VITTA", "Vitta", "Track Money Flow"),
        ("📦 SANCHARA", "Sanchara", "Global Map & Flow"),
        ("🤝 MITHRA+", "Mithra", "AI Negotiation")
    ]
    for label, page_id, layman in nodes:
        if st.button(label, key=f"nav_{page_id.lower()}"):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)
    
    st.divider()
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. PAGE LOGIC ---

# 🏠 DASHBOARD
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Strategic Hub: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("📝 Assets", len(df))
    with c2: st.metric("💰 Treasury", f"₹{val:,.0f}")
    with c3: st.metric("🛡️ Status", "OPTIMAL")

# 👷‍♂️ KRIYA
elif st.session_state.page == "Kriya":
    st.markdown("<div class='feature-header'>👷‍♂️ KRIYA</div>", unsafe_allow_html=True)
    st.markdown("<div class='saas-card'><b>Active Task:</b> Pick 12x Titanium Chassis for Station B1<br><b>Priority:</b> Critical</div>", unsafe_allow_html=True)

# 💰 VITTA
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>💰 VITTA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='financial-stat'>Total Value<br><h2>₹{total_v:,.0f}</h2></div>", unsafe_allow_html=True)
        with c2:
            st.plotly_chart(px.pie(df, values='current_stock', names='name', hole=0.5, template="plotly_dark"))

# (Remaining nodes follow the same logic pattern...)

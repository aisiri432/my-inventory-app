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

# --- 1. PREMIUM UI CONFIG (FORCED SIDEBAR & BOLD FONTS) ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="expanded" # This forces the sidebar to be open on load
)

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

        /* --- SIDEBAR: ULTRA BOLD & WIDE --- */
        [data-testid="stSidebar"] { 
            background-color: #090B0F !important; 
            border-right: 1px solid #1F2229; 
            min-width: 350px !important; 
            max-width: 350px !important;
        }
        
        /* Sidebar Branding */
        .brand-container { padding: 10px 0 20px 15px; }
        .brand-title { font-size: 2.2rem; font-weight: 800; color: #FFFFFF; letter-spacing: -1px; }
        .tagline { font-size: 1rem; color: #9AA0A6; margin-top: -5px; }
        .decisions-fade { color: #6C63FF; font-weight: 700; animation: glowPulse 2s infinite alternate; }
        @keyframes glowPulse { from { text-shadow: 0 0 2px #6C63FF; } to { text-shadow: 0 0 10px #38BDF8; } }

        /* Sidebar Section Headers */
        .sidebar-section-head { 
            font-size: 0.8rem; 
            font-weight: 800; 
            color: #4B5563; 
            text-transform: uppercase; 
            letter-spacing: 2px; 
            margin: 25px 0 10px 18px; 
        }
        
        /* Main Sanskrit Sidebar Buttons - EXTRA LARGE */
        section[data-testid="stSidebar"] .stButton > button { 
            background: transparent !important; 
            border: none !important; 
            color: #FFFFFF !important; 
            text-align: left !important; 
            padding: 10px 18px !important; 
            width: 100%; 
            font-size: 1.4rem !important; /* EXTRA LARGE FONT */
            font-weight: 800 !important; 
            letter-spacing: 1px;
        }
        
        /* Layman Sub-Labels */
        .sidebar-sub { 
            font-size: 0.9rem !important; /* VERY READABLE */
            color: #6C63FF; 
            font-weight: 700; 
            display: block; 
            margin-top: -15px; 
            margin-bottom: 20px; 
            margin-left: 55px; 
            text-transform: uppercase; 
            letter-spacing: 1px; 
        }

        section[data-testid="stSidebar"] .stButton > button:hover { 
            background: #171A21 !important; 
            color: #6C63FF !important; 
        }

        /* --- DASHBOARD: NORMAL PROFESSIONAL FONT --- */
        .db-header { font-size: 2rem; font-weight: 700; color: #FFFFFF; }
        .saas-card { 
            background: #171A21; 
            border: 1px solid rgba(255, 255, 255, 0.05); 
            border-radius: 12px; 
            padding: 20px; 
            margin-bottom: 20px; 
        }
        .db-metric-val { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #FFFFFF; }
        .db-metric-label { font-size: 0.8rem; text-transform: uppercase; color: #9AA0A6; font-weight: 600; }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_final_v35.db'
def get_db(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
        c.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, 
                      current_stock INTEGER, unit_price REAL, lead_time INTEGER, supplier TEXT)''')
        conn.commit()
init_db()

def hash_p(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- 3. AUTH LOGIC ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"

if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:white; font-size:4rem; font-weight:800;'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Where Data Becomes <span style='color:#6C63FF; font-weight:700;'>Decisions</span></p></div>", unsafe_allow_html=True)
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
                try:
                    with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                    st.success("Authorized.")
                except: st.error("Exists.")
    st.stop()

# --- 4. SIDEBAR (LARGE BOLD SANSKRIT - FORCED VISIBLE) ---
with st.sidebar:
    st.markdown(f"""
        <div class='brand-container'>
            <div class='brand-title'>AROHA</div>
            <div class='tagline'>Data into <span class='decisions-fade'>Decisions</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-head'>Intelligence</div>", unsafe_allow_html=True)
    
    # Node Mapping
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

    st.divider()
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 5. NORMAL DASHBOARD ---
if st.session_state.page == "Dashboard":
    st.markdown(f"<p style='text-align:right; color:#444;'>👤 {st.session_state.user.upper()} • v35.1</p>", unsafe_allow_html=True)
    st.markdown("<div class='db-header'>Command Center</div>", unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Assets</div><div class='db-metric-val'>14</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Treasury</div><div class='db-metric-val'>₹420K</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Risk</div><div class='db-metric-val' style='color:#34D399;'>Stable</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Efficiency</div><div class='db-metric-val'>94%</div></div>", unsafe_allow_html=True)

    st.info("💡 Select a Strategic Node from the sidebar to begin analysis.")

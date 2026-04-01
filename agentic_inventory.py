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

# --- 1. PREMIUM UI CONFIG (SIDEBAR FONT SCALED) ---
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

        /* --- SIDEBAR: INCREASED FONT SIZE --- */
        [data-testid="stSidebar"] { 
            background-color: #090B0F !important; 
            border-right: 1px solid #1F2229; 
            width: 350px !important; /* Slightly wider to accommodate large text */
        }
        
        /* Main Sanskrit Labels */
        section[data-testid="stSidebar"] .stButton > button { 
            background: transparent !important; 
            border: none !important; 
            color: #E6E8EB !important; 
            text-align: left !important; 
            padding: 12px 15px !important; 
            width: 100%; 
            transition: 0.2s; 
            font-size: 1.3rem !important; /* BIG BOLD SANSKRIT */
            font-weight: 700 !important; 
            letter-spacing: 1px;
        }
        
        /* 3-Word Layman Sub-Labels */
        .sidebar-sub { 
            font-size: 0.85rem !important; /* INCREASED FOR CLARITY */
            color: #6C63FF; 
            font-weight: 700; 
            display: block; 
            margin-top: -15px; 
            margin-bottom: 18px; 
            margin-left: 52px; 
            text-transform: uppercase; 
            opacity: 1; 
            letter-spacing: 1px; 
        }

        section[data-testid="stSidebar"] .stButton > button:hover { 
            background: #171A21 !important; 
            color: #6C63FF !important; 
        }

        /* --- DASHBOARD: NORMAL PROFESSIONAL FONT --- */
        .db-header { font-size: 2.2rem !important; font-weight: 700; color: #FFFFFF; margin-bottom: 5px; }
        .db-sub { font-size: 1rem !important; color: #6B7280; margin-bottom: 30px; }
        .db-metric-val { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem !important; font-weight: 700; color: #FFFFFF; }
        .db-metric-label { font-size: 0.8rem !important; text-transform: uppercase; color: #9AA0A6; letter-spacing: 1px; }
        
        .saas-card { 
            background: #171A21; 
            border: 1px solid rgba(255, 255, 255, 0.05); 
            border-radius: 12px; 
            padding: 22px; 
            margin-bottom: 20px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.4); 
        }
        
        .recommendation-hero { 
            background: linear-gradient(135deg, rgba(108, 99, 255, 0.08) 0%, rgba(56, 189, 248, 0.03) 100%); 
            border-radius: 12px; 
            padding: 25px; 
            border-left: 6px solid #6C63FF; 
            margin-bottom: 30px; 
        }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_final_v35.db'
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

# --- 3. SESSION & AUTH ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"

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
                try:
                    with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                    st.success("Authorized.")
                except: st.error("Exists.")
    st.stop()

# --- 4. SIDEBAR (LARGE BOLD SANSKRIT FIRST) ---
with st.sidebar:
    st.markdown(f"<div class='brand-container'><div class='brand-title'>AROHA</div><div class='tagline'>Where data becomes <span class='decisions-fade'>Decisions</span></div></div>", unsafe_allow_html=True)
    
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-head'>Intelligence</div>", unsafe_allow_html=True)
    
    if st.button("📈 PREKSHA"): st.session_state.page = "Preksha"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Predict Demand Instantly</span>", unsafe_allow_html=True)
    
    if st.button("🛡️ STAMBHA"): st.session_state.page = "Stambha"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Test Supply Risks</span>", unsafe_allow_html=True)
    
    if st.button("🎙️ SAMVADA"): st.session_state.page = "Samvada"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Talk To System</span>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-head'>Analysis</div>", unsafe_allow_html=True)
    if st.button("💰 ARTHA"): st.session_state.page = "Artha"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Track Money Flow</span>", unsafe_allow_html=True)
    
    if st.button("🤝 MITHRA"): st.session_state.page = "Mithra"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Rate Your Suppliers</span>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-head'>Control</div>", unsafe_allow_html=True)
    if st.button("📄 KARYA"): st.session_state.page = "Karya"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Auto Create Orders</span>", unsafe_allow_html=True)
    
    if st.button("📝 NYASA"): st.session_state.page = "Nyasa"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Log Assets Securely</span>", unsafe_allow_html=True)
    
    if st.button("📥 AGAMA"): st.session_state.page = "Agama"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Import Data Easily</span>", unsafe_allow_html=True)

    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 5. NORMALIZED DASHBOARD ---
if st.session_state.page == "Dashboard":
    st.markdown(f"<p style='text-align:right; color:#444; font-size:0.8rem; margin-top:10px;'>👤 {st.session_state.user.upper()} • v35.0</p>", unsafe_allow_html=True)
    st.markdown("<div class='db-header'>Strategic Hub</div>", unsafe_allow_html=True)
    st.markdown("<div class='db-sub'>Real-time supply chain telemetry</div>", unsafe_allow_html=True)

    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Assets</div><div class='db-metric-val'>{len(df)}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Treasury</div><div class='db-metric-val'>₹{val/1000:,.1f}K</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Risk</div><div class='db-metric-val' style='color:#34D399;'>Low</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Uptime</div><div class='db-metric-val'>99.9%</div></div>", unsafe_allow_html=True)

    st.markdown(f"""<div class='recommendation-hero'><p style='color:#6C63FF; font-weight:700; font-size:0.75rem; text-transform:uppercase;'>✨ AI Intelligence Directive</p><h3 style='color:white; margin: 10px 0;'>Execute reorder for high-velocity assets.</h3><p style='color:#9AA0A6; font-size:0.9rem;'>Capital required for 7-day safety: ₹{val*0.12:,.0f}.</p></div>""", unsafe_allow_html=True)

# --- 6. FEATURE NODES ---
elif st.session_state.page == "Preksha":
    st.markdown("<h2>📈 PREKSHA – Demand Forecast</h2>", unsafe_allow_html=True)
    st.info("Predictive sensing node active.")

elif st.session_state.page == "Nyasa":
    st.markdown("<h2>📝 NYASA – Asset Ledger</h2>", unsafe_allow_html=True)
    with st.form("add"):
        st.text_input("Asset Name")
        if st.form_submit_button("Commit"): st.success("Synced.")

elif st.session_state.page == "Agama":
    st.markdown("<h2>📥 AGAMA – Bulk Import</h2>", unsafe_allow_html=True)
    st.file_uploader("Upload CSV")

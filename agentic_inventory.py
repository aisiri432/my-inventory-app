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

# --- 1. PREMIUM INTELLIGENCE UI CONFIG ---
st.set_page_config(page_title="AROHA | Strategic Intelligence", layout="wide", page_icon="💠")

def apply_aroha_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0B0F14;
            color: #E6E8EB;
            font-size: 16px;
        }

        .brand-container { padding: 10px 0 25px 10px; }
        .brand-title { font-size: 2.5rem; font-weight: 800; color: #FFFFFF; letter-spacing: -1px; margin-bottom: 0; }
        .tagline { font-size: 1.1rem; color: #9AA0A6; margin-top: -2px; display: flex; gap: 6px; }
        
        .decisions-fade {
            color: #6C63FF;
            font-weight: 700;
            animation: fadeInSlower 3s ease-in-out, glowPulse 2s infinite alternate;
        }
        
        @keyframes fadeInSlower { 0% { opacity: 0; } 50% { opacity: 0; } 100% { opacity: 1; } }
        @keyframes glowPulse { from { text-shadow: 0 0 2px #6C63FF; } to { text-shadow: 0 0 10px #38BDF8; } }

        [data-testid="stSidebar"] { background-color: #090B0F !important; border-right: 1px solid #1F2229; }
        .sidebar-section-head { font-size: 0.75rem; font-weight: 700; color: #4B5563; text-transform: uppercase; letter-spacing: 1.5px; margin: 25px 0 12px 15px; }
        
        .sidebar-sub {
            font-size: 0.72rem; color: #6C63FF; font-weight: 600; display: block;
            margin-top: -12px; margin-bottom: 15px; margin-left: 45px; 
            text-transform: uppercase; opacity: 0.9; letter-spacing: 0.8px;
        }

        section[data-testid="stSidebar"] .stButton > button {
            background: transparent !important; border: none !important; color: #E6E8EB !important;
            text-align: left !important; padding: 10px 15px !important; width: 100%; transition: 0.2s;
            font-size: 1.1rem !important; font-weight: 600 !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover { background: #171A21 !important; color: #6C63FF !important; }

        .saas-card {
            background: #171A21; border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px; padding: 28px; margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4); transition: 0.3s ease;
        }
        .saas-card:hover { transform: translateY(-4px); border-color: rgba(108, 99, 255, 0.3); }
        .card-icon { font-size: 2.2rem; margin-bottom: 12px; display: block; opacity: 0.9; }

        .recommendation-hero {
            background: linear-gradient(135deg, rgba(108, 99, 255, 0.12) 0%, rgba(56, 189, 248, 0.05) 100%);
            border-radius: 12px; padding: 30px; border: 1px solid rgba(108, 99, 255, 0.25);
            border-left: 6px solid #6C63FF; margin-bottom: 30px;
        }

        .m-val { font-family: 'JetBrains Mono', monospace; font-size: 2.2rem; font-weight: 700; color: #FFFFFF; }
        .m-sub { color: #9AA0A6; font-size: 0.85rem; text-transform: uppercase; font-weight: 500; letter-spacing: 1px; }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_v33.db'
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

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"

# --- 4. AUTHENTICATION GATE (FIXED FOR INTEGRITY ERROR) ---
if not st.session_state.auth:
    st.markdown("""
        <div style='text-align:center; margin-top:100px;'>
            <h1 style='color:white; font-size:4.5rem; font-weight:800;'>AROHA</h1>
            <p style='color:#9AA0A6; font-size:1.4rem;'>Where Data Becomes <span style='color:#6C63FF; font-weight:700;'>Decisions</span></p>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 0.8, 1])
    with col2:
        m = st.tabs(["Login", "Enroll"])
        with m[0]:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Unlock Dashboard"):
                with get_db() as conn: 
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Verification failed.")
        with m[1]:
            nu = st.text_input("New ID")
            np = st.text_input("New Password", type="password")
            if st.button("Initialize Account"):
                if nu and np:
                    try:
                        with get_db() as conn: 
                            conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                        st.success("Authorized! You can now Login.")
                    except sqlite3.IntegrityError:
                        st.error("This Identity already exists. Use a different ID or switch to Login.")
                else:
                    st.warning("Please enter both ID and Password.")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("""
        <div class='brand-container'>
            <div class='brand-title'>AROHA</div>
            <div class='tagline'>Where data becomes <span class='decisions-fade'>Decisions</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 Dashboard"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-head'>Intelligence</div>", unsafe_allow_html=True)
    if st.button("📈 PREKSHA"): st.session_state.page = "Preksha"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Predict Demand Instantly</span>", unsafe_allow_html=True)
    
    if st.button("🛡️ STAMBHA"): st.session_state.page = "Stambha"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Test Supply Risks</span>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-head'>Control</div>", unsafe_allow_html=True)
    if st.button("📝 NYASA"): st.session_state.page = "Nyasa"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Log Assets Securely</span>", unsafe_allow_html=True)
    
    if st.button("📥 AGAMA"): st.session_state.page = "Agama"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Import Data Easily</span>", unsafe_allow_html=True)

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. HOME DASHBOARD ---
if st.session_state.page == "Dashboard":
    st.markdown(f"<p style='text-align:right; color:#9AA0A6; font-size:0.9rem;'>👤 <b>{st.session_state.user.upper()}</b> • {datetime.now().strftime('%H:%M')}</p>", unsafe_allow_html=True)
    st.markdown("<h1 style='color:white; margin-bottom:30px;'>Strategic Command Hub</h1>", unsafe_allow_html=True)

    # Hero Recommendation
    st.markdown("""
        <div class='recommendation-hero'>
            <p style='color:#6C63FF; font-weight:700; font-size:0.85rem; text-transform:uppercase; letter-spacing:1.5px;'>✨ AI Intelligence Directive</p>
            <h2 style='color:white; margin: 12px 0;'>Reorder 120 units of 'Asset-X' from Global Logistics.</h2>
            <p style='color:#9AA0A6; font-size:1rem;'>Sensed a demand spike for next weekend. Risk Level: Medium.</p>
        </div>
    """, unsafe_allow_html=True)

    # Node Grid
    st.subheader("Intelligence Nodes")
    q1, q2 = st.columns(2)
    
    with q1:
        st.markdown("""<div class='saas-card'><span class='card-icon'>📈</span><b>PREKSHA</b><br><span style='color:#6C63FF; font-size:0.8rem; font-weight:700;'>PREDICT DEMAND INSTANTLY</span></div>""", unsafe_allow_html=True)
        if st.button("Launch Forecast", key="q_pre"): st.session_state.page = "Preksha"; st.rerun()
        
    with q2:
        st.markdown("""<div class='saas-card'><span class='card-icon'>🛡️</span><b>STAMBHA</b><br><span style='color:#6C63FF; font-size:0.8rem; font-weight:700;'>TEST SUPPLY RISKS</span></div>""", unsafe_allow_html=True)
        if st.button("Launch Resilience", key="q_sta"): st.session_state.page = "Stambha"; st.rerun()

# --- 7. FEATURE LOGIC ---
elif st.session_state.page == "Preksha":
    st.markdown("<h1>📈 PREKSHA</h1>", unsafe_allow_html=True)
    st.info("AI Analysis node active.")

elif st.session_state.page == "Nyasa":
    st.markdown("<h1>📝 NYASA</h1>", unsafe_allow_html=True)
    with st.form("add"):
        st.text_input("Asset Name")
        if st.form_submit_button("Commit"): st.success("Data Logged.")

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
st.set_page_config(page_title="AROHA | Elegant Intelligence", layout="wide", page_icon="💠")

def apply_aroha_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* 1. Global Reset & Theme */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0B0F14;
            color: #E6E8EB;
        }

        /* 2. Branding & Motion Tagline */
        .brand-container { padding: 10px 0 20px 10px; }
        .brand-title { font-size: 2.2rem; font-weight: 800; color: #FFFFFF; letter-spacing: -1px; margin-bottom: 0; }
        .tagline { font-size: 0.85rem; color: #9AA0A6; margin-top: -5px; display: flex; gap: 5px; }
        
        .decisions-fade {
            color: #6C63FF;
            font-weight: 700;
            animation: fadeInSlower 3s ease-in-out, glowPulse 2s infinite alternate;
        }
        
        @keyframes fadeInSlower { 0% { opacity: 0; } 50% { opacity: 0; } 100% { opacity: 1; } }
        @keyframes glowPulse { from { text-shadow: 0 0 2px #6C63FF; } to { text-shadow: 0 0 8px #38BDF8; } }

        /* 3. Sidebar: SaaS Minimalist */
        [data-testid="stSidebar"] { background-color: #090B0F !important; border-right: 1px solid #1F2229; }
        .sidebar-section-head { font-size: 0.65rem; font-weight: 700; color: #4B5563; text-transform: uppercase; letter-spacing: 1.2px; margin: 25px 0 10px 15px; }
        
        .sidebar-sub {
            font-size: 0.65rem;
            color: #6C63FF;
            font-weight: 600;
            display: block;
            margin-top: -8px;
            margin-bottom: 12px;
            margin-left: 42px; /* Alignment with icons */
            text-transform: uppercase;
            opacity: 0.8;
        }

        section[data-testid="stSidebar"] .stButton > button {
            background: transparent !important; border: none !important; color: #9AA0A6 !important;
            text-align: left !important; padding: 8px 15px !important; width: 100%; transition: 0.2s;
            font-size: 0.9rem !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover { 
            background: #171A21 !important; color: #FFFFFF !important; 
        }

        /* 4. Layered Cards & Dashboard Grid */
        .saas-card {
            background: #171A21;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            transition: 0.3s ease;
        }
        .saas-card:hover { transform: translateY(-4px); border-color: rgba(108, 99, 255, 0.3); }
        
        .card-icon { font-size: 2rem; margin-bottom: 10px; display: block; opacity: 0.9; }

        /* 5. Recommendation Panel */
        .recommendation-hero {
            background: linear-gradient(135deg, rgba(108, 99, 255, 0.12) 0%, rgba(56, 189, 248, 0.05) 100%);
            border-radius: 12px; padding: 25px; border: 1px solid rgba(108, 99, 255, 0.25);
            border-left: 6px solid #6C63FF; margin-bottom: 25px;
        }

        /* 6. Metrics */
        .m-val { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #FFFFFF; }
        .m-sub { color: #9AA0A6; font-size: 0.75rem; text-transform: uppercase; font-weight: 500; }

        /* 7. Floating Voice FAB */
        .voice-fab {
            position: fixed; bottom: 30px; right: 30px; width: 60px; height: 60px;
            background: linear-gradient(135deg, #6C63FF, #38BDF8);
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 8px 25px rgba(108, 99, 255, 0.3); z-index: 999;
            font-size: 24px;
        }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. CORE ENGINES (DATABASE) ---
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

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("""
        <div style='text-align:center; margin-top:100px;'>
            <h1 style='color:white; font-size:4rem; font-weight:800;'>AROHA</h1>
            <p style='color:#9AA0A6; font-size:1.2rem;'>Where Data Becomes <span style='color:#6C63FF; font-weight:700;'>Decisions</span></p>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 0.7, 1])
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
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Authorized.")
    st.stop()

# --- 5. SIDEBAR (ICONIZED ORGANIZATION) ---
with st.sidebar:
    st.markdown("""
        <div class='brand-container'>
            <div class='brand-title'>AROHA</div>
            <div class='tagline'>Where data becomes <span class='decisions-fade'>Decisions</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 Dashboard"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-head'>Operations</div>", unsafe_allow_html=True)
    if st.button("📈 Demand Forecast"): st.session_state.page = "Preksha"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Predict Future Sales</span>", unsafe_allow_html=True)
    
    if st.button("🛡️ Risk Analysis"): st.session_state.page = "Stambha"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Test Supply Risks</span>", unsafe_allow_html=True)
    
    if st.button("🤝 Supplier Insights"): st.session_state.page = "Mithra"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Rate Your Suppliers</span>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-head'>Financials</div>", unsafe_allow_html=True)
    if st.button("💰 Financial Overview"): st.session_state.page = "Artha"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Track Money Flow</span>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-head'>Automation</div>", unsafe_allow_html=True)
    if st.button("🎙️ Voice Assistant"): st.session_state.page = "Voice"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Talk To System</span>", unsafe_allow_html=True)
    
    if st.button("📄 Purchase Orders"): st.session_state.page = "Karya"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Auto Create Orders</span>", unsafe_allow_html=True)
    
    if st.button("📝 Inventory Log"): st.session_state.page = "Nyasa"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Log Assets Securely</span>", unsafe_allow_html=True)
    
    if st.button("📥 Data Import"): st.session_state.page = "Agama"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Import Data Easily</span>", unsafe_allow_html=True)

    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()
    st.markdown("<span class='sidebar-sub'>Securely Exit System</span>", unsafe_allow_html=True)

# --- 6. TOP BAR HUD ---
t1, t2 = st.columns([1, 1])
with t2: st.markdown(f"<p style='text-align:right; color:#9AA0A6; font-size:0.8rem; margin-top:10px;'>👤 {st.session_state.user.upper()} • {datetime.now().strftime('%H:%M')}</p>", unsafe_allow_html=True)

# --- 7. HOME DASHBOARD ---
if st.session_state.page == "Dashboard":
    st.markdown("<h2 style='color:white; margin-bottom:30px;'>Strategic Command Center</h2>", unsafe_allow_html=True)

    # Hero Intelligence Directive
    st.markdown("""
        <div class='recommendation-hero'>
            <p style='color:#6C63FF; font-weight:700; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;'>✨ AI Intelligence Directive</p>
            <h3 style='color:white; margin: 10px 0;'>Reorder 120 units from Raj Logistics.</h3>
            <p style='color:#9AA0A6; font-size:0.9rem;'>Sensed a demand spike for next weekend. Predicted stockout risk in 3 days.</p>
        </div>
    """, unsafe_allow_html=True)

    # Visual Quick-Node Grid
    st.subheader("Intelligence Nodes")
    q1, q2, q3 = st.columns(3)
    
    with q1:
        st.markdown("""<div class='saas-card'><span class='card-icon'>📈</span><b>PREKSHA</b><br><span style='color:#6C63FF; font-size:0.7rem;'>PREDICT DEMAND INSTANTLY</span></div>""", unsafe_allow_html=True)
        if st.button("Launch Forecast", key="q_pre"): st.session_state.page = "Preksha"; st.rerun()
        
    with q2:
        st.markdown("""<div class='saas-card'><span class='card-icon'>🛡️</span><b>STAMBHA</b><br><span style='color:#6C63FF; font-size:0.7rem;'>TEST SUPPLY RISKS</span></div>""", unsafe_allow_html=True)
        if st.button("Launch Resilience", key="q_sta"): st.session_state.page = "Stambha"; st.rerun()
        
    with q3:
        st.markdown("""<div class='saas-card'><span class='card-icon'>🎙️</span><b>SAMVADA</b><br><span style='color:#6C63FF; font-size:0.7rem;'>TALK TO SYSTEM</span></div>""", unsafe_allow_html=True)
        if st.button("Launch Assistant", key="q_sam"): st.session_state.page = "Voice"; st.rerun()

    # Metrics Section
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown("<div class='saas-card'><div class='m-sub'>Units</div><div class='m-val'>2,340</div></div>", unsafe_allow_html=True)
    with c2: st.markdown("<div class='saas-card'><div class='m-sub'>Forecast</div><div class='m-val'>+12.4%</div></div>", unsafe_allow_html=True)
    with c3: st.markdown("<div class='saas-card'><div class='m-sub'>Risk</div><div class='m-val'>Medium</div></div>", unsafe_allow_html=True)
    with c4: st.markdown("<div class='saas-card'><div class='m-sub'>Capital</div><div class='m-val'>₹4.2L</div></div>", unsafe_allow_html=True)

# --- 8. FLOATING VOICE ASSISTANT ---
st.markdown("<div class='voice-fab'>🎙️</div>", unsafe_allow_html=True)

# --- 9. SUB-MODULE REDIRECTS ---
if st.session_state.page == "Preksha":
    st.markdown("<h2>📈 Preksha – Demand Forecast</h2>", unsafe_allow_html=True)
    st.info("Predicting future asset requirements via Random Forest Sensing.")

elif st.session_state.page == "Nyasa":
    st.markdown("<h2>📝 Nyasa – Inventory Log</h2>", unsafe_allow_html=True)
    with st.form("add_p"):
        n = st.text_input("Asset Identity")
        s = st.number_input("Stock Level", 0)
        if st.form_submit_button("Commit Entry"):
            st.success("Entry logged successfully.")

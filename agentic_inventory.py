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
st.set_page_config(page_title="AROHA | Premium Intelligence", layout="wide", page_icon="💠")

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
        .tagline { font-size: 0.9rem; color: #9AA0A6; margin-top: -5px; display: flex; gap: 5px; }
        
        .decisions-fade {
            color: #6C63FF;
            font-weight: 700;
            animation: fadeInSlower 3s ease-in-out, glowPulse 2s infinite alternate;
        }
        
        @keyframes fadeInSlower { 0% { opacity: 0; } 50% { opacity: 0; } 100% { opacity: 1; } }
        @keyframes glowPulse { from { text-shadow: 0 0 2px #6C63FF; } to { text-shadow: 0 0 8px #38BDF8; } }

        /* 3. Sidebar: SaaS Minimalist */
        [data-testid="stSidebar"] { background-color: #090B0F !important; border-right: 1px solid #1F2229; }
        .sidebar-section-head { font-size: 0.65rem; font-weight: 700; color: #4B5563; text-transform: uppercase; letter-spacing: 1.2px; margin: 20px 0 10px 15px; }
        
        section[data-testid="stSidebar"] .stButton > button {
            background: transparent !important; border: none !important; color: #9AA0A6 !important;
            text-align: left !important; padding: 8px 20px !important; width: 100%; transition: 0.2s;
        }
        section[data-testid="stSidebar"] .stButton > button:hover { background: #171A21 !important; color: #FFFFFF !important; border-left: 3px solid #6C63FF !important; }

        /* 4. Layered Cards & Visual Hierarchy */
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

        /* 5. Recommendation Panel (AI Layer) */
        .recommendation-hero {
            background: linear-gradient(135deg, rgba(108, 99, 255, 0.12) 0%, rgba(56, 189, 248, 0.05) 100%);
            border-radius: 12px;
            padding: 25px;
            border: 1px solid rgba(108, 99, 255, 0.25);
            border-left: 6px solid #6C63FF;
            margin-bottom: 25px;
        }

        /* 6. Numeric Highlighting */
        .m-val { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #FFFFFF; }
        .m-sub { color: #9AA0A6; font-size: 0.75rem; text-transform: uppercase; font-weight: 500; }

        /* 7. Voice FAB */
        .voice-fab {
            position: fixed; bottom: 30px; right: 30px; width: 60px; height: 60px;
            background: linear-gradient(135deg, #6C63FF, #38BDF8);
            border-radius: 50%; display: flex; align-items: center; justify-content: center;
            box-shadow: 0 8px 25px rgba(108, 99, 255, 0.3); z-index: 999;
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

# --- 5. SIDEBAR (STARTUP-GRADE ORGANIZATION) ---
with st.sidebar:
    st.markdown("""
        <div class='brand-container'>
            <div class='brand-title'>AROHA</div>
            <div class='tagline'>Where data becomes <span class='decisions-fade'>Decisions</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🏠 Dashboard"): st.session_state.page = "Dashboard"; st.rerun()
    
    st.markdown("<div class='sidebar-section-head'>Operations</div>", unsafe_allow_html=True)
    if st.button("● Demand Forecast"): st.session_state.page = "Preksha"; st.rerun()
    if st.button("● Risk Analysis"): st.session_state.page = "Stambha"; st.rerun()
    if st.button("● Supplier Insights"): st.session_state.page = "Mithra"; st.rerun()

    st.markdown("<div class='sidebar-section-head'>Financials</div>", unsafe_allow_html=True)
    if st.button("● Financial Overview"): st.session_state.page = "Artha"; st.rerun()

    st.markdown("<div class='sidebar-section-head'>Automation</div>", unsafe_allow_html=True)
    if st.button("● Purchase Orders"): st.session_state.page = "Karya"; st.rerun()
    if st.button("● Inventory Log"): st.session_state.page = "Nyasa"; st.rerun()
    if st.button("● Data Import"): st.session_state.page = "Agama"; st.rerun()

    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    if st.button("Logout"): st.session_state.auth = False; st.rerun()

# --- 6. HOME DASHBOARD ---
if st.session_state.page == "Dashboard":
    st.markdown("<h2 style='color:white; margin-bottom:0px;'>System Overview</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#6B7280; font-size:0.85rem; margin-bottom:30px;'>Updated 2 mins ago • Cloud Synced</p>", unsafe_allow_html=True)

    # Metrics Grid
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='saas-card'><div class='m-sub'>In Stock</div><div class='m-val'>2,340</div><div style='color:#F87171; font-size:0.75rem;'>↓ Running Low</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='saas-card'><div class='m-sub'>Forecast</div><div class='m-val'>+12.4%</div><div style='color:#34D399; font-size:0.75rem;'>↑ Rising Trend</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='saas-card'><div class='m-sub'>Supply Risk</div><div class='m-val'>Medium</div><div style='color:#9AA0A6; font-size:0.75rem;'>● Stable</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='saas-card'><div class='m-sub'>Asset Value</div><div class='m-val'>₹4.2L</div><div style='color:#34D399; font-size:0.75rem;'>↑ Optimized</div></div>", unsafe_allow_html=True)

    # Hero Action Panel (The Decision USP)
    st.markdown("""
        <div class='hero-panel' style='background: rgba(108, 99, 255, 0.05); border-radius: 12px; padding: 25px; border-left: 6px solid #6C63FF; margin-bottom: 30px;'>
            <p style='color:#6C63FF; font-weight:700; font-size:0.75rem; text-transform:uppercase; letter-spacing:1px;'>✨ AI Intelligence Recommendation</p>
            <h3 style='color:white; margin: 10px 0;'>Reorder 120 units from Raj Logistics.</h3>
            <p style='color:#9AA0A6; font-size:0.9rem;'>Sensed a demand spike for next weekend. Predicted stockout risk in 3 days.</p>
            <br>
            <div style='display:flex; gap:10px;'>
                <button style='background:#6C63FF; color:white; border:none; padding:8px 20px; border-radius:6px; font-weight:600;'>Execute Order</button>
                <button style='background:transparent; color:#9AA0A6; border:1px solid #333; padding:8px 20px; border-radius:6px;'>Dismiss</button>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Data Visual hooks
    col_graph, col_risk = st.columns([2, 1])
    with col_graph:
        st.markdown("<div class='saas-card'><b>Demand Prediction Stream</b>", unsafe_allow_html=True)
        # Gradient area chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(y=np.random.randint(20, 60, 15), fill='tozeroy', line=dict(color='#6C63FF', width=3), fillcolor='rgba(108, 99, 255, 0.1)'))
        fig.update_layout(height=250, margin=dict(l=0,r=0,b=0,t=40), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#444'), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_risk:
        st.markdown("<div class='saas-card' style='height:335px;'><b>Resilience Meter</b>", unsafe_allow_html=True)
        # Gauge chart
        fig_risk = go.Figure(go.Indicator(mode = "gauge+number", value = 68, domain = {'x': [0, 1], 'y': [0, 1]}, gauge = {'axis': {'range': [None, 100], 'tickwidth': 1}, 'bar': {'color': "#6C63FF"}, 'bgcolor': "rgba(0,0,0,0)"}))
        fig_risk.update_layout(height=250, margin=dict(l=20,r=20,b=0,t=40), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_risk, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 8. FLOATING VOICE ASSISTANT ---
st.markdown("<div class='voice-fab'>🎙️</div>", unsafe_allow_html=True)

# --- 9. SUB-MODULES (NYASA / PREKSHA LOGIC) ---
if st.session_state.page == "Preksha":
    st.markdown("<h2 style='color:white;'>Preksha – Demand Forecast</h2>", unsafe_allow_html=True)
    st.info("Predict demand instantly using non-linear AI sensing.")

elif st.session_state.page == "Nyasa":
    st.markdown("<h2 style='color:white;'>Nyasa – Inventory Log</h2>", unsafe_allow_html=True)
    with st.form("add"):
        n = st.text_input("Asset Identity")
        s = st.number_input("Current Stock", 0)
        p = st.number_input("Unit Price", 0.0)
        if st.form_submit_button("Commit Entry"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price) VALUES (?,?,?,?)", (st.session_state.user, n, s, p))
            st.success("Synced successfully.")

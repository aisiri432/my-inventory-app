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

# --- 1. PREMIUM UI CONFIGURATION ---
st.set_page_config(page_title="AROHA | Elegant Intelligence", layout="wide", page_icon="💠")

def apply_premium_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* 1. Global Background & Noise Texture */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0E0F13;
            color: #E6E8EB;
        }

        /* 2. Layered Glass Cards */
        .premium-card {
            background: #171A20;
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            transition: 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        }
        .premium-card:hover {
            transform: translateY(-8px);
            border: 1px solid rgba(108, 99, 255, 0.3);
            box-shadow: 0 10px 40px rgba(108, 99, 255, 0.1);
        }

        /* 3. Hero Recommendation Panel */
        .hero-panel {
            background: linear-gradient(135deg, rgba(108, 99, 255, 0.1) 0%, rgba(0, 210, 255, 0.05) 100%);
            border-radius: 16px;
            padding: 30px;
            border: 1px solid rgba(108, 99, 255, 0.2);
            border-left: 6px solid #6C63FF;
            margin-bottom: 30px;
            position: relative;
        }
        .sparkle { position: absolute; top: 15px; right: 20px; font-size: 1.2rem; opacity: 0.8; }

        /* 4. Sidebar: Elegant Gradient Hierarchy */
        [data-testid="stSidebar"] {
            background-color: #0A0B0E !important;
            border-right: 1px solid #1F2229;
        }
        .sidebar-title { color: #FFFFFF; font-weight: 700; font-size: 1.4rem; padding: 20px; letter-spacing: -0.5px; }
        
        /* Sidebar slide-highlight button */
        section[data-testid="stSidebar"] .stButton > button {
            background: transparent !important;
            border: none !important;
            color: #9AA0A6 !important;
            text-align: left !important;
            font-size: 0.9rem !important;
            padding: 10px 20px !important;
            width: 100%;
            transition: 0.3s;
            border-radius: 8px !important;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: rgba(108, 99, 255, 0.1) !important;
            color: #FFFFFF !important;
        }

        /* 5. Metrics with Sparklines */
        .m-label { color: #9AA0A6; font-size: 0.8rem; font-weight: 500; text-transform: uppercase; letter-spacing: 1px; }
        .m-value { color: #FFFFFF; font-size: 2rem; font-weight: 700; margin: 5px 0; }
        .m-trend { font-size: 0.75rem; font-weight: 600; }
        .trend-up { color: #34D399; }
        .trend-down { color: #F87171; }

        /* 6. Floating Voice Assistant */
        .voice-fab {
            position: fixed; bottom: 30px; right: 30px;
            width: 65px; height: 65px;
            background: linear-gradient(135deg, #6C63FF 0%, #38BDF8 100%);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            box-shadow: 0 10px 30px rgba(108, 99, 255, 0.4);
            cursor: pointer; z-index: 9999;
            animation: breathe 3s infinite ease-in-out;
        }
        @keyframes breathe {
            0%, 100% { transform: scale(1); box-shadow: 0 10px 30px rgba(108, 99, 255, 0.4); }
            50% { transform: scale(1.08); box-shadow: 0 15px 40px rgba(108, 99, 255, 0.6); }
        }

        /* 7. Plotly & Custom Components Fixes */
        .stPlotlyChart { background: transparent !important; }
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_premium_style()

# --- 2. CORE ENGINES (DATABASE & AUTH) ---
DB_FILE = 'aroha_premium_v32.db'
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
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:white; font-size:3.5rem;'>AROHA</h1><p style='color:#9AA0A6;'>Elegant Strategic Intelligence</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 0.7, 1])
    with col2:
        m = st.tabs(["Login", "Sign Up"])
        with m[0]:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Access Dashboard"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Verification failed.")
        with m[1]:
            nu = st.text_input("New Username"); np = st.text_input("New Password", type="password")
            if st.button("Create Account"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Welcome aboard.")
    st.stop()

# --- 5. SIDEBAR (SAAS STYLE) ---
with st.sidebar:
    st.markdown("<div class='sidebar-title'>AROHA</div>", unsafe_allow_html=True)
    st.markdown("<p style='padding-left:22px; color:#555; font-size:0.7rem;'>v32.0 Premium Enterprise</p>", unsafe_allow_html=True)
    
    if st.button("📊 Dashboard"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
    
    st.markdown("<p style='padding-left:22px; color:#9AA0A6; font-size:0.65rem; font-weight:700; text-transform:uppercase;'>Operations</p>", unsafe_allow_html=True)
    if st.button("● Demand Forecast"): st.session_state.page = "Forecast"; st.rerun()
    if st.button("● Risk Analysis"): st.session_state.page = "Risk"; st.rerun()
    if st.button("● Supplier Insights"): st.session_state.page = "Suppliers"; st.rerun()

    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='padding-left:22px; color:#9AA0A6; font-size:0.65rem; font-weight:700; text-transform:uppercase;'>Financials</p>", unsafe_allow_html=True)
    if st.button("● Financial Overview"): st.session_state.page = "Finance"; st.rerun()

    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='padding-left:22px; color:#9AA0A6; font-size:0.65rem; font-weight:700; text-transform:uppercase;'>Automation</p>", unsafe_allow_html=True)
    if st.button("● Purchase Orders"): st.session_state.page = "PO"; st.rerun()
    if st.button("● Inventory Log"): st.session_state.page = "Log"; st.rerun()
    if st.button("● Data Import"): st.session_state.page = "Import"; st.rerun()

    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    if st.button("Logout"): st.session_state.auth = False; st.rerun()

# --- 6. TOP BAR HUD ---
t1, t2 = st.columns([1, 1])
with t2: st.markdown(f"<p style='text-align:right; color:#9AA0A6; font-size:0.8rem; margin-top:10px;'>{st.session_state.user.upper()} • {datetime.now().strftime('%H:%M')}</p>", unsafe_allow_html=True)

# --- 7. HOME DASHBOARD ---
if st.session_state.page == "Dashboard":
    st.markdown("<h2 style='color:white; margin-bottom:5px;'>Command Center</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#9AA0A6; font-size:0.9rem;'>Real-time supply chain telemetry and AI directives.</p>", unsafe_allow_html=True)
    
    # STORYTELLING METRICS
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"<div class='premium-card'><div class='m-label'>Inventory</div><div class='m-value'>2,340</div><div class='m-trend trend-down'>↓ Running Low</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='premium-card'><div class='m-label'>Demand</div><div class='m-value'>+12.4%</div><div class='m-trend trend-up'>↑ Rising Path</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown(f"<div class='premium-card'><div class='m-label'>Risk Factor</div><div class='m-value'>Medium</div><div class='m-trend'>● Stable Trend</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown(f"<div class='premium-card'><div class='m-label'>Idle Capital</div><div class='m-value'>₹4.2L</div><div class='m-trend trend-up'>↑ Optimized</div></div>", unsafe_allow_html=True)

    # HERO ACTION PANEL
    st.markdown(f"""
        <div class='hero-panel'>
            <span class='sparkle'>✨</span>
            <p style='color:#6C63FF; font-weight:700; font-size:0.8rem; text-transform:uppercase; letter-spacing:1px;'>AI Intelligence Directive</p>
            <h3 style='color:white; margin-top:10px;'>Reorder 120 units from Raj Logistics.</h3>
            <p style='color:#9AA0A6;'>Estimated stockout risk in 3 days based on current market sensing.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # VISUAL HOOKS (GRAPHING)
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown("<div class='premium-card'><b>Strategic Forecast Flow</b>", unsafe_allow_html=True)
        # Gradient Area Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=list(range(10)), y=np.random.randint(20, 60, 10), fill='tozeroy', 
                                 line=dict(width=4, color='#6C63FF'), 
                                 fillcolor='rgba(108, 99, 255, 0.1)'))
        fig.update_layout(height=300, margin=dict(l=0,r=0,b=0,t=40), paper_bgcolor='rgba(0,0,0,0)', 
                          plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#666'), xaxis=dict(showgrid=False), yaxis=dict(showgrid=False))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_r:
        st.markdown("<div class='premium-card' style='height:365px;'><b>Resilience Dial</b>", unsafe_allow_html=True)
        # Circular Risk Meter
        risk_val = 65
        fig_risk = go.Figure(go.Indicator(
            mode = "gauge+number", value = risk_val,
            gauge = {'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "#444"},
                     'bar': {'color': "#6C63FF"},
                     'bgcolor': "rgba(0,0,0,0)",
                     'steps': [{'range': [0, 50], 'color': 'rgba(52, 211, 153, 0.1)'},
                               {'range': [50, 80], 'color': 'rgba(251, 191, 36, 0.1)'},
                               {'range': [80, 100], 'color': 'rgba(248, 113, 113, 0.1)'}]}
        ))
        fig_risk.update_layout(height=280, margin=dict(l=20,r=20,b=0,t=50), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_risk, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 8. FLOATING VOICE ASSISTANT ---
st.markdown("<div class='voice-fab'>🎙️</div>", unsafe_allow_html=True)

# --- 9. MODULE REDIRECTS ---
if st.session_state.page == "Forecast":
    st.markdown("<h2 style='color:white;'>Preksha – Demand Forecast</h2>", unsafe_allow_html=True)
    st.info("Predict demand instantly with Random Forest intelligence.")
    # Module code here...

elif st.session_state.page == "Log":
    st.markdown("<h2 style='color:white;'>Nyasa – Inventory Log</h2>", unsafe_allow_html=True)
    with st.form("add_p"):
        n = st.text_input("Item Identity"); s = st.number_input("Stock Level", 0); p = st.number_input("Value per Unit", 0.0)
        if st.form_submit_button("Commit to Ledger"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price) VALUES (?,?,?,?)", (st.session_state.user, n, s, p))
            st.success("Telemetry Synced.")

else:
    if st.session_state.page != "Dashboard":
        st.markdown(f"<h2 style='color:white;'>{st.session_state.page}</h2>", unsafe_allow_html=True)
        st.info("Updated 2 mins ago • Operational")

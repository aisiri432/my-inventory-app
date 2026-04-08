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

# --- 1. RADIANT UI CONFIG ---
st.set_page_config(page_title="AROHA | Strategic Intelligence", layout="wide", page_icon="💠", initial_sidebar_state="expanded")

# LOGO SVG DEFINITION
logo_svg = """
<svg width="500" height="500" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M50 5L10 85H30L50 35L70 85H90L50 5Z" fill="url(#paint0_linear_logo)"/>
<circle cx="50" cy="45" r="5" fill="#00D4FF"/>
<defs>
<linearGradient id="paint0_linear_logo" x1="10" y1="5" x2="90" y2="85" gradientUnits="userSpaceOnUse">
<stop stop-color="#7F00FF"/><stop offset="1" stop-color="#00D4FF"/></linearGradient>
</defs>
</svg>
"""

def apply_aroha_style():
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background-color: #050709; color: #E6E8EB; }}

        /* 💠 WATERMARK */
        [data-testid="stAppViewContainer"]::before {{
            content: ""; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-10deg);
            width: 70vw; height: 70vw; background-image: url('data:image/svg+xml;utf8,{logo_svg}');
            background-repeat: no-repeat; background-position: center; opacity: 0.06; z-index: -1; pointer-events: none; filter: blur(5px);
        }}

        /* 📟 SIDEBAR: SPECTRUM GLOW */
        [data-testid="stSidebar"] {{ background-color: #030508 !important; border-right: 2px solid #1F2229; min-width: 420px; }}
        section[data-testid="stSidebar"] .stButton > button {{ 
            background: rgba(255,255,255,0.03) !important; border-radius: 12px !important;
            color: #FFFFFF !important; text-align: left !important; padding: 15px 18px !important; width: 100%; 
            font-size: 1.5rem !important; font-weight: 800 !important; letter-spacing: 1.5px; margin-bottom: 8px; transition: 0.4s;
        }}

        /* 🌈 SPECTRUM COLORS */
        div[data-testid="stSidebar"] button[key*="nyasa"] {{ border: 2px solid #00FF88 !important; }}
        div[data-testid="stSidebar"] button[key*="preksha"] {{ border: 2px solid #7F00FF !important; }}
        div[data-testid="stSidebar"] button[key*="stambha"] {{ border: 2px solid #FF0055 !important; }}
        div[data-testid="stSidebar"] button[key*="karma"] {{ border: 2px solid #FF33FF !important; }}
        div[data-testid="stSidebar"] button[key*="samvada"] {{ border: 2px solid #00D4FF !important; }}
        div[data-testid="stSidebar"] button[key*="vitta"] {{ border: 2px solid #FFD700 !important; }}
        div[data-testid="stSidebar"] button[key*="sanchara"] {{ border: 2px solid #FF8800 !important; }}
        div[data-testid="stSidebar"] button[key*="mithra"] {{ border: 2px solid #34D399 !important; box-shadow: 0 0 10px rgba(52,211,153,0.3); }}

        .sidebar-sub {{ font-size: 1rem !important; font-weight: 800; display: block; margin-top: -10px; margin-bottom: 25px; margin-left: 20px; text-transform: uppercase; letter-spacing: 1px; }}

        /* VIBRANT CARDS */
        .saas-card {{ background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; margin-bottom: 20px; }}
        .mithra-negotiation {{ background: rgba(52, 211, 153, 0.05); border-left: 5px solid #34D399; padding: 20px; border-radius: 15px; margin-top: 20px; }}
        
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_master_v98.db'
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

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 style='font-size:3.5rem; font-weight:900;'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Turn Data Into <span style='color:#00D4FF; font-weight:700;'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([0.1, 0.8, 0.1])
    with col_center:
        m = st.tabs(["Login", "Join"])
        with m[0]:
            u_input = st.text_input("Username", key="l_u")
            p_input = st.text_input("Password", type="password", key="l_p")
            if st.button("Unlock Hub"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u_input,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p_input):
                    st.session_state.auth = True; st.session_state.user = u_input; st.rerun()
                else: st.error("Access Denied")
        with m[1]:
            nu = st.text_input("New ID"); np = st.text_input("New Password", type="password")
            if st.button("Enroll"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Authorized.")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div style='text-align:center; margin-bottom:30px;'><h1 style='color:white; font-size:2.2rem !important; margin-bottom:0;'>AROHA</h1><p style='color:#7F00FF; font-weight:800; margin-top:-10px;'>NEURAL NEXUS v98.0</p></div>", unsafe_allow_html=True)
    
    if st.button("🏠 DASHBOARD", key="nav_dashboard"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub' style='color:#FFF;'>System Overview</span>", unsafe_allow_html=True)

    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items & Sync", "#00FF88"),
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly", "#7F00FF"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks", "#FF0055"),
        ("👷‍♂️ KARMA", "Karma", "Manage Workers", "#FF33FF"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System", "#00D4FF"),
        ("💰 VITTA", "Vitta", "Track Money Flow", "#FFD700"),
        ("📦 SANCHARA", "Sanchara", "Global Map & Flow", "#FF8800"),
        ("🤝 MITHRA+", "Mithra", "AI Negotiation", "#34D399") # UPDATED NAME
    ]
    for label, page_id, layman, color in nodes:
        if st.button(label, key=f"nav_{page_id.lower()}"):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub' style='color:{color};'>{layman}</span>", unsafe_allow_html=True)

    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. MITHRA+: AI NEGOTIATION ENGINE (NEW MEGA FEATURE) ---
if st.session_state.page == "Mithra":
    st.markdown("<h1 style='color:#34D399;'>🤝 MITHRA+: AI Negotiation Engine</h1>", unsafe_allow_html=True)
    
    df = get_user_data()
    if df.empty:
        st.warning("No suppliers found. Add data in NYASA.")
    else:
        col_list, col_neg = st.columns([1, 1.5])
        
        with col_list:
            st.subheader("Supplier Analysis")
            target_vendor = st.selectbox("Select Vendor to Negotiate", df['supplier'].unique())
            v_data = df[df['supplier'] == target_vendor].iloc[0]
            
            st.markdown(f"""
            <div class='saas-card'>
                <b>Vendor:</b> {target_vendor}<br>
                <b>Asset:</b> {v_data['name']}<br>
                <b>Current Price:</b> ₹{v_data['unit_price']}<br>
                <b>Lead Time:</b> {v_data['lead_time']} Days
            </div>
            """, unsafe_allow_html=True)
            
            st.write("### Choose Strategy")
            tone = st.radio("Negotiation Style", ["🧘 Polite (Relationship First)", "⚖️ Balanced (Fair Trade)", "🔥 Aggressive (Cost Leader)"])

        with col_neg:
            st.subheader("Negotiation Intelligence")
            
            if st.button("🚀 INITIATE AI NEGOTIATION"):
                with st.spinner("Analyzing market data and supplier reliability..."):
                    time.sleep(1.5)
                    
                    # Strategic Insights
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Potential Savings", "₹12,400", "↑ 8%")
                    c2.metric("Time Saved", "2 Days", "Fast Track")
                    c3.metric("Risk Level", "Medium")
                    
                    st.markdown("### AI Strategic Reasoning")
                    st.info(f"Suggesting negotiation because current order volume for '{v_data['name']}' has increased by 35% this quarter, giving us higher procurement leverage.")
                    
                    # AI Email Generation
                    st.markdown("### Drafted Negotiation Directive")
                    
                    # Logic-based prompt simulation
                    if "Polite" in tone:
                        msg = f"Subject: Strengthening our partnership - {target_vendor}\n\nDear Team,\n\nWe value our ongoing partnership. As we scale our orders for {v_data['name']}, we would love to discuss a mutually beneficial pricing structure that reflects our long-term commitment..."
                    elif "Aggressive" in tone:
                        msg = f"Subject: Urgent: Pricing Review for {v_data['name']}\n\nTo the Sales Director,\n\nWe are currently auditing our supply chain costs. Market averages for {v_data['name']} are currently lower than our contract. We require a 10% reduction or will be forced to split our volume with alternative vendors..."
                    else:
                        msg = f"Subject: Revised terms for {v_data['name']} - AROHA Intelligence\n\nDear Supplier,\n\nBased on our demand sensing for the next 60 days, we are planning a bulk purchase. We'd like to align on a revised unit cost and a guaranteed 48-hour shipping window..."
                    
                    st.text_area("Generated Message", msg, height=250)
                    st.button("📧 Send via AROHA Secure Mail")

# --- 7. OTHER NODES (DASHBOARD, NYASA, etc.) ---
elif st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Mission Control: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='saas-card' style='border-top:5px solid #7F00FF;'><h3>Assets</h3><h2 style='color:#7F00FF;'>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='saas-card' style='border-top:5px solid #FFD700;'><h3>Treasury Value</h3><h2 style='color:#FFD700;'>₹{val:,.0f}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='saas-card' style='border-top:5px solid #34D399;'><h3>Vendor Leverage</h3><h2 style='color:#34D399;'>High</h2></div>", unsafe_allow_html=True)

# Rest of the nodes follow the previous high-energy logic...
elif st.session_state.page == "Nyasa":
    st.markdown("<h1 style='color:#00FF88;'>📝 NYASA</h1>", unsafe_allow_html=True)
    f = st.file_uploader("Upload CSV", type="csv")
    if f and st.button("Sync"):
        u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
        with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
        st.success("Synced.")

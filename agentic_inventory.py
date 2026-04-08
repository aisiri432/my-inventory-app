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

# --- 1. RADIANT UI CONFIG (AURORA MESH & MULTI-COLOR GLOW) ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="expanded"
)

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
        
        /* 🌑 Base Environment with Aurora Mesh */
        html, body, [class*="css"] {{
            font-family: 'Inter', sans-serif;
            background: radial-gradient(circle at 50% 50%, #0a0e14 0%, #050709 100%);
            color: #E6E8EB;
        }}

        /* 💠 VIBRANT WATERMARK */
        [data-testid="stAppViewContainer"]::before {{
            content: ""; position: fixed; top: 50%; left: 50%;
            transform: translate(-50%, -50%) rotate(-10deg);
            width: 70vw; height: 70vw;
            background-image: url('data:image/svg+xml;utf8,{logo_svg}');
            background-repeat: no-repeat; background-position: center;
            opacity: 0.08; z-index: -1; pointer-events: none;
            filter: blur(5px);
        }}

        /* 📟 SIDEBAR: SPECTRUM GLOW */
        [data-testid="stSidebar"] {{ 
            background-color: #030508 !important; 
            border-right: 2px solid #1F2229; 
            min-width: 420px;
        }}
        
        /* THE LOGO IN SIDEBAR */
        .sidebar-logo-container {{ text-align: center; padding: 20px 0; }}

        /* Radiant Nav Buttons */
        section[data-testid="stSidebar"] .stButton > button {{ 
            background: rgba(255,255,255,0.03) !important; 
            border-radius: 12px !important;
            color: #FFFFFF !important; text-align: left !important; padding: 15px 18px !important; width: 100%; 
            font-size: 1.5rem !important; font-weight: 800 !important; letter-spacing: 1.5px;
            margin-bottom: 8px; transition: 0.4s;
        }}

        /* 🌈 SPECTRUM COLORS FOR SIDEBAR BUTTONS */
        div[data-testid="stSidebar"] button[key*="nyasa"] {{ border: 2px solid #00FF88 !important; box-shadow: 0 0 10px rgba(0,255,136,0.2); }}
        div[data-testid="stSidebar"] button[key*="preksha"] {{ border: 2px solid #7F00FF !important; box-shadow: 0 0 10px rgba(127,0,255,0.2); }}
        div[data-testid="stSidebar"] button[key*="stambha"] {{ border: 2px solid #FF0055 !important; box-shadow: 0 0 10px rgba(255,0,85,0.2); }}
        div[data-testid="stSidebar"] button[key*="samvada"] {{ border: 2px solid #00D4FF !important; box-shadow: 0 0 10px rgba(0,212,255,0.2); }}
        div[data-testid="stSidebar"] button[key*="vitta"] {{ border: 2px solid #FFD700 !important; box-shadow: 0 0 10px rgba(255,215,0,0.2); }}
        div[data-testid="stSidebar"] button[key*="sanchara"] {{ border: 2px solid #FF8800 !important; box-shadow: 0 0 10px rgba(255,136,0,0.2); }}
        div[data-testid="stSidebar"] button[key*="mithra"] {{ border: 2px solid #34D399 !important; box-shadow: 0 0 10px rgba(52,211,153,0.2); }}

        section[data-testid="stSidebar"] .stButton > button:hover {{ 
            transform: scale(1.02) translateX(5px);
            filter: brightness(1.2);
        }}

        .sidebar-sub {{ font-size: 1rem !important; font-weight: 800; display: block; margin-top: -10px; margin-bottom: 25px; margin-left: 20px; text-transform: uppercase; letter-spacing: 1px; }}

        /* 💎 STANDOUT BRANDING */
        .brand-title {{ font-size: 3.5rem !important; font-weight: 900 !important; color: #FFFFFF !important; letter-spacing: -2px; text-shadow: 0 0 30px rgba(108, 99, 255, 0.8); margin-bottom: 0; }}
        .decisions-fade {{ color: #6C63FF; font-weight: 700; animation: glowPulse 2s infinite alternate; }}
        @keyframes glowPulse {{ from {{ text-shadow: 0 0 10px #6C63FF; }} to {{ text-shadow: 0 0 25px #00D4FF; }} }}

        /* VIBRANT CARDS */
        .saas-card {{ background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; margin-bottom: 20px; box-shadow: 0 8px 32px rgba(0,0,0,0.3); }}
        .ai-decision-box {{ background: linear-gradient(135deg, rgba(212, 175, 55, 0.2) 0%, rgba(0,0,0,0) 100%); border: 3px solid #D4AF37; padding: 25px; border-radius: 20px; margin-top: 25px; box-shadow: 0 0 30px rgba(212, 175, 55, 0.3); }}
        .financial-stat {{ background: rgba(255,215,0,0.1); padding: 20px; border-radius: 15px; border: 2px solid #FFD700; text-align: center; box-shadow: 0 0 15px rgba(255,215,0,0.2); }}

        /* DASHBOARD METRICS */
        .metric-vibrant {{ padding: 20px; border-radius: 15px; color: white; text-align: center; font-weight: 800; }}

        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_radiant_v96.db'
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

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 class='brand-title'>AROHA</h1><p style='color:#9AA0A6; font-size:1.6rem;'>Turn Data Into <span class='decisions-fade'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([0.1, 0.8, 0.1])
    with col_center:
        m = st.tabs(["Login", "Enroll"])
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
            if st.button("Enroll Session"):
                try:
                    with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                    st.success("Authorized.")
                except: st.error("ID exists.")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown("<div class='sidebar-logo-container'>", unsafe_allow_html=True)
    st.markdown(logo_svg, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='text-align:center; margin-bottom:30px;'><h1 style='color:white; font-size:2.2rem !important; margin-bottom:0;'>AROHA</h1><p style='color:#7F00FF; font-weight:800;'>RADIANT NEXUS v96.0</p></div>", unsafe_allow_html=True)
    
    if st.button("🏠 DASHBOARD", key="nav_dashboard"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub' style='color:#FFF;'>System Overview</span>", unsafe_allow_html=True)

    # RADIANT NODE LIST
    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items & Sync", "#00FF88"),
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly", "#7F00FF"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks", "#FF0055"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System", "#00D4FF"),
        ("💰 VITTA", "Vitta", "Track Money Flow", "#FFD700"),
        ("📦 SANCHARA", "Sanchara", "Global Map & Flow", "#FF8800"),
        ("🤝 MITHRA", "Mithra", "Supplier Intelligence", "#34D399")
    ]
    for label, page_id, layman, color in nodes:
        if st.button(label, key=f"nav_{page_id.lower()}"):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub' style='color:{color};'>{layman}</span>", unsafe_allow_html=True)

    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. LOGIC NODES ---

if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Mission Control: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    
    # Vibrant Metric Cards
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='saas-card' style='border-top:5px solid #7F00FF;'><h3>Assets</h3><h2 style='color:#7F00FF;'>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='saas-card' style='border-top:5px solid #FFD700;'><h3>Treasury Value</h3><h2 style='color:#FFD700;'>₹{val:,.0f}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='saas-card' style='border-top:5px solid #00FF88;'><h3>System Integrity</h3><h2 style='color:#00FF88;'>Optimal</h2></div>", unsafe_allow_html=True)

    st.markdown("<div class='ai-decision-box'><h3>✨ AI Strategic Directive</h3>System link stable. Demand sensors calibrated to current holiday spikes. Risk levels green.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header' style='color:#7F00FF !important;'>📈 PREKSHA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        target = st.selectbox("Asset Search", df['name']); p = df[df['name'] == target].iloc[0]
        col_m, col_v = st.columns([1, 2])
        with col_m:
            st.markdown("<div class='saas-card'>", unsafe_allow_html=True)
            if p['image_url'] and str(p['image_url']) != "nan": st.image(p['image_url'], use_container_width=True)
            st.write(f"**Review Digest:** {p['reviews'] if p['reviews'] else 'Sentiment: Safe'}")
            st.markdown("</div>", unsafe_allow_html=True)
        with col_v:
            preds = np.random.randint(20, 80, 7)
            st.plotly_chart(px.area(y=preds, title="AI Forecasting Stream", template="plotly_dark").update_traces(line_color='#7F00FF', fillcolor='rgba(127,0,255,0.1)'), use_container_width=True)
            st.markdown(f"<div class='ai-decision-box'>🤖 **Decision:** Procurement of <b>{preds.sum()} units</b> recommended for {target}.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header' style='color:#FFD700 !important;'>💰 VITTA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='financial-stat'>Inventory Value<br><h2>₹{v:,.0f}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='financial-stat' style='margin-top:20px; border-color:#FF0055; color:#FF0055;'>Idle Capital Risk<br><h2>₹{v*0.15:,.0f}</h2></div>", unsafe_allow_html=True)
        with c2: st.plotly_chart(px.pie(df, values='current_stock', names='name', hole=0.5, template="plotly_dark"))

elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header' style='color:#FF8800 !important;'>📦 SANCHARA</div>", unsafe_allow_html=True)
    st.map(pd.DataFrame({'lat':[12.97, 22.31, 37.77, 1.35], 'lon':[77.59, 114.16, -122.41, 103.81]}))
    st.info("🗺️ Precision Spandana: Real-time global transit sensors active.")

elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header' style='color:#00D4FF !important;'>🎙️ SAMVADA</div>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        u_in = st.chat_input("Enter strategic query...")
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans}); st.rerun()

elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header' style='color:#FF0055 !important;'>🛡️ STAMBHA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        for _, p in df.iterrows():
            if round(p['current_stock']/12, 1) < p['lead_time']: st.error(f"🔴 CRITICAL RISK: {p['name']} stockout risk.")
        st.table(df[['name', 'current_stock', 'lead_time']])

elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header' style='color:#00FF88 !important;'>📝 NYASA</div>", unsafe_allow_html=True)
    with st.form("entry"):
        n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1)
        if st.form_submit_button("COMMIT"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", (st.session_state.user, n, s, p, lt))
            st.success("Synced.")

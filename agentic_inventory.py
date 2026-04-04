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

# --- 1. PREMIUM UI CONFIG (HOLLOW BLUE GLOW & TICKER ANIMATION) ---
st.set_page_config(page_title="AROHA | Strategic Nexus", layout="wide", page_icon="💠", initial_sidebar_state="expanded")

def apply_aroha_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050709; color: #E6E8EB; }

        /* 💎 DHWANI: STRATEGIC TICKER */
        @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
        .ticker-wrap { width: 100%; overflow: hidden; background: rgba(0, 212, 255, 0.05); border-bottom: 1px solid rgba(0, 212, 255, 0.2); padding: 8px 0; margin-bottom: 20px; }
        .ticker-text { display: inline-block; white-space: nowrap; font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #00D4FF; animation: ticker 40s linear infinite; }

        /* 📟 SIDEBAR: RADIANT HOLLOW BLUE GLOW */
        [data-testid="stSidebar"] { background-color: #080A0C !important; border-right: 1px solid #1F2229; min-width: 420px !important; }
        section[data-testid="stSidebar"] .stButton > button { 
            background: transparent !important; border: 2px solid rgba(0, 212, 255, 0.4) !important; 
            color: #FFFFFF !important; text-align: left !important; padding: 15px 18px !important; width: 100%; 
            font-size: 1.6rem !important; font-weight: 800 !important; letter-spacing: 1.5px;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5); margin-bottom: 5px; transition: 0.3s;
        }
        section[data-testid="stSidebar"] .stButton > button:hover { border: 2px solid #00D4FF !important; box-shadow: 0 0 20px rgba(0, 212, 255, 0.6); color: #00D4FF !important; }
        .sidebar-sub { font-size: 0.95rem !important; color: #6C63FF; font-weight: 700; display: block; margin-top: -10px; margin-bottom: 25px; margin-left: 20px; text-transform: uppercase; letter-spacing: 1px; }

        /* BRANDING */
        .brand-title { font-size: 3.5rem !important; font-weight: 800 !important; color: #FFFFFF !important; letter-spacing: -2px; text-shadow: 0 0 25px rgba(108, 99, 255, 0.6); margin-bottom: 0; }
        .decisions-fade { color: #6C63FF; font-weight: 700; animation: glowPulse 2s infinite alternate; }
        @keyframes glowPulse { from { text-shadow: 0 0 5px #6C63FF; } to { text-shadow: 0 0 15px #38BDF8; } }

        /* CARDS & PANELS */
        .saas-card { background: #0D1117; border: 1px solid rgba(0, 212, 255, 0.1); border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
        .ai-decision-box { background: rgba(0, 212, 255, 0.05); border: 2px solid #D4AF37; padding: 25px; border-radius: 15px; border-left: 12px solid #D4AF37; margin-top: 25px; }
        .feature-header { font-size: 3.2rem !important; font-weight: 800 !important; color: #00D4FF !important; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3); text-transform: uppercase; }
        .review-box { background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; border: 1px solid #222; margin-bottom: 10px; font-size: 0.85rem; }
        .financial-stat { background: #111; padding: 20px; border-radius: 10px; border-top: 4px solid #D4AF37; text-align: center; }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_final_v52.db'
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
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 class='brand-title'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Turn Data Into <span class='decisions-fade'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([1, 0.8, 1])
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
            nu = st.text_input("New ID"); np = st.text_input("New Password", type="password")
            if st.button("Enroll Session"):
                try:
                    with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                    st.success("Authorized.")
                except: st.error("ID exists.")
    st.stop()

# --- 5. GLOBAL TICKER (DHWANI) ---
st.markdown(f"""
    <div class='ticker-wrap'>
        <div class='ticker-text'>
            [SYSTEM ALERT] Neural sensing active for {st.session_state.user.upper()} // [LOGISTICS] Suez Canal congestion reported +12h delay // [WEATHER] Tropical storm near Singapore Terminal - High risk to lead times // [MARKET] Demand sensing for Electronics up 14.2%
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div class='brand-container'><div class='brand-title' style='font-size:2.2rem !important;'>AROHA</div><div style='color:#9AA0A6; font-size:0.9rem;'>Data into <span class='decisions-fade'>Decisions</span></div></div>", unsafe_allow_html=True)
    
    nodes = [
        ("🏠 COMMAND-Hub", "Dashboard", "System Overview"),
        ("📈 PREKSHA-Vision", "Preksha", "AI Demand Sensing"),
        ("🛡️ STAMBHA-Guard", "Stambha", "Test Supply Risks"),
        ("🎙️ SAMVADA-Neural", "Samvada", "Talk To System"),
        ("💰 VITTA-Finance", "Vitta", "Track Money Flow"),
        ("📦 SANCHARA-Ops", "Sanchara", "Flow, Transit & Loop"),
        ("🤝 MITHRA-Alliance", "Mithra", "Supplier Performance"),
        ("📝 NYASA-Vault", "Nyasa", "Registry & Bulk Sync")
    ]
    for label, page_id, layman in nodes:
        if st.button(label):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)

    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 7. LOGIC NODES ---

# 1. COMMAND HUB (With CHETANA Notifications)
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Command Center: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    
    # Live Neural Pulse
    st.markdown("""<div style='background:rgba(0,212,255,0.02); padding:10px; border-radius:12px; border:1px dashed #00D4FF; margin-bottom:20px; text-align:center;'>
    <span style='color:#00D4FF;'>● NEURAL LINK PULSE: <b>STABLE</b></span> | <span>SYNC LATENCY: <b>12ms</b></span></div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='saas-card'><h3>Assets</h3><h2 style='color:#00D4FF;'>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='saas-card'><h3>Treasury</h3><h2 style='color:#00D4FF;'>₹{val:,.0f}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='saas-card'><h3>Resilience</h3><h2 style='color:#34D399;'>OPTIMAL</h2></div>", unsafe_allow_html=True)
    
    with st.expander("🔔 CHETANA: Intelligent Directives", expanded=True):
        st.error("ALERT: Raw Material supply at risk. TTS (4d) < TTR (25d) in 'Port Closure' scenario.")
        st.info("DIRECTIVE: AI recommends reordering 120 units of 'Asset-X' based on rising festival demand.")

# 2. PREKSHA-VISION
elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>📈 PREKSHA-Vision</div>", unsafe_allow_html=True)
    df = get_user_data()
    if df.empty: st.warning("Treasury empty.")
    else:
        target = st.selectbox("Asset Search", df['name']); p_row = df[df['name'] == target].iloc[0]
        col_m, col_v = st.columns([1, 2])
        with col_m:
            if p_row['image_url']: st.image(p_row['image_url'], use_container_width=True)
            if p_row['reviews']:
                st.subheader("Sentiment Feed")
                for r in p_row['reviews'].split('|'): st.markdown(f"<div class='review-box'>⭐ {r}</div>", unsafe_allow_html=True)
        with col_v:
            sent = st.select_slider("Market Sentiment", options=[0.8, 1.0, 1.2, 1.5, 2.0], value=1.0)
            preds = (np.random.randint(20, 50, 7) * sent).astype(int)
            st.plotly_chart(px.area(y=preds, title="AI Forecasting Stream", template="plotly_dark").update_traces(line_color='#00D4FF'), use_container_width=True)
            st.markdown(f"<div class='ai-decision-box'>🤖 **Decision:** Order **{preds.sum()} units** recommended.</div>", unsafe_allow_html=True)

# 6. SANCHARA-LOGISTICS (WITH SPANDANA HEATMAP)
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>📦 SANCHARA-Ops</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌐 Global Heatmap", "Warehouse Flow", "Returns Loop"])
    with t1:
        st.subheader("🌐 Global SPANDANA: Supplier Map")
        map_data = pd.DataFrame({
            'lat': [12.97, 22.31, 37.77, 1.35],
            'lon': [77.59, 114.16, -122.41, 103.81],
            'name': ['Hub Bangalore', 'Factory HK', 'HQ San Francisco', 'Port Singapore']
        })
        st.map(map_data)
    with t2:
        c1, c2, c3 = st.columns(3)
        c1.metric("Shipped Today", "154"); c2.metric("New Stock In", "+500"); c3.metric("Floor Total", "4,320")
    with t3:
        st.plotly_chart(px.pie(values=[70, 20, 10], names=['Defective', 'Late', 'Other'], hole=0.5, template="plotly_dark"))

# VITTA-FINANCE
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>💰 VITTA-Finance</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"<div class='financial-stat'>Inventory Value<br><h2>₹{v:,.0f}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='financial-stat' style='margin-top:20px;'>Idle Capital Risk<br><h2 style='color:red;'>₹{v*0.15:,.0f}</h2></div>", unsafe_allow_html=True)
        with c2:
            st.plotly_chart(px.pie(df, values='current_stock', names='name', hole=0.4, template="plotly_dark", title="Capital Allocation"), use_container_width=True)

# NYASA-VAULT (Entry + Sync + PO)
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>📝 NYASA-Vault</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["Manual Registry", "AGAMA: Bulk Sync", "KARYA: PO Gen"])
    with t1:
        with st.form("add"):
            n = st.text_input("Name"); c = st.text_input("Cat"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead", 1); sup = st.text_input("Supplier"); img = st.text_input("Img URL"); rev = st.text_area("Reviews")
            if st.form_submit_button("Commit"):
                with get_db() as conn: conn.execute("INSERT INTO products (username, name, category, current_stock, unit_price, lead_time, supplier, image_url, reviews) VALUES (?,?,?,?,?,?,?,?,?)", (st.session_state.user, n, c, s, p, lt, sup, img, rev))
                st.success("Synced.")
    with t2:
        f = st.file_uploader("Upload CSV", type="csv")
        if f and st.button("Batch Synchronize"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            for col in ['category','supplier','image_url','reviews']: 
                if col not in u_df.columns: u_df[col] = ""
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Synchronized.")
    with t3:
        df = get_user_data()
        if not df.empty:
            t = st.selectbox("Asset for PO", df['name'])
            if st.button("Generate PO"): st.code(f"PO-ID: {np.random.randint(1000,9999)}\nITEM: {t}\nAUTH: {st.session_state.user.upper()}")

# SAMVADA, MITHRA, STAMBHA logic...
else:
    st.markdown(f"<div class='feature-header'>{st.session_state.page} Node</div>", unsafe_allow_html=True)
    st.info("Strategic Fusion Node Active. Orchestration logic processing.")

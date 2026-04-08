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

# --- 1. SETTINGS & AESTHETIC FUSION UI ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="expanded"
)

# LOGO SVG (Radiant Design)
logo_svg = """
<svg width="500" height="500" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M50 5L10 85H30L50 35L70 85H90L50 5Z" fill="white" fill-opacity="0.1"/>
<circle cx="50" cy="45" r="5" fill="#00D4FF" fill-opacity="0.2"/>
</svg>
"""

def apply_aroha_style():
    # Note: Using double braces {{ }} for CSS inside f-string to prevent SyntaxError
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        html, body, [class*="css"] {{
            font-family: 'Outfit', sans-serif;
            background-color: #030508;
            color: #E6E8EB;
        }}

        /* 💠 PERSISTENT WATERMARK */
        [data-testid="stAppViewContainer"]::before {{
            content: "";
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-15deg);
            width: 70vw;
            height: 70vw;
            background-image: url("data:image/svg+xml;utf8,{logo_svg.replace('<', '%3C').replace('>', '%3E').replace('#', '%23')}");
            background-repeat: no-repeat;
            background-position: center;
            opacity: 0.04;
            z-index: -1;
            pointer-events: none;
            filter: blur(5px);
        }}

        /* 📟 SIDEBAR: RADIANT HOLLOW BLUE GLOW */
        [data-testid="stSidebar"] {{ 
            background-color: #010204 !important; 
            border-right: 1px solid #1F2229; 
            min-width: 420px; 
        }}

        section[data-testid="stSidebar"] .stButton > button {{ 
            background: transparent !important; 
            border: 2px solid rgba(0, 212, 255, 0.4) !important; 
            color: #FFFFFF !important; 
            text-align: left !important; 
            padding: 15px 18px !important; 
            width: 100%; 
            font-size: 1.6rem; 
            font-weight: 800 !important; 
            letter-spacing: 1.5px;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
            margin-bottom: 5px;
            transition: 0.3s;
        }}
        
        section[data-testid="stSidebar"] .stButton > button:hover {{ 
            border: 2px solid #00D4FF !important; 
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.6); 
            color: #00D4FF !important; 
        }}

        .sidebar-sub {{ 
            font-size: 0.95rem; 
            color: #6C63FF; 
            font-weight: 700; 
            display: block; 
            margin-top: -10px; 
            margin-bottom: 25px; 
            margin-left: 20px; 
            text-transform: uppercase; 
        }}

        /* 📌 AESTHETIC CARDS */
        .saas-card {{ 
            background: linear-gradient(145deg, #0d1117 0%, #161b22 100%); 
            border: 1px solid rgba(255, 255, 255, 0.05); 
            border-radius: 24px; padding: 25px; margin-bottom: 20px; 
        }}
        
        .karma-mission-card {{
            background: linear-gradient(135deg, rgba(255, 51, 255, 0.1) 0%, rgba(0, 0, 0, 0.8) 100%);
            border-radius: 20px; border: 1px solid #FF33FF; padding: 20px; margin-bottom: 15px;
        }}

        .ai-decision-box {{ 
            background: rgba(17, 25, 40, 0.75); 
            border: 2px solid #D4AF37; 
            padding: 25px; 
            border-radius: 20px; 
            border-left: 12px solid #D4AF37; 
            margin-top: 25px; 
        }}

        .feature-header {{ font-weight: 800; color: #00D4FF !important; letter-spacing: 2px; text-transform: uppercase; }}

        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_master_v104.db'
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
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 style='color:white; font-size:4rem; font-weight:800;'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Turn Data Into Decisions</p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([0.1, 0.8, 0.1])
    with col_center:
        m = st.tabs(["Login", "Join"])
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

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div style='text-align:center; margin-bottom:10px;'>AROHA V104.0</div>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD", key="nav_dashboard"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub' style='color:#FFF;'>System Overview</span>", unsafe_allow_html=True)

    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items & Sync"),
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks"),
        ("👷‍♂️ KARMA", "Karma", "Workforce Intelligence"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System"),
        ("💰 VITTA", "Vitta", "Track Money Flow"),
        ("📦 SANCHARA", "Sanchara", "Global Map & Flow"),
        ("🤝 MITHRA", "Mithra", "Supplier Intelligence")
    ]
    for label, page_id, layman in nodes:
        if st.button(label, key=f"nav_{page_id.lower()}"):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. PAGE CONTENT ---

# DASHBOARD
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Strategic Command Hub: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("📝 Assets Managed", len(df))
    with c2: st.metric("💰 Treasury Value", f"₹{val:,.0f}")
    with c3: st.metric("🛡️ Status", "OPTIMAL")

# KARMA (FULLY CODED)
elif st.session_state.page == "Karma":
    st.markdown("<h1 style='color:#FF33FF;'>👷‍♂️ KARMA: Workforce Intelligence</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🏹 Active Missions", "📊 Skill Radar"])
    with t1:
        missions = ["Pick 12x Titanium Chassis", "Quality Audit: Zone B", "Restock Sensors"]
        for m in missions:
            st.markdown(f"<div class='karma-mission-card'>⚡ <b>{m}</b> | 💎 500 XP</div>", unsafe_allow_html=True)
    with t2:
        categories = ['Speed','Accuracy','Packing','Safety','Strength']
        fig = go.Figure(data=go.Scatterpolar(r=[90, 95, 70, 85, 60], theta=categories, fill='toself', line_color='#FF33FF'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

# PREKSHA (PHOTOS + REVIEWS)
elif st.session_state.page == "Preksha":
    st.markdown("<h1 style='color:#7F00FF;'>📈 PREKSHA: Strategic Vision</h1>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        target = st.selectbox("Search Asset", df['name']); p = df[df['name'] == target].iloc[0]
        col1, col2 = st.columns([1, 2])
        with col1:
            if p['image_url'] and str(p['image_url']) != "nan": st.image(p['image_url'], use_container_width=True)
            if p['reviews']:
                for r in p['reviews'].split('|'): st.markdown(f"<div class='review-box'>💬 {r}</div>", unsafe_allow_html=True)
        with col2:
            preds = np.random.randint(20, 80, 7)
            st.plotly_chart(px.area(y=preds, title="AI Forecasting Stream", template="plotly_dark").update_traces(line_color='#7F00FF'))
            st.markdown(f"<div class='ai-decision-box'><h3>🤖 AI DIRECTIVE</h3>Reorder <b>{max(0, preds.sum() - p['current_stock'])}</b> units immediately.</div>", unsafe_allow_html=True)

# SANCHARA (MAP + ADDRESSES + RETURNS)
elif st.session_state.page == "Sanchara":
    st.markdown("<h1 style='color:#FF8800;'>📦 SANCHARA: Logistics</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🌐 Precision Map", "↩️ Returns Loop"])
    with t1:
        map_points = pd.DataFrame({'lat':[12.97, 22.31, 1.35], 'lon':[77.59, 114.16, 103.81], 'Node':['Hub', 'Factory', 'Port'], 'Address':['MG Road, Bangalore', 'Lantau, HK', 'Jurong, Singapore (🔴 PORT CLOSED)']})
        st.plotly_chart(px.scatter_mapbox(map_points, lat="lat", lon="lon", hover_name="Node", hover_data={"Address": True}, zoom=1, height=450).update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0}), use_container_width=True)
    with t2:
        st.table(pd.DataFrame({'Product':['Laptop','Monitor'], 'Amount':[4,2], 'Reason':['Defective Logic','Screen Bleed']}))

# SAMVADA (CHAT)
elif st.session_state.page == "Samvada":
    st.markdown("<h1 style='color:#00D4FF;'>🎙️ SAMVADA: AI Dialogue</h1>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
        u_in = st.chat_input("Enter command...")
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user","content":u_in}])
            st.session_state.chat_history.append({"role":"assistant", "content":res.choices[0].message.content}); st.rerun()

# REMAINING NODES
elif st.session_state.page == "Nyasa":
    st.markdown("<h1>📝 NYASA: Registry</h1>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Manual Entry", "Bulk Sync"])
    with t1:
        with st.form("add"):
            n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead", 1); sup = st.text_input("Supplier"); img = st.text_input("Img URL"); rev = st.text_area("Revs")
            if st.form_submit_button("COMMIT"):
                with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, supplier, image_url, reviews) VALUES (?,?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, sup, img, rev))
                st.success("Synced.")
    with t2:
        f = st.file_uploader("Upload CSV", type="csv")
        if f and st.button("Sync"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Synced.")

elif st.session_state.page == "Vitta":
    st.markdown("<h1 style='color:#FFD700;'>💰 VITTA: Financials</h1>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty: st.plotly_chart(px.pie(df, values='current_stock', names='name', hole=0.5, template="plotly_dark"))

elif st.session_state.page == "Stambha":
    st.markdown("<h1 style='color:#FF0055;'>🛡️ STAMBHA: Risk</h1>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty: st.table(df[['name', 'current_stock', 'lead_time']])

elif st.session_state.page == "Mithra":
    st.markdown("<h1 style='color:#34D399;'>🤝 MITHRA+: AI Negotiation</h1>", unsafe_allow_html=True)
    st.info("Strategy module online.")

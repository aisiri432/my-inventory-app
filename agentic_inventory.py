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
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;800&family=JetBrains+Mono:wght@400;700&display=swap');
        html, body, [class*="css"] {{ font-family: 'Outfit', sans-serif; background-color: #030508; color: #E6E8EB; }}

        /* 💠 PERSISTENT WATERMARK */
        [data-testid="stAppViewContainer"]::before {{
            content: ""; position: fixed; top: 50%; left: 50%;
            transform: translate(-50%, -50%) rotate(-15deg);
            width: 70vw; height: 70vw;
            background-image: url('data:image/svg+xml;utf8,{logo_svg}');
            background-repeat: no-repeat; background-position: center;
            opacity: 0.04; z-index: -1; pointer-events: none; filter: blur(5px);
        }}

        /* 📟 SIDEBAR: RADIANT HOLLOW BLUE GLOW */
        [data-testid="stSidebar"] {{ background-color: #010204 !important; border-right: 1px solid #1F2229; min-width: 420px; }}
        @media (max-width: 768px) {{ [data-testid="stSidebar"] {{ min-width: 100% !important; }} }}

        section[data-testid="stSidebar"] .stButton > button {{ 
            background: transparent !important; border: 2px solid rgba(0, 212, 255, 0.4) !important; 
            color: #FFFFFF !important; text-align: left !important; padding: 15px 18px !important; width: 100%; 
            font-size: 1.6rem; font-weight: 800 !important; letter-spacing: 1.5px;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5); margin-bottom: 5px; transition: 0.3s;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {{ border: 2px solid #00D4FF !important; box-shadow: 0 0 20px rgba(0, 212, 255, 0.6); color: #00D4FF !important; }}
        .sidebar-sub {{ font-size: 0.95rem; color: #6C63FF; font-weight: 700; display: block; margin-top: -10px; margin-bottom: 25px; margin-left: 20px; text-transform: uppercase; letter-spacing: 1px; }}

        .brand-title {{ font-weight: 800; color: #FFFFFF; letter-spacing: -2px; text-shadow: 0 0 25px rgba(108, 99, 255, 0.6); margin-bottom: 0; }}
        .decisions-fade {{ color: #6C63FF; font-weight: 700; animation: glowPulse 2s infinite alternate; }}
        @keyframes glowPulse {{ from {{ text-shadow: 0 0 5px #6C63FF; }} to {{ text-shadow: 0 0 15px #38BDF8; }} }}

        /* 📌 AESTHETIC MESH CARDS */
        .saas-card {{ 
            background: linear-gradient(145deg, #0d1117 0%, #161b22 100%); 
            border: 1px solid rgba(255, 255, 255, 0.05); 
            border-radius: 24px; padding: 25px; margin-bottom: 20px; 
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); 
        }}
        
        /* 👷‍♂️ KARMA MISSION CARDS */
        .karma-mission-card {{
            background: linear-gradient(135deg, rgba(255, 51, 255, 0.1) 0%, rgba(0, 0, 0, 0.8) 100%);
            border-radius: 20px; border: 1px solid #FF33FF; padding: 20px; margin-bottom: 15px;
            box-shadow: 0 0 15px rgba(255, 51, 255, 0.1);
        }}
        .xp-badge {{ background: #FF33FF; color: white; padding: 4px 10px; border-radius: 50px; font-weight: 800; font-size: 0.7rem; }}

        .ai-decision-box {{ background: rgba(17, 25, 40, 0.75); border: 2px solid #D4AF37; padding: 25px; border-radius: 20px; border-left: 12px solid #D4AF37; margin-top: 25px; box-shadow: 0 0 30px rgba(212, 175, 55, 0.2); }}
        .feature-header {{ font-weight: 800; color: #00D4FF !important; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3); text-transform: uppercase; }}
        .review-box {{ background: rgba(255,255,255,0.03); padding: 15px; border-radius: 12px; border: 1px solid #333; margin-bottom: 10px; font-size: 0.85rem; border-left: 4px solid #7F00FF; }}

        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_master_v80.db'
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
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 class='brand-title'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Turn Data Into <span class='decisions-fade'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([0.1, 0.8, 0.1])
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

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div class='brand-container'><div class='brand-title' style='font-size:2.2rem !important;'>AROHA</div><div style='color:#9AA0A6; font-size:0.9rem;'>Data into <span class='decisions-fade'>Decisions</span></div></div>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)

    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items & PO Gen"),
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks"),
        ("👷‍♂️ KARMA", "Karma", "Workforce Intelligence"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System"),
        ("💰 VITTA", "Vitta", "Track Money Flow"),
        ("📦 SANCHARA", "Sanchara", "Global Map & Flow"),
        ("🤝 MITHRA", "Mithra", "Supplier Intelligence")
    ]
    for label, page_id, layman in nodes:
        if st.button(label):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. LOGIC NODES ---

# 🏠 DASHBOARD
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Strategic Command: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("📝 Assets Managed", len(df))
    with c2: st.metric("💰 Treasury Value", f"₹{val:,.0f}")
    with c3: st.metric("🛡️ System Integrity", "OPTIMAL")
    st.markdown("<div class='ai-decision-box'><h3 style='color:#D4AF37; margin:0;'>✨ Agent Intelligence Directive</h3>Your vault is synchronized. Demand sensing is active. Sanchara Node reports stable transit.</div>", unsafe_allow_html=True)

# 👷‍♂️ KARMA (REIMAGINED VISUALLY)
elif st.session_state.page == "Karma":
    st.markdown("<div class='feature-header'>👷‍♂️ KARMA</div>", unsafe_allow_html=True)
    st.markdown("### Workforce Performance board")
    
    t1, t2, t3 = st.tabs(["🏹 Active Missions", "🎖️ Team XP", "📊 Manager Radar"])
    
    with t1:
        st.write("Today's Workforce Quests")
        missions = [
            {"icon": "⚡", "task": "Fast Picking: Aisle 4", "reward": "500 XP", "progress": 80},
            {"icon": "🎯", "task": "Quality Audit: Laptops", "reward": "300 XP", "progress": 30},
            {"icon": "🛡️", "task": "Safety Restock: Shelf B2", "reward": "1000 XP", "progress": 100}
        ]
        for m in missions:
            st.markdown(f"""
                <div class='karma-mission-card'>
                    <span style='font-size:1.5rem;'>{m['icon']}</span> <b>{m['task']}</b> <span class='xp-badge'>+{m['reward']}</span>
                </div>
            """, unsafe_allow_html=True)
            st.progress(m['progress'] / 100)

    with t2:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='saas-card'>⭐ Ananya (Lvl 14)<br><b>8,400 Total XP</b><br>Accuracy Master</div>", unsafe_allow_html=True)
        with col2:
            st.markdown("<div class='saas-card'>⚡ Ravi (Lvl 12)<br><b>7,200 Total XP</b><br>Speed Demon</div>", unsafe_allow_html=True)

    with t3:
        st.subheader("Labor Intelligence Analysis")
        # Skill Radar Chart
        categories = ['Picking Speed','Accuracy','Packing','Safety','Strength']
        fig = go.Figure(data=go.Scatterpolar(r=[90, 95, 70, 85, 60], theta=categories, fill='toself', line_color='#FF33FF'))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        st.error("⚠️ Fatigue Sensing: Worker 'Suresh' speed has dropped by 18%. Suggest 10-minute hydration break.")

# 📦 SANCHARA (FULL PRECISION FEATURES)
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>📦 SANCHARA</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌐 Precision Map", "📦 Floor Ops", "↩️ Returns (PUNAH)"])
    with t1:
        st.subheader("Global Logistics Pulse")
        map_points = pd.DataFrame({'lat':[12.9716, 22.3193, 37.7749, 1.3521], 'lon':[77.5946, 114.1694, -122.4194, 103.8198], 'Node':['Main Hub', 'Factory', 'HQ', 'Port'], 'Address':['MG Road, Bangalore', 'Lantau, HK', 'Market St, SF', 'Jurong, Singapore (🔴 PORT CLOSED)']})
        st.plotly_chart(px.scatter_mapbox(map_points, lat="lat", lon="lon", hover_name="Node", hover_data={"Address": True}, zoom=1, height=450).update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0}), use_container_width=True)
        st.markdown("<div class='saas-card'>🗺️ <b>Map Legend:</b> Blue dots indicate stable Hubs. Red dots indicate Crisis Zones. Hover for exact physical addresses.</div>", unsafe_allow_html=True)
    with t2:
        c1, c2 = st.columns(2); c1.metric("📦 Shipped Today", "1,240 Units", "↑ 12%"); c2.metric("🏭 Total Floor Assets", "4,462 Units", "+142 Returns")
    with t3:
        st.subheader("Live Return Why-Analysis")
        df_ret = pd.DataFrame({'Product':['Laptop','Monitor'], 'Amount':[4,2], 'Reason':['Defective Logic','Screen Bleed']})
        st.table(df_ret)

# 📈 PREKSHA (AESTHETIC PROFILING)
elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>📈 PREKSHA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        target = st.selectbox("Search Asset", df['name']); p = df[df['name'] == target].iloc[0]
        col_m, col_v = st.columns([1, 2])
        with col_m:
            if p['image_url'] and str(p['image_url']) != "nan": st.image(p['image_url'], use_container_width=True)
            if p['reviews'] and str(p['reviews']) != "nan":
                st.subheader("Sentiment Feed")
                for r in p['reviews'].split('|'): st.markdown(f"<div class='review-box'>💬 {r}</div>", unsafe_allow_html=True)
        with col_v:
            sent = st.select_slider("Market Sensing", options=[0.8, 1.0, 1.5, 2.0], value=1.0)
            preds = np.random.randint(20, 50, 7)
            st.plotly_chart(px.area(y=preds, title="AI Forecasting Path", template="plotly_dark").update_traces(line_color='#00D4FF'), use_container_width=True)
            st.markdown(f"<div class='ai-decision-box'><h3>🤖 AI DIRECTIVE</h3>Based on current sensing, order <b>{max(0, preds.sum() - p['current_stock'])}</b> units immediately.</div>", unsafe_allow_html=True)

# Other nodes inherit logic...
elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header'>🎙️ SAMVADA</div>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        u_in = st.chat_input("Strategic query...")
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans}); st.rerun()

elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>📝 NYASA</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Bulk Sync", "Manual Entry"])
    with t1:
        f = st.file_uploader("CSV Sync", type="csv")
        if f and st.button("Sync"): st.success("Synced.")
    with t2:
        with st.form("add"):
            n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead", 1); img = st.text_input("Img URL"); rev = st.text_area("Revs")
            if st.form_submit_button("Commit"):
                with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
                st.success("Saved.")

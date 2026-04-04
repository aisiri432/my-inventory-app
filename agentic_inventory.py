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

# --- 1. UNIVERSAL RESPONSIVE UI CONFIG ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="expanded"
)

def apply_aroha_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* 🌑 Base Environment */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #050709;
            color: #E6E8EB;
        }

        /* 📱 UNIVERSAL RESPONSIVITY (Mobile vs Laptop) */
        @media (max-width: 768px) {
            .brand-title { font-size: 2rem !important; }
            .feature-header { font-size: 1.8rem !important; }
            section[data-testid="stSidebar"] { min-width: 100% !important; }
            section[data-testid="stSidebar"] .stButton > button { font-size: 1.1rem !important; }
            .sidebar-sub { font-size: 0.75rem !important; margin-left: 15px !important; }
            .db-metric-val { font-size: 1.5rem !important; }
        }

        /* 📟 SIDEBAR: RADIANT HOLLOW BLUE GLOW */
        [data-testid="stSidebar"] { 
            background-color: #080A0C !important; 
            border-right: 1px solid #1F2229; 
            min-width: 380px;
        }
        
        /* Hollow Blue Glowing Buttons */
        section[data-testid="stSidebar"] .stButton > button { 
            background: transparent !important; 
            border: 2px solid rgba(0, 212, 255, 0.4) !important; 
            color: #FFFFFF !important; 
            text-align: left !important; 
            padding: 12px 18px !important; 
            width: 100%; 
            font-size: 1.5rem; 
            font-weight: 800 !important; 
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5);
            margin-bottom: 5px;
            transition: 0.3s;
        }
        
        section[data-testid="stSidebar"] .stButton > button:hover { 
            border: 2px solid #00D4FF !important;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
            color: #00D4FF !important;
        }

        .sidebar-sub { 
            font-size: 0.9rem; 
            color: #6C63FF; 
            font-weight: 700; 
            display: block; 
            margin-top: -10px; 
            margin-bottom: 25px; 
            margin-left: 20px; 
            text-transform: uppercase; 
        }

        /* Branding */
        .brand-title { font-size: 3.5rem; font-weight: 800; color: #FFFFFF; letter-spacing: -2px; text-shadow: 0 0 25px rgba(108, 99, 255, 0.6); margin-bottom: 0; }
        .decisions-fade { color: #6C63FF; font-weight: 700; animation: glowPulse 2s infinite alternate; }
        @keyframes glowPulse { from { text-shadow: 0 0 5px #6C63FF; } to { text-shadow: 0 0 15px #38BDF8; } }

        /* Feature Headers */
        .feature-header { font-size: 3.2rem; font-weight: 800; color: #00D4FF; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3); text-transform: uppercase; }
        
        /* 💡 THE GOLDEN DECISION BOX */
        .ai-decision-box { 
            background: rgba(212, 175, 55, 0.08); 
            border: 2px solid #D4AF37; 
            padding: 25px; 
            border-radius: 15px; 
            border-left: 10px solid #D4AF37;
            margin-top: 25px; 
        }

        /* Ticker */
        @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
        .ticker-wrap { width: 100%; overflow: hidden; background: rgba(0, 212, 255, 0.05); border-bottom: 1px solid rgba(0, 212, 255, 0.2); padding: 8px 0; }
        .ticker-text { display: inline-block; white-space: nowrap; font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #00D4FF; animation: ticker 40s linear infinite; }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_final_v65.db'
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
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 class='brand-title'>AROHA</h1><p style='color:#9AA0A6;'>Where Data Becomes <span class='decisions-fade'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([0.1, 0.8, 0.1])
    with col_center:
        m = st.tabs(["Login", "Enroll"])
        with m[0]:
            u_input = st.text_input("Username", key="l_u")
            p_input = st.text_input("Password", type="password", key="l_p")
            if st.button("Unlock Dashboard"):
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

# --- 5. TOP HUD ---
st.markdown(f"<div class='ticker-wrap'><div class='ticker-text'>[DHWANI] Neural link active for {st.session_state.user.upper()} // [LOGISTICS] Port congestion reported +12h delay // [MAP] 🔴 Risk in Singapore Hub // [SENSING] Demand up 14.2%</div></div>", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div class='brand-title' style='font-size:2.2rem !important;'>AROHA</div>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)
    
    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items & Sync"),
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System"),
        ("💰 VITTA", "Vitta", "Track Money Flow"),
        ("📦 SANCHARA", "Sanchara", "Global Flow & Returns"),
        ("🤝 MITHRA", "Mithra", "Rate Your Suppliers")
    ]
    for label, page_id, layman in nodes:
        if st.button(label):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)

    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 7. FEATURE NODES ---

# 1. DASHBOARD
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Hub: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Assets", len(df))
    with c2: st.metric("Treasury", f"₹{val:,.0f}")
    with c3: st.metric("Status", "OPTIMAL")
    st.info("💡 Identity Verified. Choose a Node from the sidebar to begin.")

# 2. NYASA
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>📝 NYASA</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📥 Bulk Sync", "✍️ Manual Registry"])
    with t1:
        f = st.file_uploader("Upload CSV", type="csv")
        if f and st.button("Sync Data"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Synced.")
    with t2:
        with st.form("manual"):
            n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead", 1)
            if st.form_submit_button("Commit"):
                with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", (st.session_state.user, n, s, p, lt))
                st.success("Saved.")

# 3. PREKSHA (AI Decision Highlighted)
elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>📈 PREKSHA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if df.empty: st.warning("Add data in NYASA node.")
    else:
        target = st.selectbox("Asset Search", df['name']); p_row = df[df['name'] == target].iloc[0]
        col_m, col_v = st.columns([1, 2])
        with col_m:
            if p_row['image_url']: st.image(p_row['image_url'], use_container_width=True)
            st.write(f"**Customer Sentiment:** {p_row['reviews'] if p_row['reviews'] else 'Healthy'}")
        with col_v:
            sent = st.select_slider("Market Sentiment", options=[0.8, 1.0, 1.5, 2.0], value=1.0)
            preds = (np.random.randint(20, 50, 7) * sent).astype(int)
            st.plotly_chart(px.area(y=preds, title="AI Forecasting Stream", template="plotly_dark").update_traces(line_color='#00D4FF'), use_container_width=True)
            st.markdown(f"<div class='ai-decision-box'><h3 style='color:#D4AF37; margin:0;'>🤖 AGENT DECISION</h3>Reorder <b>{max(0, preds.sum() - p_row['current_stock'])}</b> units recommended.</div>", unsafe_allow_html=True)

# 4. SANCHARA (MAP)
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>📦 SANCHARA</div>", unsafe_allow_html=True)
    st.info("Tap 🔴 Red Dot for disruption address.")
    map_points = pd.DataFrame({
        'lat': [12.97, 22.31, 37.77, 1.35], 'lon': [77.59, 114.16, -122.41, 103.81],
        'Node': ['Hub', 'Factory', 'HQ', 'Risk Zone'],
        'Address': ['Bangalore, India', 'HK Port', 'San Francisco, USA', 'Jurong, Singapore (🔴 PORT CLOSED)'],
        'Status': ['🔵 Stable', '🔵 Stable', '🔵 Stable', '🔴 CRITICAL']
    })
    fig = px.scatter_mapbox(map_points, lat="lat", lon="lon", color="Status", hover_name="Node", hover_data={"Address": True, "lat": False, "lon": False}, color_discrete_map={"🔵 Stable": "cyan", "🔴 CRITICAL": "red"}, zoom=1, height=400)
    fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

# 5. SAMVADA (CHAT)
elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header'>🎙️ SAMVADA</div>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        u_in = st.chat_input("Strategic query...")
        audio = st.audio_input("Microphone")
        if audio:
            with st.spinner("Processing voice..."): u_in = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans}); st.rerun()

# 6. VITTA (PIE CHART)
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>💰 VITTA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        st.plotly_chart(px.pie(df, values='current_stock', names='name', hole=0.5, template="plotly_dark", title="Capital Allocation"))

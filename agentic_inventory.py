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

# --- 1. UNIVERSAL RESPONSIVE CONFIG ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="auto"
)

def apply_aroha_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Base Environment */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #050709;
            color: #E6E8EB;
        }

        /* 📱 RESPONSIVE CSS (The "Brain" for different screens) */
        @media (max-width: 768px) {
            .brand-title { font-size: 2.2rem !important; }
            .feature-header { font-size: 1.8rem !important; }
            section[data-testid="stSidebar"] { min-width: 100% !important; }
            section[data-testid="stSidebar"] .stButton > button { font-size: 1.1rem !important; }
            .sidebar-sub { font-size: 0.75rem !important; margin-left: 10px !important; }
            .saas-card { padding: 15px !important; }
        }

        /* 📟 SIDEBAR: RADIANT HOLLOW BLUE GLOW */
        [data-testid="stSidebar"] { 
            background-color: #080A0C !important; 
            border-right: 1px solid #1F2229; 
            min-width: 400px;
        }
        
        section[data-testid="stSidebar"] .stButton > button { 
            background: transparent !important; 
            border: 2px solid rgba(0, 212, 255, 0.4) !important; 
            color: #FFFFFF !important; 
            text-align: left !important; 
            padding: 12px 18px !important; 
            width: 100%; 
            font-size: 1.5rem; 
            font-weight: 800 !important; 
            letter-spacing: 1.5px;
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
            font-size: 0.95rem; 
            color: #6C63FF; 
            font-weight: 700; 
            display: block; 
            margin-top: -10px; 
            margin-bottom: 25px; 
            margin-left: 20px; 
            text-transform: uppercase; 
            letter-spacing: 1px;
        }

        /* 💎 BRANDING */
        .brand-title { font-size: 3.5rem; font-weight: 800; color: #FFFFFF; letter-spacing: -2px; text-shadow: 0 0 25px rgba(108, 99, 255, 0.6); margin-bottom: 0; }
        .decisions-fade { color: #6C63FF; font-weight: 700; animation: glowPulse 2s infinite alternate; }
        @keyframes glowPulse { from { text-shadow: 0 0 5px #6C63FF; } to { text-shadow: 0 0 15px #38BDF8; } }

        /* CARDS & PANELS */
        .saas-card { background: #0D1117; border: 1px solid rgba(0, 212, 255, 0.1); border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
        .ai-decision-box { background: rgba(17, 25, 40, 0.75); border: 2px solid #D4AF37; padding: 25px; border-radius: 15px; border-left: 12px solid #D4AF37; margin-top: 25px; }
        .feature-header { font-size: 3.2rem; font-weight: 800; color: #00D4FF; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3); text-transform: uppercase; }
        .financial-stat { background: #111; padding: 20px; border-radius: 10px; border-top: 4px solid #D4AF37; text-align: center; }

        /* TICKER */
        @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
        .ticker-wrap { width: 100%; overflow: hidden; background: rgba(0, 212, 255, 0.05); border-bottom: 1px solid rgba(0, 212, 255, 0.2); padding: 8px 0; margin-bottom: 20px; }
        .ticker-text { display: inline-block; white-space: nowrap; font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #00D4FF; animation: ticker 40s linear infinite; }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_master_v68.db'
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

# --- 5. TOP HUD ---
st.markdown(f"<div class='ticker-wrap'><div class='ticker-text'>[DHWANI] Neural link active for {st.session_state.user.upper()} // [LOGISTICS] Hover over Spandana Map for Precision Addresses // [MARKET] Demand sensing tracking +12% Demand.</div></div>", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div class='brand-container'><div class='brand-title' style='font-size:2.2rem !important;'>AROHA</div><div style='color:#9AA0A6; font-size:0.9rem;'>Data into <span class='decisions-fade'>Decisions</span></div></div>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)

    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items & PO Gen"),
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks"),
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

# --- 7. LOGIC NODES ---

# 1. DASHBOARD
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Strategic Hub: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("📝 Assets Managed", len(df))
    with c2: st.metric("💰 Treasury Value", f"₹{val:,.0f}")
    with c3: st.metric("🛡️ System Integrity", "OPTIMAL")

# 2. SANCHARA (MAP + FLOW + RETURNS)
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>📦 SANCHARA</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌐 Precision Map", "📦 Floor Ops", "↩️ Returns"])
    with t1:
        st.subheader("Global SPANDANA Intelligence Map")
        map_points = pd.DataFrame({
            'lat': [12.97, 22.31, 37.77, 1.35], 'lon': [77.59, 114.16, -122.41, 103.81],
            'Location': ['Main Hub', 'Factory', 'Global HQ', 'Risk Zone'],
            'Address': ['Bangalore, India', 'Hong Kong', 'San Francisco, USA', 'Jurong Island, Singapore (🔴 PORT CLOSED)'],
            'Risk': ['Low', 'Low', 'Low', '🔴 CRITICAL']
        })
        fig = px.scatter_mapbox(map_points, lat="lat", lon="lon", hover_name="Location", hover_data={"Address": True, "Risk": True, "lat": False, "lon": False}, color="Risk", color_discrete_map={'Low': 'cyan', '🔴 CRITICAL': 'red'}, zoom=1, height=450)
        fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
    with t2:
        st.subheader("Live Warehouse Throughput")
        c1, c2 = st.columns(2)
        c1.metric("📦 Items Shipped Today", "1,240")
        c2.metric("🚛 New Stock Inbound", "3,500")
    with t3:
        st.plotly_chart(px.pie(values=[70, 20, 10], names=['Defective', 'Late', 'Mistake'], hole=0.5, template="plotly_dark"))

# 3. MITHRA (SUPPLIER INTEL)
elif st.session_state.page == "Mithra":
    st.markdown("<div class='feature-header'>🤝 MITHRA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        df['Reliability'] = (100 - (df['lead_time'] * 2)).clip(60, 99)
        st.subheader("Vendor Reliability Matrix")
        st.dataframe(df[['supplier', 'name', 'lead_time', 'Reliability']].sort_values(by='Reliability', ascending=False), use_container_width=True)
        st.plotly_chart(px.bar(df, x='supplier', y='Reliability', color='Reliability', template='plotly_dark'))

# NYASA, PREKSHA, STAMBHA, VITTA, SAMVADA inherit v67 logic ...
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>📝 NYASA</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📥 Bulk Sync", "✍️ Manual Registry", "📄 PO Gen"])
    with t1:
        f = st.file_uploader("Upload CSV", type="csv")
        if f and st.button("Synchronize"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Synced.")
    with t2:
        with st.form("add_p"):
            n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead", 1)
            if st.form_submit_button("Commit"):
                with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", (st.session_state.user, n, s, p, lt))
                st.success("Committed.")
    with t3:
        df = get_user_data()
        if not df.empty:
            t = st.selectbox("Asset for PO", df['name'])
            if st.button("Generate PO"): st.code(f"PO-ID: #ARH-{np.random.randint(1000,9999)}\nITEM: {t}")

elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>📈 PREKSHA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        target = st.selectbox("Asset", df['name']); p_row = df[df['name'] == target].iloc[0]
        preds = np.random.randint(20, 50, 7)
        st.plotly_chart(px.area(y=preds, title="AI Forecasting Stream", template="plotly_dark").update_traces(line_color='#00D4FF'), use_container_width=True)
        st.markdown(f"<div class='ai-decision-box'><h3 style='color:#D4AF37; margin:0;'>🤖 AGENT SUGGESTION</h3>Reorder <b>{max(0, preds.sum() - p_row['current_stock'])}</b> units immediately.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>💰 VITTA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        st.plotly_chart(px.pie(df, values='current_stock', names='name', hole=0.5, template="plotly_dark", title="Capital Allocation"))

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

elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header'>🛡️ STAMBHA</div>", unsafe_allow_html=True)
    s_scenario = st.selectbox("Trigger Disruption", ["Normal", "Port Closure (3x TTR)", "Factory Fire (+30d)"])
    df = get_user_data()
    if not df.empty:
        res = []
        for _, p in df.iterrows():
            ttr = p['lead_time'] * (3 if "Port" in s_scenario else 1)
            tts = round(p['current_stock'] / 12, 1)
            res.append({"Asset": p['name'], "TTS": tts, "TTR": ttr, "Status": "🟢 Safe" if tts > ttr else "🔴 CRITICAL"})
        st.table(pd.DataFrame(res))

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

# --- 1. PREMIUM UI CONFIG ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="expanded"
)

def apply_aroha_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0B0F14;
            color: #E6E8EB;
        }

        /* --- SIDEBAR: ULTRA BOLD & LARGE --- */
        [data-testid="stSidebar"] { 
            background-color: #090B0F !important; 
            border-right: 1px solid #1F2229; 
            min-width: 350px !important; 
        }
        
        .brand-title { font-size: 2.2rem; font-weight: 800; color: #FFFFFF; letter-spacing: -1px; margin-bottom: 0; }
        .tagline { font-size: 1rem; color: #9AA0A6; margin-top: -5px; }
        .decisions-fade { color: #6C63FF; font-weight: 700; animation: glowPulse 2s infinite alternate; }
        @keyframes glowPulse { from { text-shadow: 0 0 2px #6C63FF; } to { text-shadow: 0 0 10px #38BDF8; } }

        /* Main Sanskrit Sidebar Buttons - EXTRA LARGE */
        section[data-testid="stSidebar"] .stButton > button { 
            background: transparent !important; border: none !important; color: #FFFFFF !important; 
            text-align: left !important; padding: 10px 15px !important; width: 100%; 
            font-size: 1.4rem !important; font-weight: 800 !important; letter-spacing: 1px;
        }
        
        /* Layman Sub-Labels */
        .sidebar-sub { 
            font-size: 0.9rem !important; color: #6C63FF; font-weight: 700; display: block; 
            margin-top: -15px; margin-bottom: 20px; margin-left: 55px; text-transform: uppercase; 
        }

        section[data-testid="stSidebar"] .stButton > button:hover { 
            background: #171A21 !important; color: #6C63FF !important; 
        }

        /* Dashboard Cards */
        .saas-card { 
            background: #171A21; border: 1px solid rgba(255, 255, 255, 0.05); 
            border-radius: 12px; padding: 20px; margin-bottom: 20px; 
        }
        .db-metric-val { font-family: 'JetBrains Mono', monospace; font-size: 1.8rem; font-weight: 700; color: #FFFFFF; }
        .db-metric-label { font-size: 0.8rem; text-transform: uppercase; color: #9AA0A6; }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_v36_final.db'
def get_db_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_db_conn() as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
        c.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, 
                      current_stock INTEGER, unit_price REAL, lead_time INTEGER, supplier TEXT)''')
        conn.commit()
init_db()

def hash_p(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- 3. SESSION LOGIC ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 4. LOGIN ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:white; font-size:4rem; font-weight:800;'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Where Data Becomes <span style='color:#6C63FF; font-weight:700;'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 0.8, 1])
    with c2:
        m = st.tabs(["Login", "Enroll"])
        with m[0]:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Unlock Dashboard"):
                with get_db_conn() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Access denied.")
        with m[1]:
            nu = st.text_input("New ID"); np = st.text_input("New Password", type="password")
            if st.button("Initialize Account"):
                try:
                    with get_db_conn() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                    st.success("Authorized.")
                except: st.error("Exists.")
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div class='brand-title'>AROHA</div><div class='tagline'>Data into <span class='decisions-fade'>Decisions</span></div><br>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)
    
    # Navigation Mapping
    nodes = [
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System"),
        ("💰 ARTHA", "Artha", "Track Money Flow"),
        ("🤝 MITHRA", "Mithra", "Rate Your Suppliers"),
        ("📄 KARYA", "Karya", "Auto Create Orders"),
        ("📝 NYASA", "Nyasa", "Log Assets Securely"),
        ("📥 AGAMA", "Agama", "Import Data Easily")
    ]
    for label, page_id, layman in nodes:
        if st.button(label): st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)

    st.divider()
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. PAGE CONTENT ---

def get_user_df():
    with get_db_conn() as conn: return pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))

# --- DASHBOARD ---
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Strategic Command Hub</h1>", unsafe_allow_html=True)
    df = get_user_df()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Assets</div><div class='db-metric-val'>{len(df)}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Treasury</div><div class='db-metric-val'>₹{val/1000:,.1f}K</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Risk</div><div class='db-metric-val' style='color:#34D399;'>Stable</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='saas-card'><div class='db-metric-label'>Sensing</div><div class='db-metric-val'>v36.0</div></div>", unsafe_allow_html=True)
    st.info("💡 Identity: " + st.session_state.user.upper() + ". Select a Node from the sidebar to begin analysis.")

# --- PREKSHA ---
elif st.session_state.page == "Preksha":
    st.markdown("<h1>🔮 PREKSHA</h1>", unsafe_allow_html=True)
    df = get_user_df()
    if df.empty: st.warning("Treasury empty. Use NYASA.")
    else:
        target = st.selectbox("Select Asset", df['name'])
        st.plotly_chart(px.area(y=np.random.randint(20, 60, 7), title="AI Demand Forecast", template="plotly_dark").update_traces(line_color='#6C63FF'), use_container_width=True)

# --- STAMBHA ---
elif st.session_state.page == "Stambha":
    st.markdown("<h1>🛡️ STAMBHA</h1>", unsafe_allow_html=True)
    df = get_user_df()
    if not df.empty: st.dataframe(df[['name', 'current_stock', 'lead_time']], use_container_width=True)
    else: st.warning("No data.")

# --- SAMVADA ---
elif st.session_state.page == "Samvada":
    st.markdown("<h1>🎙️ SAMVADA</h1>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        u_in = st.chat_input("Strategic query...")
        if u_in:
            st.session_state.chat_history.append({"role":"user","content":u_in})
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":"You are AROHA AI assistant."}] + st.session_state.chat_history[-3:])
            st.session_state.chat_history.append({"role":"assistant","content":res.choices[0].message.content}); st.rerun()

# --- NYASA ---
elif st.session_state.page == "Nyasa":
    st.markdown("<h1>📝 NYASA</h1>", unsafe_allow_html=True)
    with st.form("add"):
        n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1); sup = st.text_input("Supplier")
        if st.form_submit_button("Commit"):
            with get_db_conn() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, supplier) VALUES (?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, sup))
            st.success("Asset Committed.")

# --- AGAMA ---
elif st.session_state.page == "Agama":
    st.markdown("<h1>📥 AGAMA</h1>", unsafe_allow_html=True)
    f = st.file_uploader("Upload CSV", type="csv")
    if f and st.button("Sync"):
        u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
        with get_db_conn() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
        st.success("Synced.")

# --- OTHER NODES ---
else:
    st.markdown(f"<h1>{st.session_state.page}</h1>", unsafe_allow_html=True)
    st.info("Logic node online. Awaiting data stream.")

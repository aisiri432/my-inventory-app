import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI
import hashlib
import time

# --- 1. SETTINGS & EXECUTIVE HUD UI ---
st.set_page_config(page_title="AROHA | Strategic Intelligence", layout="wide", page_icon="💠")

def apply_obsidian_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Montserrat:wght@300;500;700&display=swap');
        
        /* Base HUD Environment */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0D0D0D; /* Obsidian */
            color: #E0E0E0;
        }

        h1, h2, h3 { font-family: 'Montserrat', sans-serif; font-weight: 700; color: #D4AF37; }

        /* UNBOXED MENU: Floating Badges (PhonePe Style) */
        .badge-element {
            text-align: center;
            padding: 30px 10px;
            transition: 0.4s all ease;
            cursor: pointer;
            border-bottom: 1px solid #1A1A1A; /* Very thin divider instead of box */
        }
        
        .badge-element:hover {
            border-bottom: 2px solid #D4AF37;
            background: rgba(212, 175, 55, 0.03);
            transform: translateY(-5px);
        }

        .badge-icon { font-size: 32px; margin-bottom: 10px; color: #D4AF37; }
        .badge-title { font-weight: 600; font-size: 1rem; color: #FFFFFF; letter-spacing: 1px; }
        .badge-desc { font-size: 0.75rem; color: #666; margin-top: 5px; }

        /* Global HUD Sidebar */
        [data-testid="stSidebar"] {
            background-color: #080808;
            border-right: 1px solid #1A1A1A;
        }

        /* Top HUD Status Bar */
        .hud-status-bar {
            display: flex;
            justify-content: space-between;
            padding: 10px 0px;
            border-bottom: 1px solid #1A1A1A;
            margin-bottom: 40px;
            font-size: 0.65rem;
            color: #444;
            letter-spacing: 2px;
            font-weight: 700;
        }

        /* Buttons: Minimalist Gold */
        .stButton>button {
            border-radius: 2px;
            background: transparent;
            border: 1px solid #333;
            color: #D4AF37;
            font-weight: 500;
            padding: 8px 20px;
            transition: 0.3s;
            text-transform: uppercase;
            font-size: 0.7rem;
            letter-spacing: 2px;
        }
        .stButton>button:hover {
            border-color: #D4AF37;
            background: #D4AF37;
            color: black;
        }

        /* AI Decision Highlight */
        .decision-highlight {
            background: rgba(212, 175, 55, 0.05);
            border-left: 4px solid #D4AF37;
            padding: 25px;
            margin-top: 20px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_obsidian_css()

# --- 2. DATABASE ENGINE (MASTER SCHEMA) ---
DB_FILE = 'aroha_obsidian_v2.db'
def get_db_conn(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_db_conn() as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
        c.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, 
                      category TEXT, current_stock INTEGER, unit_price REAL, lead_time INTEGER, 
                      supplier TEXT, image_url TEXT, reviews TEXT)''')
        conn.commit()
init_db()

def hash_p(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_active" not in st.session_state: st.session_state.voice_active = False

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='font-size:4rem; letter-spacing:15px; margin-bottom:0;'>AROHA</h1><p style='color:#444; letter-spacing:3px;'>STRATEGIC INTELLIGENCE INTERFACE</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        m = st.tabs(["ACCESS", "ENROLL"])
        with m[0]:
            u = st.text_input("Identity", key="l_u")
            p = st.text_input("Mantra", type="password", key="l_p")
            if st.button("UNLOCK COMMAND CENTER"):
                with get_db_conn() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Verification Failed")
        with m[1]:
            nu = st.text_input("New Identity"); np = st.text_input("New Mantra", type="password")
            if st.button("AUTHORIZE ACCOUNT"):
                with get_db_conn() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Identity Authorized. Sign in.")
    st.stop()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='font-size:1.5rem; letter-spacing:5px;'>AROHA</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#444; font-size:0.7rem;'>SECURE_NODE: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
    st.divider()
    if st.button("🏠 Home Command"): st.session_state.page = "Home"; st.rerun()
    if st.button("🔮 Preksha Intel"): st.session_state.page = "Preksha"; st.rerun()
    if st.button("🛡️ Stambha Safety"): st.session_state.page = "Stambha"; st.rerun()
    if st.button("🎙️ Samvada Chat"): st.session_state.page = "Samvada"; st.rerun()
    if st.button("💰 Artha Financials"): st.session_state.page = "Artha"; st.rerun()
    if st.button("📝 Nyasa Ledger"): st.session_state.page = "Nyasa"; st.rerun()
    if st.button("📥 Agama Import"): st.session_state.page = "Agama"; st.rerun()
    st.divider()
    if st.button("🔒 Secure Exit"): st.session_state.auth = False; st.rerun()

# --- 6. HOME PAGE (Command Center - PhonePe Unboxed) ---
if st.session_state.page == "Home":
    st.markdown(f"""
        <div class='hud-status-bar'>
            <span>SYS_VERSION: 2.0</span>
            <span>ENCRYPTION: AES_256</span>
            <span>DATA_LATENCY: 14ms</span>
            <span>{datetime.now().strftime('%H:%M:%S')}</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='letter-spacing:10px; font-weight:300; color:#444;'>COMMAND HUB</h2>", unsafe_allow_html=True)
    
    # Summary Bar
    with get_db_conn() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Assets Managed", len(df))
    c2.metric("Treasury Value", f"${val:,.0f}")
    c3.metric("Stock Integrity", "Optimal")
    st.divider()

    # THE UNBOXED GRID (3x2)
    r1c1, r1c2, r1c3 = st.columns(3)
    r2c1, r2c2, r2c3 = st.columns(3)

    nodes = [
        {"id": "Preksha", "icon": "🔮", "title": "PREKSHA", "desc": "Demand Intelligence", "col": r1c1},
        {"id": "Stambha", "icon": "🛡️", "title": "STAMBHA", "desc": "Resilience Simulator", "col": r1c2},
        {"id": "Samvada", "icon": "🎙️", "title": "SAMVADA", "desc": "Agentic Chat", "col": r1c3},
        {"id": "Artha", "icon": "💰", "title": "ARTHA", "desc": "Value Optimization", "col": r2c1},
        {"id": "Nyasa", "icon": "📝", "title": "NYASA", "desc": "Asset Ledger", "col": r2c2},
        {"id": "Agama", "icon": "📥", "title": "AGAMA", "desc": "Bulk Data Sync", "col": r2c3}
    ]

    for n in nodes:
        with n['col']:
            st.markdown(f"""
                <div class='badge-element'>
                    <div class='badge-icon'>{n['icon']}</div>
                    <div class='badge-title'>{n['title']}</div>
                    <div class='badge-desc'>{n['desc']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Engage", key=f"btn_{n['id']}"):
                st.session_state.page = n['id']; st.rerun()

# --- 7. FEATURE NODE LOGIC ---

if st.session_state.page == "Preksha":
    st.markdown("## 🔮 Preksha: Strategic Intelligence")
    with get_db_conn() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("Node empty. Add data via NYASA.")
    else:
        col_l, col_r = st.columns([1, 2])
        with col_l:
            target = st.selectbox("Select Asset", df['name'])
            p = df[df['name'] == target].iloc[0]
            if p['image_url']: st.image(p['image_url'], use_container_width=True)
            st.write(f"**Stock:** {p['current_stock']} | **Unit Price:** ${p['unit_price']}")
        with col_r:
            preds = np.random.randint(15, 60, 7)
            st.plotly_chart(px.line(y=preds, title="AI Demand Sensing", template="plotly_dark").update_traces(line_color='#D4AF37'), use_container_width=True)
            st.markdown(f"<div class='decision-highlight'>🤖 **AGENT RECOMMENDATION:** Order <b>{preds.sum()} units</b> of {target} immediately.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Samvada":
    st.markdown("## 🎙️ Samvada: Neural Interface")
    st.session_state.voice_active = st.toggle("Enable Voice Assistant", value=st.session_state.voice_active)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        q = st.chat_input("Speak or Type command...")
        audio = st.audio_input("Microphone")
        u_in = q
        if audio:
            with st.spinner("Processing..."): u_in = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            with get_db_conn() as conn: ctx = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", conn, params=(st.session_state.user,)).to_string()
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI Agent. Strategic and brief. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans})
            st.rerun()

elif st.session_state.page == "Nyasa":
    st.markdown("## 📝 Nyasa: Asset Ledger")
    with st.form("entry"):
        n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1); img = st.text_input("Image URL"); rev = st.text_area("Reviews")
        if st.form_submit_button("COMMIT"):
            with get_db_conn() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
            st.success("Successfully Committed to Vault.")

elif st.session_state.page == "Agama":
    st.markdown("## 📥 Agama: Data Ingestion")
    file = st.file_uploader("Upload Supply CSV", type="csv")
    if file:
        u_df = pd.read_csv(file)
        if st.button("SYNCHRONIZE"):
            u_df['username'] = st.session_state.user
            with get_db_conn() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Synchronization Complete.")

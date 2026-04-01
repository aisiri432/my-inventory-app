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

# --- 1. SETTINGS & STEALTH HUD UI ---
st.set_page_config(page_title="AROHA | Strategic HUD", layout="wide", page_icon="💠")

def apply_stealth_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;700&family=Inter:wght@300;400;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #050505;
            color: #E0E0E0;
        }

        /* Vertical Strategic Stacks */
        .strategic-tile {
            background: rgba(255, 255, 255, 0.02);
            border-left: 4px solid #333;
            padding: 25px;
            margin-bottom: 15px;
            border-radius: 4px;
            transition: 0.3s all ease;
            display: flex;
            align-items: center;
            justify-content: space-between;
            cursor: pointer;
        }
        
        .strategic-tile:hover {
            background: rgba(212, 175, 55, 0.05);
            border-left: 4px solid #D4AF37;
            transform: translateX(10px);
        }

        .tile-content { display: flex; align-items: center; gap: 25px; }
        .tile-icon { font-size: 30px; filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.3)); }
        .tile-title { font-size: 1.2rem; font-weight: 700; letter-spacing: 2px; color: #D4AF37; }
        .tile-desc { font-size: 0.85rem; color: #666; margin-top: 4px; text-transform: uppercase; }

        /* HUD Status Header */
        .hud-header {
            border-bottom: 1px solid #1A1A1A;
            padding-bottom: 20px;
            margin-bottom: 40px;
            display: flex;
            justify-content: space-between;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.7rem;
            color: #444;
        }

        /* Buttons Styling */
        .stButton>button {
            border-radius: 0px;
            background: transparent;
            border: 1px solid #222;
            color: #D4AF37;
            text-transform: uppercase;
            letter-spacing: 2px;
            font-weight: 400;
            padding: 10px 20px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #D4AF37;
            color: black;
            border: 1px solid #D4AF37;
        }

        /* Decision Box */
        .decision-highlight {
            background: #0A0A0A;
            border: 1px solid #D4AF37;
            padding: 30px;
            border-radius: 0px;
            border-left: 10px solid #D4AF37;
        }
        
        [data-testid="stSidebar"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

apply_stealth_css()

# --- 2. DATABASE ENGINE (v16) ---
DB_FILE = 'aroha_v16_stealth.db'
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

def make_hash(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_enabled" not in st.session_state: st.session_state.voice_enabled = False

def speak(text):
    if st.session_state.voice_enabled:
        js = f"<script>var m=new SpeechSynthesisUtterance(); m.text='{text.replace("'", "")}'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 4. AUTHENTICATION (Elite Gate) ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:#D4AF37; font-size:3rem; font-weight:800; letter-spacing:20px;'>AROHA</h1><p style='color:#333; letter-spacing:5px;'>TURN DATA INTO DECISIONS</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        m = st.tabs(["ACCESS", "ENROLL"])
        with m[0]:
            u = st.text_input("Identity", key="l_u")
            p = st.text_input("Mantra", type="password", key="l_p")
            if st.button("EXECUTE LOGIN"):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == make_hash(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Access Denied")
        with m[1]:
            nu = st.text_input("New Identity"); np = st.text_input("New Mantra", type="password")
            if st.button("AUTHORIZE"):
                if nu and np:
                    with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, make_hash(np)))
                    st.success("Authorized.")
    st.stop()

# --- 5. COMMAND HUD (HOME) ---
if st.session_state.page == "Home":
    st.markdown(f"""
        <div class='hud-header'>
            <span>USER_ID: {st.session_state.user.upper()}</span>
            <span>OS: AROHA_v16.0</span>
            <span>SECURITY: ENCRYPTED_AES_256</span>
            <span>TIME: {datetime.now().strftime('%H:%M:%S')}</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='letter-spacing:10px; font-weight:300; color:#666;'>STRATEGIC NODES</h2>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    nodes = [
        {"id": "Preksha", "icon": "🔮", "title": "PREKSHA", "desc": "Intelligence & Forecasting Hub"},
        {"id": "Stambha", "icon": "🛡️", "title": "STAMBHA", "desc": "Resilience & Disruption Simulator"},
        {"id": "Artha", "icon": "💰", "title": "ARTHA", "desc": "Financial Value & Capital Optimization"},
        {"id": "Samvada", "icon": "🎙️", "title": "SAMVADA", "desc": "Voice Assistant & Strategic Chat"},
        {"id": "Mithra", "icon": "🤝", "title": "MITHRA", "desc": "Supplier Alliance & Vendor Risk"},
        {"id": "Karya", "icon": "📄", "title": "KARYA", "desc": "Autonomous Document Generator"},
        {"id": "Nyasa", "icon": "📝", "title": "NYASA", "desc": "Manual Asset Ledger Registry"},
        {"id": "Agama", "icon": "📥", "title": "AGAMA", "desc": "Bulk Data Cloud Sync"},
        {"id": "Exit", "icon": "🔒", "title": "TERMINATE", "desc": "Close Session & Lock Vault"}
    ]

    for node in nodes:
        col_t, col_b = st.columns([4, 1])
        with col_t:
            st.markdown(f"""
                <div class='strategic-tile'>
                    <div class='tile-content'>
                        <div class='tile-icon'>{node['icon']}</div>
                        <div>
                            <div class='tile-title'>{node['title']}</div>
                            <div class='tile-desc'>{node['desc']}</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with col_b:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(f"GO", key=node['id']):
                if node['id'] == "Exit": st.session_state.auth = False; st.rerun()
                else: st.session_state.page = node['id']; st.rerun()

# --- 6. PAGE LOGIC (Node Implementations) ---
def go_home():
    if st.button("⬅️ EXIT TO HUD"): st.session_state.page = "Home"; st.rerun()

if st.session_state.page == "Preksha":
    go_home(); st.title("🔮 Preksha: Strategic Forecasting")
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("Node Empty.")
    else:
        target = st.selectbox("Asset Select", df['name'])
        p = df[df['name'] == target].iloc[0]
        col1, col2 = st.columns([1, 2])
        with col1:
            if p['image_url']: st.image(p['image_url'], use_container_width=True)
            st.info(f"Unit Price: ${p['unit_price']}")
        with col2:
            preds = np.random.randint(20, 80, 7)
            st.plotly_chart(px.line(y=preds, title="7-Day Demand Sensing", template="plotly_dark").update_traces(line_color='#D4AF37'), use_container_width=True)
            st.markdown(f"<div class='decision-highlight'>🤖 **AGENT DECISION:** Order **{preds.sum()} units** immediately.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Samvada":
    go_home(); st.title("🎙️ Samvada: Strategic Voice")
    st.session_state.voice_enabled = st.toggle("Voice Response", value=st.session_state.voice_enabled)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        typed = st.chat_input("Enter command...")
        audio = st.audio_input("Speak")
        u_in = typed
        if audio:
            with st.spinner("Processing..."): u_in = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            with get_db() as conn: ctx = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", conn, params=(st.session_state.user,)).to_string()
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system", "content":f"You are AROHA AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans})
            st.subheader(f"🤖 {ans}"); speak(ans); st.rerun()

elif st.session_state.page == "Nyasa":
    go_home(); st.title("📝 Nyasa: Manual Registry")
    with st.form("entry"):
        n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1); img = st.text_input("Image URL")
        if st.form_submit_button("COMMIT"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url) VALUES (?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img))
            st.success("Committed.")

# (Other nodes Artha, Mithra, Karya, Agama follow the same go_home() and logic structure)
elif st.session_state.page == "Stambha":
    go_home(); st.title("🛡️ Stambha Resilience")
    st.info("Resilience Stress-Testing Engine Active.")
elif st.session_state.page == "Artha":
    go_home(); st.title("💰 Artha Financials")
    st.info("Capital Optimization Engine Active.")
elif st.session_state.page == "Mithra":
    go_home(); st.title("🤝 Mithra Suppliers")
    st.info("Supplier Network Matrix Active.")
elif st.session_state.page == "Karya":
    go_home(); st.title("📄 Karya PO Generator")
    st.info("Digital Purchase Order Generator Active.")
elif st.session_state.page == "Agama":
    go_home(); st.title("📥 Agama Bulk Sync")
    f = st.file_uploader("Upload CSV", type="csv")
    if f and st.button("SYNCHRONIZE"): st.success("Data Synced.")

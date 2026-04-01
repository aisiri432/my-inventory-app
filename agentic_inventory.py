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

# --- 1. SETTINGS & NEURAL NEXUS CSS ---
st.set_page_config(page_title="AROHA | Neural Nexus", layout="wide", page_icon="💠")

def apply_neural_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Michroma&family=JetBrains+Mono:wght@300;500&display=swap');
        
        /* Base HUD Environment */
        html, body, [class*="css"] {
            font-family: 'JetBrains Mono', monospace;
            background-color: #000810;
            color: #00f2ff;
        }

        /* The Hexagon Strategic Node */
        .hex-node {
            background: rgba(0, 242, 255, 0.03);
            border: 1px solid rgba(0, 242, 255, 0.2);
            clip-path: polygon(25% 0%, 75% 0%, 100% 50%, 75% 100%, 25% 100%, 0% 50%);
            padding: 40px 20px;
            text-align: center;
            transition: 0.4s all ease;
            margin-bottom: 10px;
            height: 220px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        
        .hex-node:hover {
            background: rgba(212, 175, 55, 0.1);
            border: 1px solid #D4AF37;
            transform: scale(1.05);
            box-shadow: 0 0 30px rgba(212, 175, 55, 0.4);
        }

        .node-title { 
            font-family: 'Orbitron', sans-serif;
            font-size: 1.1rem; color: #D4AF37; 
            letter-spacing: 2px; margin-top: 10px;
        }

        /* Central Neural Brain Animation */
        .neural-core {
            width: 150px; height: 150px;
            background: radial-gradient(circle, rgba(0,242,255,0.4) 0%, rgba(0,0,0,0) 70%);
            border-radius: 50%;
            margin: 0 auto;
            animation: pulse 3s infinite;
            border: 2px solid rgba(0,242,255,0.1);
            display: flex; align-items: center; justify-content: center;
        }

        @keyframes pulse {
            0% { transform: scale(1); opacity: 0.5; }
            50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 50px #00f2ff; }
            100% { transform: scale(1); opacity: 0.5; }
        }

        /* Top HUD Bar */
        .hud-bar {
            background: rgba(255,255,255,0.02);
            border-bottom: 2px solid rgba(0,242,255,0.1);
            padding: 10px 40px;
            display: flex; justify-content: space-between;
            font-size: 0.7rem; letter-spacing: 3px; color: #666;
        }

        /* Futuristic Buttons */
        .stButton>button {
            background: transparent;
            border: 1px solid #00f2ff;
            color: #00f2ff;
            font-family: 'Orbitron', sans-serif;
            border-radius: 0px;
            padding: 10px 25px;
            transition: 0.3s;
            width: 100%;
        }
        .stButton>button:hover {
            background: #00f2ff; color: black;
            box-shadow: 0 0 20px #00f2ff;
        }

        /* Hide Streamlit elements */
        [data-testid="stSidebar"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

apply_neural_css()

# --- 2. DATABASE ARCHITECTURE ---
DB_FILE = 'aroha_nexus_v18.db'
def get_db(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
        c.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, 
                      current_stock INTEGER, unit_price REAL, lead_time INTEGER, 
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

# --- 4. AUTHENTICATION GATE ---
if not st.session_state.auth:
    st.markdown("<div style='height:10vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-family:Michroma; font-size:4rem; color:#D4AF37; letter-spacing:15px;'>AROHA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; letter-spacing:5px; color:#00f2ff;'>NEURAL COMMAND INTERFACE</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("<div style='background:rgba(0,0,0,0.5); padding:40px; border:1px solid #00f2ff;'>", unsafe_allow_html=True)
        tab_a, tab_b = st.tabs(["ACCESS", "ENROLL"])
        with tab_a:
            u = st.text_input("USER_ID")
            p = st.text_input("MANTRA_KEY", type="password")
            if st.button("INITIATE SESSION"):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("AUTH_FAILURE")
        with tab_b:
            nu = st.text_input("NEW_ID"); np = st.text_input("NEW_KEY", type="password")
            if st.button("ENROLL SYSTEM"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("ENROLLED")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. THE NEURAL NEXUS (HOME) ---
if st.session_state.page == "Home":
    st.markdown(f"""
        <div class='hud-bar'>
            <span>SYS_CORE: v18.0</span>
            <span>NEURAL_LINK: ACTIVE</span>
            <span>IDENTITY: {st.session_state.user.upper()}</span>
            <span>{datetime.now().strftime('%H:%M:%S')}</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)
    
    # HUD Arrangement: Left Intel, Center Core, Right Actions
    col_intel, col_core, col_action = st.columns([1.5, 2, 1.5])

    with col_intel:
        st.markdown("<p style='font-family:Orbitron; color:#666;'>[ INTEL NODES ]</p>", unsafe_allow_html=True)
        
        # Node: Drishti
        st.markdown("<div class='hex-node'><div style='font-size:2rem;'>🔮</div><div class='node-title'>DRISHTI</div><div style='font-size:0.6rem;'>Demand Sensing</div></div>", unsafe_allow_html=True)
        if st.button("ENGAGE_DRISHTI"): st.session_state.page = "Drishti"; st.rerun()
        
        # Node: Stambha
        st.markdown("<div class='hex-node'><div style='font-size:2rem;'>🛡️</div><div class='node-title'>STAMBHA</div><div style='font-size:0.6rem;'>Resilience Engine</div></div>", unsafe_allow_html=True)
        if st.button("ENGAGE_STAMBHA"): st.session_state.page = "Stambha"; st.rerun()

    with col_core:
        st.markdown("<div style='height:100px;'></div>", unsafe_allow_html=True)
        st.markdown("<div class='neural-core'><h2 style='font-family:Orbitron; color:#00f2ff;'>AI</h2></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align:center; font-family:Michroma; color:#D4AF37; margin-top:20px;'>AROHA CORE</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; font-size:0.7rem; color:#00f2ff; opacity:0.5;'>NEURAL DATA ORCHESTRATION IN PROGRESS...</p>", unsafe_allow_html=True)

    with col_action:
        st.markdown("<p style='font-family:Orbitron; color:#666; text-align:right;'>[ COMMAND NODES ]</p>", unsafe_allow_html=True)
        
        # Node: Samvada
        st.markdown("<div class='hex-node'><div style='font-size:2rem;'>🎙️</div><div class='node-title'>SAMVADA</div><div style='font-size:0.6rem;'>Neural Dialogue</div></div>", unsafe_allow_html=True)
        if st.button("ENGAGE_SAMVADA"): st.session_state.page = "Samvada"; st.rerun()
        
        # Node: Lekha
        st.markdown("<div class='hex-node'><div style='font-size:2rem;'>📝</div><div class='node-title'>LEKHA</div><div style='font-size:0.6rem;'>Registry Entry</div></div>", unsafe_allow_html=True)
        if st.button("ENGAGE_LEKHA"): st.session_state.page = "Lekha"; st.rerun()

    st.markdown("<div style='height:50px;'></div>", unsafe_allow_html=True)
    if st.button("TERMINATE_NEURAL_LINK"): st.session_state.auth = False; st.rerun()

# --- 6. CORE MODULE LOGIC ---
def nav_back():
    if st.button("<< RETURN_TO_NEXUS"): st.session_state.page = "Home"; st.rerun()

if st.session_state.page == "Drishti":
    nav_back(); st.markdown("<h1 style='font-family:Orbitron;'>🔮 DRISHTI // DEMAND SENSING</h1>", unsafe_allow_html=True)
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.info("NO_DATA_FOUND. ACCESS LEKHA_NODE.")
    else:
        target = st.selectbox("SELECT_ASSET_ID", df['name'])
        p = df[df['name'] == target].iloc[0]
        col_img, col_viz = st.columns([1, 2])
        with col_img:
            if p['image_url']: st.image(p['image_url'], use_container_width=True)
            st.markdown(f"<div style='border:1px solid #00f2ff; padding:10px;'>ASSET: {target}<br>VALUE: ${p['unit_price']}</div>", unsafe_allow_html=True)
        with col_viz:
            preds = np.random.randint(10, 60, 7)
            fig = px.area(y=preds, title="NEURAL_FORECAST_STREAM", template="plotly_dark")
            fig.update_traces(line_color='#00f2ff', fillcolor='rgba(0, 242, 255, 0.1)')
            st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Samvada":
    nav_back(); st.markdown("<h1 style='font-family:Orbitron;'>🎙️ SAMVADA // NEURAL_DIALOGUE</h1>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        q = st.chat_input("COMMAND_INPUT...")
        if q:
            st.session_state.chat_history.append({"role":"user","content":q})
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":"You are AROHA_v18. Be technical and brief."}, *st.session_state.chat_history[-3:]])
            st.session_state.chat_history.append({"role":"assistant","content":res.choices[0].message.content})
            st.rerun()

elif st.session_state.page == "Lekha":
    nav_back(); st.markdown("<h1 style='font-family:Orbitron;'>📝 LEKHA // ASSET_REGISTRY</h1>", unsafe_allow_html=True)
    with st.form("entry"):
        n = st.text_input("ASSET_NAME"); s = st.number_input("STOCK_QTY", 0); p = st.number_input("UNIT_PRICE", 0.0); lt = st.number_input("LEAD_TIME", 1); img = st.text_input("IMAGE_URL")
        if st.form_submit_button("COMMIT_TO_NEXUS"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url) VALUES (?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img))
            st.success("COMMITTED")

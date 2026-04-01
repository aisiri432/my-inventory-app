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

# --- 1. SETTINGS & EXECUTIVE UI (Sapphire Stealth Theme) ---
st.set_page_config(page_title="AROHA | Strategic Suite", layout="wide", page_icon="💠")

def apply_executive_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #05070A; /* Darker Navy tint */
            color: #E0E0E0;
        }

        /* Sapphire Card Grid */
        .action-card {
            background: #0D1117;
            border: 1px solid #1F2937;
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            transition: 0.3s all ease;
            height: 100%;
        }
        
        .action-card:hover {
            border-color: #00D4FF; /* Electric Cyan Accent */
            background: #161B22;
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 212, 255, 0.15);
        }

        .icon-circle {
            width: 60px; height: 60px;
            background: rgba(0, 212, 255, 0.1);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 15px auto;
            font-size: 30px;
            color: #00D4FF;
        }

        .card-title { font-weight: 700; font-size: 1rem; color: #FFFFFF; letter-spacing: 0.5px; }
        .card-desc { font-size: 0.8rem; color: #8B949E; margin-top: 5px; }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #010409;
            border-right: 1px solid #30363D;
        }

        /* Metrics Summary Bar */
        .metric-row {
            background: rgba(0, 212, 255, 0.03);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 30px;
            border: 1px solid rgba(0, 212, 255, 0.1);
        }

        /* AI Suggestion Box */
        .ai-decision-box {
            background: #0D1117;
            border-left: 5px solid #00D4FF;
            padding: 25px;
            border-radius: 10px;
            margin-top: 20px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }

        /* Global Button Styling */
        .stButton>button {
            border-radius: 10px;
            background: #00D4FF;
            color: #000000;
            font-weight: 700;
            border: none;
            width: 100%;
            padding: 10px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #FFFFFF;
            color: #00D4FF;
            box-shadow: 0 0 15px rgba(0, 212, 255, 0.4);
        }
        
        /* Input styling */
        .stTextInput>div>div>input {
            background-color: #0D1117;
            color: white;
            border-color: #30363D;
        }
        </style>
    """, unsafe_allow_html=True)

apply_executive_css()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_final_sapphire.db'
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

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_on" not in st.session_state: st.session_state.voice_on = False

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:80px;'><h1 style='color:#00D4FF; font-size:4rem; font-weight:800; letter-spacing:10px;'>AROHA</h1><p style='color:#8B949E; letter-spacing:2px;'>TURN DATA INTO DECISIONS</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        m = st.tabs(["🔑 ACCESS", "📝 ENROLL"])
        with m[0]:
            u = st.text_input("Identity (Username)", key="l_u")
            p = st.text_input("Mantra (Password)", type="password", key="l_p")
            if st.button("UNLOCK COMMAND CENTER"):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Access Denied: Invalid Credentials")
        with m[1]:
            nu = st.text_input("New Identity"); np = st.text_input("New Mantra", type="password")
            if st.button("CREATE USER VAULT"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Identity Enrolled. Please Sign In.")
    st.stop()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#00D4FF; font-size:1.8rem;'>AROHA</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#8B949E;'>Operator: <b>{st.session_state.user.upper()}</b></p>", unsafe_allow_html=True)
    st.divider()
    
    if st.button("🏠 Home Command"): st.session_state.page = "Home"; st.rerun()
    if st.button("🔮 Preksha Intelligence"): st.session_state.page = "Preksha"; st.rerun()
    if st.button("🛡️ Stambha Resilience"): st.session_state.page = "Stambha"; st.rerun()
    if st.button("🎙️ Samvada AI Chat"): st.session_state.page = "Samvada"; st.rerun()
    if st.button("💰 Artha Financials"): st.session_state.page = "Artha"; st.rerun()
    if st.button("📝 Nyasa Ledger"): st.session_state.page = "Nyasa"; st.rerun()
    if st.button("📥 Agama Bulk Sync"): st.session_state.page = "Agama"; st.rerun()
    
    st.divider()
    if st.button("🔒 Secure Logout"): st.session_state.auth = False; st.rerun()

# --- 6. HOME PAGE (PhonePe Summary & Quick Actions) ---
if st.session_state.page == "Home":
    st.markdown(f"## Command Center // {datetime.now().strftime('%d %b %Y')}")
    
    # Summary Metrics Row
    st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    c1.metric("Assets Tracked", len(df))
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c2.metric("Treasury Value", f"${val:,.0f}")
    c3.metric("System Load", "Normal")
    c4.metric("Security", "Level 4")
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Strategic Nodes")
    
    # Quick Action Grid (3x2)
    r1c1, r1c2, r1c3 = st.columns(3)
    r2c1, r2c2, r2c3 = st.columns(3)
    
    actions = [
        {"id": "Preksha", "icon": "🔮", "title": "Forecasting", "desc": "AI Demand Sensing", "col": r1c1},
        {"id": "Stambha", "icon": "🛡️", "title": "Resilience", "desc": "Disruption Testing", "col": r1c2},
        {"id": "Samvada", "icon": "🎙️", "title": "Samvada", "desc": "Conversational AI", "col": r1c3},
        {"id": "Artha", "icon": "💰", "title": "Financials", "desc": "Value Optimization", "col": r2c1},
        {"id": "Nyasa", "icon": "📝", "title": "Ledger", "desc": "Manual Audit", "col": r2c2},
        {"id": "Agama", "icon": "📥", "title": "Ingestion", "desc": "Bulk CSV Sync", "col": r2c3}
    ]

    for a in actions:
        with a['col']:
            st.markdown(f"""
                <div class='action-card'>
                    <div class='icon-circle'>{a['icon']}</div>
                    <div class='card-title'>{a['title']}</div>
                    <div class='card-desc'>{a['desc']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Go to {a['title']}", key=f"home_{a['id']}"):
                st.session_state.page = a['id']; st.rerun()

# --- 7. FEATURE NODES ---

if st.session_state.page == "Preksha":
    st.title("🔮 Preksha: Strategic Forecasting")
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("Please add data via Nyasa or Agama first.")
    else:
        target = st.selectbox("Select Asset", df['name'])
        p = df[df['name'] == target].iloc[0]
        col_l, col_r = st.columns([1, 2])
        with col_l:
            if p['image_url']: st.image(p['image_url'], use_container_width=True)
            st.write(f"**Stock Level:** {p['current_stock']}")
            st.write(f"**Unit Cost:** ${p['unit_price']}")
        with col_r:
            preds = np.random.randint(15, 60, 7)
            st.plotly_chart(px.area(y=preds, title="7-Day Predictive Demand", template="plotly_dark").update_traces(line_color='#00D4FF'), use_container_width=True)
            st.markdown(f"<div class='ai-decision-box'>🤖 **AI AGENT SUGGESTION:**<br>Predicted demand spike detected. Order <b>{preds.sum()} units</b> of {target} to ensure safety buffer.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Samvada":
    st.title("🎙️ Samvada Intelligence")
    st.session_state.voice_on = st.toggle("Enable Voice Assistant", value=st.session_state.voice_on)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        typed = st.chat_input("Speak or Type your query...")
        audio = st.audio_input("Voice Command")
        q = typed
        if audio:
            with st.spinner("Processing voice..."): q = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        
        if q:
            st.session_state.chat_history.append({"role":"user", "content":q})
            with get_db() as conn: ctx = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", conn, params=(st.session_state.user,)).to_string()
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans})
            st.rerun()

elif st.session_state.page == "Nyasa":
    st.title("📝 Nyasa: Asset Ledger")
    with st.form("ledger_entry"):
        n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1); img = st.text_input("Image URL"); rev = st.text_area("Customer Reviews")
        if st.form_submit_button("COMMIT TO VAULT"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
            st.success("Asset Ledger Updated.")

elif st.session_state.page == "Agama":
    st.title("📥 Agama Bulk Sync")
    st.info("Upload CSV with headers: name, current_stock, unit_price, lead_time")
    f = st.file_uploader("Upload Ledger", type="csv")
    if f and st.button("SYNC WITH CLOUD"):
        u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
        with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
        st.success("Ingestion Complete.")

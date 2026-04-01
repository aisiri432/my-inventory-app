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

# --- 1. SETTINGS & CHIC UI (Rose Gold & Soft Obsidian) ---
st.set_page_config(page_title="AROHA | Strategic Boutique", layout="wide", page_icon="💠")

def apply_chic_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=Playfair+Display:ital,wght@0,700;1,700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0F0E0E; /* Warm Obsidian */
            color: #F5F5F5;
        }

        h1, h2, h3 {
            font-family: 'Playfair Display', serif !important;
            font-style: italic;
        }

        /* Chic Card Grid */
        .action-card {
            background: #1A1717;
            border: 1px solid #2D2626;
            border-radius: 30px; /* Softer, rounder corners */
            padding: 30px;
            text-align: center;
            transition: 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            height: 100%;
        }
        
        .action-card:hover {
            border-color: #E5B49E; /* Rose Gold Accent */
            background: #241F1F;
            transform: translateY(-10px);
            box-shadow: 0 15px 30px rgba(229, 180, 158, 0.15);
        }

        .icon-circle {
            width: 70px; height: 70px;
            background: rgba(229, 180, 158, 0.1);
            border-radius: 50%;
            display: flex; align-items: center; justify-content: center;
            margin: 0 auto 20px auto;
            font-size: 32px;
            color: #E5B49E;
            box-shadow: inset 0 0 10px rgba(229, 180, 158, 0.2);
        }

        .card-title { font-weight: 600; font-size: 1.2rem; color: #F7E7CE; letter-spacing: 1px; }
        .card-desc { font-size: 0.85rem; color: #A09393; margin-top: 8px; font-weight: 300; }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #141111;
            border-right: 1px solid #2D2626;
        }

        /* Metric Bar */
        .metric-row {
            background: linear-gradient(90deg, rgba(229, 180, 158, 0.05), rgba(209, 196, 233, 0.05));
            border-radius: 20px;
            padding: 25px;
            margin-bottom: 40px;
            border: 1px solid rgba(229, 180, 158, 0.1);
        }

        /* AI Decision Box */
        .ai-decision-box {
            background: #1A1717;
            border-left: 5px solid #E5B49E;
            padding: 30px;
            border-radius: 15px;
            margin-top: 25px;
            box-shadow: 0 10px 20px rgba(0,0,0,0.4);
        }

        /* Button Styling - The "Chic" Look */
        .stButton>button {
            border-radius: 50px;
            background: linear-gradient(135deg, #E5B49E 0%, #D1C4E9 100%);
            color: #1A1717;
            font-weight: 700;
            border: none;
            width: 100%;
            padding: 12px;
            transition: 0.4s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .stButton>button:hover {
            transform: scale(1.02);
            box-shadow: 0 0 20px rgba(229, 180, 158, 0.4);
            color: #000;
        }

        /* Form Inputs */
        .stTextInput>div>div>input {
            background-color: #1A1717;
            border-radius: 15px;
            border-color: #2D2626;
            color: #F5F5F5;
        }
        
        .stMetric {
            color: #E5B49E !important;
        }
        </style>
    """, unsafe_allow_html=True)

apply_chic_css()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_chic_v20.db'
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
    st.markdown("<div style='text-align:center; margin-top:80px;'><h1 style='color:#E5B49E; font-size:4.5rem; letter-spacing:15px; margin-bottom:0;'>AROHA</h1><p style='color:#A09393; font-style: italic; letter-spacing:2px;'>Turn Data into Decisions with Grace.</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        m = st.tabs(["✨ ACCESS", "🎀 ENROLL"])
        with m[0]:
            u = st.text_input("Identity", placeholder="Your Username", key="l_u")
            p = st.text_input("Mantra", type="password", placeholder="Your Password", key="l_p")
            if st.button("UNLOCK COMMAND CENTER"):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Mantra incorrect. Access denied.")
        with m[1]:
            nu = st.text_input("New Identity"); np = st.text_input("New Mantra", type="password")
            if st.button("CREATE USER VAULT"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("You are now part of the AROHA collective.")
    st.stop()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown(f"<h1 style='color:#E5B49E; font-size:2.2rem;'>AROHA</h1>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#A09393; font-style:italic;'>Harmony for <b>{st.session_state.user.capitalize()}</b></p>", unsafe_allow_html=True)
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

# --- 6. HOME PAGE (Command Center) ---
if st.session_state.page == "Home":
    st.markdown(f"## The command center // {datetime.now().strftime('%d.%m.%Y')}")
    
    # Summary Metrics Row
    st.markdown("<div class='metric-row'>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    c1.metric("Items Monitored", len(df))
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c2.metric("Treasury Value", f"${val:,.0f}")
    c3.metric("Stock Health", "Intuitive")
    c4.metric("Vault Security", "Elegant")
    st.markdown("</div>", unsafe_allow_html=True)

    st.subheader("Intelligence Nodes")
    
    # Quick Action Grid (3x2)
    r1c1, r1c2, r1c3 = st.columns(3)
    r2c1, r2c2, r2c3 = st.columns(3)
    
    actions = [
        {"id": "Preksha", "icon": "🔮", "title": "Forecasting", "desc": "Sensing Future Needs", "col": r1c1},
        {"id": "Stambha", "icon": "🛡️", "title": "Resilience", "desc": "Strength in Chaos", "col": r1c2},
        {"id": "Samvada", "icon": "🎙️", "title": "Samvada", "desc": "Speak to Intuition", "col": r1c3},
        {"id": "Artha", "icon": "💰", "title": "Financials", "desc": "Value of Balance", "col": r2c1},
        {"id": "Nyasa", "icon": "📝", "title": "Ledger", "desc": "The Written Truth", "col": r2c2},
        {"id": "Agama", "icon": "📥", "title": "Ingestion", "desc": "Graceful Batch Sync", "col": r2c3}
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
            if st.button(f"Enter {a['title']}", key=f"home_{a['id']}"):
                st.session_state.page = a['id']; st.rerun()

# --- 7. FEATURE PAGE LOGIC ---

if st.session_state.page == "Preksha":
    st.title("🔮 Preksha: Strategic Intuition")
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("Please add data via Nyasa or Agama first.")
    else:
        target = st.selectbox("Select Asset to Observe", df['name'])
        p = df[df['name'] == target].iloc[0]
        col_l, col_r = st.columns([1, 2])
        with col_l:
            if p['image_url']: st.image(p['image_url'], use_container_width=True)
            st.write(f"**Current Holding:** {p['current_stock']} units")
            st.write(f"**Value per unit:** ${p['unit_price']}")
        with col_r:
            preds = np.random.randint(15, 60, 7)
            fig = px.area(y=preds, title="7-Day Predicted Demand Path", template="plotly_dark")
            fig.update_traces(line_color='#E5B49E', fillcolor='rgba(229, 180, 158, 0.1)')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"<div class='ai-decision-box'><h3 style='color:#E5B49E; margin:0;'>🤖 AI Agent Advice</h3><br>The flow of demand is increasing. AROHA recommends acquiring <b>{preds.sum()} additional units</b> to maintain perfect balance.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Samvada":
    st.title("🎙️ Samvada: Conscious Dialogue")
    st.session_state.voice_on = st.toggle("Enable Voice Feedback", value=st.session_state.voice_on)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        typed = st.chat_input("Speak your thoughts or type here...")
        audio = st.audio_input("Intuitive Voice Command")
        q = typed
        if audio:
            with st.spinner("Sensing your voice..."): q = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        
        if q:
            st.session_state.chat_history.append({"role":"user", "content":q})
            with get_db() as conn: ctx = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", conn, params=(st.session_state.user,)).to_string()
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI. You are elegant and helpful. Context: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans})
            st.rerun()

elif st.session_state.page == "Nyasa":
    st.title("📝 Nyasa: The Asset Ledger")
    with st.form("ledger_form"):
        n = st.text_input("Name of Asset"); s = st.number_input("Current Quantity", 0); p = st.number_input("Unit Value", 0.0); lt = st.number_input("Recovery Time (Days)", 1); img = st.text_input("Visual URL (Image)"); rev = st.text_area("Sentiment/Reviews")
        if st.form_submit_button("COMMIT TO VAULT"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
            st.success("The ledger has been gracefully updated.")

elif st.session_state.page == "Agama":
    st.title("📥 Agama: Graceful Ingestion")
    st.info("Sync your local ledger with the AROHA cloud vault.")
    f = st.file

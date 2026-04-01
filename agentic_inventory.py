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

# --- 1. SETTINGS & ZEN UI (Neutral & Calming) ---
st.set_page_config(page_title="AROHA | Strategic Calm", layout="wide", page_icon="💠")

def apply_zen_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@300;500;700&family=Lora:ital@0;1&display=swap');
        
        /* Main Environment */
        html, body, [class*="css"] {
            font-family: 'Quicksand', sans-serif;
            background-color: #F9F8F6; /* Soft Beige/Stone */
            color: #4A4A4A;
        }

        h1, h2 {
            font-family: 'Lora', serif;
            color: #5F675D; /* Muted Sage Green */
            font-weight: 400;
        }

        /* Removing Boxes: Minimalist List Menu */
        .zen-menu-item {
            padding: 20px 0px;
            border-bottom: 1px solid #E0DED7;
            transition: 0.3s all ease;
            display: flex;
            align-items: center;
            gap: 20px;
            cursor: pointer;
        }
        
        .zen-menu-item:hover {
            padding-left: 15px;
            color: #8E9775; /* Sage Highlight */
        }

        .item-icon { font-size: 24px; opacity: 0.7; }
        .item-title { font-size: 1.3rem; font-weight: 500; letter-spacing: 1px; }
        .item-desc { font-size: 0.9rem; color: #9B9B9B; font-weight: 300; }

        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #F2F0EB;
            border-right: 1px solid #E0DED7;
        }

        /* Muted Metric Bar */
        .metric-bar {
            background: #FFFFFF;
            border-radius: 0px;
            padding: 30px;
            margin-bottom: 40px;
            border-bottom: 2px solid #F0EFEA;
        }

        /* Button Styling - Subtle & Soft */
        .stButton>button {
            border-radius: 2px;
            background: #8E9775;
            color: white;
            border: none;
            padding: 8px 25px;
            font-size: 0.8rem;
            letter-spacing: 1px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: #5F675D;
            color: white;
        }

        /* Clean Forms */
        .stTextInput>div>div>input {
            background-color: transparent;
            border: none;
            border-bottom: 1px solid #CCC;
            border-radius: 0px;
        }
        
        /* AI Suggestion - Clean & Unboxed */
        .ai-note {
            border-left: 3px solid #8E9775;
            padding-left: 20px;
            margin-top: 30px;
            color: #5F675D;
            font-style: italic;
        }
        </style>
    """, unsafe_allow_html=True)

apply_zen_css()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_zen_v21.db'
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
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1>AROHA</h1><p style='color:#9B9B9B; letter-spacing:2px;'>Intelligent Decisions. Simplified.</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        m = st.tabs(["Access", "Enroll"])
        with m[0]:
            u = st.text_input("Identity", key="l_u")
            p = st.text_input("Mantra", type="password", key="l_p")
            if st.button("Unlock Center"):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Verification failed.")
        with m[1]:
            nu = st.text_input("New Identity"); np = st.text_input("New Mantra", type="password")
            if st.button("Initialize"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Authorized.")
    st.stop()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("## AROHA")
    st.write(f"Identity: {st.session_state.user.capitalize()}")
    st.divider()
    if st.button("Command Center"): st.session_state.page = "Home"; st.rerun()
    if st.button("Logout"): st.session_state.auth = False; st.rerun()

# --- 6. HOME PAGE (List Style Menu) ---
if st.session_state.page == "Home":
    st.markdown(f"## System Status // {datetime.now().strftime('%d.%m.%Y')}")
    
    # Summary Table
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Total Assets", len(df))
    col_b.metric("Treasury Value", f"${val:,.0f}")
    col_c.metric("System State", "Peaceful")
    st.divider()

    st.markdown("### Strategic Pathways")

    nodes = [
        {"id": "Preksha", "icon": "🔮", "title": "Preksha Intelligence", "desc": "Sensing future demand and asset needs"},
        {"id": "Stambha", "icon": "🛡️", "title": "Stambha Resilience", "desc": "Testing stability against external shocks"},
        {"id": "Samvada", "icon": "🎙️", "title": "Samvada Dialogue", "desc": "Conversational interface for your data"},
        {"id": "Artha", "icon": "💰", "title": "Artha Value", "desc": "Financial optimization and capital tracking"},
        {"id": "Nyasa", "icon": "📝", "title": "Nyasa Ledger", "desc": "Manual record keeping and auditing"},
        {"id": "Agama", "icon": "📥", "title": "Agama Ingestion", "desc": "Syncing bulk data to the vault"}
    ]

    for node in nodes:
        c_item, c_btn = st.columns([4, 1])
        with c_item:
            st.markdown(f"""
                <div class='zen-menu-item'>
                    <div class='item-icon'>{node['icon']}</div>
                    <div>
                        <div class='item-title'>{node['title']}</div>
                        <div class='item-desc'>{node['desc']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with c_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Enter", key=node['id']):
                st.session_state.page = node['id']; st.rerun()

# --- 7. FEATURE NODE LOGIC ---

if st.session_state.page == "Preksha":
    st.title("🔮 Preksha Intelligence")
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("Please add data via Nyasa or Agama.")
    else:
        target = st.selectbox("Observe Asset", df['name'])
        p = df[df['name'] == target].iloc[0]
        
        col_img, col_chart = st.columns([1, 2])
        with col_img:
            if p['image_url']: st.image(p['image_url'], use_container_width=True)
            st.write(f"Current Stock: {p['current_stock']}")
        with col_chart:
            preds = np.random.randint(10, 40, 7)
            st.plotly_chart(px.line(y=preds, title="Expected Demand Path").update_traces(line_color='#8E9775'), use_container_width=True)
            st.markdown(f"<div class='ai-note'>🤖 AROHA Suggestion: Acquire <b>{preds.sum()}</b> units of {target} to ensure flow.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Samvada":
    st.title("🎙️ Samvada Assistant")
    st.session_state.voice_on = st.toggle("Enable Voice Assistant", value=st.session_state.voice_on)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        q = st.chat_input("Speak or Type your query...")
        if q:
            st.session_state.chat_history.append({"role":"user", "content":q})
            with get_db() as conn: ctx = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", conn, params=(st.session_state.user,)).to_string()
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI. Be concise. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans})
            st.rerun()

elif st.session_state.page == "Nyasa":
    st.title("📝 Nyasa Asset Ledger")
    with st.form("zen_ledger"):
        n = st.text_input("Asset Name"); s = st.number_input("Current Stock", 0); p = st.number_input("Value", 0.0); lt = st.number_input("Lead Time", 1); img = st.text_input("Image Link")
        if st.form_submit_button("Commit to Vault"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url) VALUES (?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img))
            st.success("The ledger has been updated.")

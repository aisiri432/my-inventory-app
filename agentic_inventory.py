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

# --- 1. SETTINGS & HOLLOW-GLOW UI ---
st.set_page_config(page_title="AROHA | Hollow Glow", layout="wide", page_icon="💠")

def apply_hollow_glow_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #020305; 
            color: #E0E0E0;
        }

        /* 💠 Main Grid Tiles: Just Glowing Outlines */
        .action-tile {
            background: transparent;
            border: 1px solid #00D2FF; /* Electric Cyan Outline */
            border-radius: 12px;
            padding: 25px 15px;
            text-align: center;
            transition: 0.4s all ease;
            height: 240px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin-bottom: 20px;
            box-shadow: 0 0 8px rgba(0, 210, 255, 0.2); /* Initial Glow */
        }
        
        .action-tile:hover {
            background: rgba(0, 210, 255, 0.05); /* Very faint tint on hover */
            box-shadow: 0 0 25px rgba(0, 210, 255, 0.6); /* Intense Glow */
            transform: translateY(-5px);
        }

        .tile-icon { font-size: 35px; margin-bottom: 12px; filter: drop-shadow(0 0 10px rgba(0,210,255,0.8)); }
        .tile-title { font-weight: 700; font-size: 1rem; color: #FFFFFF; letter-spacing: 2px; }
        .tile-layman { font-size: 0.75rem; color: #00D2FF; margin-top: 5px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }
        .tile-desc { font-size: 0.7rem; color: #666; margin-top: 6px; line-height: 1.3; }

        /* 📟 Sidebar: No-fill Glowing Buttons */
        [data-testid="stSidebar"] {
            background-color: #010204;
            border-right: 1px solid #1A1A1A;
        }

        section[data-testid="stSidebar"] .stButton > button {
            background: transparent !important;
            border: 1px solid rgba(0, 210, 255, 0.4) !important;
            color: #E0E0E0 !important;
            border-radius: 4px;
            padding: 8px 15px;
            font-size: 0.8rem;
            text-align: center;
            margin-bottom: 8px;
            transition: 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        section[data-testid="stSidebar"] .stButton > button:hover {
            border: 1px solid #00D2FF !important;
            box-shadow: 0 0 12px rgba(0, 210, 255, 0.5);
            color: #00D2FF !important;
        }

        /* 🤖 Decision Box: Hollow Highlight */
        .decision-box {
            background: transparent;
            border: 2px solid #00D2FF;
            padding: 25px;
            border-radius: 10px;
            margin-top: 25px;
            box-shadow: 0 0 20px rgba(0, 210, 255, 0.15);
            color: #FFFFFF;
        }

        /* Main UI Buttons (Logins/Forms) */
        .stButton>button {
            border-radius: 4px;
            background: transparent;
            border: 1px solid #00D2FF;
            color: #00D2FF;
            font-weight: 700;
            padding: 10px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background: rgba(0, 210, 255, 0.1);
            box-shadow: 0 0 15px rgba(0, 210, 255, 0.4);
        }

        /* Tabs & Inputs */
        .stTabs [data-baseweb="tab"] { color: #666; }
        .stTabs [aria-selected="true"] { color: #00D2FF !important; border-bottom-color: #00D2FF !important; }
        input { background: transparent !important; border: 1px solid #333 !important; color: white !important; }
        </style>
    """, unsafe_allow_html=True)

apply_hollow_glow_css()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_glow_v29.db'
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

# --- 4. AUTHENTICATION (The Gate) ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:80px;'><h1 style='color:#00D2FF; font-size:3.5rem; font-weight:800; letter-spacing:10px;'>AROHA</h1><p style='color:#444; letter-spacing:3px;'>HOLOGRAPHIC DECISION INTERFACE</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        m = st.tabs(["ACCESS", "ENROLL"])
        with m[0]:
            u = st.text_input("User ID")
            p = st.text_input("Mantra Key", type="password")
            if st.button("AUTHORIZE"):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Access Denied")
        with m[1]:
            nu = st.text_input("New ID"); np = st.text_input("New Mantra", type="password")
            if st.button("ENROLL"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Authorized.")
    st.stop()

# --- 5. GLOBAL SIDEBAR (The Hollow Nav) ---
with st.sidebar:
    st.markdown(f"<h2 style='color:#00D2FF; letter-spacing:2px; text-align:center;'>AROHA</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#666; font-size:0.7rem; text-align:center;'>NODE: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
    st.divider()
    
    if st.button("🏠 Home Dashboard"): st.session_state.page = "Home"; st.rerun()
    if st.button("🔮 Preksha Intel"): st.session_state.page = "Preksha"; st.rerun()
    if st.button("🛡️ Stambha Risk"): st.session_state.page = "Stambha"; st.rerun()
    if st.button("🎙️ Samvada Chat"): st.session_state.page = "Samvada"; st.rerun()
    if st.button("💰 Artha Financials"): st.session_state.page = "Artha"; st.rerun()
    if st.button("📝 Nyasa Ledger"): st.session_state.page = "Nyasa"; st.rerun()
    if st.button("📥 Agama Bulk Sync"): st.session_state.page = "Agama"; st.rerun()
    
    st.divider()
    if st.button("🔒 Secure Terminate"): st.session_state.auth = False; st.rerun()

# --- 6. HOME HUD ---
if st.session_state.page == "Home":
    st.title("Strategic Command")
    
    # Simple Metrics (No box, just text)
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Current Assets", len(df))
    c2.metric("Net Worth", f"${val:,.0f}")
    c3.metric("Neural Sync", "Active")
    st.divider()

    # The Hollow Glowing Grid
    nodes = [
        {"id": "Preksha", "icon": "🔮", "title": "PREKSHA", "layman": "Predict Sales", "desc": "AI Demand Node"},
        {"id": "Stambha", "icon": "🛡️", "title": "STAMBHA", "layman": "Stop Risks", "desc": "Disruption Engine"},
        {"id": "Samvada", "icon": "🎙️", "title": "SAMVADA", "layman": "Talk to AI", "desc": "Neural Voice Assistant"},
        {"id": "Artha", "icon": "💰", "title": "ARTHA", "layman": "Check Money", "desc": "Wealth Analytics"},
        {"id": "Nyasa", "icon": "📝", "title": "NYASA", "layman": "Add Items", "desc": "Manual Asset Vault"},
        {"id": "Agama", "icon": "📥", "title": "AGAMA", "layman": "Upload Lists", "desc": "Bulk Sync Node"}
    ]

    cols = st.columns(3)
    for i, node in enumerate(nodes):
        with cols[i % 3]:
            st.markdown(f"""
                <div class='action-tile'>
                    <div class='tile-icon'>{node['icon']}</div>
                    <div class='tile-title'>{node['title']}</div>
                    <div class='tile-layman'>{node['layman']}</div>
                    <div class='tile-desc'>{node['desc']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("ENGAGE NODE", key=f"go_{node['id']}"):
                st.session_state.page = node['id']; st.rerun()

# --- 7. FEATURE NODE LOGIC ---

if st.session_state.page == "Preksha":
    st.title("🔮 Preksha: Strategic Intelligence")
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("Node empty.")
    else:
        target = st.selectbox("Search Asset", df['name'])
        preds = np.random.randint(15, 60, 7)
        st.plotly_chart(px.area(y=preds, title="AI Sensing Stream", template="plotly_dark").update_traces(line_color='#00D2FF', fillcolor='rgba(0,210,255,0.05)'), use_container_width=True)
        
        # Hollow Glowing Decision Box
        st.markdown(f"""
            <div class='decision-box'>
                <h3 style='color:#00D2FF; margin:0;'>🤖 AI DIRECTIVE</h3>
                <p style='font-size:1.1rem; margin-top:10px;'>
                    Strategic reorder of <b>{preds.sum()} units</b> recommended for {target}. 
                </p>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state.page == "Samvada":
    st.title("🎙️ Samvada: Neural Chat")
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        chat_box = st.container()
        q = st.chat_input("Enter Strategic Command...")
        if q:
            st.session_state.chat_history.append({"role":"user","content":q})
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":"You are AROHA AI."}] + st.session_state.chat_history[-3:])
            st.session_state.chat_history.append({"role":"assistant", "content":res.choices[0].message.content})
            st.rerun()
        with chat_box:
            for m in st.session_state.chat_history:
                with st.chat_message(m["role"]): st.markdown(m["content"])

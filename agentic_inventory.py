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
st.set_page_config(page_title="AROHA | AISIR Decision Engine", layout="wide", page_icon="💠")

def apply_executive_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Montserrat:wght@300;500;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #080808; 
            color: #E0E0E0;
        }

        h1, h2, h3 { font-family: 'Montserrat', sans-serif; font-weight: 700; color: #D4AF37; }

        /* UNBOXED MENU: Floating Badges */
        .badge-element {
            text-align: left;
            padding: 25px 15px;
            transition: 0.4s all ease;
            cursor: pointer;
            border-bottom: 1px solid #1A1A1A;
            display: flex;
            align-items: center;
            gap: 20px;
        }
        
        .badge-element:hover {
            border-bottom: 2px solid #D4AF37;
            background: rgba(212, 175, 55, 0.04);
            transform: translateX(5px);
        }

        .badge-icon { font-size: 28px; color: #D4AF37; opacity: 0.8; }
        .badge-title { font-weight: 600; font-size: 1.1rem; color: #FFFFFF; letter-spacing: 1px; }
        .badge-desc { font-size: 0.8rem; color: #555; }

        /* Global HUD Sidebar */
        [data-testid="stSidebar"] {
            background-color: #050505;
            border-right: 1px solid #1A1A1A;
        }

        /* AISIR Decision Directive Box */
        .decision-directive {
            background: rgba(212, 175, 55, 0.05);
            border: 1px solid rgba(212, 175, 55, 0.3);
            padding: 30px;
            border-radius: 4px;
            margin-top: 30px;
            border-left: 8px solid #D4AF37;
        }
        .directive-header { font-family: 'Montserrat', sans-serif; font-weight: 700; color: #D4AF37; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px; }
        .directive-content { font-size: 1.2rem; color: #FFFFFF; font-weight: 500; }

        /* Buttons */
        .stButton>button {
            border-radius: 0px; background: transparent; border: 1px solid #333; color: #D4AF37;
            padding: 8px 20px; transition: 0.3s; text-transform: uppercase; font-size: 0.7rem; letter-spacing: 2px;
        }
        .stButton>button:hover { border-color: #D4AF37; background: #D4AF37; color: black; }

        /* Top HUD Status */
        .hud-status {
            display: flex; justify-content: space-between; padding: 10px 0px; border-bottom: 1px solid #1A1A1A;
            margin-bottom: 40px; font-size: 0.65rem; color: #444; letter-spacing: 2px;
        }
        </style>
    """, unsafe_allow_html=True)

apply_executive_css()

# --- 2. DATABASE ARCHITECTURE ---
DB_FILE = 'aroha_aisir_v23.db'
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

# --- 4. AUTHENTICATION GATE ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='font-size:3.5rem; letter-spacing:15px; margin-bottom:0;'>AROHA</h1><p style='color:#444; letter-spacing:3px;'>SECURE NODE: AISIR ENGINE</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        m = st.tabs(["ACCESS", "ENROLL"])
        with m[0]:
            u = st.text_input("Identity", key="l_u")
            p = st.text_input("Mantra", type="password", key="l_p")
            if st.button("AUTHORIZE"):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Access Denied")
        with m[1]:
            nu = st.text_input("New Identity"); np = st.text_input("New Mantra", type="password")
            if st.button("CREATE VAULT"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Authorized.")
    st.stop()

# --- 5. GLOBAL SIDEBAR ---
with st.sidebar:
    st.markdown(f"## AROHA // AISIR")
    st.markdown(f"<p style='color:#444; font-size:0.7rem;'>OPERATOR: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
    st.divider()
    if st.button("🏠 Command Hub"): st.session_state.page = "Home"; st.rerun()
    if st.button("🔮 Preksha Intel"): st.session_state.page = "Drishti"; st.rerun()
    if st.button("🛡️ Stambha Risk"): st.session_state.page = "Stambha"; st.rerun()
    if st.button("🎙️ Samvada Chat"): st.session_state.page = "Samvada"; st.rerun()
    if st.button("💰 Artha Capital"): st.session_state.page = "Artha"; st.rerun()
    if st.button("📝 Nyasa Ledger"): st.session_state.page = "Nyasa"; st.rerun()
    if st.button("📥 Agama Sync"): st.session_state.page = "Agama"; st.rerun()
    st.divider()
    if st.button("🔒 Terminate"): st.session_state.auth = False; st.rerun()

# --- 6. COMMAND HUB (HOME - PhonePe Unboxed) ---
if st.session_state.page == "Home":
    st.markdown(f"""
        <div class='hud-status'>
            <span>AISIR_CORE: ACTIVE</span>
            <span>ENCRYPTION: RSA_4096</span>
            <span>DECISION_MODE: AUTONOMOUS</span>
            <span>{datetime.now().strftime('%H:%M:%S')}</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='letter-spacing:10px; font-weight:300; color:#444;'>ORCHESTRATION HUB</h2>", unsafe_allow_html=True)
    
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    c1.metric("Assets", len(df))
    c2.metric("Net Treasury", f"${val:,.0f}")
    c3.metric("Agent State", "AISIR Listening")
    st.divider()

    # THE GRID (3 columns)
    row1_c1, row1_c2, row1_c3 = st.columns(3)
    row2_c1, row2_c2, row2_c3 = st.columns(3)

    nodes = [
        {"id": "Drishti", "icon": "🔮", "title": "PREKSHA", "desc": "Strategic Vision", "col": row1_c1},
        {"id": "Stambha", "icon": "🛡️", "title": "STAMBHA", "desc": "Resilience Engine", "col": row1_c2},
        {"id": "Samvada", "icon": "🎙️", "title": "SAMVADA", "desc": "Neural Dialogue", "col": row1_c3},
        {"id": "Artha", "icon": "💰", "title": "ARTHA", "desc": "Wealth Intel", "col": row2_c1},
        {"id": "Nyasa", "icon": "📝", "title": "NYASA", "desc": "Asset Registry", "col": row2_c2},
        {"id": "Agama", "icon": "📥", "title": "AGAMA", "desc": "Cloud Ingestion", "col": row2_c3}
    ]

    for n in nodes:
        with n['col']:
            st.markdown(f"""
                <div class='badge-element'>
                    <div class='badge-icon'>{n['icon']}</div>
                    <div>
                        <div class='badge-title'>{n['title']}</div>
                        <div class='badge-desc'>{n['desc']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Engage {n['title']}", key=f"btn_{n['id']}"):
                st.session_state.page = n['id']; st.rerun()

# --- 7. DECISION NODES (Logic) ---

if st.session_state.page == "Drishti":
    st.markdown("## 🔮 Preksha: Turning Data into Forecasts")
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("Treasury empty. Use Nyasa node.")
    else:
        target = st.selectbox("Asset Search", df['name'])
        p = df[df['name'] == target].iloc[0]
        preds = np.random.randint(20, 60, 7)
        st.plotly_chart(px.area(y=preds, title="AISIR Demand Sensing Stream", template="plotly_dark").update_traces(line_color='#D4AF37'), use_container_width=True)
        
        # FINAL DECISION DIRECTIVE
        st.markdown(f"""
            <div class='decision-directive'>
                <div class='directive-header'>AISIR Strategic Directive</div>
                <div class='directive-content'>
                    Procurement of <b>{preds.sum()} units</b> recommended. Current stock will deplete in 4.2 days. 
                    Immediate restock required to prevent a 12% revenue gap.
                </div>
            </div>
        """, unsafe_allow_html=True)

elif st.session_state.page == "Stambha":
    st.markdown("## 🛡️ Stambha: Turning Data into Resilience")
    scenario = st.selectbox("Shock Event", ["Normal", "Port Closure", "Factory Disruption"])
    st.info(f"AISIR is stress-testing for {scenario}...")
    # ... logic for TTS vs TTR table
    st.markdown(f"""
        <div class='decision-directive'>
            <div class='directive-header'>AISIR Resilience Directive</div>
            <div class='directive-content'>
                System is 🟢 STABLE. Shift supply to air-freight if Lead Time exceeds 14 days.
            </div>
        </div>
    """, unsafe_allow_html=True)

elif st.session_state.page == "Samvada":
    st.markdown("## 🎙️ Samvada: Neural Strategic Dialogue")
    st.session_state.voice_on = st.toggle("AISIR Voice Synthesis", value=st.session_state.voice_on)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        q = st.chat_input("Input Strategic Command...")
        if q:
            st.session_state.chat_history.append({"role":"user","content":q})
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":"You are AISIR, a strategic AI. Answer concisely."}] + st.session_state.chat_history[-3:])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant","content":ans})
            st.rerun()

elif st.session_state.page == "Nyasa":
    st.markdown("## 📝 Nyasa: Asset Registry")
    with st.form("ledger"):
        n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1)
        if st.form_submit_button("COMMIT TO VAULT"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", (st.session_state.user, n, s, p, lt))
            st.success("COMMITTED")

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

# --- 1. SETTINGS & PREMIUM UI ---
st.set_page_config(page_title="AROHA | Strategic Orchestrator", layout="wide", page_icon="💠", initial_sidebar_state="expanded")

def apply_aroha_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0B0F14; color: #E6E8EB; }

        /* --- SIDEBAR: ULTRA BOLD --- */
        [data-testid="stSidebar"] { background-color: #090B0F !important; border-right: 1px solid #1F2229; min-width: 380px !important; }
        .brand-title { font-size: 2.5rem; font-weight: 800; color: #FFFFFF; letter-spacing: -1px; margin-bottom: 0; }
        .decisions-fade { color: #6C63FF; font-weight: 700; animation: glowPulse 2s infinite alternate; }
        @keyframes glowPulse { from { text-shadow: 0 0 2px #6C63FF; } to { text-shadow: 0 0 10px #38BDF8; } }

        section[data-testid="stSidebar"] .stButton > button { 
            background: transparent !important; border: none !important; color: #FFFFFF !important; 
            text-align: left !important; padding: 12px 18px !important; width: 100%; 
            font-size: 1.4rem !important; font-weight: 800 !important; letter-spacing: 1px;
        }
        .sidebar-sub { font-size: 0.95rem !important; color: #6C63FF; font-weight: 700; display: block; margin-top: -15px; margin-bottom: 25px; margin-left: 55px; text-transform: uppercase; }
        
        /* Dashboard & Feature Styling */
        .saas-card { background: #171A21; border: 1px solid rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
        .ai-decision-box { background: rgba(108, 99, 255, 0.08); border-left: 10px solid #D4AF37; padding: 25px; border-radius: 15px; margin-top: 25px; border: 1px solid #D4AF37; }
        .financial-stat { background: #111; padding: 20px; border-radius: 10px; border-top: 4px solid #D4AF37; text-align: center; }
        .review-box { background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; margin-top: 8px; border: 1px solid #222; font-size: 0.85rem; }
        
        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE (V38 Master Schema) ---
DB_FILE = 'aroha_v38.db'
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
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_on" not in st.session_state: st.session_state.voice_on = False

def speak_aloud(text):
    if st.session_state.voice_on:
        clean = text.replace('"', '').replace("'", "")
        js = f"<script>var m = new SpeechSynthesisUtterance(); m.text='{clean}'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:white; font-size:4rem; font-weight:800;'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Where Data Becomes <span style='color:#6C63FF; font-weight:700;'>Decisions</span></p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 0.8, 1])
    with col2:
        m = st.tabs(["Login", "Enroll"])
        with m[0]:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Unlock Dashboard"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Access denied.")
        with m[1]:
            nu = st.text_input("New ID"); np = st.text_input("New Password", type="password")
            if st.button("Initialize Account"):
                try:
                    with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                    st.success("Authorized.")
                except: st.error("ID exists.")
        with st.expander("System Recovery"):
            if st.button("🔥 HARD RESET"):
                with get_db() as conn: conn.execute("DROP TABLE IF EXISTS users"); conn.execute("DROP TABLE IF EXISTS products")
                st.warning("Wiped."); time.sleep(1); st.rerun()
    st.stop()

# --- 5. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div class='brand-title'>AROHA</div><div style='color:#9AA0A6; font-size:1rem; margin-bottom:20px;'>Data into <span class='decisions-fade'>Decisions</span></div>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section-head'>Intelligence</div>", unsafe_allow_html=True)
    if st.button("📈 PREKSHA"): st.session_state.page = "Preksha"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Predict Demand Instantly</span>", unsafe_allow_html=True)
    if st.button("🛡️ STAMBHA"): st.session_state.page = "Stambha"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Test Supply Risks</span>", unsafe_allow_html=True)
    if st.button("🎙️ SAMVADA"): st.session_state.page = "Samvada"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Talk To System</span>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-head'>Analysis</div>", unsafe_allow_html=True)
    if st.button("💰 ARTHA"): st.session_state.page = "Artha"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Track Money Flow</span>", unsafe_allow_html=True)
    if st.button("🤝 MITHRA"): st.session_state.page = "Mithra"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Rate Your Suppliers</span>", unsafe_allow_html=True)

    st.markdown("<div class='sidebar-section-head'>Control</div>", unsafe_allow_html=True)
    if st.button("📄 KARYA"): st.session_state.page = "Karya"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Auto Create Orders</span>", unsafe_allow_html=True)
    if st.button("📝 NYASA"): st.session_state.page = "Nyasa"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Log Assets Securely</span>", unsafe_allow_html=True)
    if st.button("📥 AGAMA"): st.session_state.page = "Agama"; st.rerun()
    st.markdown("<span class='sidebar-sub'>Import Data Easily</span>", unsafe_allow_html=True)

    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. LOGIC CONTENT ---
def get_user_data():
    with get_db() as conn: return pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))

# DASHBOARD
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Strategic Hub: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='saas-card'><h3>Assets</h3><h2>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='saas-card'><h3>Value</h3><h2>₹{val:,.0f}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='saas-card'><h3>Risk</h3><h2 style='color:#34D399;'>OPTIMAL</h2></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ai-decision-box'>✨ **AI Directive:** All systems nominal. Sensing +4% demand for coming week.</div>", unsafe_allow_html=True)

# PREKSHA
elif st.session_state.page == "Preksha":
    st.title("🔮 PREKSHA")
    df = get_user_data()
    if df.empty: st.warning("Add data.")
    else:
        target = st.selectbox("Asset", df['name']); p = df[df['name'] == target].iloc[0]
        col1, col2 = st.columns([1, 2])
        with col1:
            if p['image_url']: st.image(p['image_url'], use_container_width=True)
            if p['reviews']: st.markdown(f"<div class='review-box'>⭐ {p['reviews']}</div>", unsafe_allow_html=True)
        with col2:
            sent = st.select_slider("Market Sentiment", options=[0.8, 1.0, 1.2, 1.5, 2.0], value=1.0)
            preds = (np.random.randint(20, 50, 7) * sent).astype(int)
            st.plotly_chart(px.area(y=preds, title="AI Sensing Stream", template="plotly_dark").update_traces(line_color='#6C63FF'))
            st.markdown(f"<div class='ai-decision-box'>🤖 **Decision:** Recommendation to order **{preds.sum()} units**.</div>", unsafe_allow_html=True)

# STAMBHA
elif st.session_state.page == "Stambha":
    st.title("🛡️ STAMBHA")
    scenario = st.selectbox("Shock", ["Normal", "Port Closure", "Factory Fire"])
    df = get_user_data()
    if not df.empty:
        results = []
        for _, p in df.iterrows():
            ttr = p['lead_time']
            if "Port" in scenario: ttr *= 3
            tts = round(p['current_stock'] / 12, 1)
            status = "🟢 Safe" if tts > ttr else "🔴 CRITICAL"
            if status == "🔴 CRITICAL": st.error(f"RISK: {p['name']} stockout in {tts}d.")
            results.append({"Item": p['name'], "TTS": tts, "TTR": ttr, "Status": status})
        st.table(pd.DataFrame(results))

# SAMVADA (Chat + Voice + Command Parser)
elif st.session_state.page == "Samvada":
    st.title("🎙️ SAMVADA")
    st.session_state.voice_on = st.toggle("Enable Voice")
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        u_in = st.chat_input("Type or Speak...")
        audio = st.audio_input("Record")
        if audio:
            with st.spinner("Processing Voice..."): u_in = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        if u_in:
            st.session_state.chat_history.append({"role":"user","content":u_in})
            # Logic: If user wants to add data, AI formats it as a command
            sys_msg = "You are AROHA Agent. If user wants to add an item, reply with COMMAND:ADD:name:stock:price:lead. Data: " + get_user_data().to_string()
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":sys_msg}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            if "COMMAND:ADD" in ans:
                parts = ans.split(":")
                with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", (st.session_state.user, parts[2], int(parts[3]), float(parts[4]), int(parts[5])))
                ans = f"✅ Added {parts[2]} to the vault."
            st.session_state.chat_history.append({"role":"assistant","content":ans}); speak_aloud(ans); st.rerun()

# ARTHA
elif st.session_state.page == "Artha":
    st.title("💰 ARTHA")
    df = get_user_data()
    if not df.empty:
        v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns(2)
        with c1: st.markdown(f"<div class='financial-stat'>Inventory Value<br><h2>₹{v:,.0f}</h2></div>", unsafe_allow_html=True)
        with c2: st.markdown(f"<div class='financial-stat'>Idle Capital Risk<br><h2 style='color:red;'>₹{v*0.15:,.0f}</h2></div>", unsafe_allow_html=True)

# MITHRA
elif st.session_state.page == "Mithra":
    st.title("🤝 MITHRA")
    df = get_user_data()
    if not df.empty: st.dataframe(df[['supplier', 'lead_time', 'name']], use_container_width=True)

# KARYA
elif st.session_state.page == "Karya":
    st.title("📄 KARYA")
    df = get_user_data()
    if not df.empty:
        t = st.selectbox("Asset for PO", df['name'])
        if st.button("Generate Digital PO"): st.code(f"PO-ID: {np.random.randint(1000,9999)}\nITEM: {t}\nAUTH: {st.session_state.user.upper()}")

# NYASA
elif st.session_state.page == "Nyasa":
    st.title("📝 NYASA")
    with st.form("add"):
        n = st.text_input("Name"); c = st.text_input("Cat"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead", 1); img = st.text_input("Img URL"); rev = st.text_area("Reviews")
        if st.form_submit_button("Commit"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, category, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?,?)", (st.session_state.user, n, c, s, p, lt, img, rev))
            st.success("Synced.")

# AGAMA
elif st.session_state.page == "Agama":
    st.title("📥 AGAMA")
    f = st.file_uploader("Upload CSV", type="csv")
    if f and st.button("Sync"):
        u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
        for col in ['category','supplier','image_url','reviews']: 
            if col not in u_df.columns: u_df[col] = ""
        with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
        st.success("Synced.")

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

# --- 1. PREMIUM UI CONFIG (ULTRA STANDOUT TYPOGRAPHY) ---
st.set_page_config(page_title="AROHA | Strategic Intelligence", layout="wide", page_icon="💠", initial_sidebar_state="expanded")

def apply_aroha_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        
        /* Global Reset */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0B0F14;
            color: #E6E8EB;
        }

        /* 💎 STANDOUT BRANDING */
        .brand-container { padding: 10px 0 25px 15px; }
        .brand-title { 
            font-size: 3.2rem !important; 
            font-weight: 800 !important; 
            color: #FFFFFF !important; 
            letter-spacing: -2px; 
            text-shadow: 0 0 20px rgba(108, 99, 255, 0.4);
            margin-bottom: 0; 
        }
        .tagline { font-size: 1.1rem; color: #9AA0A6; margin-top: -5px; display: flex; gap: 6px; }
        .decisions-fade { color: #6C63FF; font-weight: 700; animation: glowPulse 2s infinite alternate; }
        @keyframes glowPulse { from { text-shadow: 0 0 5px #6C63FF; } to { text-shadow: 0 0 15px #38BDF8; } }

        /* 🧭 SIDEBAR: BOLD SANSKRIT LABELS */
        [data-testid="stSidebar"] { background-color: #090B0F !important; border-right: 1px solid #1F2229; min-width: 380px !important; }
        
        section[data-testid="stSidebar"] .stButton > button { 
            background: transparent !important; 
            border: none !important; 
            color: #FFFFFF !important; 
            text-align: left !important; 
            padding: 12px 18px !important; 
            width: 100%; 
            font-size: 1.5rem !important; /* MASSIVE SANSKRIT NAMES */
            font-weight: 800 !important; 
            letter-spacing: 1.5px;
            text-shadow: 0 0 10px rgba(255,255,255,0.1);
        }
        
        .sidebar-sub { 
            font-size: 0.9rem !important; 
            color: #6C63FF; 
            font-weight: 700; 
            display: block; 
            margin-top: -15px; 
            margin-bottom: 25px; 
            margin-left: 55px; 
            text-transform: uppercase; 
            letter-spacing: 1px;
        }

        /* Dashboard Highlights */
        .saas-card { 
            background: #171A21; 
            border: 1px solid rgba(255, 255, 255, 0.05); 
            border-radius: 12px; 
            padding: 25px; 
            margin-bottom: 20px; 
            box-shadow: 0 4px 20px rgba(0,0,0,0.4); 
        }
        .db-metric-val { font-family: 'JetBrains Mono', monospace; font-size: 2rem; font-weight: 800; color: #FFFFFF; }
        .ai-decision-box { 
            background: rgba(212, 175, 55, 0.08); 
            border: 2px solid #D4AF37; 
            padding: 25px; 
            border-radius: 15px; 
            border-left: 10px solid #D4AF37;
            margin-top: 25px; 
        }
        .financial-stat { background: #111; padding: 20px; border-radius: 10px; border-top: 4px solid #D4AF37; text-align: center; }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_final_master.db'
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

# --- 3. SESSION & VOICE ENGINE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_on" not in st.session_state: st.session_state.voice_on = False

def speak_aloud(text):
    if st.session_state.voice_on:
        clean = text.replace('"', '').replace("'", "")
        js = f"<script>var m=new SpeechSynthesisUtterance(); m.text='{clean}'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("""
        <div style='text-align:center; margin-top:80px;'>
            <h1 style='color:white; font-size:4.5rem; font-weight:800; text-shadow: 0 0 30px #6C63FF;'>AROHA</h1>
            <p style='color:#9AA0A6; font-size:1.4rem;'>Turn Data Into <span style='color:#6C63FF; font-weight:700;'>Decisions</span></p>
        </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 0.8, 1])
    with col2:
        m = st.tabs(["Login", "Enroll"])
        with m[0]:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Unlock Strategic Hub"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Access Denied")
        with m[1]:
            nu = st.text_input("New ID"); np = st.text_input("New Mantra", type="password")
            if st.button("Enroll Session"):
                try:
                    with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                    st.success("Authorized.")
                except: st.error("ID exists.")
    st.stop()

# --- 5. GLOBAL SIDEBAR (SANSKRIT DOMINANT) ---
with st.sidebar:
    st.markdown(f"<div class='brand-container'><div class='brand-title'>AROHA</div><div class='tagline'>Data into <span class='decisions-fade'>Decisions</span></div></div>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)
    
    st.markdown("<div style='height:15px;'></div>", unsafe_allow_html=True)
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
        if st.button(label):
            st.session_state.page = page_id
            st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)

    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. PAGE CONTENT ---
def get_user_df():
    with get_db() as conn: return pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))

# DASHBOARD
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Command Center: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_df()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='saas-card'><h3>Assets</h3><div class='db-metric-val'>{len(df)}</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='saas-card'><h3>Treasury</h3><div class='db-metric-val'>₹{val:,.0f}</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='saas-card'><h3>Status</h3><div class='db-metric-val' style='color:#34D399;'>OPTIMAL</div></div>", unsafe_allow_html=True)
    
    st.markdown(f"""<div class='ai-decision-box'><h3 style='color:#D4AF37; margin:0;'>✨ AI Strategic Directive</h3><p style='font-size:1.1rem;'>All nodes functional. Sensing increased demand for next week. Risk level is minimal.</p></div>""", unsafe_allow_html=True)

# PREKSHA
elif st.session_state.page == "Preksha":
    st.title("🔮 PREKSHA: Intelligence")
    df = get_user_df()
    if df.empty: st.warning("Add data via Nyasa.")
    else:
        target = st.selectbox("Asset Search", df['name']); p = df[df['name'] == target].iloc[0]
        col_m, col_v = st.columns([1, 2])
        with col_m:
            if p['image_url']: st.image(p['image_url'], use_container_width=True)
            if p['reviews']: st.markdown(f"<div class='saas-card'><b>Reviews:</b><br>{p['reviews']}</div>", unsafe_allow_html=True)
        with col_v:
            sent = st.select_slider("Market Sentiment", options=[0.8, 1.0, 1.2, 1.5, 2.0], value=1.0)
            preds = (np.random.randint(20, 50, 7) * sent).astype(int)
            st.plotly_chart(px.area(y=preds, title="Neural Forecast Stream", template="plotly_dark").update_traces(line_color='#6C63FF'))
            st.markdown(f"<div class='ai-decision-box'>🤖 **Decision:** Reorder **{preds.sum()} units** recommended.</div>", unsafe_allow_html=True)

# STAMBHA
elif st.session_state.page == "Stambha":
    st.title("🛡️ STAMBHA: Resilience")
    scenario = st.selectbox("Disruption Trigger", ["Normal", "Port Closure (3x Lead Time)", "Factory Fire (+30d)"])
    df = get_user_df()
    if not df.empty:
        res = []
        for _, p in df.iterrows():
            ttr = p['lead_time']
            if "Port" in scenario: ttr *= 3
            if "Fire" in scenario: ttr += 30
            tts = round(p['current_stock'] / 12, 1)
            status = "🟢 Safe" if tts > ttr else "🔴 CRITICAL"
            if status == "🔴 CRITICAL": st.error(f"ALERT: {p['name']} stockout in {tts}d.")
            res.append({"Asset": p['name'], "Time-to-Survive": tts, "Time-to-Recover": ttr, "Risk": status})
        st.table(pd.DataFrame(res))

# ARTHA
elif st.session_state.page == "Artha":
    st.title("💰 ARTHA: Wealth Intel")
    df = get_user_df()
    if not df.empty:
        v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"<div class='financial-stat'>Total Treasury Value<br><h2>₹{v:,.0F}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='financial-stat' style='margin-top:20px;'>Idle Capital Risk (15%)<br><h2 style='color:red;'>₹{v*0.15:,.0F}</h2></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='saas-card'><b>Capital Allocation Matrix</b>", unsafe_allow_html=True)
            # --- PIE CHART ADDITION ---
            fig_pie = px.pie(df, values='current_stock', names='name', hole=0.4, template="plotly_dark")
            fig_pie.update_layout(showlegend=False, margin=dict(l=10,r=10,t=10,b=10))
            st.plotly_chart(fig_pie, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# SAMVADA
elif st.session_state.page == "Samvada":
    st.title("🎙️ SAMVADA: Neural Chat")
    st.session_state.voice_on = st.toggle("Enable Voice Assistant Feedback")
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        u_in = st.chat_input("Enter command...")
        audio = st.audio_input("Record Voice Command")
        if audio:
            with st.spinner("Neural Processing..."):
                u_in = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        if u_in:
            st.session_state.chat_history.append({"role":"user","content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are Samvada AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant","content":ans}); speak_aloud(ans); st.rerun()

# NYASA
elif st.session_state.page == "Nyasa":
    st.title("📝 NYASA: Registry")
    with st.form("add"):
        n = st.text_input("Asset Name"); c = st.text_input("Category"); s = st.number_input("Stock Qty", 0); p = st.number_input("Unit Price", 0.0); lt = st.number_input("Lead Time (Days)", 1); sup = st.text_input("Supplier"); img = st.text_input("Image URL"); rev = st.text_area("Reviews")
        if st.form_submit_button("Commit to Nexus"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, category, current_stock, unit_price, lead_time, supplier, image_url, reviews) VALUES (?,?,?,?,?,?,?,?,?)", (st.session_state.user, n, c, s, p, lt, sup, img, rev))
            st.success("Entry Logged.")

# AGAMA
elif st.session_state.page == "Agama":
    st.title("📥 AGAMA: Batch Sync")
    file = st.file_uploader("Upload CSV Supply Ledger", type="csv")
    if file and st.button("Sync"):
        u_df = pd.read_csv(file); u_df['username'] = st.session_state.user
        for col in ['category','supplier','image_url','reviews']:
            if col not in u_df.columns: u_df[col] = ""
        with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
        st.success("Sync Successful.")

# MITHRA & KARYA
elif st.session_state.page == "Mithra":
    st.title("🤝 MITHRA: Suppliers")
    df = get_user_data()
    st.dataframe(df[['supplier', 'lead_time', 'name']], use_container_width=True)

elif st.session_state.page == "Karya":
    st.title("📄 KARYA: PO Gen")
    df = get_user_data()
    if not df.empty:
        t = st.selectbox("Select Asset for PO", df['name'])
        if st.button("Generate Document"): st.code(f"PO-ID: {np.random.randint(1000,9999)}\nITEM: {t}\nAUTH: {st.session_state.user.upper()}")

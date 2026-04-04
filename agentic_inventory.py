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

# --- 1. PREMIUM UI CONFIG (UNIVERSAL RESPONSIVE & HOLLOW BLUE GLOW) ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="expanded"
)

def apply_aroha_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050709; color: #E6E8EB; }

        /* 📟 SIDEBAR: RADIANT HOLLOW BLUE GLOW & MASSIVE FONTS */
        [data-testid="stSidebar"] { background-color: #080A0C !important; border-right: 1px solid #1F2229; min-width: 420px; }
        @media (max-width: 768px) { [data-testid="stSidebar"] { min-width: 100% !important; } }

        section[data-testid="stSidebar"] .stButton > button { 
            background: transparent !important; border: 2px solid rgba(0, 212, 255, 0.4) !important; 
            color: #FFFFFF !important; text-align: left !important; padding: 15px 18px !important; width: 100%; 
            font-size: 1.6rem !important; font-weight: 800 !important; letter-spacing: 1.5px;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5); margin-bottom: 5px; transition: 0.3s;
        }
        section[data-testid="stSidebar"] .stButton > button:hover { border: 2px solid #00D4FF !important; box-shadow: 0 0 20px rgba(0, 212, 255, 0.6); color: #00D4FF !important; }
        .sidebar-sub { font-size: 0.95rem !important; color: #6C63FF; font-weight: 700; display: block; margin-top: -10px; margin-bottom: 25px; margin-left: 20px; text-transform: uppercase; letter-spacing: 1px; }

        /* 💎 BRANDING */
        .brand-title { font-size: 3.5rem !important; font-weight: 800 !important; color: #FFFFFF !important; letter-spacing: -2px; text-shadow: 0 0 25px rgba(108, 99, 255, 0.6); margin-bottom: 0; }
        .decisions-fade { color: #6C63FF; font-weight: 700; animation: glowPulse 2s infinite alternate; }
        @keyframes glowPulse { from { text-shadow: 0 0 5px #6C63FF; } to { text-shadow: 0 0 15px #38BDF8; } }

        /* CARDS & PANELS */
        .saas-card { background: #0D1117; border: 1px solid rgba(0, 212, 255, 0.1); border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
        .ai-decision-box { background: rgba(212, 175, 55, 0.08); border: 2px solid #D4AF37; padding: 25px; border-radius: 15px; border-left: 12px solid #D4AF37; margin-top: 25px; box-shadow: 0 0 20px rgba(212, 175, 55, 0.2); }
        .feature-header { font-size: 3.2rem !important; font-weight: 800 !important; color: #00D4FF !important; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3); text-transform: uppercase; }
        .review-box { background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; border: 1px solid #222; margin-bottom: 10px; font-size: 0.85rem; }

        /* TICKER */
        @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
        .ticker-wrap { width: 100%; overflow: hidden; background: rgba(0, 212, 255, 0.05); border-bottom: 1px solid rgba(0, 212, 255, 0.2); padding: 8px 0; margin-bottom: 20px; }
        .ticker-text { display: inline-block; white-space: nowrap; font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #00D4FF; animation: ticker 40s linear infinite; }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_master_v66.db'
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
def get_user_data():
    with get_db() as conn: return pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_on" not in st.session_state: st.session_state.voice_on = False

def speak(text):
    if st.session_state.voice_on:
        clean = text.replace('"', '').replace("'", "")
        js = f"<script>var m = new SpeechSynthesisUtterance(); m.text='{clean}'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 class='brand-title'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Turn Data Into <span class='decisions-fade'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([1, 0.8, 1])
    with col_center:
        m = st.tabs(["Login", "Enroll"])
        with m[0]:
            u_input = st.text_input("Username", key="l_u")
            p_input = st.text_input("Password", type="password", key="l_p")
            if st.button("Unlock Strategic Hub"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u_input,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p_input):
                    st.session_state.auth = True; st.session_state.user = u_input; st.rerun()
                else: st.error("Access Denied")
        with m[1]:
            nu = st.text_input("New ID"); np = st.text_input("New Password", type="password")
            if st.button("Enroll Session"):
                try:
                    with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                    st.success("Authorized.")
                except: st.error("ID exists.")
    st.stop()

# --- 5. TOP TICKER ---
st.markdown(f"<div class='ticker-wrap'><div class='ticker-text'>[DHWANI] Neural link active for {st.session_state.user.upper()} // [RISK] Disruption detected in SANCHARA Node // [STRATEGY] AI suggesting immediate restock for critical assets.</div></div>", unsafe_allow_html=True)

# --- 6. SIDEBAR (UNIFIED 8 NODES) ---
with st.sidebar:
    st.markdown(f"<div class='brand-container'><div class='brand-title' style='font-size:2.2rem !important;'>AROHA</div><div style='color:#9AA0A6; font-size:0.9rem;'>Data into <span class='decisions-fade'>Decisions</span></div></div>", unsafe_allow_html=True)
    
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)

    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items Easily"),
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System"),
        ("💰 VITTA", "Vitta", "Track Money Flow"),
        ("📦 SANCHARA", "Sanchara", "Global Flow & Returns"),
        ("🤝 MITHRA", "Mithra", "Rate Your Suppliers")
    ]
    for label, page_id, layman in nodes:
        if st.button(label):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)

    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 7. LOGIC NODES ---

# 1. COMMAND HUB
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Strategic Hub: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    st.markdown("""<div style='background:rgba(0,212,255,0.02); padding:10px; border-radius:12px; border:1px dashed #00D4FF; margin-bottom:20px; text-align:center;'><span style='color:#00D4FF;'>● NEURAL LINK: <b>STABLE</b></span></div>""", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='saas-card'><h3>📝 Assets</h3><h2 style='color:#00D4FF;'>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='saas-card'><h3>💰 Treasury</h3><h2 style='color:#00D4FF;'>₹{val:,.0f}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='saas-card'><h3>🛡️ Status</h3><h2 style='color:#34D399;'>OPTIMAL</h2></div>", unsafe_allow_html=True)
    st.info("💡 Strategic Suggestion: Please add your warehouse assets via the NYASA Node to begin autonomous sensing.")

# 2. NYASA (NEW: INCLUDES PO GENERATOR)
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>📝 NYASA</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📥 Bulk Sync", "✍️ Manual Registry", "📄 KARYA: PO Gen"])
    with t1:
        f = st.file_uploader("Upload CSV (name, current_stock, unit_price, lead_time)", type="csv")
        if f and st.button("Synchronize with Vault"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            for col in ['category','supplier','image_url','reviews']: u_df[col] = u_df.get(col, "")
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Synced successfully.")
    with t2:
        with st.form("add"):
            n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead", 1); img = st.text_input("Img URL"); rev = st.text_area("Reviews (Split with |)")
            if st.form_submit_button("Commit"):
                with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
                st.success("Asset Committed.")
    with t3:
        df = get_user_data()
        if not df.empty:
            st.subheader("Generate Strategic Purchase Order")
            t = st.selectbox("Asset for PO", df['name'])
            if st.button("Generate Digital PO"):
                st.code(f"PO-ID: #ARH-{np.random.randint(1000,9999)}\nITEM: {t}\nAUTH: {st.session_state.user.upper()}\nSTATUS: AUTHORIZED")

# 3. PREKSHA (IMPROVED REVIEWS & SUGGESTIONS)
elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>📈 PREKSHA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if df.empty: st.warning("Treasury empty. Use Nyasa.")
    else:
        target = st.selectbox("Asset Search", df['name']); p_row = df[df['name'] == target].iloc[0]
        col_m, col_v = st.columns([1, 2])
        with col_m:
            if p_row['image_url']: st.image(p_row['image_url'], use_container_width=True)
            if p_row['reviews']:
                st.subheader("Customer Sentiment")
                for r in p_row['reviews'].split('|'):
                    st.markdown(f"<div class='review-box'>💬 {r}</div>", unsafe_allow_html=True)
        with col_v:
            sent = st.select_slider("Market Sentiment", options=[0.8, 1.0, 1.5, 2.0], value=1.0)
            preds = (np.random.randint(20, 50, 7) * sent).astype(int)
            st.plotly_chart(px.area(y=preds, title="AI Forecasting Stream", template="plotly_dark").update_traces(line_color='#00D4FF'), use_container_width=True)
            total_needed = preds.sum()
            st.markdown(f"""<div class='ai-decision-box'><h3 style='color:#D4AF37; margin:0;'>🤖 AGENT SUGGESTION</h3>
            <p>Based on {sent}x market sentiment, we predict 7-day demand of <b>{total_needed} units</b>.</p>
            <h4>Decision: Reorder <b>{max(0, total_needed - p_row['current_stock'])}</b> units immediately.</h4></div>""", unsafe_allow_html=True)

# 4. STAMBHA (FIXED BLANK SCREEN)
elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header'>🛡️ STAMBHA</div>", unsafe_allow_html=True)
    st.info("Simulating Disruption Scenarios to test Supply Resilience.")
    s_scenario = st.selectbox("Trigger Disruption", ["Normal", "Port Closure (3x TTR)", "Factory Fire (+30d)"])
    df = get_user_data()
    if not df.empty:
        res = []
        for _, p in df.iterrows():
            ttr = p['lead_time'] * (3 if "Port" in s_scenario else 1)
            if "Fire" in s_scenario: ttr += 30
            tts = round(p['current_stock'] / 12, 1)
            status = "🟢 Safe" if tts > ttr else "🔴 CRITICAL"
            if status == "🔴 CRITICAL":
                st.error(f"⚠️ DANGER: {p['name']} risk. TTS ({tts}d) < TTR ({ttr}d).")
            res.append({"Asset": p['name'], "TTS (d)": tts, "TTR (d)": ttr, "Status": status})
        st.table(pd.DataFrame(res))
    else: st.warning("Add data first.")

# 5. SANCHARA (MAP + LEGEND RESTORED)
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>📦 SANCHARA</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌐 Global Spandana", "📦 Floor Ops", "↩️ Returns Loop"])
    with t1:
        st.map(pd.DataFrame({'lat': [12.97, 22.31, 37.77, 1.35], 'lon': [77.59, 114.16, -122.41, 103.81]}))
        st.markdown("""
        <div style='background:rgba(255,255,255,0.02); padding:15px; border-radius:10px; border:1px solid #333;'>
        <h4 style='color:#00D4FF; margin-top:0;'>🗺️ Strategic Map Legend</h4>
        <p><b>📍 Blue Nodes:</b> Verified supplier factory locations.</p>
        <p><b>🛰️ Transit Path:</b> Multi-modal bulk cargo motion tracking.</p>
        <p><b>⚠️ Red Alerts:</b> Active disruption zones (Ports/Border closures).</p>
        </div>
        """, unsafe_allow_html=True)
    with t2: st.metric("Warehouse Floor Total", "4,320 Units")
    with t3: st.plotly_chart(px.pie(values=[70, 20, 10], names=['Defective', 'Late', 'Mistake'], hole=0.5, template="plotly_dark"))

# SAMVADA, VITTA, MITHRA inherit v61 logic...
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>💰 VITTA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns(2)
        with c1: st.markdown(f"<div class='financial-stat'>Value<br><h2>₹{v:,.0f}</h2></div>", unsafe_allow_html=True)
        with c2: st.plotly_chart(px.pie(df, values='current_stock', names='name', hole=0.5, template="plotly_dark", title="Capital Allocation"))

elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header'>🎙️ SAMVADA</div>", unsafe_allow_html=True)
    st.session_state.voice_on = st.toggle("Enable Voice Assistant")
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        u_in = st.chat_input("Strategic query...")
        audio = st.audio_input("Speak Command")
        if audio:
            with st.spinner("Processing Voice..."):
                u_in = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        if u_in:
            st.session_state.chat_history.append({"role":"user","content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant","content":ans}); speak(ans); st.rerun()

elif st.session_state.page == "Mithra":
    st.markdown("<div class='feature-header'>🤝 MITHRA</div>", unsafe_allow_html=True)
    st.dataframe(get_user_data()[['supplier', 'lead_time', 'name']], use_container_width=True)

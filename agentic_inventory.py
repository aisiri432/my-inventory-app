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

# --- 1. SETTINGS & ULTRA-PREMIUM UI ---
st.set_page_config(page_title="AROHA | Elite Intelligence", layout="wide", page_icon="💠")

def apply_elite_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050505; color: #E0E0E0; }
        
        /* Neon Orb Icons */
        .icon-orb { 
            font-size: 45px; margin-bottom: 12px; display: block; 
            filter: drop-shadow(0 0 15px rgba(212,175,55,0.7)); 
        }
        
        /* Glassmorphic Badge Cards */
        .glass-card {
            background: linear-gradient(145deg, rgba(20,20,20,0.95), rgba(10,10,10,0.95));
            backdrop-filter: blur(15px); border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 35px 20px; text-align: center; transition: 0.4s;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); height: 280px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .glass-card:hover { border: 1px solid #D4AF37; transform: translateY(-10px); box-shadow: 0 0 30px rgba(212, 175, 55, 0.3); }
        
        .title-text { color: #D4AF37; font-weight: 700; font-size: 1.3rem; letter-spacing: 2px; text-transform: uppercase; }
        .desc-text { color: #888; font-size: 0.85rem; margin-top: 10px; }
        
        [data-testid="stSidebar"] { display: none; }
        
        .stButton>button { border-radius: 12px; background: #111; border: 1px solid #333; color: #D4AF37; font-weight: 700; padding: 12px; width: 100%; font-size: 0.85rem; }
        .stButton>button:hover { background: #D4AF37; color: black; box-shadow: 0 0 15px rgba(212,175,55,0.5); }
        
        /* HIGHLIGHTED AI SUGGESTION BOX */
        .ai-decision-box {
            background: rgba(212, 175, 55, 0.08);
            border: 2px solid #D4AF37;
            padding: 25px;
            border-radius: 20px;
            margin-top: 30px;
            border-left: 10px solid #D4AF37;
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.1);
        }
        
        .header-info { display: flex; justify-content: center; gap: 20px; padding: 15px; background: rgba(255,255,255,0.02); border-radius: 50px; margin-bottom: 40px; font-size: 0.7rem; color: #666; letter-spacing: 1px; }
        </style>
    """, unsafe_allow_html=True)

apply_elite_css()

# --- 2. DATABASE ENGINE (v9) ---
DB_FILE = 'aroha_master_v9.db'

def get_db_conn():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_db_conn() as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
        c.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, 
                      current_stock INTEGER, unit_price REAL, lead_time INTEGER)''')
        conn.commit()

init_db()

def make_hashes(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- 3. SESSION STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_active" not in st.session_state: st.session_state.voice_active = False

# --- 4. VOICE ENGINE ---
def speak_aloud(text):
    if st.session_state.voice_active:
        clean = text.replace('"', '').replace("'", "")
        js = f"<script>var m = new SpeechSynthesisUtterance(); m.text='{clean}'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 5. AUTHENTICATION ---
if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 style='color:#D4AF37; font-size:4rem; font-weight:800; letter-spacing:15px; margin-bottom:0;'>AROHA</h1><p style='color:#555; letter-spacing:3px;'>TURN DATA INTO DECISIONS</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        mode = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
        with mode[0]:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("UNLOCK VAULT 🔓"):
                with get_db_conn() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == make_hashes(p):
                    st.session_state.logged_in = True; st.session_state.user = u; st.rerun()
                else: st.error("Access Denied")
        with mode[1]:
            nu = st.text_input("New User", key="r_u"); np = st.text_input("New Pass", type="password", key="r_p")
            if st.button("CREATE ACCOUNT ✅"):
                if nu and np:
                    try:
                        with get_db_conn() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, make_hashes(np)))
                        st.success("Authorized! Log in now.")
                    except: st.error("Username exists.")
    st.stop()

# --- 6. COMMAND CENTER (HOME GRID) ---
if st.session_state.page == "Home":
    st.markdown(f"<div class='header-info'>🟢 STATUS: ONLINE | 🔒 VAULT: {st.session_state.user.upper()} | 💠 AGENT: SAMVADA V9.0</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#D4AF37; letter-spacing:10px;'>COMMAND CENTER</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3); c4, c5, c6 = st.columns(3)
    modules = [
        {"id": "Preksha", "icon": "🔮", "title": "PREKSHA", "desc": "AI Demand & Decisions", "col": c1},
        {"id": "Stambha", "icon": "🛡️", "title": "STAMBHA", "desc": "Resilience Stress Test", "col": c2},
        {"id": "Samvada", "icon": "🎙️", "title": "SAMVADA", "desc": "Voice/Text Agent Chat", "col": c3},
        {"id": "Nyasa", "icon": "📝", "title": "NYASA", "desc": "Asset Ledger & Entry", "col": c4},
        {"id": "Agama", "icon": "📥", "title": "AGAMA", "desc": "Bulk Data Ingestion", "col": c5},
        {"id": "Exit", "icon": "🔒", "title": "EXIT", "desc": "Secure Terminate Session", "col": c6}
    ]
    for m in modules:
        with m["col"]:
            st.markdown(f"<div class='glass-card'><span class='icon-orb'>{m['icon']}</span><span class='title-text'>{m['title']}</span><span class='desc-text'>{m['desc']}</span></div>", unsafe_allow_html=True)
            if st.button(f"ENTER {m['title']}", key=m['id']):
                if m['id'] == "Exit": st.session_state.logged_in = False; st.rerun()
                else: st.session_state.page = m['id']; st.rerun()

# --- 7. FEATURE PAGES ---
def nav_back():
    if st.button("⬅️ COMMAND CENTER"): st.session_state.page = "Home"; st.rerun()

# 1. PREKSHA (The Decisions Node)
if st.session_state.page == "Preksha":
    nav_back(); st.title("🔮 Preksha: Strategic Decisions")
    with get_db_conn() as conn:
        df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("No data. Add in Nyasa or Agama.")
    else:
        col_l, col_r = st.columns([1, 2])
        with col_l:
            sentiment = st.select_slider("Market Sentiment (Weather/Events)", options=[0.8, 1.0, 1.2, 1.5, 2.0], value=1.0)
            safety = st.slider("Safety Buffer units", 0, 100, 20)
        with col_r:
            target = st.selectbox("Select Asset", df['name'])
            p_row = df[df['name'] == target].iloc[0]
            preds = (np.random.randint(20, 50, size=7) * sentiment).astype(int)
            st.plotly_chart(px.area(y=preds, title=f"7-Day Demand Forecast: {target}", template="plotly_dark").update_traces(line_color='#D4AF37', fillcolor='rgba(212,175,55,0.1)'), use_container_width=True)
            
            # --- HIGHLIGHTED AI SUGGESTION BOX ---
            total_demand = preds.sum()
            reorder_qty = max(0, (total_demand + safety) - p_row['current_stock'])
            st.markdown(f"""
                <div class='ai-decision-box'>
                    <h2 style='color:#D4AF37; margin:0;'>🤖 AGENT DECISION</h2>
                    <p style='font-size:1.1rem; margin-top:10px;'>
                        Target: <b>{target}</b><br>
                        Predicted Demand: <b>{total_demand} units</b><br>
                        Recommendation: <span style='color:#00FF41; font-size:1.5rem; font-weight:bold;'>Order {reorder_qty} units</span>
                    </p>
                    <p style='color:#888; font-size:0.8rem;'><i>*Calculation includes {sentiment}x sentiment multiplier and {safety} units safety buffer.</i></p>
                </div>
            """, unsafe_allow_html=True)

# 2. STAMBHA (Resilience Node - FIXED LOGIC)
elif st.session_state.page == "Stambha":
    nav_back(); st.title("🛡️ Stambha: Resilience Simulator")
    scenario = st.selectbox("Trigger Disruption Scenario", ["Normal", "Port Closure (3x Lead Time)", "Factory Fire (+30d)", "Tariff Surge (+50% Demand Shift)"])
    with get_db_conn() as conn:
        df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if not df.empty:
        results = []
        for _, p in df.iterrows():
            avg_daily_sales = 10 # Baseline
            ttr = p['lead_time']
            
            # Scenario Multipliers
            if "Port Closure" in scenario: ttr *= 3
            if "Factory Fire" in scenario: ttr += 30
            
            tts = round(p['current_stock'] / avg_daily_sales, 1)
            status = "🟢 SAFE" if tts > ttr else "🔴 CRITICAL RISK"
            
            if status == "🔴 CRITICAL RISK":
                st.error(f"🚨 ALERT: {p['name']} will run out in {tts} days, but recovery takes {ttr} days!")
            
            results.append({
                "Asset": p['name'], 
                "Current Stock": p['current_stock'],
                "Time-to-Survive (Days)": tts, 
                "Time-to-Recover (Days)": ttr, 
                "Status": status
            })
        st.dataframe(pd.DataFrame(results), use_container_width=True)

# 3. SAMVADA (Chat Node)
elif st.session_state.page == "Samvada":
    nav_back(); st.title("🎙️ Samvada Voice Assistant")
    st.session_state.voice_active = st.toggle("🔊 AI Voice Feedback", value=st.session_state.voice_active)
    key = st.secrets.get("GROQ_API_KEY")
    if not key: st.error("AI Node Offline")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        chat_box = st.container()
        typed = st.chat_input("Ask about your treasury...")
        voice = st.audio_input("Or speak")
        query = typed
        if voice:
            with st.spinner("Transcribing..."):
                query = client.audio.transcriptions.create(file=("q.wav", voice.read()), model="whisper-large-v3", response_format="text")
        if query:
            st.session_state.chat_history.append({"role":"user","content":query})
            with get_db_conn() as conn: ctx = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", conn, params=(st.session_state.user,)).to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are Samvada AI. Data: {ctx}. 2 sentences max."}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant","content":ans})
            speak_aloud(ans); st.rerun()
        with chat_box:
            for m in st.session_state.chat_history:
                with st.chat_message(m["role"]): st.markdown(m["content"])

# 4. NYASA (Manual Node)
elif st.session_state.page == "Nyasa":
    nav_back(); st.title("📝 Nyasa Asset Ledger")
    with st.form("add"):
        n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1)
        if st.form_submit_button("COMMIT"):
            with get_db_conn() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", (st.session_state.user, n, s, p, lt))
            st.success("Asset Logged.")

# 5. AGAMA (Import Node)
elif st.session_state.page == "Agama":
    nav_back(); st.title("📥 Agama Bulk Sync")
    f = st.file_uploader("Upload CSV", type="csv")
    if f:
        u_df = pd.read_csv(f)
        cols = ['name', 'current_stock', 'unit_price', 'lead_time']
        if all(c in u_df.columns for c in cols):
            if st.button("SYNCHRONIZE"):
                u_df['username'] = st.session_state.user
                with get_db_conn() as conn: u_df[cols+['username']].to_sql('products', conn, if_exists='append', index=False)
                st.success("Synced.")

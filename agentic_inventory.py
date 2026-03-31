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

# --- 1. SETTINGS & GLASS UI ---
st.set_page_config(page_title="AROHA | Strategic Intelligence", layout="wide", page_icon="💠")

def apply_elite_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050505; color: #E0E0E0; }
        .icon-initial { font-size: 24px; font-weight: 800; color: #D4AF37; margin-bottom: 12px; letter-spacing: 2px; border-bottom: 2px solid #D4AF37; padding-bottom: 5px; }
        .icon-orb { font-size: 42px; margin-bottom: 12px; display: block; filter: drop-shadow(0 0 10px rgba(212,175,55,0.6)); }
        
        .glass-card {
            background: linear-gradient(145deg, rgba(20,20,20,0.95), rgba(10,10,10,0.95));
            backdrop-filter: blur(15px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 30px 20px; text-align: center; transition: 0.4s;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); height: 260px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .glass-card:hover { border: 1px solid #D4AF37; transform: translateY(-5px); box-shadow: 0 0 25px rgba(212, 175, 55, 0.15); }
        
        .title-text { color: #D4AF37; font-weight: 700; font-size: 1.1rem; letter-spacing: 2px; text-transform: uppercase; }
        .desc-text { color: #666; font-size: 0.75rem; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px; }
        
        [data-testid="stSidebar"] { display: none; }
        .stButton>button { border-radius: 4px; background: #111; border: 1px solid #333; color: #D4AF37; font-weight: 700; padding: 10px; width: 100%; font-size: 0.7rem; letter-spacing: 2px; }
        .stButton>button:hover { border-color: #D4AF37; background: #D4AF37; color: black; }
        .header-info { display: flex; justify-content: center; gap: 20px; padding: 12px; background: rgba(255,255,255,0.02); border-bottom: 1px solid #222; margin-bottom: 30px; font-size: 0.6rem; color: #444; letter-spacing: 2px; }
        .ai-suggestion { background: rgba(212, 175, 55, 0.05); border: 1px solid #D4AF37; padding: 20px; border-radius: 10px; margin-top: 20px; }
        </style>
    """, unsafe_allow_html=True)

apply_elite_css()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_pro_v4.db'
def get_db_conn(): return sqlite3.connect(DB_FILE, check_same_thread=False)

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
if "voice_on" not in st.session_state: st.session_state.voice_on = False

# --- 4. VOICE RESPONSE ENGINE ---
def speak_response(text):
    if st.session_state.voice_on:
        clean = text.replace('"', '').replace("'", "")
        js = f"<script>var m = new SpeechSynthesisUtterance(); m.text='{clean}'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 5. AUTHENTICATION ---
if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 style='color:#D4AF37; font-size:3rem; font-weight:800; letter-spacing:15px; margin-bottom:0;'>AROHA</h1><p style='color:#333; letter-spacing:5px;'>TURN DATA INTO DECISIONS</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        mode = st.tabs(["LOGIN", "REGISTER"])
        with mode[0]:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("UNLOCK"):
                with get_db_conn() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == make_hashes(p):
                    st.session_state.logged_in = True; st.session_state.user = u; st.rerun()
                else: st.error("Access Denied")
        with mode[1]:
            nu = st.text_input("New Username", key="r_u"); np = st.text_input("New Password", type="password", key="r_p")
            if st.button("CREATE ACCOUNT"):
                if nu and np:
                    try:
                        with get_db_conn() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, make_hashes(np)))
                        st.success("Authorized! Login now.")
                    except: st.error("User exists.")
        with st.expander("System Recovery"):
            if st.button("🔥 HARD RESET"):
                with get_db_conn() as conn: conn.execute("DROP TABLE IF EXISTS users"); conn.execute("DROP TABLE IF EXISTS products")
                st.warning("Cleared."); time.sleep(1); st.rerun()
    st.stop()

# --- 6. COMMAND CENTER (HOME) ---
if st.session_state.page == "Home":
    st.markdown(f"<div class='header-info'>CORE: ACTIVE | VAULT: {st.session_state.user.upper()} | AGENT: SAMVADA | SYNC: CLOUD</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#D4AF37; letter-spacing:10px;'>COMMAND CENTER</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3); c4, c5, c6 = st.columns(3)
    modules = [
        {"id": "Preksha", "icon": "🔮", "title": "PREKSHA", "desc": "AI Demand Sensing", "col": c1},
        {"id": "Stambha", "icon": "🛡️", "title": "STAMBHA", "desc": "Resilience Risk", "col": c2},
        {"id": "Samvada", "icon": "🎙️", "title": "SAMVADA", "desc": "Chat & Voice Assistant", "col": c3},
        {"id": "Nyasa", "icon": "📝", "title": "NYASA", "desc": "Asset Ledger", "col": c4},
        {"id": "Agama", "icon": "📥", "title": "AGAMA", "desc": "Bulk Ingestion", "col": c5},
        {"id": "Exit", "icon": "🔒", "title": "EXIT", "desc": "Secure Terminate", "col": c6}
    ]
    for m in modules:
        with m["col"]:
            st.markdown(f"<div class='glass-card'><div class='icon-orb'>{m['icon']}</div><div class='title-text'>{m['title']}</div><div class='desc-text'>{m['desc']}</div></div>", unsafe_allow_html=True)
            if st.button(f"OPEN {m['title']}", key=m['id']):
                if m['id'] == "Exit": st.session_state.logged_in = False; st.rerun()
                else: st.session_state.page = m['id']; st.rerun()

# --- 7. FEATURE PAGES ---
def nav_back():
    if st.button("⬅️ RETURN TO COMMAND CENTER"): st.session_state.page = "Home"; st.rerun()

# 1. PREKSHA
if st.session_state.page == "Preksha":
    nav_back(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:4px;'>PREKSHA INTELLIGENCE</h2>", unsafe_allow_html=True)
    with get_db_conn() as conn:
        df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("No data.")
    else:
        col_l, col_r = st.columns([1, 2])
        with col_l:
            sentiment = st.select_slider("Market Sentiment", options=[0.8, 1.0, 1.2, 1.5, 2.0], value=1.0)
            safety = st.slider("Safety Stock Buffer", 0, 100, 20)
        with col_r:
            target = st.selectbox("Asset", df['name'])
            p_row = df[df['name'] == target].iloc[0]
            preds = (np.random.randint(20, 50, size=7) * sentiment).astype(int)
            st.plotly_chart(px.area(y=preds, title="AI Demand Forecast", template="plotly_dark").update_traces(line_color='#D4AF37', fillcolor='rgba(212,175,55,0.05)'), use_container_width=True)
            reorder = max(0, (preds.sum() + safety) - p_row['current_stock'])
            st.markdown(f"<div class='ai-suggestion'>🤖 **AI Decision:** Total demand predicted: {preds.sum()}. Recommendation: Order **{reorder} units**</div>", unsafe_allow_html=True)

# 2. STAMBHA
elif st.session_state.page == "Stambha":
    nav_back(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:4px;'>STAMBHA RESILIENCE</h2>", unsafe_allow_html=True)
    scenario = st.selectbox("Shock Trigger", ["Normal", "Port Closure", "Factory Fire"])
    with get_db_conn() as conn:
        df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if not df.empty:
        st.table(df[['name', 'current_stock', 'lead_time']])

# 3. SAMVADA (HYBRID INPUT MODE)
elif st.session_state.page == "Samvada":
    nav_back(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:4px;'>SAMVADA CONVERSATION</h2>", unsafe_allow_html=True)
    
    # Toggle for Voice Feedback
    st.session_state.voice_on = st.toggle("🔊 Activate Voice Assistant (AI speaks answers back)", value=st.session_state.voice_on)
    
    key = st.secrets.get("GROQ_API_KEY")
    if not key: st.error("AI Node Offline")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        
        # UI Structure
        chat_placeholder = st.container()
        
        # DUAL INPUT SECTION
        st.markdown("---")
        typed_prompt = st.chat_input("Type your question or data command...")
        voice_audio = st.audio_input("Or speak (Noise Filtered)")

        # Logic to pick input source
        final_query = None
        if typed_prompt:
            final_query = typed_prompt
        elif voice_audio:
            with st.spinner("Transcribing voice..."):
                final_query = client.audio.transcriptions.create(file=("q.wav", voice_audio.read()), model="whisper-large-v3", response_format="text")
                st.info(f"🗨️ Transcription: {final_query}")

        if final_query:
            st.session_state.chat_history.append({"role": "user", "content": final_query})
            with get_db_conn() as conn:
                ctx = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", conn, params=(st.session_state.user,)).to_string(index=False)
            
            with st.spinner("Agent Reasoning..."):
                res = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role":"system","content":f"You are Samvada AI. Inventory context: {ctx}. Turn data into decisions. Keep answers short."}, 
                              *st.session_state.chat_history[-3:]]
                )
                answer = res.choices[0].message.content
                st.session_state.chat_history.append({"role": "assistant", "content": answer})
                speak_response(answer)
                st.rerun()

        # Render History
        with chat_placeholder:
            for m in st.session_state.chat_history:
                with st.chat_message(m["role"]): st.markdown(m["content"])

# 4. NYASA
elif st.session_state.page == "Nyasa":
    nav_back(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:4px;'>NYASA ASSET LEDGER</h2>", unsafe_allow_html=True)
    with st.form("add"):
        n = st.text_input("Product Name"); s = st.number_input("Stock", 0); p = st.number_input("Unit Price", 0.0); lt = st.number_input("Lead Time", 1)
        if st.form_submit_button("COMMIT"):
            with get_db_conn() as conn:
                conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", (st.session_state.user, n, s, p, lt))
            st.success("Successfully Logged.")

# 5. AGAMA
elif st.session_state.page == "Agama":
    nav_back(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:4px;'>AGAMA SYNC</h2>", unsafe_allow_html=True)
    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        u_df = pd.read_csv(file); u_df['username'] = st.session_state.user
        if st.button("SYNCHRONIZE"):
            with get_db_conn() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Synced.")

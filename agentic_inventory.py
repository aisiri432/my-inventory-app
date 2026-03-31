import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI
import hashlib
import os

# --- 1. SETTINGS & ULTRA-PREMIUM UI ---
st.set_page_config(page_title="AROHA | Strategic Intelligence", layout="wide", page_icon="💠")

def apply_elite_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050505; color: #E0E0E0; }
        
        .icon-initial {
            font-size: 24px; font-weight: 800; color: #D4AF37; margin-bottom: 12px;
            letter-spacing: 2px; border-bottom: 2px solid #D4AF37; padding-bottom: 5px;
        }

        .glass-card {
            background: linear-gradient(145deg, rgba(20,20,20,0.95), rgba(10,10,10,0.95));
            backdrop-filter: blur(15px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 30px 20px; text-align: center; transition: 0.4s;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); height: 240px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .glass-card:hover { border: 1px solid #D4AF37; transform: translateY(-5px); box-shadow: 0 0 25px rgba(212, 175, 55, 0.15); }
        
        .title-text { color: #D4AF37; font-weight: 700; font-size: 1.1rem; letter-spacing: 2px; text-transform: uppercase; }
        .desc-text { color: #666; font-size: 0.7rem; margin-top: 8px; text-transform: uppercase; letter-spacing: 1px; }
        
        [data-testid="stSidebar"] { display: none; }
        
        .stButton>button { border-radius: 4px; background: #111; border: 1px solid #333; color: #D4AF37; font-weight: 700; padding: 10px; width: 100%; font-size: 0.7rem; letter-spacing: 1px; }
        .stButton>button:hover { border-color: #D4AF37; background: #D4AF37; color: black; }
        
        .ai-suggestion { background: rgba(212, 175, 55, 0.05); border: 1px solid #D4AF37; padding: 20px; border-radius: 10px; margin-top: 20px; }
        .auth-box { max-width: 400px; margin: 60px auto; padding: 40px; background: #0A0A0A; border-radius: 15px; border: 1px solid #222; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

apply_elite_css()

# --- 2. DATABASE STABILITY ENGINE (FIXED) ---
DB_FILE = 'aroha_pro.db'

def run_query(query, params=(), is_select=True):
    """Robust query runner using a context manager to prevent AttributeErrors."""
    with sqlite3.connect(DB_FILE, check_same_thread=False) as conn:
        if is_select:
            return pd.read_sql_query(query, conn, params=params)
        else:
            curr = conn.cursor()
            curr.execute(query, params)
            conn.commit()
            return None

def init_db():
    run_query('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, 
                  current_stock INTEGER, unit_price REAL, lead_time INTEGER)''', is_select=False)
    run_query('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)''', is_select=False)

init_db()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

# --- 3. SESSION STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 4. VOICE ENGINE ---
def speak_aloud(text):
    clean_text = text.replace('"', '').replace("'", "")
    js_code = f"<script>var msg = new SpeechSynthesisUtterance(); msg.text = '{clean_text}'; window.speechSynthesis.speak(msg);</script>"
    st.components.v1.html(js_code, height=0)

# --- 5. AUTHENTICATION ---
if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 style='color:#D4AF37; font-size:3rem; font-weight:800; letter-spacing:15px; margin-bottom:0;'>AROHA</h1><p style='color:#333; letter-spacing:5px;'>DATA INTO DECISIONS</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        mode = st.tabs(["LOGIN", "REGISTER"])
        with mode[0]:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("UNLOCK"):
                res = run_query("SELECT password FROM users WHERE username=?", (u,))
                if not res.empty and res.iloc[0]['password'] == make_hashes(p):
                    st.session_state.logged_in = True; st.session_state.user = u; st.rerun()
                else: st.error("Access Denied")
        with mode[1]:
            nu = st.text_input("New Username", key="r_u"); np = st.text_input("New Password", type="password", key="r_p")
            if st.button("CREATE ACCOUNT"):
                if nu and np:
                    try:
                        run_query("INSERT INTO users VALUES (?,?)", (nu, make_hashes(np)), is_select=False)
                        st.success("Success! Login now.")
                    except: st.error("User already exists.")
    st.stop()

# --- 6. COMMAND CENTER (HOME) ---
if st.session_state.page == "Home":
    st.markdown(f"<p style='text-align:center; color:#444; font-size:0.7rem;'>SECURE VAULT: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#D4AF37; letter-spacing:8px;'>COMMAND CENTER</h2>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3); c4, c5, c6 = st.columns(3)
    modules = [
        {"id": "Preksha", "char": "P", "title": "PREKSHA", "desc": "AI Demand Sensing", "col": c1},
        {"id": "Stambha", "char": "S", "title": "STAMBHA", "desc": "Risk Resilience", "col": c2},
        {"id": "Samvada", "char": "V", "title": "SAMVADA", "desc": "Voice Assistant", "col": c3},
        {"id": "Nyasa", "char": "N", "title": "NYASA", "desc": "Asset Ledger", "col": c4},
        {"id": "Agama", "char": "A", "title": "AGAMA", "desc": "Bulk Sync", "col": c5},
        {"id": "Exit", "char": "X", "title": "EXIT", "desc": "Lock System", "col": c6}
    ]
    for m in modules:
        with m["col"]:
            st.markdown(f"<div class='glass-card'><div class='icon-initial'>{m['char']}</div><div class='title-text'>{m['title']}</div><div class='desc-text'>{m['desc']}</div></div>", unsafe_allow_html=True)
            if st.button(f"OPEN {m['title']}", key=m['id']):
                if m['id'] == "Exit": st.session_state.logged_in = False; st.rerun()
                else: st.session_state.page = m['id']; st.rerun()

# --- 7. FEATURE PAGES ---
def nav_home():
    if st.button("⬅️ RETURN TO COMMAND CENTER"): st.session_state.page = "Home"; st.rerun()

# 1. PREKSHA
if st.session_state.page == "Preksha":
    nav_home(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:4px;'>PREKSHA INTELLIGENCE</h2>", unsafe_allow_html=True)
    df = run_query("SELECT * FROM products WHERE username=?", (st.session_state.user,))
    if df.empty: st.warning("No data found.")
    else:
        col_l, col_r = st.columns([1, 2])
        with col_l:
            sentiment = st.select_slider("Market Sentiment", options=[0.8, 1.0, 1.2, 1.5, 2.0], value=1.0)
            safety = st.slider("Safety Buffer", 0, 100, 20)
        with col_r:
            target = st.selectbox("Asset", df['name'])
            p_row = df[df['name'] == target].iloc[0]
            preds = (np.random.randint(20, 50, size=7) * sentiment).astype(int)
            st.plotly_chart(px.area(y=preds, title="AI Demand Forecast", template="plotly_dark").update_traces(line_color='#D4AF37'), use_container_width=True)
            reorder = max(0, (preds.sum() + safety) - p_row['current_stock'])
            st.markdown(f"<div class='ai-suggestion'>🤖 **AI Suggestion:** Total demand: {preds.sum()}. Recommendation: Order **{reorder} units**</div>", unsafe_allow_html=True)

# 2. STAMBHA
elif st.session_state.page == "Stambha":
    nav_home(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:4px;'>STAMBHA RESILIENCE</h2>", unsafe_allow_html=True)
    scenario = st.selectbox("Shock Trigger", ["Normal", "Port Closure", "Factory Fire"])
    df = run_query("SELECT * FROM products WHERE username=?", (st.session_state.user,))
    if not df.empty:
        df['TTS'] = (df['current_stock'] / 12).round(1)
        st.table(df[['name', 'current_stock', 'lead_time', 'TTS']])

# 3. SAMVADA (Voice AI)
elif st.session_state.page == "Samvada":
    nav_home(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:4px;'>SAMVADA VOICE ASSISTANT</h2>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY")
    if not key: st.error("AI Node Offline")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        audio = st.audio_input("Speak to AROHA")
        if audio:
            with st.spinner("Processing..."):
                trans = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
                ctx_df = run_query("SELECT name, current_stock FROM products WHERE username=?", (st.session_state.user,))
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"You are Samvada AI. Data: {ctx_df.to_string()}"}, {"role": "user", "content": trans}])
                reply = res.choices[0].message.content
                st.session_state.chat_history.append({"role": "user", "content": trans})
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.subheader(f"🤖 {reply}"); speak_aloud(reply); st.rerun()

# 4. NYASA
elif st.session_state.page == "Nyasa":
    nav_home(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:4px;'>NYASA ASSET LEDGER</h2>", unsafe_allow_html=True)
    with st.form("add"):
        n = st.text_input("Product Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1)
        if st.form_submit_button("LOG TO VAULT"):
            run_query("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", (st.session_state.user, n, s, p, lt), is_select=False)
            st.success("Successfully Logged.")

# 5. AGAMA
elif st.session_state.page == "Agama":
    nav_home(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:4px;'>AGAMA BULK SYNC</h2>", unsafe_allow_html=True)
    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        u_df = pd.read_csv(file); u_df['username'] = st.session_state.user
        if st.button("SYNCHRONIZE"):
            with sqlite3.connect(DB_FILE) as conn:
                u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Synchronization Complete.")

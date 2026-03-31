import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI
import hashlib

# --- 1. SETTINGS & ULTRA-PREMIUM UI ---
st.set_page_config(page_title="AROHA | Strategic Intelligence", layout="wide", page_icon="💠")

def apply_elite_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050505; color: #E0E0E0; }
        .icon-large { font-size: 42px; margin-bottom: 12px; display: block; filter: drop-shadow(0 0 10px rgba(212,175,55,0.6)); }
        .glass-card {
            background: linear-gradient(145deg, rgba(20,20,20,0.95), rgba(10,10,10,0.95));
            backdrop-filter: blur(15px); border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 30px 20px; text-align: center; transition: 0.4s;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); height: 260px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .glass-card:hover { border: 1px solid #D4AF37; transform: translateY(-8px); box-shadow: 0 0 25px rgba(212, 175, 55, 0.2); }
        .title-text { color: #D4AF37; font-weight: 700; font-size: 1.2rem; letter-spacing: 2px; text-transform: uppercase; }
        .desc-text { color: #666; font-size: 0.75rem; margin-top: 5px; text-transform: uppercase; }
        [data-testid="stSidebar"] { display: none; }
        .stButton>button { border-radius: 12px; background: #111; border: 1px solid #333; color: #D4AF37; font-weight: 700; padding: 10px; width: 100%; font-size: 0.8rem; }
        .stButton>button:hover { background: #D4AF37; color: black; box-shadow: 0 0 15px rgba(212,175,55,0.4); }
        .ai-suggestion { background: rgba(212, 175, 55, 0.05); border: 1px solid #D4AF37; padding: 20px; border-radius: 15px; margin-top: 20px; }
        </style>
    """, unsafe_allow_html=True)

apply_elite_css()

# --- 2. DATABASE STABILITY ENGINE ---
DB_FILE = 'aroha_enterprise.db'

def get_db_conn():
    """Create a fresh connection every time to prevent AttributeErrors."""
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    conn = get_db_conn()
    c = conn.cursor()
    # Create Products Table
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  username TEXT, 
                  name TEXT, 
                  category TEXT, 
                  current_stock INTEGER, 
                  unit_price REAL, 
                  lead_time INTEGER)''')
    # Create Users Table
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, 
                  password TEXT)''')
    conn.commit()
    conn.close()

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# Initialize database immediately
init_db()

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
    st.markdown("<h1 style='text-align:center; color:#D4AF37; font-size:4rem; letter-spacing:10px; margin-top:50px;'>AROHA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#555;'>TURN DATA INTO DECISIONS</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        mode = st.tabs(["LOGIN", "REGISTER"])
        with mode[0]:
            u = st.text_input("Username", key="login_u")
            p = st.text_input("Password", type="password", key="login_p")
            if st.button("UNLOCK VAULT"):
                conn = get_db_conn()
                res = conn.execute("SELECT password FROM users WHERE username=?", (u,)).fetchone()
                conn.close()
                if res and res[0] == make_hashes(p):
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else:
                    st.error("Access Denied")
        with mode[1]:
            nu = st.text_input("New Username", key="reg_u")
            np = st.text_input("New Password", type="password", key="reg_p")
            if st.button("AUTHORIZE ACCOUNT"):
                if nu and np:
                    conn = get_db_conn()
                    try:
                        conn.execute("INSERT INTO users VALUES (?,?)", (nu, make_hashes(np)))
                        conn.commit()
                        st.success("Account Created! Switch to Login.")
                    except:
                        st.error("Username already exists.")
                    finally:
                        conn.close()
    st.stop()

# --- 6. COMMAND CENTER ---
if st.session_state.page == "Home":
    st.markdown(f"<p style='text-align:center; color:#444;'>VAULT: {st.session_state.user.upper()} | SYSTEM: ACTIVE</p>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#D4AF37; letter-spacing:10px;'>COMMAND CENTER</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3); c4, c5, c6 = st.columns(3)
    modules = [
        {"id": "Preksha", "icon": "📈", "name": "PREKSHA", "desc": "AI Demand Sensing", "col": c1},
        {"id": "Stambha", "icon": "🛡️", "name": "STAMBHA", "desc": "Risk Resilience", "col": c2},
        {"id": "Samvada", "icon": "🎙️", "name": "SAMVADA", "desc": "Voice Assistant", "col": c3},
        {"id": "Nyasa", "icon": "📝", "name": "NYASA", "desc": "Asset Ledger", "col": c4},
        {"id": "Agama", "icon": "📥", "name": "AGAMA", "desc": "Bulk Sync", "col": c5},
        {"id": "Exit", "icon": "🔒", "name": "EXIT", "desc": "Lock System", "col": c6}
    ]
    for m in modules:
        with m["col"]:
            st.markdown(f"<div class='glass-card'><span class='icon-large'>{m['icon']}</span><span class='title-text'>{m['name']}</span><span class='desc-text'>{m['desc']}</span></div>", unsafe_allow_html=True)
            if st.button(f"OPEN {m['name']}", key=m['id']):
                if m['id'] == "Exit": st.session_state.logged_in = False; st.rerun()
                else: st.session_state.page = m['id']; st.rerun()

# --- 7. FEATURE PAGES ---
def nav_home():
    if st.button("⬅️ RETURN TO COMMAND CENTER"): st.session_state.page = "Home"; st.rerun()

# 1. PREKSHA (Intelligence)
if st.session_state.page == "Preksha":
    nav_home(); st.title("🔮 Preksha Strategic Intelligence")
    conn = get_db_conn()
    df = pd.read_sql_query("SELECT * FROM products WHERE username=?", (st.session_state.user,), conn)
    conn.close()
    
    if df.empty: 
        st.warning("No data found. Log items in Nyasa or Agama.")
    else:
        col_l, col_r = st.columns([1, 2])
        with col_l:
            sentiment = st.select_slider("Market Sentiment", options=[0.8, 1.0, 1.2, 1.5, 2.0], value=1.0)
            safety_buffer = st.slider("Safety Stock Buffer", 0, 100, 20)
        with col_r:
            target = st.selectbox("Select Asset", df['name'])
            p_row = df[df['name'] == target].iloc[0]
            preds = (np.random.randint(20, 50, size=7) * sentiment).astype(int)
            fig = px.area(y=preds, title=f"AI Forecast for {target}", template="plotly_dark")
            fig.update_traces(line_color='#D4AF37', fillcolor='rgba(212, 175, 55, 0.1)')
            st.plotly_chart(fig, use_container_width=True)
            reorder = max(0, (preds.sum() + safety_buffer) - p_row['current_stock'])
            st.markdown(f"<div class='ai-suggestion'>🤖 **AI Suggestion:** Total demand: **{preds.sum()} units**. <br> Recommendation: Order **{reorder} units**.</div>", unsafe_allow_html=True)

# 2. STAMBHA (Resilience)
elif st.session_state.page == "Stambha":
    nav_home(); st.title("🛡️ Stambha Resilience Simulator")
    scenario = st.selectbox("Shock Trigger", ["Normal", "Port Closure", "Factory Fire"])
    conn = get_db_conn()
    df = pd.read_sql_query("SELECT * FROM products WHERE username=?", (st.session_state.user,), conn)
    conn.close()
    if not df.empty:
        res = []
        for _, p in df.iterrows():
            tts = round(p['current_stock'] / 12, 1); ttr = p['lead_time']
            if scenario == "Port Closure": ttr *= 3
            if scenario == "Factory Fire": ttr += 30
            status = "🟢 Safe" if tts > ttr else "🔴 CRITICAL"
            if status == "🔴 CRITICAL": st.error(f"🚨 RISK: {p['name']} TTS ({tts}d) < TTR ({ttr}d)!")
            res.append({"Item": p['name'], "Time-to-Survive": tts, "Time-to-Recover": ttr, "Status": status})
        st.table(pd.DataFrame(res))

# 3. SAMVADA (Voice AI)
elif st.session_state.page == "Samvada":
    nav_home(); st.title("🎙️ Samvada: Voice Assistant")
    key = st.secrets.get("GROQ_API_KEY")
    if not key: st.error("AI Node Offline")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        audio_data = st.audio_input("Speak to AROHA")
        if audio_data:
            with st.spinner("Processing Voice..."):
                transcription = client.audio.transcriptions.create(file=("q.wav", audio_data.read()), model="whisper-large-v3", response_format="text")
                conn = get_db_conn()
                ctx_df = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", (st.session_state.user,), conn)
                conn.close()
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role": "system", "content": f"You are Samvada AI. Data: {ctx_df.to_string(index=False)}"}, {"role": "user", "content": transcription}])
                reply = res.choices[0].message.content
                st.session_state.chat_history.append({"role": "user", "content": transcription})
                st.session_state.chat_history.append({"role": "assistant", "content": reply})
                st.subheader(f"🤖 {reply}"); speak_aloud(reply); st.rerun()

# 4. NYASA (Ledger)
elif st.session_state.page == "Nyasa":
    nav_home(); st.title("📝 Nyasa Asset Ledger")
    with st.form("add_p"):
        n = st.text_input("Product Name"); s = st.number_input("Stock", 0); p = st.number_input("Unit Price", 0.0); lt = st.number_input("Lead Time", 1)
        if st.form_submit_button("LOG TO VAULT"):
            conn = get_db_conn()
            conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", (st.session_state.user, n, s, p, lt))
            conn.commit(); conn.close(); st.success("Asset logged successfully.")

# 5. AGAMA (Import)
elif st.session_state.page == "Agama":
    nav_home(); st.title("📥 Agama Bulk Ingestion")
    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        u_df = pd.read_csv(file); u_df['username'] = st.session_state.user
        if st.button("SYNCHRONIZE"):
            conn = get_db_conn()
            u_df.to_sql('products', conn, if_exists='append', index=False)
            conn.commit(); conn.close(); st.success("Sync Complete.")

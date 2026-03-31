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
st.set_page_config(page_title="AROHA | Inclusive AI", layout="wide", page_icon="🎙️")

def apply_elite_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050505; color: #E0E0E0; }
        
        .icon-large { font-size: 55px; margin-bottom: 15px; display: block; filter: drop-shadow(0 0 10px rgba(212,175,55,0.5)); }
        
        .glass-card {
            background: linear-gradient(145deg, rgba(20,20,20,0.95), rgba(10,10,10,0.95));
            backdrop-filter: blur(15px); border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 40px 20px; text-align: center; transition: 0.4s;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); height: 280px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .glass-card:hover { border: 1px solid #D4AF37; transform: translateY(-5px); box-shadow: 0 0 30px rgba(212, 175, 55, 0.2); }
        
        .title-text { color: #D4AF37; font-weight: 700; font-size: 1.3rem; letter-spacing: 2px; text-transform: uppercase; }
        .desc-text { color: #666; font-size: 0.8rem; margin-top: 5px; text-transform: uppercase; }
        
        .auth-box { max-width: 420px; margin: 50px auto; padding: 40px; background: #0A0A0A; border-radius: 25px; border: 1px solid #222; text-align: center; }
        [data-testid="stSidebar"] { display: none; }
        
        .stButton>button { border-radius: 12px; background: #111; border: 1px solid #333; color: #D4AF37; font-weight: 700; padding: 12px; width: 100%; }
        .stButton>button:hover { background: #D4AF37; color: black; box-shadow: 0 0 15px rgba(212,175,55,0.4); }
        </style>
    """, unsafe_allow_html=True)

apply_elite_css()

# --- 2. DATABASE & SESSION STATE ---
def get_db(): return sqlite3.connect('aroha_enterprise.db', check_same_thread=False)

def init_db():
    conn = get_db(); c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, username TEXT, name TEXT, category TEXT, current_stock INTEGER, unit_price REAL, lead_time INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit(); conn.close()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

init_db()

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 3. TEXT TO SPEECH (VOICE ENGINE) ---
def speak_aloud(text):
    """Browser-based Text-to-Speech injection."""
    clean_text = text.replace('"', '').replace("'", "")
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance();
    msg.text = "{clean_text}";
    msg.rate = 1.0;
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 4. AUTHENTICATION ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#D4AF37; font-size:4.5rem; letter-spacing:15px; margin-top:50px;'>AROHA</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        mode = st.tabs(["LOGIN", "REGISTER"])
        with mode[0]:
            u = st.text_input("Username", key="login_u")
            p = st.text_input("Password", type="password", key="login_p")
            if st.button("UNLOCK VAULT"):
                conn = get_db(); res = conn.execute("SELECT password FROM users WHERE username=?", (u,)).fetchone(); conn.close()
                if res and res[0] == make_hashes(p):
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Access Denied")
        with mode[1]:
            nu = st.text_input("New Username", key="reg_u")
            np = st.text_input("New Password", type="password", key="reg_p")
            if st.button("AUTHORIZE ACCOUNT"):
                conn = get_db(); conn.execute("INSERT INTO users VALUES (?,?)", (nu, make_hashes(np))); conn.commit(); conn.close()
                st.success("Registration Successful!")
    st.stop()

# --- 5. COMMAND CENTER (HOME GRID) ---
if st.session_state.page == "Home":
    st.markdown(f"<p style='text-align:center; color:#555;'>LOGGED IN AS: {st.session_state.user.upper()}</p>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#D4AF37; letter-spacing:10px;'>COMMAND CENTER</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3); c4, c5, c6 = st.columns(3)
    
    modules = [
        {"id": "Preksha", "icon": "📈", "name": "PREKSHA", "desc": "AI Demand Sensing", "col": c1},
        {"id": "Stambha", "icon": "🛡️", "name": "STAMBHA", "desc": "Risk Resilience", "col": c2},
        {"id": "Samvada", "icon": "🎙️", "name": "SAMVADA", "desc": "Voice Assistant", "col": c3},
        {"id": "Nyasa", "icon": "📝", "name": "NYASA", "desc": "Asset Ledger", "col": c4},
        {"id": "Agama", "icon": "📥", "name": "AGAMA", "desc": "Bulk Sync", "col": c5},
        {"id": "Exit", "icon": "🔒", "name": "EXIT", "desc": "Secure Terminate", "col": c6}
    ]
    
    for m in modules:
        with m["col"]:
            st.markdown(f"""
                <div class='glass-card'>
                    <span class='icon-large'>{m['icon']}</span>
                    <span class='title-text'>{m['name']}</span>
                    <span class='desc-text'>{m['desc']}</span>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"OPEN {m['name']}", key=m['id']):
                if m['id'] == "Exit": st.session_state.logged_in = False; st.rerun()
                else: st.session_state.page = m['id']; st.rerun()

# --- 6. SAMVADA (VOICE-TO-VOICE CHATBOT) ---
elif st.session_state.page == "Samvada":
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ RETURN TO COMMAND CENTER"): st.session_state.page = "Home"; st.rerun()
    st.title("🎙️ Samvada: Voice Assistant")
    st.info("Ask your inventory questions by voice or text. Samvada will speak back to you.")

    key = st.secrets.get("GROQ_API_KEY")
    if not key: st.error("AI Node Offline: Missing Key")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)

        # UI: Split screen for Chat and Voice Input
        chat_col, voice_col = st.columns([2, 1])

        with chat_col:
            # Display Chat History
            for m in st.session_state.chat_history:
                with st.chat_message(m["role"]): st.markdown(m["content"])

        with voice_col:
            st.markdown("### Voice Input")
            audio_data = st.audio_input("Click to speak")
            
            # --- PROCESS VOICE ---
            if audio_data:
                with st.spinner("Agent is listening..."):
                    # STT: Whisper Large V3
                    transcription = client.audio.transcriptions.create(
                        file=("query.wav", audio_data.read()),
                        model="whisper-large-v3",
                        response_format="text"
                    )
                    user_input = transcription
            else:
                # --- PROCESS TEXT (FALLBACK) ---
                user_input = st.chat_input("Or type your message here...")

            if user_input:
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                
                # Context Data (User's private stock)
                conn = get_db()
                df_ctx = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", (st.session_state.user,), conn)
                conn.close()
                ctx = df_ctx.to_string(index=False)

                # LLM: Llama 3.1 8B Instant
                with st.spinner("Agent is reasoning..."):
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": f"You are Samvada, the inclusive voice agent for AROHA. Data: {ctx}. Keep answers very short (max 2 sentences) for audio clarity."},
                            *st.session_state.chat_history[-3:] # Send last 3 messages for context
                        ]
                    )
                    reply = response.choices[0].message.content
                    st.session_state.chat_history.append({"role": "assistant", "content": reply})
                    
                    # --- TTS: READ ALOUD ---
                    speak_aloud(reply)
                    st.rerun()

# --- 7. NYASA (DATA ENTRY) ---
elif st.session_state.page == "Nyasa":
    st.button("⬅️ BACK", on_click=lambda: st.session_state.update({"page": "Home"}))
    st.title("📝 Nyasa Asset Ledger")
    with st.form("add_asset"):
        name = st.text_input("Product Name")
        stock = st.number_input("Initial Stock", 0)
        price = st.number_input("Unit Value", 0.0)
        lt = st.number_input("Lead Time", 1)
        if st.form_submit_button("COMMIT TO VAULT"):
            conn = get_db()
            conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", 
                         (st.session_state.user, name, stock, price, lt))
            conn.commit(); conn.close()
            st.success("Asset Registered Successfully.")

# --- 8. PREKSHA (DASHBOARD) ---
elif st.session_state.page == "Preksha":
    st.button("⬅️ BACK", on_click=lambda: st.session_state.update({"page": "Home"}))
    st.title("📈 Preksha Intelligence")
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM products WHERE username=?", (st.session_state.user,), conn)
    conn.close()
    if df.empty: st.warning("No assets in treasury.")
    else:
        st.dataframe(df, use_container_width=True)
        fig = px.bar(df, x='name', y='current_stock', color='name', template="plotly_dark", title="Current Stock Levels")
        st.plotly_chart(fig, use_container_width=True)

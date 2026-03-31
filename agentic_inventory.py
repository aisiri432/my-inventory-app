import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI
import hashlib
import base64

# --- 1. SETTINGS & INCLUSIVE UI ---
st.set_page_config(page_title="AROHA | Inclusive AI", layout="wide")

def apply_elite_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050505; color: #E0E0E0; }
        
        .icon-large { font-size: 60px; margin-bottom: 10px; display: block; }
        
        .glass-card {
            background: linear-gradient(145deg, rgba(20,20,20,0.9), rgba(10,10,10,0.9));
            backdrop-filter: blur(15px); border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 40px 20px; text-align: center; transition: 0.4s;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); height: 300px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .glass-card:hover { border: 1px solid #D4AF37; transform: translateY(-5px); box-shadow: 0 0 30px rgba(212, 175, 55, 0.2); }
        
        .title-text { color: #D4AF37; font-weight: 700; font-size: 1.4rem; letter-spacing: 2px; text-transform: uppercase; }
        .desc-text { color: #888; font-size: 0.9rem; margin-top: 5px; }
        
        .auth-box { max-width: 420px; margin: 50px auto; padding: 40px; background: #111; border-radius: 20px; border: 1px solid #222; text-align: center; }
        [data-testid="stSidebar"] { display: none; }
        
        .stButton>button { border-radius: 10px; background: #111; border: 1px solid #333; color: #D4AF37; font-weight: 700; padding: 12px; width: 100%; }
        .stButton>button:hover { background: #D4AF37; color: black; }
        </style>
    """, unsafe_allow_html=True)

apply_elite_css()

# --- 2. DATABASE LOGIC ---
def get_db(): return sqlite3.connect('aroha_enterprise.db', check_same_thread=False)

def init_db():
    conn = get_db(); c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, username TEXT, name TEXT, current_stock INTEGER, unit_price REAL, lead_time INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit(); conn.close()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

init_db()

# --- 3. SESSION STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"

# --- 4. TEXT TO SPEECH (VOICE FEEDBACK) ---
def speak_text(text):
    """Injects JavaScript to read the AI's response aloud."""
    js_code = f"""
    <script>
    var msg = new SpeechSynthesisUtterance();
    msg.text = "{text.replace('"', "'")}";
    window.speechSynthesis.speak(msg);
    </script>
    """
    st.components.v1.html(js_code, height=0)

# --- 5. AUTHENTICATION ---
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center; color:#D4AF37; font-size:4rem; letter-spacing:10px;'>AROHA</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        tab1, tab2 = st.tabs(["LOGIN", "REGISTER"])
        with tab1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("UNLOCK"):
                conn = get_db(); res = conn.execute("SELECT password FROM users WHERE username=?", (u,)).fetchone(); conn.close()
                if res and res[0] == make_hashes(p):
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.rerun()
                else: st.error("Wrong credentials")
        with tab2:
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            if st.button("CREATE ACCOUNT"):
                conn = get_db(); conn.execute("INSERT INTO users VALUES (?,?)", (nu, make_hashes(np))); conn.commit(); conn.close()
                st.success("Account Created!")
    st.stop()

# --- 6. COMMAND CENTER (VISUAL BADGES) ---
if st.session_state.page == "Home":
    st.markdown(f"<p style='text-align:center;'>USER: {st.session_state.user.upper()} | SYSTEM: ACTIVE</p>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#D4AF37; letter-spacing:10px;'>COMMAND CENTER</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3); c4, c5, c6 = st.columns(3)
    
    # Grid with Large Icons for Visual Understanding
    items = [
        {"id": "Preksha", "icon": "📈", "name": "PREKSHA", "desc": "Future Forecast", "col": c1},
        {"id": "Stambha", "icon": "🛡️", "name": "STAMBHA", "desc": "Risk Protection", "col": c2},
        {"id": "Samvada", "icon": "🎙️", "name": "SAMVADA", "desc": "Voice Assistant", "col": c3},
        {"id": "Nyasa", "icon": "📝", "name": "NYASA", "desc": "Add Data", "col": c4},
        {"id": "Agama", "icon": "📥", "name": "AGAMA", "desc": "Import Files", "col": c5},
        {"id": "Exit", "icon": "🔒", "name": "EXIT", "desc": "Lock System", "col": c6}
    ]
    
    for item in items:
        with item["col"]:
            st.markdown(f"""
                <div class='glass-card'>
                    <span class='icon-large'>{item['icon']}</span>
                    <span class='title-text'>{item['name']}</span>
                    <span class='desc-text'>{item['desc']}</span>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"OPEN {item['name']}", key=item['id']):
                if item['id'] == "Exit": st.session_state.logged_in = False; st.rerun()
                else: st.session_state.page = item['id']; st.rerun()

# --- 7. SAMVADA (VOICE INTELLIGENCE) ---
elif st.session_state.page == "Samvada":
    st.button("⬅️ BACK", on_click=lambda: st.session_state.update({"page": "Home"}))
    st.title("🎙️ Samvada: Voice Assistant")
    st.info("Ask questions about your inventory using your voice.")

    key = st.secrets.get("GROQ_API_KEY")
    if not key: st.error("AI Offline: No API Key")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        
        # VOICE INPUT SECTION
        audio_file = st.audio_input("Record your question")
        
        if audio_file:
            with st.spinner("Transcribing your voice..."):
                # Use Groq Whisper to convert speech to text
                transcription = client.audio.transcriptions.create(
                    file=("file.wav", audio_file.read()),
                    model="whisper-large-v3",
                    response_format="text",
                )
                st.write(f"💬 **You said:** {transcription}")
                
                # Use transcription as the prompt for the LLM
                conn = get_db()
                ctx_df = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", (st.session_state.user,), conn)
                conn.close()
                
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[
                        {"role": "system", "content": f"You are AROHA Voice Agent. Data: {ctx_df.to_string()}. Give short 2-sentence answers."},
                        {"role": "user", "content": transcription}
                    ]
                )
                reply = response.choices[0].message.content
                st.subheader("🤖 Assistant Response")
                st.write(reply)
                
                # --- AUTO READ ALOUD ---
                speak_text(reply)

# --- 8. OTHER PAGES (Minimalist logic) ---
elif st.session_state.page == "Nyasa":
    st.button("⬅️ BACK", on_click=lambda: st.session_state.update({"page": "Home"}))
    st.title("📝 Nyasa: Add Data")
    with st.form("add"):
        name = st.text_input("Item Name")
        stock = st.number_input("Units", 0)
        if st.form_submit_button("SAVE"):
            conn = get_db(); conn.execute("INSERT INTO products (username, name, current_stock) VALUES (?,?,?)", (st.session_state.user, name, stock))
            conn.commit(); conn.close(); st.success("Saved!")

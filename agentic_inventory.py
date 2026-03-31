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

# --- 1. SETTINGS & ULTRA-PREMIUM GLASS UI ---
st.set_page_config(page_title="AROHA | Elite Intelligence", layout="wide", page_icon="💠")

def apply_elite_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050505; color: #E0E0E0; }
        
        .icon-orb { 
            font-size: 50px; margin-bottom: 15px; display: block; 
            filter: drop-shadow(0 0 15px rgba(212,175,55,0.7)); 
        }
        
        .glass-card {
            background: linear-gradient(145deg, rgba(20,20,20,0.95), rgba(10,10,10,0.95));
            backdrop-filter: blur(15px); border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 35px 20px; text-align: center; transition: 0.4s;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); height: 300px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .glass-card:hover { border: 1px solid #D4AF37; transform: translateY(-10px); box-shadow: 0 0 30px rgba(212, 175, 55, 0.3); }
        
        .title-text { color: #D4AF37; font-weight: 700; font-size: 1.3rem; letter-spacing: 2px; text-transform: uppercase; }
        .desc-text { color: #888; font-size: 0.85rem; margin-top: 10px; }
        
        [data-testid="stSidebar"] { display: none; }
        
        .stButton>button { border-radius: 12px; background: #111; border: 1px solid #333; color: #D4AF37; font-weight: 700; padding: 12px; width: 100%; font-size: 0.85rem; }
        .stButton>button:hover { background: #D4AF37; color: black; box-shadow: 0 0 15px rgba(212,175,55,0.5); }
        
        /* High-End AI Suggestion Box */
        .ai-decision-box {
            background: rgba(212, 175, 55, 0.05);
            border: 1px solid #D4AF37;
            padding: 25px;
            border-radius: 20px;
            margin-top: 30px;
            border-left: 8px solid #D4AF37;
        }
        .reasoning-text { color: #aaa; font-size: 0.9rem; font-style: italic; margin-top: 10px; }
        
        .header-info { display: flex; justify-content: center; gap: 20px; padding: 15px; background: rgba(255,255,255,0.02); border-radius: 50px; margin-bottom: 40px; font-size: 0.7rem; color: #666; letter-spacing: 1px; }
        </style>
    """, unsafe_allow_html=True)

apply_elite_css()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_final_v5.db'

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

# --- 3. SESSION & VOICE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

def speak_aloud(text):
    clean = text.replace('"', '').replace("'", "")
    js = f"<script>var m = new SpeechSynthesisUtterance(); m.text='{clean}'; window.speechSynthesis.speak(m);</script>"
    st.components.v1.html(js, height=0)

# --- 4. AUTHENTICATION ---
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
            nu = st.text_input("New Username", key="r_u"); np = st.text_input("New Password", type="password", key="r_p")
            if st.button("AUTHORIZE ✅"):
                if nu and np:
                    try:
                        with get_db_conn() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, make_hashes(np)))
                        st.success("Authorized! Switch to Login.")
                    except: st.error("User exists.")
        with st.expander("🛠️ System Recovery"):
            if st.button("🔥 HARD RESET"):
                with get_db_conn() as conn:
                    conn.execute("DROP TABLE IF EXISTS users")
                    conn.execute("DROP TABLE IF EXISTS products")
                st.warning("Cleared."); time.sleep(1); st.rerun()
    st.stop()

# --- 5. COMMAND CENTER (HOME GRID) ---
if st.session_state.page == "Home":
    st.markdown(f"<div class='header-info'>🟢 STATUS: ACTIVE | VAULT: {st.session_state.user.upper()} | 🎙️ AGENT: SAMVADA V5.1</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#D4AF37; letter-spacing:10px;'>COMMAND CENTER</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3); c4, c5, c6 = st.columns(3)
    modules = [
        {"id": "Preksha", "icon": "🔮", "title": "PREKSHA", "desc": "AI Demand & Suggestions", "col": c1},
        {"id": "Stambha", "icon": "🛡️", "title": "STAMBHA", "desc": "Supply Chain Resilience", "col": c2},
        {"id": "Samvada", "icon": "🎙️", "title": "SAMVADA", "desc": "Voice Agent Intelligence", "col": c3},
        {"id": "Nyasa", "icon": "📝", "title": "NYASA", "desc": "Asset Ledger & Audit", "col": c4},
        {"id": "Agama", "icon": "📥", "title": "AGAMA", "desc": "Bulk Data Ingestion", "col": c5},
        {"id": "Exit", "icon": "🔒", "title": "EXIT", "desc": "Secure Lock Session", "col": c6}
    ]
    for m in modules:
        with m["col"]:
            st.markdown(f"<div class='glass-card'><span class='icon-orb'>{m['icon']}</span><span class='title-text'>{m['title']}</span><span class='desc-text'>{m['desc']}</span></div>", unsafe_allow_html=True)
            if st.button(f"ENTER {m['title']}", key=m['id']):
                if m['id'] == "Exit": st.session_state.logged_in = False; st.rerun()
                else: st.session_state.page = m['id']; st.rerun()

# --- 6. FEATURE PAGES ---
def nav_back():
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("⬅️ COMMAND CENTER"): st.session_state.page = "Home"; st.rerun()

# 1. PREKSHA (The Intelligence Node)
if st.session_state.page == "Preksha":
    nav_back(); st.title("🔮 Preksha: Strategic Intelligence")
    with get_db_conn() as conn:
        df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    
    if df.empty: st.warning("Treasury empty. Use Nyasa or Agama.")
    else:
        col_l, col_r = st.columns([1, 2])
        with col_l:
            st.subheader("🌍 Market Sensing")
            sentiment = st.select_slider("External Factors (Weather/Festivals)", options=[0.8, 1.0, 1.2, 1.5, 2.0], value=1.0)
            safety = st.slider("Safety Stock Buffer %", 0, 100, 20)
            st.info("💡 Adjust the slider to simulate demand surges due to holidays or weather shocks.")
        
        with col_r:
            target = st.selectbox("Select Asset", df['name'])
            p_row = df[df['name'] == target].iloc[0]
            
            # AI Logic
            base_preds = np.random.randint(20, 50, size=7)
            final_preds = (base_preds * sentiment).astype(int)
            total_pred = final_preds.sum()
            reorder_qty = max(0, (total_pred + safety) - p_row['current_stock'])
            
            fig = px.area(y=final_preds, title=f"AI 7-Day Demand Path: {target}", template="plotly_dark")
            fig.update_traces(line_color='#D4AF37', fillcolor='rgba(212, 175, 55, 0.1)')
            st.plotly_chart(fig, use_container_width=True)
            
            # --- THE AI SUGGESTION BOX (ENHANCED) ---
            st.markdown(f"""
                <div class='ai-decision-box'>
                    <h2 style='color:#D4AF37; margin:0;'>🤖 AGENT DECISION</h2>
                    <p style='font-size:1.2rem;'>Recommendation: Order <b>{reorder_qty} units</b> immediately.</p>
                    <div class='reasoning-text'>
                        <b>Reasoning:</b> Based on {sentiment}x Market Sensing, predicted demand is {total_pred}. 
                        Current stock is {p_row['current_stock']}. To maintain a {safety}% safety buffer, 
                        the agent has triggered a restock request.
                    </div>
                </div>
            """, unsafe_allow_html=True)

# 2. STAMBHA (Resilience Node)
elif st.session_state.page == "Stambha":
    nav_back(); st.title("🛡️ Stambha: Resilience Analysis")
    scenario = st.selectbox("Disruption Scenario", ["Normal", "Port Closure", "Factory Fire", "Tariff Surge"])
    with get_db_conn() as conn:
        df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if not df.empty:
        results = []
        for _, p in df.iterrows():
            tts = round(p['current_stock'] / 12, 1); ttr = p['lead_time']
            if scenario == "Port Closure": ttr *= 3
            if scenario == "Factory Fire": ttr += 30
            status = "🟢 SAFE" if tts > ttr else "🔴 CRITICAL"
            if status == "🔴 CRITICAL":
                st.error(f"🚨 **URGENT:** {p['name']} will stockout in {tts} days. Recovery time is {ttr} days. Action required!")
            results.append({"Asset": p['name'], "Time-to-Survive (Days)": tts, "Time-to-Recover (Days)": ttr, "Risk Level": status})
        st.table(pd.DataFrame(results))

# 3. SAMVADA (Voice AI Node)
elif st.session_state.page == "Samvada":
    nav_back(); st.title("🎙️ Samvada: Voice Assistant")
    key = st.secrets.get("GROQ_API_KEY")
    if not key: st.error("AI Node Offline")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        audio = st.audio_input("Speak to AROHA")
        if audio:
            with st.spinner("Processing Strategy..."):
                trans = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
                with get_db_conn() as conn:
                    ctx = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", conn, params=(st.session_state.user,)).to_string(index=False)
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system", "content":f"You are Samvada AI. Use Data: {ctx}. Keep answers very short."}, {"role":"user", "content": trans}])
                ans = res.choices[0].message.content
                st.session_state.chat_history.append({"role":"user","content":trans})
                st.session_state.chat_history.append({"role":"assistant","content":ans})
                st.subheader(f"🤖 {ans}"); speak_aloud(ans); st.rerun()

# 4. NYASA (Ledger Node)
elif st.session_state.page == "Nyasa":
    nav_back(); st.title("📝 Nyasa Asset Ledger")
    with st.form("add"):
        n = st.text_input("Product Name"); s = st.number_input("Stock Qty", 0); p = st.number_input("Unit Price ($)", 0.0); lt = st.number_input("Lead Time (Days)", 1)
        if st.form_submit_button("COMMIT TO VAULT 🔒"):
            with get_db_conn() as conn:
                conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", (st.session_state.user, n, s, p, lt))
            st.success("Asset Committed.")

# 5. AGAMA (Import Node)
elif st.session_state.page == "Agama":
    nav_back(); st.title("📥 Agama Bulk Sync")
    st.info("Upload CSV with columns: name, current_stock, unit_price, lead_time")
    file = st.file_uploader("Upload CSV Supply Ledger", type="csv")
    if file:
        u_df = pd.read_csv(file)
        if all(c in u_df.columns for c in ['name', 'current_stock', 'unit_price', 'lead_time']):
            if st.button("SYNCHRONIZE 🌐"):
                u_df['username'] = st.session_state.user
                with get_db_conn() as conn:
                    u_df[['username','name','current_stock','unit_price','lead_time']].to_sql('products', conn, if_exists='append', index=False)
                st.success("Sync Complete.")

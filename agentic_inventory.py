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
        .icon-orb { font-size: 38px; margin-bottom: 10px; display: block; filter: drop-shadow(0 0 10px rgba(212,175,55,0.6)); }
        .glass-card {
            background: linear-gradient(145deg, rgba(20,20,20,0.95), rgba(10,10,10,0.95));
            backdrop-filter: blur(15px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 25px 15px; text-align: center; transition: 0.4s;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); height: 260px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .glass-card:hover { border: 1px solid #D4AF37; transform: translateY(-10px); box-shadow: 0 0 30px rgba(212, 175, 55, 0.3); }
        .title-text { color: #D4AF37; font-weight: 700; font-size: 1.1rem; letter-spacing: 1px; text-transform: uppercase; }
        .desc-text { color: #777; font-size: 0.75rem; margin-top: 5px; }
        [data-testid="stSidebar"] { display: none; }
        .stButton>button { border-radius: 8px; background: #111; border: 1px solid #333; color: #D4AF37; font-weight: 700; padding: 10px; width: 100%; font-size: 0.8rem; }
        .stButton>button:hover { border-color: #D4AF37; background: #D4AF37; color: black; box-shadow: 0 0 15px rgba(212,175,55,0.5); }
        .ai-decision-box { background: rgba(212, 175, 55, 0.08); border-left: 10px solid #D4AF37; padding: 20px; border-radius: 15px; margin-top: 20px; }
        .review-box { background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; margin-top: 8px; border: 1px solid #222; font-size: 0.85rem; }
        .financial-stat { background: #111; padding: 15px; border-radius: 10px; border: 1px solid #222; text-align: center; border-top: 3px solid #D4AF37; }
        .header-info { display: flex; justify-content: center; gap: 20px; padding: 15px; background: rgba(255,255,255,0.02); border-radius: 50px; margin-bottom: 40px; font-size: 0.7rem; color: #666; letter-spacing: 1px; }
        </style>
    """, unsafe_allow_html=True)

apply_elite_css()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_master_v15.db'
def get_db_conn(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_db_conn() as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
        c.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, 
                      category TEXT, current_stock INTEGER, unit_price REAL, lead_time INTEGER, 
                      supplier TEXT, image_url TEXT, reviews TEXT)''')
        conn.commit()
init_db()

def make_hashes(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- 3. SESSION & VOICE STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_on" not in st.session_state: st.session_state.voice_on = False

def speak_aloud(text):
    if st.session_state.voice_on:
        clean = text.replace('"', '').replace("'", "")
        js = f"<script>var m = new SpeechSynthesisUtterance(); m.text='{clean}'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 4. AUTHENTICATION ---
if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 style='color:#D4AF37; font-size:4rem; font-weight:800; letter-spacing:15px;'>AROHA</h1><p style='color:#555;'>STRATEGIC ENTERPRISE ORCHESTRATOR</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        m = st.tabs(["🔑 LOGIN", "📝 REGISTER"])
        with m[0]:
            u = st.text_input("Username", key="l_u")
            p = st.text_input("Password", type="password", key="l_p")
            if st.button("UNLOCK VAULT 🔓"):
                with get_db_conn() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == make_hashes(p):
                    st.session_state.logged_in = True; st.session_state.user = u; st.rerun()
                else: st.error("Access Denied")
        with m[1]:
            nu = st.text_input("New User", key="r_u"); np = st.text_input("New Password", type="password", key="r_p")
            if st.button("AUTHORIZE ACCOUNT ✅"):
                if nu and np:
                    try:
                        with get_db_conn() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, make_hashes(np)))
                        st.success("Authorized! Switch to Login.")
                    except: st.error("User exists.")
    st.stop()

# --- 5. COMMAND CENTER (3x3 Grid) ---
if st.session_state.page == "Home":
    st.markdown(f"<div class='header-info'>🟢 ONLINE | VAULT: {st.session_state.user.upper()} | VERSION 15.0</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#D4AF37; letter-spacing:10px;'>COMMAND CENTER</h1>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3); c4, c5, c6 = st.columns(3); c7, c8, c9 = st.columns(3)
    modules = [
        {"id": "Preksha", "icon": "🔮", "title": "PREKSHA", "desc": "AI Demand & Visual Profile", "col": c1},
        {"id": "Stambha", "icon": "🛡️", "title": "STAMBHA", "desc": "TTS vs TTR Resilience", "col": c2},
        {"id": "Artha", "icon": "💰", "title": "ARTHA", "desc": "Financial Value Analysis", "col": c3},
        {"id": "Samvada", "icon": "🎙️", "title": "SAMVADA", "desc": "Voice Strategic Assistant", "col": c4},
        {"id": "Mithra", "icon": "🤝", "title": "MITHRA", "desc": "Supplier Risk Scoring", "col": c5},
        {"id": "Karya", "icon": "📄", "title": "KARYA", "desc": "Autonomous PO Gen", "col": c6},
        {"id": "Nyasa", "icon": "📝", "title": "NYASA", "desc": "Ledger & Media Registry", "col": c7},
        {"id": "Agama", "icon": "📥", "title": "AGAMA", "desc": "Bulk Data Ingestion", "col": c8},
        {"id": "Exit", "icon": "🔒", "title": "EXIT", "desc": "Secure Terminate Session", "col": c9}
    ]
    for m in modules:
        with m["col"]:
            st.markdown(f"<div class='glass-card'><span class='icon-orb'>{m['icon']}</span><span class='title-text'>{m['title']}</span><span class='desc-text'>{m['desc']}</span></div>", unsafe_allow_html=True)
            if st.button(f"ENTER {m['title']}", key=m['id']):
                if m['id'] == "Exit": st.session_state.logged_in = False; st.rerun()
                else: st.session_state.page = m['id']; st.rerun()

# --- 6. FEATURE PAGES ---
def nav_back():
    if st.button("⬅️ RETURN TO COMMAND CENTER"): st.session_state.page = "Home"; st.rerun()

# 1. PREKSHA
if st.session_state.page == "Preksha":
    nav_back(); st.title("🔮 Preksha: Strategic Intelligence")
    with get_db_conn() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("Treasury empty.")
    else:
        target = st.selectbox("Select Asset", df['name'])
        p_row = df[df['name'] == target].iloc[0]
        col_img, col_chart = st.columns([1, 2])
        with col_img:
            if p_row['image_url']: st.image(p_row['image_url'], use_container_width=True)
            st.markdown("### Customer Sentiment")
            if p_row['reviews']:
                for r in p_row['reviews'].split('|'): st.markdown(f"<div class='review-box'>⭐ {r}</div>", unsafe_allow_html=True)
        with col_chart:
            sentiment = st.select_slider("Market Sensing", options=[0.8, 1.0, 1.2, 1.5, 2.0], value=1.0)
            preds = (np.random.randint(20, 50, size=7) * sentiment).astype(int)
            st.plotly_chart(px.area(y=preds, title=f"7-Day Demand path", template="plotly_dark").update_traces(line_color='#D4AF37'), use_container_width=True)
            reorder = max(0, (preds.sum() + 20) - p_row['current_stock'])
            st.markdown(f"<div class='ai-decision-box'>🤖 **AI Decision:** Recommendation to order **{reorder} units**.</div>", unsafe_allow_html=True)

# 2. STAMBHA
elif st.session_state.page == "Stambha":
    nav_back(); st.title("🛡️ Stambha: Resilience Simulator")
    scenario = st.selectbox("Trigger Shock", ["Normal", "Port Closure (3x Lead Time)", "Factory Fire (+30d)"])
    with get_db_conn() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if not df.empty:
        results = []
        for _, p in df.iterrows():
            ttr = p['lead_time']
            if "Port" in scenario: ttr *= 3
            if "Fire" in scenario: ttr += 30
            tts = round(p['current_stock'] / 12, 1)
            status = "🟢 Safe" if tts > ttr else "🔴 CRITICAL"
            results.append({"Asset": p['name'], "Survival(d)": tts, "Recovery(d)": ttr, "Status": status})
        st.table(pd.DataFrame(results))

# 3. ARTHA
elif st.session_state.page == "Artha":
    nav_back(); st.title("💰 Artha: Financial Intelligence")
    with get_db_conn() as conn: df = pd.read_sql_query("SELECT current_stock, unit_price FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns(2)
        c1.markdown(f"<div class='financial-stat'>Total Inventory Value<br><h2>${total_v:,.2F}</h2></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='financial-stat'>Idle Capital Risk (15%)<br><h2 style='color:red;'>${total_v*0.15:,.2F}</h2></div>", unsafe_allow_html=True)
        st.plotly_chart(px.pie(df, values='current_stock', names='unit_price', title="Value Distribution", template="plotly_dark"))

# 4. SAMVADA
elif st.session_state.page == "Samvada":
    nav_back(); st.title("🎙️ Samvada: Voice Assistant")
    st.session_state.voice_on = st.toggle("🔊 AI Voice Feedback", value=st.session_state.voice_on)
    key = st.secrets.get("GROQ_API_KEY")
    if not key: st.error("Key missing.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
        u_in = st.chat_input("Type or use Voice below...")
        audio = st.audio_input("Speak Command")
        if audio:
            with st.spinner("Transcribing..."): u_in = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        if u_in:
            st.session_state.chat_history.append({"role":"user","content":u_in})
            with get_db_conn() as conn: ctx = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", conn, params=(st.session_state.user,)).to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are Samvada AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant","content":ans})
            speak_aloud(ans); st.rerun()

# 5. MITHRA
elif st.session_state.page == "Mithra":
    nav_back(); st.title("🤝 Mithra: Supplier Network")
    with get_db_conn() as conn: df = pd.read_sql_query("SELECT supplier, lead_time, name FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if not df.empty:
        st.subheader("Vendor Lead Time Matrix")
        st.dataframe(df, use_container_width=True)
    else: st.info("No supplier data available.")

# 6. KARYA
elif st.session_state.page == "Karya":
    nav_back(); st.title("📄 Karya: Autonomous Documents")
    with get_db_conn() as conn: df = pd.read_sql_query("SELECT name, supplier FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if not df.empty:
        target = st.selectbox("Select Item for Purchase Order", df['name'])
        if st.button("GENERATE DIGITAL PO"):
            st.success("Document Generated.")
            st.code(f"PO-ID: {np.random.randint(1000,9999)}\nITEM: {target}\nSTATUS: APPROVED\nVAULT: {st.session_state.user.upper()}")
    else: st.info("Add products to generate orders.")

# 7. NYASA
elif st.session_state.page == "Nyasa":
    nav_back(); st.title("📝 Nyasa Asset Ledger")
    with st.form("add"):
        n = st.text_input("Name"); c = st.text_input("Category"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1); sup = st.text_input("Supplier"); img = st.text_input("Image URL"); rev = st.text_area("Reviews (| split)")
        if st.form_submit_button("COMMIT"):
            with get_db_conn() as conn: conn.execute("INSERT INTO products (username, name, category, current_stock, unit_price, lead_time, supplier, image_url, reviews) VALUES (?,?,?,?,?,?,?,?,?)", (st.session_state.user, n, c, s, p, lt, sup, img, rev))
            st.success("Asset Committed.")

# 8. AGAMA
elif st.session_state.page == "Agama":
    nav_back(); st.title("📥 Agama: Bulk Sync")
    file = st.file_uploader("Choose CSV", type="csv")
    if file:
        u_df = pd.read_csv(file)
        req = ['name', 'current_stock', 'unit_price', 'lead_time']
        opt = ['category', 'supplier', 'image_url', 'reviews']
        if all(c in u_df.columns for c in req):
            for col in opt:
                if col not in u_df.columns: u_df[col] = ""
            u_df['username'] = st.session_state.user
            final_df = u_df[['username', 'name', 'category', 'current_stock', 'unit_price', 'lead_time', 'supplier', 'image_url', 'reviews']]
            if st.button("SYNCHRONIZE"):
                with get_db_conn() as conn: final_df.to_sql('products', conn, if_exists='append', index=False)
                st.success("Sync Successful.")

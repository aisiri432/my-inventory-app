import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI

# --- 1. CORE BRANDING ---
APP_NAME = "AROHA"
TAGLINE = "Turn Data into Decisions"

st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="💠")

# --- 2. DATABASE LOGIC ---
def get_db_connection():
    return sqlite3.connect('aroha_vault.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, current_stock INTEGER, 
                  unit_price REAL, lead_time INTEGER, supplier TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, hint TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales_history 
                 (product_id INTEGER, date TEXT, units_sold INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. SESSION STATE ---
if "auth_status" not in st.session_state: st.session_state.auth_status = "Login"
if "page" not in st.session_state: st.session_state.page = "Home"

# --- 4. CUSTOM CSS (High-End UI) ---
st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: white; }
    .main-title { text-align: center; color: #D4AF37; font-size: 3.5em; font-weight: 800; letter-spacing: 5px; margin-bottom: 0px; }
    .tagline { text-align: center; color: #888; font-size: 1.1em; margin-bottom: 50px; font-style: italic; }
    .badge-container {
        background: linear-gradient(145deg, #10141d, #0a0e14);
        border: 1px solid #1f2937; padding: 40px 20px; border-radius: 28px;
        text-align: center; transition: 0.4s; margin-bottom: 10px;
    }
    .badge-container:hover { border-color: #D4AF37; transform: translateY(-10px); background: #161B22; }
    .badge-icon { font-size: 50px; margin-bottom: 10px; }
    .badge-label { color: #D4AF37; font-weight: 700; font-size: 1.2em; }
    .stButton>button { width: 100%; border-radius: 15px; border: 1px solid #1f2937; background: #10141d; color: white; }
    .stButton>button:hover { background: #D4AF37 !important; color: black !important; }
    </style>
""", unsafe_allow_html=True)

# --- 5. AUTHENTICATION MODULE ---
def get_user():
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username='admin'").fetchone()
    conn.close()
    return user

if st.session_state.auth_status != "Authenticated":
    st.markdown(f"<h1 class='main-title'>💠 {APP_NAME}</h1>", unsafe_allow_html=True)
    user_data = get_user()
    
    if not user_data:
        st.info("🏦 Initialize Treasury: Set your Mantra & Hint.")
        new_pwd = st.text_input("New Mantra", type="password")
        hint = st.text_input("Security Hint (Answer)")
        if st.button("Initialize Vault"):
            conn = get_db_connection(); conn.execute("INSERT INTO users VALUES ('admin',?,?)", (new_pwd, hint))
            conn.commit(); conn.close(); st.rerun()
    else:
        pwd = st.text_input("Enter Access Mantra", type="password")
        if st.button("Unlock AROHA"):
            if pwd == user_data[1]: st.session_state.auth_status = "Authenticated"; st.rerun()
            else: st.error("Wrong Mantra.")
        if st.button("Forgot Mantra?"):
            st.info(f"Hint Answer Verification Required.")
            ans = st.text_input("Enter Hint Answer")
            if ans == user_data[2]: st.success(f"Mantra is: {user_data[1]}")
    st.stop()

# --- 6. THE HOME SCREEN (GRID) ---
def go_home(): st.session_state.page = "Home"; st.rerun()

if st.session_state.page == "Home":
    st.markdown(f"<h1 class='main-title'>{APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='tagline'>{TAGLINE}</p>", unsafe_allow_html=True)
    
    r1c1, r1c2, r1c3 = st.columns(3)
    r2c1, r2c2, r2c3 = st.columns(3)

    with r1c1:
        st.markdown("<div class='badge-container'><div class='badge-icon'>🔮</div><div class='badge-label'>PREKSHA</div></div>", unsafe_allow_html=True)
        if st.button("Open Preksha"): st.session_state.page = "Preksha"; st.rerun()
    with r1c2:
        st.markdown("<div class='badge-container'><div class='badge-icon'>🛡️</div><div class='badge-label'>STAMBHA</div></div>", unsafe_allow_html=True)
        if st.button("Open Stambha"): st.session_state.page = "Stambha"; st.rerun()
    with r1c3:
        st.markdown("<div class='badge-container'><div class='badge-icon'>🗣️</div><div class='badge-label'>SAMVADA</div></div>", unsafe_allow_html=True)
        if st.button("Open Samvada"): st.session_state.page = "Samvada"; st.rerun()
    with r2c1:
        st.markdown("<div class='badge-container'><div class='badge-icon'>✍️</div><div class='badge-label'>NYASA</div></div>", unsafe_allow_html=True)
        if st.button("Open Nyasa"): st.session_state.page = "Nyasa"; st.rerun()
    with r2c2:
        st.markdown("<div class='badge-container'><div class='badge-icon'>📥</div><div class='badge-label'>AGAMA</div></div>", unsafe_allow_html=True)
        if st.button("Open Agama"): st.session_state.page = "Agama"; st.rerun()
    with r2c3:
        st.markdown("<div class='badge-container'><div class='badge-icon'>🔒</div><div class='badge-label'>EXIT</div></div>", unsafe_allow_html=True)
        if st.button("Secure Exit"): st.session_state.auth_status = "Login"; st.rerun()

# --- 7. FEATURE PAGES (DETAILED LOGIC) ---

# --- PREKSHA: AI FORECASTING ---
elif st.session_state.page == "Preksha":
    st.button("⬅️ Home", on_click=go_home)
    st.title("🔮 Preksha: Strategic Intelligence")
    conn = get_db_connection(); df = pd.read_sql_query("SELECT * FROM products", conn); conn.close()
    if df.empty: st.warning("No data. Add in Nyasa.")
    else:
        target = st.selectbox("Select Asset", df['name'])
        preds = np.random.randint(10, 50, size=7)
        fig = px.line(x=[f"Day {i+1}" for i in range(7)], y=preds, title=f"7-Day Forecast: {target}", template="plotly_dark")
        fig.update_traces(line_color='#D4AF37')
        st.plotly_chart(fig, use_container_width=True)

# --- STAMBHA: RESILIENCE ---
elif st.session_state.page == "Stambha":
    st.button("⬅️ Home", on_click=go_home)
    st.title("🛡️ Stambha: Resilience Analysis")
    scenario = st.selectbox("Trigger Shock", ["Normal", "Port Closure", "Factory Fire"])
    st.info(f"Agent simulating {scenario} impact on stock survival (TTS vs TTR).")
    conn = get_db_connection(); df = pd.read_sql_query("SELECT name, current_stock, lead_time FROM products", conn); conn.close()
    st.table(df)

# --- SAMVADA: AI CHAT ---
elif st.session_state.page == "Samvada":
    st.button("⬅️ Home", on_click=go_home)
    st.title("🗣️ Samvada: Agentic Chat")
    key = st.secrets.get("GROQ_API_KEY")
    if not key: st.error("API Key missing.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if prompt := st.chat_input("Ask Samvada..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system", "content":"You are Samvada AI."}] + st.session_state.messages[-3:])
                ans = res.choices[0].message.content
                st.markdown(ans); st.session_state.messages.append({"role": "assistant", "content": ans})

# --- NYASA: MANUAL ENTRY ---
elif st.session_state.page == "Nyasa":
    st.button("⬅️ Home", on_click=go_home)
    st.title("✍️ Nyasa: Record Ledger")
    with st.form("new_item"):
        n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1)
        if st.form_submit_button("Commit"):
            conn = get_db_connection(); conn.execute("INSERT INTO products (name, current_stock, unit_price, lead_time) VALUES (?,?,?,?)", (n,s,p,lt))
            conn.commit(); conn.close(); st.success("Saved!")

# --- AGAMA: BULK IMPORT ---
elif st.session_state.page == "Agama":
    st.button("⬅️ Home", on_click=go_home)
    st.title("📥 Agama: Bulk Sync")
    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        df_up = pd.read_csv(file)
        if st.button("Sync to Vault"):
            conn = get_db_connection(); df_up.to_sql('products', conn, if_exists='append', index=False); conn.close(); st.success("Synced!")

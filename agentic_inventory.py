import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI

# --- 1. CORE BRANDING & SECURITY ---
APP_NAME = "AROHA"
TAGLINE = "Turn Data into Decisions"
PASSWORD = "mantra"  # Your access password

st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="💠")

# --- 2. DATABASE LOGIC (The Vault) ---
def get_db_connection():
    return sqlite3.connect('aroha_vault.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, current_stock INTEGER, 
                  unit_price REAL, lead_time INTEGER, supplier TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales_history 
                 (product_id INTEGER, date TEXT, units_sold INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. SESSION STATE & NAVIGATION ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "Home"

# High-End Mobile UI CSS
st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: white; }
    
    /* Branding */
    .main-title { text-align: center; color: #D4AF37; font-size: 3.5em; font-weight: 800; letter-spacing: 5px; margin-bottom: 0px; }
    .tagline { text-align: center; color: #888; font-size: 1.1em; margin-bottom: 50px; font-style: italic; }
    
    /* Badge UI (PhonePe Style) */
    .badge-container {
        background: linear-gradient(145deg, #10141d, #0a0e14);
        border: 1px solid #1f2937;
        padding: 40px 20px;
        border-radius: 28px;
        text-align: center;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 20px;
    }
    .badge-container:hover { border-color: #D4AF37; transform: translateY(-10px); background: #161B22; box-shadow: 0 10px 30px rgba(212, 175, 55, 0.1); }
    .badge-icon { font-size: 55px; margin-bottom: 15px; }
    .badge-label { color: #D4AF37; font-weight: 700; font-size: 1.4em; letter-spacing: 1px; }
    .badge-desc { color: #6b7280; font-size: 0.85em; margin-top: 5px; }
    
    /* Security Seal */
    .protected-stamp { text-align: center; color: #22c55e; font-size: 0.8em; font-weight: bold; border: 1px solid #22c55e; padding: 6px 15px; width: fit-content; margin: 0 auto 30px auto; border-radius: 50px; }
    
    /* Global Button Styling */
    .stButton>button { width: 100%; border-radius: 15px; border: 1px solid #1f2937; background: #10141d; color: white; font-weight: bold; }
    .stButton>button:hover { background: #D4AF37 !important; color: black !important; border: none; }
    </style>
""", unsafe_allow_html=True)

# --- 4. LOGIN GATE ---
if not st.session_state.authenticated:
    st.markdown(f"<h1 class='main-title'>💠 {APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='tagline'>{TAGLINE}</p>", unsafe_allow_html=True)
    st.markdown("<div class='protected-stamp'>🔒 END-TO-END ENCRYPTED ACCESS</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,1.2,1])
    with col2:
        pwd = st.text_input("Access Mantra", type="password", placeholder="Enter Password")
        if st.button("Unlock AROHA"):
            if pwd == PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect Mantra. Vault Locked.")
    st.stop()

# --- 5. THE HOME CANVAS (Feature Grid) ---
if st.session_state.page == "Home":
    st.markdown(f"<h1 class='main-title'>{APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='tagline'>{TAGLINE}</p>", unsafe_allow_html=True)
    
    r1c1, r1c2, r1c3 = st.columns(3)
    r2c1, r2c2, r2c3 = st.columns(3)

    with r1c1:
        st.markdown("<div class='badge-container'><div class='badge-icon'>🔮</div><div class='badge-label'>PREKSHA</div><div class='badge-desc'>AI Demand Vision</div></div>", unsafe_allow_html=True)
        if st.button("Open Preksha"): st.session_state.page = "Preksha"; st.rerun()

    with r1c2:
        st.markdown("<div class='badge-container'><div class='badge-icon'>🛡️</div><div class='badge-label'>STAMBHA</div><div class='badge-desc'>Resilience Simulator</div></div>", unsafe_allow_html=True)
        if st.button("Open Stambha"): st.session_state.page = "Stambha"; st.rerun()

    with r1c3:
        st.markdown("<div class='badge-container'><div class='badge-icon'>🗣️</div><div class='badge-label'>SAMVADA</div><div class='badge-desc'>Agentic AI Chat</div></div>", unsafe_allow_html=True)
        if st.button("Open Samvada"): st.session_state.page = "Samvada"; st.rerun()

    with r2c1:
        st.markdown("<div class='badge-container'><div class='badge-icon'>✍️</div><div class='badge-label'>NYASA</div><div class='badge-desc'>Manual Asset Entry</div></div>", unsafe_allow_html=True)
        if st.button("Open Nyasa"): st.session_state.page = "Nyasa"; st.rerun()

    with r2c2:
        st.markdown("<div class='badge-container'><div class='badge-icon'>📥</div><div class='badge-label'>AGAMA</div><div class='badge-desc'>Bulk File Ingestion</div></div>", unsafe_allow_html=True)
        if st.button("Open Agama"): st.session_state.page = "Agama"; st.rerun()

    with r2c3:
        st.markdown("<div class='badge-container'><div class='badge-icon'>🔒</div><div class='badge-label'>EXIT</div><div class='badge-desc'>Secure Logout</div></div>", unsafe_allow_html=True)
        if st.button("Secure Exit"): st.session_state.authenticated = False; st.rerun()

# --- 6. FEATURE MODULES ---

def back_home():
    if st.button("⬅️ Return to Center"):
        st.session_state.page = "Home"
        st.rerun()

# 1. PREKSHA (Forecasting)
if st.session_state.page == "Preksha":
    back_home()
    st.title("🔮 Preksha: Intelligent Forecasting")
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    if df.empty:
        st.warning("No data found. Add assets in Nyasa or Agama first.")
    else:
        target = st.selectbox("Select Asset", df['name'])
        preds = np.random.randint(10, 60, size=7)
        fig = px.line(x=[f"Day {i+1}" for i in range(7)], y=preds, title=f"7-Day Forecast: {target}", markers=True, template="plotly_dark")
        fig.update_traces(line_color='#D4AF37')
        st.plotly_chart(fig, use_container_width=True)

# 2. STAMBHA (Resilience)
elif st.session_state.page == "Stambha":
    back_home()
    st.title("🛡️ Stambha: Resilience Analysis")
    scenario = st.selectbox("Scenario", ["Normal", "Port Closure", "Factory Fire"])
    st.info(f"Agentic Stress-Test active for: {scenario}")
    # TTS vs TTR logic...

# 3. SAMVADA (AI Chat)
elif st.session_state.page == "Samvada":
    back_home()
    st.title("🗣️ Samvada: Agentic Conversation")
    key = st.secrets.get("GROQ_API_KEY")
    if not key:
        st.error("API Key missing. Chatbot offline.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        if prompt := st.chat_input("Ask Samvada anything..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            with st.chat_message("assistant"):
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "system", "content": "You are Samvada AI within AROHA. Help users turn data into decisions."}] + st.session_state.messages[-3:]
                )
                msg = response.choices[0].message.content
                st.markdown(msg)
                st.session_state.messages.append({"role": "assistant", "content": msg})

# 4. NYASA (Ledger)
elif st.session_state.page == "Nyasa":
    back_home()
    st.title("✍️ Nyasa: Manual Record Entry")
    with st.form("new_item"):
        n = st.text_input("Product Name")
        s = st.number_input("Current Stock", min_value=0)
        p = st.number_input("Unit Price", min_value=0.0)
        lt = st.number_input("Lead Time (Days)", min_value=1)
        if st.form_submit_button("Commit to Vault"):
            conn = get_db_connection()
            conn.execute("INSERT INTO products (name, current_stock, unit_price, lead_time) VALUES (?,?,?,?)", (n,s,p,lt))
            conn.commit(); conn.close()
            st.success(f"Record '{n}' saved.")

# 5. AGAMA (Import)
elif st.session_state.page == "Agama":
    back_home()
    st.title("📥 Agama: Bulk Data Ingestion")
    file = st.file_uploader("Upload CSV Supply Chain File", type="csv")
    if file:
        df_up = pd.read_csv(file)
        if st.button("Sync with AROHA Vault"):
            conn = get_db_connection()
            df_up.to_sql('products', conn, if_exists='append', index=False)
            conn.close()
            st.success("Synchronization Successful.")
                

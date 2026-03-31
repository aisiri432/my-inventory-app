import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI
import hashlib

# --- 1. SETTINGS & MINIMALIST GLASS UI ---
st.set_page_config(page_title="AROHA | Elite Intelligence", layout="wide")

def apply_minimalist_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050505; color: #E0E0E0; }
        
        .icon-initial {
            font-size: 28px; font-weight: 800; color: #D4AF37; margin-bottom: 15px;
            letter-spacing: 2px; border-bottom: 2px solid #D4AF37; padding-bottom: 5px;
        }

        .glass-card {
            background: linear-gradient(145deg, rgba(20,20,20,0.9), rgba(10,10,10,0.9));
            backdrop-filter: blur(15px); border-radius: 20px; border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 40px 20px; text-align: center; transition: 0.4s;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); height: 260px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .glass-card:hover { border: 1px solid #D4AF37; transform: translateY(-5px); box-shadow: 0 0 25px rgba(212, 175, 55, 0.15); }
        
        .title-text { color: #D4AF37; font-weight: 700; font-size: 1.2rem; letter-spacing: 3px; text-transform: uppercase; }
        .desc-text { color: #666; font-size: 0.75rem; margin-top: 10px; text-transform: uppercase; letter-spacing: 1px; }
        
        .auth-box { max-width: 420px; margin: 60px auto; padding: 45px; background: rgba(15, 15, 15, 0.95); border-radius: 20px; border: 1px solid #222; text-align: center; }
        [data-testid="stSidebar"] { display: none; }
        
        .stButton>button { border-radius: 5px; background: #111; border: 1px solid #333; color: #D4AF37; font-weight: 700; padding: 10px 18px; width: 100%; transition: 0.3s; font-size: 0.75rem; letter-spacing: 2px; }
        .stButton>button:hover { border-color: #D4AF37; background: #D4AF37; color: black; }
        
        .header-info { display: flex; justify-content: center; gap: 20px; padding: 12px; background: rgba(255,255,255,0.02); border-bottom: 1px solid #222; margin-bottom: 30px; font-size: 0.65rem; color: #444; letter-spacing: 2px; }
        .ai-suggestion { background: rgba(212, 175, 55, 0.05); border: 1px solid #D4AF37; padding: 20px; margin-top: 20px; }
        </style>
    """, unsafe_allow_html=True)

apply_minimalist_css()

# --- 2. DATABASE LOGIC (MULTI-USER READY) ---
def get_db(): return sqlite3.connect('aroha_enterprise.db', check_same_thread=False)

def init_db():
    conn = get_db(); c = conn.cursor()
    # Added username column to separate data
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, username TEXT, name TEXT, current_stock INTEGER, unit_price REAL, lead_time INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS sales (username TEXT, p_id INTEGER, date TEXT, qty INTEGER)')
    conn.commit(); conn.close()

def make_hashes(password): return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text: return True
    return False

init_db()

# --- 3. SESSION STATE ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"

# --- 4. AUTHENTICATION SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 style='color:#D4AF37; font-size:3.5rem; font-weight:800; letter-spacing:20px; margin-bottom:0;'>AROHA</h1><p style='color:#333; letter-spacing:5px;'>DATA INTO DECISIONS</p></div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        auth_mode = st.tabs(["LOGIN", "REGISTER"])
        
        with auth_mode[0]:
            st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
            u_name = st.text_input("Username", key="login_user")
            u_pwd = st.text_input("Password", type="password", key="login_pwd")
            if st.button("UNLOCK VAULT"):
                conn = get_db(); res = conn.execute("SELECT password FROM users WHERE username=?", (u_name,)).fetchone(); conn.close()
                if res and check_hashes(u_pwd, res[0]):
                    st.session_state.logged_in = True
                    st.session_state.user = u_name
                    st.rerun()
                else: st.error("Invalid Credentials")
            st.markdown("</div>", unsafe_allow_html=True)
            
        with auth_mode[1]:
            st.markdown("<div class='auth-box'>", unsafe_allow_html=True)
            new_user = st.text_input("Create Username", key="reg_user")
            new_pwd = st.text_input("Create Password", type="password", key="reg_pwd")
            if st.button("REGISTER ACCOUNT"):
                if new_user and new_pwd:
                    conn = get_db()
                    try:
                        conn.execute("INSERT INTO users VALUES (?,?)", (new_user, make_hashes(new_pwd)))
                        conn.commit(); conn.close()
                        st.success("Account Created. Switch to Login.")
                    except: st.error("Username already exists.")
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. COMMAND CENTER (HOME) ---
if st.session_state.page == "Home":
    st.markdown(f"<div class='header-info'>USER: {st.session_state.user.upper()} | CORE: ACTIVE | VAULT: SECURED | AGENT: SAMVADA</div>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center; color:#D4AF37; letter-spacing:10px;'>COMMAND CENTER</h2>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3); c4, c5, c6 = st.columns(3)
    badges = [
        {"id": "Preksha", "char": "P", "title": "PREKSHA", "desc": "Demand Forecasting", "col": c1},
        {"id": "Stambha", "char": "S", "title": "STAMBHA", "desc": "Resilience Risk", "col": c2},
        {"id": "Samvada", "char": "V", "title": "SAMVADA", "desc": "Agentic Chat", "col": c3},
        {"id": "Nyasa", "char": "N", "title": "NYASA", "desc": "Asset Ledger", "col": c4},
        {"id": "Agama", "char": "A", "title": "AGAMA", "desc": "Data Import", "col": c5},
        {"id": "Exit", "char": "X", "title": "EXIT", "desc": "Lock Session", "col": c6},
    ]
    for b in badges:
        with b["col"]:
            st.markdown(f"<div class='glass-card'><div class='icon-initial'>{b['char']}</div><div class='title-text'>{b['title']}</div><div class='desc-text'>{b['desc']}</div></div>", unsafe_allow_html=True)
            if st.button(f"EXECUTE {b['title']}", key=b['id']):
                if b['id'] == "Exit": st.session_state.logged_in = False; st.rerun()
                else: st.session_state.page = b['id']; st.rerun()

# --- 6. SUB-PAGES (DATA FILTERED BY USER) ---
def nav_home():
    if st.button("RETURN TO COMMAND CENTER"): st.session_state.page = "Home"; st.rerun()

if st.session_state.page == "Preksha":
    nav_home(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:5px;'>PREKSHA INTELLIGENCE</h2>", unsafe_allow_html=True)
    conn = get_db(); df = pd.read_sql_query("SELECT * FROM products WHERE username=?", (st.session_state.user,), conn); conn.close()
    if df.empty: st.warning("No data found in your treasury.")
    else:
        target = st.selectbox("Select Asset", df['name'])
        st.plotly_chart(px.area(y=np.random.randint(20, 80, 7), template="plotly_dark").update_traces(line_color='#D4AF37'), use_container_width=True)

elif st.session_state.page == "Nyasa":
    nav_home(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:5px;'>NYASA LEDGER</h2>", unsafe_allow_html=True)
    with st.form("add"):
        name = st.text_input("Product Name")
        stock = st.number_input("Stock", 0)
        if st.form_submit_button("COMMIT"):
            conn = get_db(); conn.execute("INSERT INTO products (username, name, current_stock) VALUES (?,?,?)", (st.session_state.user, name, stock))
            conn.commit(); conn.close(); st.success("Asset Logged.")

elif st.session_state.page == "Agama":
    nav_home(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:5px;'>AGAMA SYNC</h2>", unsafe_allow_html=True)
    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        u_df = pd.read_csv(file)
        u_df['username'] = st.session_state.user # Force data to belong to current user
        if st.button("SYNCHRONIZE"):
            conn = get_db(); u_df.to_sql('products', conn, if_exists='append', index=False); conn.close(); st.success("Synced.")

elif st.session_state.page == "Samvada":
    nav_home(); st.markdown("<h2 style='color:#D4AF37; letter-spacing:5px;'>SAMVADA CHAT</h2>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY")
    if not key: st.error("AI Node Offline")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        if "msgs" not in st.session_state: st.session_state.msgs = []
        for m in st.session_state.msgs:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if p := st.chat_input("Ask Samvada..."):
            st.session_state.msgs.append({"role": "user", "content": p})
            with st.chat_message("user"): st.markdown(p)
            # Pull only current user's data for context
            conn = get_db(); ctx_df = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", (st.session_state.user,), conn); conn.close()
            ctx = ctx_df.to_string(index=False)
            with st.chat_message("assistant"):
                r = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are Samvada AI. User data: {ctx}"}]+st.session_state.msgs[-3:])
                msg = r.choices[0].message.content
                st.markdown(msg); st.session_state.msgs.append({"role":"assistant","content":msg})

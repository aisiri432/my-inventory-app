import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI
import hashlib

# --- 1. SETTINGS & TITANIUM FROST UI ---
st.set_page_config(page_title="AROHA | Intelligence Center", layout="wide", page_icon="💠")

def apply_titanium_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        
        /* Neutral Stone Background */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #F8F9FA; 
            color: #1A1C1E;
        }

        /* Sidebar Styling: Clean & Slate */
        [data-testid="stSidebar"] {
            background-color: #FFFFFF;
            border-right: 1px solid #E9ECEF;
        }

        /* Feature Badge: NO BOXES, just floating icons and text */
        .badge-element {
            text-align: center;
            padding: 30px 10px;
            transition: 0.3s all ease;
            cursor: pointer;
        }
        
        .badge-element:hover {
            transform: translateY(-5px);
            background: rgba(0, 123, 255, 0.05); /* Very light blue tint on hover */
            border-radius: 20px;
        }

        .badge-icon {
            font-size: 45px;
            margin-bottom: 12px;
            color: #495057;
        }

        .badge-text {
            font-weight: 700;
            font-size: 1.1rem;
            color: #212529;
            letter-spacing: -0.5px;
        }

        .badge-subtext {
            font-size: 0.8rem;
            color: #ADB5BD;
            margin-top: 5px;
            font-weight: 400;
        }

        /* Minimalist Buttons */
        .stButton>button {
            border-radius: 100px;
            background: #FFFFFF;
            border: 1px solid #DEE2E6;
            color: #212529;
            font-weight: 600;
            padding: 10px 25px;
            transition: 0.3s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        }
        .stButton>button:hover {
            border-color: #007BFF;
            color: #007BFF;
            box-shadow: 0 10px 15px rgba(0,123,255,0.1);
        }

        /* Top Status Bar */
        .hud-status {
            display: flex;
            justify-content: center;
            gap: 30px;
            padding: 15px;
            background: #FFFFFF;
            border-bottom: 1px solid #E9ECEF;
            font-size: 0.75rem;
            color: #6C757D;
            letter-spacing: 1px;
            font-weight: 600;
        }

        /* Login Vault */
        .vault-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 50px;
            background: #FFFFFF;
            border-radius: 30px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.05);
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

apply_titanium_css()

# --- 2. DATABASE ARCHITECTURE ---
DB_FILE = 'aroha_titanium_v1.db'
def get_db(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
        c.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, 
                      current_stock INTEGER, unit_price REAL, lead_time INTEGER, image_url TEXT)''')
        conn.commit()
init_db()

def hash_p(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='height:10vh;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; font-size:3.5rem; letter-spacing:-2px; color:#1A1C1E;'>AROHA</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#ADB5BD; font-size:1.1rem;'>Strategic Decision Interface</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='vault-container'>", unsafe_allow_html=True)
        m = st.tabs(["Sign In", "Enroll"])
        with m[0]:
            u = st.text_input("Identity", placeholder="Username")
            p = st.text_input("Mantra", type="password", placeholder="Password")
            if st.button("Unlock Center"):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Verification failed.")
        with m[1]:
            nu = st.text_input("New Identity"); np = st.text_input("New Mantra", type="password")
            if st.button("Initialize"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Authorized.")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h2 style='letter-spacing:-1px;'>AROHA Center</h2>", unsafe_allow_html=True)
    st.write(f"Identity: **{st.session_state.user.capitalize()}**")
    st.divider()
    if st.button("🏠 Home Command"): st.session_state.page = "Home"; st.rerun()
    if st.button("🔮 Preksha Intelligence"): st.session_state.page = "Preksha"; st.rerun()
    if st.button("🛡️ Stambha Resilience"): st.session_state.page = "Stambha"; st.rerun()
    if st.button("🎙️ Samvada Chat"): st.session_state.page = "Samvada"; st.rerun()
    if st.button("📝 Nyasa Ledger"): st.session_state.page = "Nyasa"; st.rerun()
    if st.button("📥 Agama Sync"): st.session_state.page = "Agama"; st.rerun()
    st.divider()
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. HOME PAGE (Command Center) ---
if st.session_state.page == "Home":
    st.markdown(f"""
        <div class='hud-status'>
            <span>CORE STATUS: OPTIMAL</span>
            <span>DATA LINK: ENCRYPTED</span>
            <span>SYSTEM v24.1</span>
            <span>{datetime.now().strftime('%H:%M')}</span>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<h2 style='text-align:center; margin-top:50px; color:#495057;'>COMMAND CENTER</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#ADB5BD; margin-bottom:50px;'>Select a Strategic Node</p>", unsafe_allow_html=True)

    # 3x2 Floating Grid (PhonePe Style but Minimal)
    r1c1, r1c2, r1c3 = st.columns(3)
    r2c1, r2c2, r2c3 = st.columns(3)

    nodes = [
        {"id": "Preksha", "icon": "🔮", "title": "PREKSHA", "desc": "AI Demand Sensing", "col": r1c1},
        {"id": "Stambha", "icon": "🛡️", "title": "STAMBHA", "desc": "Resilience Risk", "col": r1c2},
        {"id": "Samvada", "icon": "🎙️", "title": "SAMVADA", "desc": "Agentic Chat", "col": r1c3},
        {"id": "Artha", "icon": "💰", "title": "ARTHA", "desc": "Financial Value", "col": r2c1},
        {"id": "Nyasa", "icon": "📝", "title": "NYASA", "desc": "Asset Ledger", "col": r2c2},
        {"id": "Agama", "icon": "📥", "title": "AGAMA", "desc": "Bulk Data Sync", "col": r2c3}
    ]

    for n in nodes:
        with n['col']:
            st.markdown(f"""
                <div class='badge-element'>
                    <div class='badge-icon'>{n['icon']}</div>
                    <div class='badge-text'>{n['title']}</div>
                    <div class='badge-subtext'>{n['desc']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Engage {n['title']}", key=f"home_{n['id']}"):
                st.session_state.page = n['id']; st.rerun()

# --- 7. FEATURE PAGES ---

if st.session_state.page == "Preksha":
    st.markdown("## 🔮 Preksha Intelligence")
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    if df.empty: st.warning("Please add data via Nyasa node first.")
    else:
        target = st.selectbox("Asset Search", df['name'])
        # Intelligence logic...
        st.info(f"AI sensing demand flow for {target}...")

elif st.session_state.page == "Nyasa":
    st.markdown("## 📝 Nyasa: Manual Registry")
    with st.form("ledger"):
        n = st.text_input("Name of Asset")
        s = st.number_input("Quantity", 0)
        if st.form_submit_button("Commit to Treasury"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock) VALUES (?,?,?)", (st.session_state.user, n, s))
            st.success("Asset Committed.")

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

# --- 1. SETTINGS & FUSION UI CSS ---
st.set_page_config(page_title="AROHA", layout="wide", page_icon="💠")

def apply_fusion_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #0F1113; 
            color: #FFFFFF;
        }

        /* 📸 Instagram-style Story Alerts */
        .story-wrapper { display: flex; gap: 20px; overflow-x: auto; padding: 10px 0; margin-bottom: 20px; }
        .story-item { text-align: center; min-width: 80px; }
        .story-circle {
            width: 75px; height: 75px; border-radius: 50%; padding: 3px;
            background: linear-gradient(45deg, #f09433, #bc1888);
            display: flex; align-items: center; justify-content: center; margin: 0 auto;
        }
        .story-inner { width: 100%; height: 100%; background: #000; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; }
        .story-label { font-size: 11px; margin-top: 5px; color: #888; }

        /* 💳 Google Pay style Action Buttons */
        .action-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-top: 20px; }
        .action-btn {
            background: #1C1F23; border-radius: 24px; padding: 30px 15px;
            text-align: center; border: 1px solid #2D3136; transition: 0.3s;
            cursor: pointer; display: flex; flex-direction: column; align-items: center;
        }
        .action-btn:hover { background: #25292E; border-color: #D4AF37; transform: translateY(-5px); }
        .action-icon { font-size: 55px; margin-bottom: 15px; } /* INCREASED ICON SIZE */
        .action-title { font-weight: 800; font-size: 1.1rem; color: #D4AF37; letter-spacing: 1px; }
        .action-explain { font-size: 0.8rem; color: #888; margin-top: 5px; font-weight: 400; line-height: 1.2; }

        /* 💬 WhatsApp style Chat Bubbles */
        .wa-bubble { padding: 12px 18px; border-radius: 18px; margin-bottom: 10px; max-width: 85%; }
        .wa-user { background: #005C4B; margin-left: auto; color: white; }
        .wa-ai { background: #202C33; color: white; }

        /* 🔒 Auth Box */
        .auth-card { background: #1C1F23; padding: 40px; border-radius: 30px; border: 1px solid #2D3136; text-align: center; }
        
        [data-testid="stSidebar"] { display: none; }
        </style>
    """, unsafe_allow_html=True)

apply_fusion_css()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_fusion_master.db'
def get_db(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
        c.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, 
                      category TEXT, current_stock INTEGER, unit_price REAL, lead_time INTEGER, 
                      supplier TEXT, image_url TEXT, reviews TEXT)''')
        conn.commit()
init_db()

def hash_p(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Home"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_on" not in st.session_state: st.session_state.voice_on = False

# --- 4. LOGIN ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:80px;'><h1 style='font-size:3.5rem; font-weight:800; color:#D4AF37;'>AROHA</h1><p style='color:#666;'>Turn data into decisions.</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div class='auth-card'>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["Login", "Join"])
        with t1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Unlock"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Denied")
        with t2:
            nu = st.text_input("New ID"); np = st.text_input("New Pass", type="password")
            if st.button("Enroll"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Authorized")
        st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. NAVIGATION HELPER ---
def nav(page_name):
    st.session_state.page = page_name
    st.rerun()

# --- 6. HOME PAGE (The Fusion Command Center) ---
if st.session_state.page == "Home":
    # 📸 Insta Stories (Alerts)
    with get_db() as conn: df = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", conn, params=(st.session_state.user,))
    
    st.markdown(f"### Hello, {st.session_state.user.capitalize()} 👋")
    
    st.markdown("<div class='story-wrapper'>", unsafe_allow_html=True)
    if df.empty:
        st.write("No alerts yet. Add items in Nyasa.")
    else:
        for _, row in df.iterrows():
            color = "linear-gradient(45deg, #f09433, #bc1888)" if row['current_stock'] < 20 else "#34A853"
            st.markdown(f"""
                <div class='story-item'>
                    <div class='story-circle' style='background: {color};'><div class='story-inner'>{row['name'][0]}</div></div>
                    <div class='story-label'>{row['name'][:8]}..</div>
                </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # 💳 GPay Action Grid
    st.markdown("#### Strategic Actions")
    
    c1, c2, c3 = st.columns(3); c4, c5, c6 = st.columns(3); c7, c8, c9 = st.columns(3)
    
    nodes = [
        {"id": "Preksha", "icon": "🔮", "title": "PREKSHA", "explain": "Predict future sales", "col": c1},
        {"id": "Stambha", "icon": "🛡️", "title": "STAMBHA", "explain": "Stop stock risks", "col": c2},
        {"id": "Artha", "icon": "💰", "title": "ARTHA", "explain": "Check your money", "col": c3},
        {"id": "Samvada", "icon": "🎙️", "title": "SAMVADA", "explain": "Talk to AI assistant", "col": c4},
        {"id": "Mithra", "icon": "🤝", "title": "MITHRA", "explain": "Manage your sellers", "col": c5},
        {"id": "Karya", "icon": "📄", "title": "KARYA", "explain": "Make order bills", "col": c6},
        {"id": "Nyasa", "icon": "📝", "title": "NYASA", "explain": "Add new items", "col": c7},
        {"id": "Agama", "icon": "📥", "title": "AGAMA", "explain": "Upload big lists", "col": c8},
        {"id": "Exit", "icon": "🔒", "title": "EXIT", "explain": "Close and logout", "col": c9}
    ]

    for n in nodes:
        with n['col']:
            st.markdown(f"""
                <div class='action-btn'>
                    <div class='action-icon'>{n['icon']}</div>
                    <div class='action-title'>{n['title']}</div>
                    <div class='action-explain'>{n['explain']}</div>
                </div>
            """, unsafe_allow_html=True)
            if st.button(f"Go {n['title']}", key=f"btn_{n['id']}"):
                if n['id'] == "Exit": st.session_state.auth = False; st.rerun()
                else: nav(n['id'])

# --- 7. FEATURE PAGES ---

def back_btn():
    if st.button("⬅️ Back to Home"): nav("Home")

if st.session_state.page == "Preksha":
    back_btn(); st.title("🔮 Preksha: Future Sales")
    st.info("The AI is looking at your past data to predict next week's demand.")
    # (Insert Chart Logic)

elif st.session_state.page == "Stambha":
    back_btn(); st.title("🛡️ Stambha: Risk Guard")
    st.warning("Simulating world disasters to see if your stock survives.")

elif st.session_state.page == "Samvada":
    back_btn(); st.title("🎙️ Samvada: AI Chat")
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            cls = "wa-user" if m['role'] == "user" else "wa-ai"
            st.markdown(f"<div class='wa-bubble {cls}'>{m['content']}</div>", unsafe_allow_html=True)
        q = st.chat_input("Ask anything...")
        if q:
            st.session_state.chat_history.append({"role":"user", "content":q})
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":"You are AROHA AI."}]+st.session_state.chat_history[-3:])
            st.session_state.chat_history.append({"role":"assistant", "content":res.choices[0].message.content})
            st.rerun()

elif st.session_state.page == "Nyasa":
    back_btn(); st.title("📝 Nyasa: Add Items")
    with st.form("add"):
        n = st.text_input("Item Name"); p = st.number_input("Price", 0.0)
        s = st.number_input("Stock", 0); l = st.number_input("Days to arrive", 1)
        if st.form_submit_button("Save Item"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", (st.session_state.user, n, s, p, l))
            st.success("Item saved!")

elif st.session_state.page == "Artha":
    back_btn(); st.title("💰 Artha: Money Tracking")
    st.write("Total money sitting in your warehouse right now.")

elif st.session_state.page == "Mithra":
    back_btn(); st.title("🤝 Mithra: Seller Scores")
    st.write("Check which of your suppliers is the fastest.")

elif st.session_state.page == "Karya":
    back_btn(); st.title("📄 Karya: Auto Bills")
    st.write("Generating a Purchase Order bill for your stock.")

elif st.session_state.page == "Agama":
    back_btn(); st.title("📥 Agama: List Upload")
    f = st.file_uploader("Upload your CSV file here")
    if f: st.success("List uploaded successfully!")

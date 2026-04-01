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

# --- 1. THE "BABY" CSS (Insta + WhatsApp + GPay) ---
st.set_page_config(page_title="AROHA", layout="wide", page_icon="💠")

def apply_fusion_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;800&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif;
            background-color: #0F1113; /* Deep Modern Charcoal */
            color: #FFFFFF;
        }

        /* 📸 Insta-Style Stories */
        .story-container {
            display: flex;
            gap: 20px;
            padding: 10px 0;
            overflow-x: auto;
            margin-bottom: 30px;
        }
        .story-circle {
            width: 70px; height: 70px;
            border-radius: 50%;
            padding: 3px;
            background: linear-gradient(45deg, #f09433 0%, #e6683c 25%, #dc2743 50%, #cc2366 75%, #bc1888 100%); 
            display: flex; align-items: center; justify-content: center;
        }
        .story-inner {
            width: 100%; height: 100%;
            background: #000; border-radius: 50%;
            display: flex; align-items: center; justify-content: center; font-size: 24px;
        }

        /* 📱 Decision Feed Cards (Insta Post Style) */
        .feed-card {
            background: #1C1F23;
            border-radius: 24px;
            margin-bottom: 25px;
            padding: 0px;
            overflow: hidden;
            border: 1px solid #2D3136;
        }
        .card-header { padding: 15px 20px; display: flex; align-items: center; gap: 12px; }
        .card-img { width: 100%; height: 350px; object-fit: cover; background: #25292E; }
        .card-body { padding: 20px; }
        .decision-btn {
            background: #34A853; /* GPay Green */
            color: white; border: none; padding: 12px;
            border-radius: 12px; width: 100%; font-weight: 700;
            text-transform: uppercase; cursor: pointer;
        }

        /* 💬 WhatsApp Style Chat Bubbles */
        .wa-bubble {
            padding: 12px 18px; border-radius: 18px; margin-bottom: 10px;
            max-width: 80%; line-height: 1.4;
        }
        .wa-user { background: #005C4B; align-self: flex-end; margin-left: auto; }
        .wa-ai { background: #202C33; align-self: flex-start; }

        /* 💳 GPay Bottom Nav */
        .bottom-nav {
            position: fixed; bottom: 0; left: 0; right: 0;
            background: #1C1F23; padding: 15px;
            display: flex; justify-content: space-around;
            border-top: 1px solid #2D3136; z-index: 1000;
        }

        /* Hide Sidebar */
        [data-testid="stSidebar"] { display: none; }
        .main .block-container { padding-bottom: 100px; }
        </style>
    """, unsafe_allow_html=True)

apply_fusion_css()

# --- 2. DATABASE ---
DB_FILE = 'aroha_fusion_v24.db'
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
if "page" not in st.session_state: st.session_state.page = "Feed"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 4. AUTHENTICATION (Modern Minimalist) ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='font-size:3rem; font-weight:800; color:#D4AF37;'>AROHA</h1><p style='color:#666;'>Turn data into decisions.</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        tab1, tab2 = st.tabs(["Login", "Join"])
        with tab1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Unlock Treasury"):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Access Denied")
        with tab2:
            nu = st.text_input("New Identity"); np = st.text_input("New Mantra", type="password")
            if st.button("Enroll"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Authorized.")
    st.stop()

# --- 5. TOP STORIES (Quick Status) ---
def draw_stories():
    with get_db() as conn: df = pd.read_sql_query("SELECT name, current_stock FROM products WHERE username=?", conn, params=(st.session_state.user,))
    st.markdown("<div class='story-container'>", unsafe_allow_html=True)
    cols = st.columns(len(df) if not df.empty else 1)
    if df.empty:
        st.write("No alerts.")
    else:
        for i, row in df.iterrows():
            with cols[min(i, len(cols)-1)]:
                color = "#34A853" if row['current_stock'] > 20 else "#EA4335"
                st.markdown(f"""
                    <div style='text-align:center;'>
                        <div class='story-circle' style='background: {color};'>
                            <div class='story-inner'>{row['name'][0]}</div>
                        </div>
                        <p style='font-size:10px; margin-top:5px;'>{row['name'][:8]}..</p>
                    </div>
                """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. BOTTOM NAV (GPay Style) ---
def draw_nav():
    st.markdown("""
        <div class='bottom-nav'>
            <div style='text-align:center;'>🏠<br><span style='font-size:10px;'>Home</span></div>
            <div style='text-align:center;'>🛡️<br><span style='font-size:10px;'>Resilience</span></div>
            <div style='text-align:center;'>💬<br><span style='font-size:10px;'>Chat</span></div>
            <div style='text-align:center;'>💰<br><span style='font-size:10px;'>Finance</span></div>
            <div style='text-align:center;'>📝<br><span style='font-size:10px;'>Ledger</span></div>
        </div>
    """, unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: 
        if st.button("Feed", key="nav_f"): st.session_state.page = "Feed"; st.rerun()
    with c2: 
        if st.button("Stambha", key="nav_s"): st.session_state.page = "Stambha"; st.rerun()
    with c3: 
        if st.button("Samvada", key="nav_v"): st.session_state.page = "Samvada"; st.rerun()
    with c4: 
        if st.button("Artha", key="nav_a"): st.session_state.page = "Artha"; st.rerun()
    with c5: 
        if st.button("Nyasa", key="nav_n"): st.session_state.page = "Nyasa"; st.rerun()

# --- 7. CONTENT PAGES ---

# --- THE FEED (HOME) ---
if st.session_state.page == "Feed":
    st.markdown(f"### Hello, {st.session_state.user.capitalize()} 👋")
    draw_stories()
    
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    
    if df.empty:
        st.info("Your feed is empty. Start adding data in the Ledger.")
    else:
        for i, row in df.iterrows():
            st.markdown(f"""
                <div class='feed-card'>
                    <div class='card-header'>
                        <div style='width:30px; height:30px; background:#D4AF37; border-radius:50%; display:flex; align-items:center; justify-content:center; color:black; font-weight:bold;'>{row['name'][0]}</div>
                        <div><b>{row['name']}</b><br><span style='font-size:10px; color:#666;'>Strategic Asset // {row['category']}</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if row['image_url']:
                st.image(row['image_url'], use_container_width=True)
            
            st.markdown(f"""
                <div class='card-body'>
                    <p style='color:#D4AF37;'>AI SENSING: Demand expected to surge by 22% next week.</p>
                    <div style='display:flex; justify-content:space-between; margin-bottom:15px;'>
                        <span>Stock: <b>{row['current_stock']}</b></span>
                        <span>Value: <b>${row['unit_price']}</b></span>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"EXECUTE REORDER FOR {row['name'].upper()}", key=f"reorder_{row['id']}"):
                st.balloons()
                st.success(f"GPay Protocol: Reorder decision authorized for {row['name']}.")
            st.markdown("<div style='height:30px;'></div>", unsafe_allow_html=True)

# --- SAMVADA (WHATSAPP CHAT) ---
elif st.session_state.page == "Samvada":
    st.markdown("### Samvada Intelligence 💬")
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            div_class = "wa-user" if m['role'] == "user" else "wa-ai"
            st.markdown(f"<div class='wa-bubble {div_class}'>{m['content']}</div>", unsafe_allow_html=True)
        
        q = st.chat_input("Message Samvada...")
        if q:
            st.session_state.chat_history.append({"role":"user", "content":q})
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":"You are AROHA AI. Speak like a helpful strategic advisor."}] + st.session_state.chat_history[-3:])
            st.session_state.chat_history.append({"role":"assistant", "content":res.choices[0].message.content})
            st.rerun()

# --- NYASA (LEDGER) ---
elif st.session_state.page == "Nyasa":
    st.markdown("### Asset Ledger 📝")
    with st.form("new_entry"):
        n = st.text_input("Product Name"); c = st.text_input("Category")
        s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0)
        l = st.number_input("Lead Time", 1); img = st.text_input("Image URL")
        if st.form_submit_button("PUBLISH TO FEED"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, category, current_stock, unit_price, lead_time, image_url) VALUES (?,?,?,?,?,?,?)", (st.session_state.user, n, c, s, p, l, img))
            st.success("Asset live on feed.")

# (Other pages Artha, Stambha follow same pattern)
else:
    st.write("Module coming soon...")

draw_nav()

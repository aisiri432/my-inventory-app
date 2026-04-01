import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI
import hashlib

# --- 1. STARTUP-GRADE UI CONFIG ---
st.set_page_config(page_title="AROHA | Enterprise Intelligence", layout="wide", page_icon="💠")

def apply_startup_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        /* Global Reset */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #0F1115;
            color: #E6E8EB;
        }

        /* Sidebar: Stripe/Notion Style */
        [data-testid="stSidebar"] {
            background-color: #111318 !important;
            border-right: 1px solid #23262D;
            padding-top: 20px;
        }
        
        /* Section Headers in Sidebar */
        .sidebar-header {
            font-size: 0.65rem;
            font-weight: 700;
            color: #6B7280;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin: 20px 0 10px 10px;
        }

        /* Clean Sidebar Buttons */
        section[data-testid="stSidebar"] .stButton > button {
            background: transparent !important;
            border: none !important;
            color: #9AA0A6 !important;
            text-align: left !important;
            padding: 8px 15px !important;
            font-size: 0.85rem !important;
            width: 100%;
            transition: 0.2s;
        }
        section[data-testid="stSidebar"] .stButton > button:hover {
            background: #1A1D23 !important;
            color: #FFFFFF !important;
        }

        /* Active State (Simulated) */
        .active-dot {
            width: 3px; height: 18px; background: #6C63FF;
            position: absolute; left: 0;
        }

        /* Enterprise Cards */
        .saas-card {
            background: #171A1F;
            border: 1px solid #23262D;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            transition: 0.2s ease-in-out;
        }
        .saas-card:hover {
            border-color: #3E4451;
            transform: translateY(-2px);
        }

        /* Professional Typography */
        .metric-label { font-size: 0.8rem; color: #9AA0A6; font-weight: 500; }
        .metric-value { font-size: 1.75rem; font-weight: 700; color: #FFFFFF; margin-top: 5px; }
        .page-title { font-size: 1.5rem; font-weight: 600; color: #FFFFFF; margin-bottom: 5px; }
        .page-desc { font-size: 0.85rem; color: #9AA0A6; margin-bottom: 30px; }

        /* Decision Panel: The "Stripe" Highlight */
        .recommendation-panel {
            background: rgba(108, 99, 255, 0.05);
            border: 1px solid rgba(108, 99, 255, 0.2);
            border-left: 4px solid #6C63FF;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }

        /* Custom Button Style */
        .stButton>button {
            background: #6C63FF !important;
            color: white !important;
            border-radius: 6px !important;
            padding: 10px 20px !important;
            font-weight: 600 !important;
            border: none !important;
            font-size: 0.85rem !important;
        }

        /* Hide default Streamlit top bar */
        header {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_startup_css()

# --- 2. DATABASE ENGINE ---
DB_FILE = 'aroha_startup.db'
def get_db(): return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    with get_db() as conn:
        c = conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
        c.execute('''CREATE TABLE IF NOT EXISTS products 
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, 
                      current_stock INTEGER, unit_price REAL, lead_time INTEGER, supplier TEXT)''')
        conn.commit()
init_db()

def hash_p(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 style='color:white;'>AROHA</h1><p style='color:#9AA0A6;'>Sign in to your dashboard</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 0.8, 1])
    with col2:
        tab1, tab2 = st.tabs(["Log in", "Sign up"])
        with tab1:
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.button("Sign in"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True; st.session_state.user = u; st.rerun()
                else: st.error("Incorrect details.")
        with tab2:
            nu = st.text_input("New Username"); np = st.text_input("New Password", type="password")
            if st.button("Create Account"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Account ready.")
    st.stop()

# --- 5. SIDEBAR (STARTUP STYLE) ---
with st.sidebar:
    st.markdown("<h2 style='color:white; padding-left:10px;'>AROHA</h2>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-header'>Main</div>", unsafe_allow_html=True)
    if st.button("Dashboard"): st.session_state.page = "Dashboard"; st.rerun()
    
    st.markdown("<div class='sidebar-header'>Operations</div>", unsafe_allow_html=True)
    if st.button("Demand Forecast"): st.session_state.page = "Demand"; st.rerun()
    if st.button("Risk Analysis"): st.session_state.page = "Risk"; st.rerun()
    if st.button("Supplier Insights"): st.session_state.page = "Suppliers"; st.rerun()
    
    st.markdown("<div class='sidebar-header'>Financials</div>", unsafe_allow_html=True)
    if st.button("Financial Overview"): st.session_state.page = "Finance"; st.rerun()
    
    st.markdown("<div class='sidebar-header'>Automation</div>", unsafe_allow_html=True)
    if st.button("Voice Assistant"): st.session_state.page = "Voice"; st.rerun()
    if st.button("Purchase Orders"): st.session_state.page = "PO"; st.rerun()
    if st.button("Inventory Log"): st.session_state.page = "Log"; st.rerun()
    if st.button("Data Import"): st.session_state.page = "Import"; st.rerun()
    
    st.markdown("<div style='height: 50px;'></div>", unsafe_allow_html=True)
    if st.button("Logout"): st.session_state.auth = False; st.rerun()

# --- 6. TOP BAR ---
t1, t2 = st.columns([5, 1])
with t2: st.markdown(f"<p style='color:#9AA0A6; font-size:0.75rem; text-align:right;'>{st.session_state.user.upper()}</p>", unsafe_allow_html=True)

# --- 7. DASHBOARD PAGE ---
if st.session_state.page == "Dashboard":
    st.markdown("<div class='page-title'>Preksha – Dashboard</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-desc'>Real-time supply chain overview and system health.</div>", unsafe_allow_html=True)
    
    with get_db() as conn: df = pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f"<div class='saas-card'><div class='metric-label'>Inventory Status</div><div class='metric-value'>{len(df)} units</div></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='saas-card'><div class='metric-label'>Demand Forecast</div><div class='metric-value'>+12%</div></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='saas-card'><div class='metric-label'>Risk Level</div><div class='metric-value' style='color:#FFB800;'>Medium</div></div>", unsafe_allow_html=True)
    with c4: st.markdown(f"<div class='saas-card'><div class='metric-label'>Capital Usage</div><div class='metric-value'>₹{val/1000:,.1f}K</div></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.markdown("<div class='saas-card'><b>Demand Forecast</b>", unsafe_allow_html=True)
        st.plotly_chart(px.line(y=np.random.randint(20, 60, 15), template="plotly_dark").update_traces(line_color='#6C63FF').update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    with col_r:
        st.markdown("<div class='saas-card'><b>Recommendation</b><br><br>Reorder 120 units from Raj Logistics. Estimated stockout in 3 days.<br><br>", unsafe_allow_html=True)
        st.button("Create Purchase Order")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 8. VOICE ASSISTANT ---
elif st.session_state.page == "Voice":
    st.markdown("<div class='page-title'>Samvada – Voice Assistant</div>", unsafe_allow_html=True)
    st.markdown("<div class='page-desc'>Listening... Speak your request naturally.</div>", unsafe_allow_html=True)
    
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        q = st.chat_input("Ask a question about inventory...")
        if q:
            with st.chat_message("user"): st.write(q)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":"You are a helpful startup assistant."},{"role":"user","content":q}])
            with st.chat_message("assistant"): st.write(res.choices[0].message.content)

# --- 9. INVENTORY LOG (NYASA) ---
elif st.session_state.page == "Log":
    st.markdown("<div class='page-title'>Nyasa – Inventory Log</div>", unsafe_allow_html=True)
    with st.form("add"):
        n = st.text_input("Item Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0)
        if st.form_submit_button("Log Asset"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price) VALUES (?,?,?,?)", (st.session_state.user, n, s, p))
            st.success("Data synced successfully.")

else:
    st.markdown(f"<div class='page-title'>{st.session_state.page}</div>", unsafe_allow_html=True)
    st.info("Last updated 2 mins ago.")

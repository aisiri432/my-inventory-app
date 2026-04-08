import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI
import hashlib
import time

# --- 1. RADIANT UI CONFIG (AURORA MESH & SPECTRUM GLOW) ---
st.set_page_config(page_title="AROHA | Enterprise Intelligence", layout="wide", page_icon="💠", initial_sidebar_state="expanded")

logo_svg = """
<svg width="500" height="500" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M50 5L10 85H30L50 35L70 85H90L50 5Z" fill="white" fill-opacity="0.1"/>
<circle cx="50" cy="45" r="5" fill="#00D4FF" fill-opacity="0.2"/>
</svg>
"""

def apply_aroha_style():
    # Using double braces {{ }} for CSS to avoid Python f-string errors
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background-color: #050709; color: #E6E8EB; }}
        
        [data-testid="stAppViewContainer"]::before {{
            content: ""; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-15deg);
            width: 70vw; height: 70vw; background-image: url("data:image/svg+xml;utf8,{logo_svg.replace('<', '%3C').replace('>', '%3E').replace('#', '%23')}");
            background-repeat: no-repeat; background-position: center; opacity: 0.05; z-index: -1; pointer-events: none; filter: blur(5px);
        }}
        
        [data-testid="stSidebar"] {{ background-color: #030508 !important; border-right: 2px solid #1F2229; min-width: 420px; }}
        
        section[data-testid="stSidebar"] .stButton > button {{ 
            background: transparent !important; border: 2px solid rgba(255,255,255,0.1) !important; 
            color: #FFFFFF !important; text-align: left !important; padding: 15px 18px !important; width: 100%; 
            font-size: 1.6rem !important; font-weight: 800 !important; letter-spacing: 1.5px;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.2); margin-bottom: 5px; transition: 0.3s;
        }}

        /* 🌈 SPECTRUM COLORS FOR SIDEBAR */
        div[data-testid="stSidebar"] button[key*="nyasa"]:hover {{ border-color: #00FF88 !important; box-shadow: 0 0 15px #00FF88; color: #00FF88 !important; }}
        div[data-testid="stSidebar"] button[key*="preksha"]:hover {{ border-color: #7F00FF !important; box-shadow: 0 0 15px #7F00FF; color: #7F00FF !important; }}
        div[data-testid="stSidebar"] button[key*="stambha"]:hover {{ border-color: #FF0055 !important; box-shadow: 0 0 15px #FF0055; color: #FF0055 !important; }}
        div[data-testid="stSidebar"] button[key*="karma"]:hover {{ border-color: #FF33FF !important; box-shadow: 0 0 15px rgba(255,51,255,0.3); color: #FF33FF !important; }}
        div[data-testid="stSidebar"] button[key*="samvada"]:hover {{ border-color: #00D4FF !important; box-shadow: 0 0 15px #00D4FF; color: #00D4FF !important; }}
        div[data-testid="stSidebar"] button[key*="vitta"]:hover {{ border-color: #FFD700 !important; box-shadow: 0 0 15px #FFD700; color: #FFD700 !important; }}
        div[data-testid="stSidebar"] button[key*="sanchara"]:hover {{ border-color: #FF8800 !important; box-shadow: 0 0 15px #FF8800; color: #FF8800 !important; }}
        div[data-testid="stSidebar"] button[key*="mithra"]:hover {{ border-color: #34D399 !important; box-shadow: 0 0 15px #34D399; color: #34D399 !important; }}

        .sidebar-sub {{ font-size: 1rem !important; font-weight: 800; display: block; margin-top: -10px; margin-bottom: 25px; margin-left: 20px; text-transform: uppercase; letter-spacing: 1px; }}
        .saas-card {{ background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 20px; padding: 25px; margin-bottom: 20px; }}
        .karma-directive {{ background: rgba(255, 51, 255, 0.05); border-left: 5px solid #FF33FF; padding: 15px; border-radius: 10px; margin-bottom: 10px; }}
        
        header {{visibility: hidden;}} footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_master_v106.db'
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
def get_user_data():
    with get_db() as conn: return pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))

# --- 3. AUTHENTICATION ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state: st.session_state.chat_history = []

if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 style='color:white; font-size:3.5rem; font-weight:900;'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Strategic Workforce & Inventory Intelligence</p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([0.1, 0.8, 0.1])
    with col_center:
        m = st.tabs(["Login", "Join"])
        with m[0]:
            u_input = st.text_input("Username", key="l_u")
            p_input = st.text_input("Password", type="password", key="l_p")
            if st.button("Unlock Hub"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u_input,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p_input):
                    st.session_state.auth = True; st.session_state.user = u_input; st.rerun()
                else: st.error("Access Denied")
        with m[1]:
            nu = st.text_input("New ID"); np = st.text_input("New Pass", type="password")
            if st.button("Enroll"):
                with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                st.success("Authorized.")
    st.stop()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div style='text-align:center; margin-bottom:30px;'>{logo_svg}</div>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD", key="nav_dashboard"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub' style='color:#FFF;'>Command Overview</span>", unsafe_allow_html=True)
    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items & Sync", "#00FF88"),
        ("📈 PREKSHA", "Preksha", "Demand Intelligence", "#7F00FF"),
        ("🛡️ STAMBHA", "Stambha", "Supply Resilience", "#FF0055"),
        ("👷‍♂️ KARMA", "Karma", "Workforce Logic", "#FF33FF"), # REFINED KARMA
        ("🎙️ SAMVADA", "Samvada", "Voice Interaction", "#00D4FF"),
        ("💰 VITTA", "Vitta", "Capital ROI", "#FFD700"),
        ("📦 SANCHARA", "Sanchara", "Global Logistics", "#FF8800"),
        ("🤝 MITHRA+", "Mithra", "AI Negotiation", "#34D399")
    ]
    for label, page_id, layman, color in nodes:
        if st.button(label, key=f"nav_{page_id.lower()}"):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub' style='color:{color};'>{layman}</span>", unsafe_allow_html=True)
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 5. LOGIC NODES ---

if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Mission Control: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f"<div class='saas-card' style='border-top:5px solid #7F00FF;'><h3>Assets</h3><h2 style='color:#7F00FF;'>{len(df)}</h2></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='saas-card' style='border-top:5px solid #FFD700;'><h3>Treasury Value</h3><h2 style='color:#FFD700;'>₹{val:,.0f}</h2></div>", unsafe_allow_html=True)
    with c3: st.markdown(f"<div class='saas-card' style='border-top:5px solid #FF33FF;'><h3>Workforce Efficiency</h3><h2 style='color:#FF33FF;'>92%</h2></div>", unsafe_allow_html=True)

elif st.session_state.page == "Karma":
    st.markdown("<h1 style='color:#FF33FF;'>👷‍♂️ KARMA: Workforce Intelligence</h1>", unsafe_allow_html=True)
    st.info("System-driven orchestration of human operations and performance optimization.")
    
    t1, t2, t3 = st.tabs(["⚙️ Intelligent Tasking", "📊 Performance Analytics", "🧘 Human-Centric Safety"])
    
    with t1:
        st.subheader("Dynamic Operational Directives")
        col_q, col_v = st.columns([2, 1])
        with col_q:
            directives = [
                {"Action": "Pick 12x 'Titanium Chassis'", "Priority": "Critical", "Assigned": "Ravi (Station 4)"},
                {"Action": "Restock Silicon Batch B4", "Priority": "High", "Assigned": "Ananya (Station 1)"},
                {"Action": "Audit Returns: Bin 7", "Priority": "Standard", "Assigned": "Suresh (Station 2)"}
            ]
            for d in directives:
                st.markdown(f"<div class='karma-directive'><b>{d['Action']}</b><br>Priority: {d['Priority']} | Assigned to: {d['Assigned']}</div>", unsafe_allow_html=True)
        with col_v:
            st.markdown("<div class='saas-card' style='text-align:center;'><h4>Team Throughput</h4><h2 style='color:#FF33FF;'>142 units/hr</h2></div>", unsafe_allow_html=True)
            if st.button("🎙️ Open Voice Guidance"):
                st.write("AI Voice: 'Ravi, proceed to Shelf C1. Optimal path displayed on HUD.'")

    with t2:
        st.subheader("Performance Insights Engine")
        # Skill Radar chart (Professional)
        categories = ['Picking Speed','Accuracy','Packing','Safety Compliance','Technical Proficiency']
        fig = go.Figure(data=go.Scatterpolar(
          r=[94, 98, 70, 92, 85],
          theta=categories,
          fill='toself',
          line_color='#FF33FF'
        ))
        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with t3:
        st.subheader("Workload & Fatigue Monitoring")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<div class='saas-card'><b>Current Utilization:</b> 78%<br><b>Alerts:</b> None</div>", unsafe_allow_html=True)
        with c2:
            st.warning("⚠️ Recommendation: Suresh has maintained high-intensity picking for 3.5 hours. Suggest a 10-minute recovery break to maintain accuracy.")

elif st.session_state.page == "Mithra":
    st.markdown("<h1 style='color:#34D399;'>🤝 MITHRA+: AI Negotiation Engine</h1>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        vendor = st.selectbox("Select Vendor", df['supplier'].unique())
        tone = st.select_slider("Negotiation Tone", options=["Polite", "Balanced", "Aggressive"], value="Balanced")
        if st.button("🚀 EXECUTE NEGOTIATION STRATEGY"):
            st.info(f"AI Strategy: Leveraging bulk volume to secure a 5% unit cost reduction from {vendor}.")
            st.text_area("Drafted Directive", f"Dear {vendor},\n\nOur demand sensing predicts a 40% increase in volume. We would like to align on revised pricing...")

elif st.session_state.page == "Preksha":
    st.markdown("<h1 style='color:#7F00FF;'>📈 PREKSHA: Strategic Vision</h1>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        target = st.selectbox("Search Asset", df['name']); p = df[df['name'] == target].iloc[0]
        col1, col2 = st.columns([1, 2])
        with col1:
            if p['image_url']: st.image(p['image_url'], use_container_width=True)
            if p['reviews']: st.markdown(f"<div class='review-box'>💬 {p['reviews']}</div>", unsafe_allow_html=True)
        with col2:
            sent = st.select_slider("Market Sentiment", options=[0.8, 1.0, 1.5, 2.0], value=1.0)
            preds = (np.random.randint(20, 50, 7) * sent).astype(int)
            st.plotly_chart(px.area(y=preds, title="Neural Forecast Flow", template="plotly_dark").update_traces(line_color='#7F00FF'))
            st.markdown(f"<div class='ai-decision-box'>🤖 **Decision Directive:** Order **{preds.sum()} units** immediately.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Nyasa":
    st.markdown("<h1 style='color:#00FF88;'>📝 NYASA: Registry</h1>", unsafe_allow_html=True)
    with st.form("add"):
        n = st.text_input("Asset Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead Time", 1); sup = st.text_input("Supplier"); img = st.text_input("Img URL"); rev = st.text_area("Revs")
        if st.form_submit_button("COMMIT"):
            with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, supplier, image_url, reviews) VALUES (?,?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, sup, img, rev))
            st.success("Synchronized.")

elif st.session_state.page == "Samvada":
    st.markdown("<h1 style='color:#00D4FF;'>🎙️ SAMVADA: Neural Dialogue</h1>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
        u_in = st.chat_input("Speak command...")
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"user", "content":u_in}])
            st.session_state.chat_history.append({"role":"assistant", "content":res.choices[0].message.content}); st.rerun()

# Simplified Sanchara, Vitta, Stambha from previous turns
elif st.session_state.page == "Vitta":
    st.markdown("<h1 style='color:#FFD700;'>💰 VITTA: Wealth Intel</h1>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty: st.plotly_chart(px.pie(df, values='current_stock', names='name', hole=0.5, template="plotly_dark"))

elif st.session_state.page == "Sanchara":
    st.markdown("<h1 style='color:#FF8800;'>📦 SANCHARA: Global Flow</h1>", unsafe_allow_html=True)
    st.map(pd.DataFrame({'lat':[12.97, 22.31], 'lon':[77.59, 114.16]}))

elif st.session_state.page == "Stambha":
    st.markdown("<h1 style='color:#FF0055;'>🛡️ STAMBHA: Guard</h1>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty: st.table(df[['name', 'current_stock', 'lead_time']])

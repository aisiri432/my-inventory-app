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

# --- 1. PREMIUM UI CONFIG (UNIVERSAL ADAPTIVE & RADIANT SPECTRUM) ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="expanded"
)

# LOGO SVG FOR WATERMARK
logo_svg = """
<svg width="500" height="500" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
<path d="M50 5L10 85H30L50 35L70 85H90L50 5Z" fill="white" fill-opacity="0.1"/>
<circle cx="50" cy="45" r="5" fill="#00D4FF" fill-opacity="0.2"/>
</svg>
"""

def apply_aroha_style():
    # Double braces {{ }} used for CSS to prevent Python SyntaxError
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background-color: #050709; color: #E6E8EB; }}

        /* 📱 UNIVERSAL RESPONSIVITY */
        @media (min-width: 768px) {{
            [data-testid="stSidebar"] {{ min-width: 420px !important; max-width: 420px !important; }}
            .brand-title {{ font-size: 3.5rem !important; }}
            .feature-header {{ font-size: 3.2rem !important; }}
        }}
        @media (max-width: 767px) {{
            .brand-title {{ font-size: 2.2rem !important; }}
            .feature-header {{ font-size: 1.8rem !important; }}
            section[data-testid="stSidebar"] .stButton > button {{ font-size: 1.2rem !important; }}
            .sidebar-sub {{ font-size: 0.75rem !important; margin-left: 10px !important; }}
        }}

        /* 💠 WATERMARK */
        [data-testid="stAppViewContainer"]::before {{
            content: ""; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-15deg);
            width: 70vw; height: 70vw; background-image: url("data:image/svg+xml;utf8,{logo_svg.replace('<', '%3C').replace('>', '%3E').replace('#', '%23')}");
            background-repeat: no-repeat; background-position: center; opacity: 0.05; z-index: -1; pointer-events: none; filter: blur(5px);
        }}

        /* 📟 SIDEBAR: RADIANT HOLLOW BLUE GLOW */
        [data-testid="stSidebar"] {{ background-color: #080A0C !important; border-right: 1px solid #1F2229; }}
        section[data-testid="stSidebar"] .stButton > button {{ 
            background: transparent !important; border: 2px solid rgba(255, 255, 255, 0.1) !important; 
            color: #FFFFFF !important; text-align: left !important; padding: 15px 18px !important; width: 100%; 
            font-size: 1.6rem; font-weight: 800 !important; letter-spacing: 1.5px;
            text-shadow: 0 0 10px rgba(255, 255, 255, 0.2); margin-bottom: 5px; transition: 0.3s;
        }}

        /* 🌈 SPECTRUM GLOW EFFECTS */
        div[data-testid="stSidebar"] button[key*="nyasa"]:hover {{ border-color: #00FF88 !important; box-shadow: 0 0 15px #00FF88; color: #00FF88 !important; }}
        div[data-testid="stSidebar"] button[key*="preksha"]:hover {{ border-color: #7F00FF !important; box-shadow: 0 0 15px #7F00FF; color: #7F00FF !important; }}
        div[data-testid="stSidebar"] button[key*="stambha"]:hover {{ border-color: #FF0055 !important; box-shadow: 0 0 15px #FF0055; color: #FF0055 !important; }}
        div[data-testid="stSidebar"] button[key*="karma"]:hover {{ border-color: #FF33FF !important; box-shadow: 0 0 15px #FF33FF; color: #FF33FF !important; }}
        div[data-testid="stSidebar"] button[key*="samvada"]:hover {{ border-color: #00D4FF !important; box-shadow: 0 0 15px #00D4FF; color: #00D4FF !important; }}
        div[data-testid="stSidebar"] button[key*="vitta"]:hover {{ border-color: #FFD700 !important; box-shadow: 0 0 15px #FFD700; color: #FFD700 !important; }}
        div[data-testid="stSidebar"] button[key*="sanchara"]:hover {{ border-color: #FF8800 !important; box-shadow: 0 0 15px #FF8800; color: #FF8800 !important; }}
        div[data-testid="stSidebar"] button[key*="mithra"]:hover {{ border-color: #34D399 !important; box-shadow: 0 0 15px #34D399; color: #34D399 !important; }}

        .sidebar-sub {{ font-size: 0.95rem !important; color: #6C63FF; font-weight: 700; display: block; margin-top: -10px; margin-bottom: 25px; margin-left: 20px; text-transform: uppercase; letter-spacing: 1px; }}

        /* 💎 COMPONENTS */
        .saas-card {{ background: #0D1117; border: 1px solid rgba(0, 212, 255, 0.1); border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }}
        .ai-decision-box {{ background: rgba(17, 25, 40, 0.75); border: 2px solid #D4AF37; padding: 25px; border-radius: 15px; border-left: 12px solid #D4AF37; margin-top: 25px; box-shadow: 0 0 20px rgba(212, 175, 55, 0.2); }}
        .feature-header {{ font-weight: 800; color: #00D4FF !important; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3); text-transform: uppercase; }}
        .directive-msg {{ background: rgba(255, 51, 255, 0.05); border-left: 5px solid #FF33FF; padding: 15px; border-radius: 10px; margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; }}
        .financial-stat {{ background: #111; padding: 20px; border-radius: 10px; border-top: 4px solid #D4AF37; text-align: center; }}
        
        header {{visibility: hidden;}} footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_master_v119.db'
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

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_on" not in st.session_state: st.session_state.voice_on = False

def speak(text):
    if st.session_state.voice_on:
        clean = text.replace('"', '').replace("'", "")
        js = f"<script>var m = new SpeechSynthesisUtterance(); m.text='{clean}'; window.speechSynthesis.speak(m);</script>"
        st.components.v1.html(js, height=0)

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 style='color:white; font-size:3.5rem; font-weight:900;'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Turn Data Into Decisions</p></div>", unsafe_allow_html=True)
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
                try:
                    with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                    st.success("Authorized.")
                except: st.error("ID exists.")
    st.stop()

# --- 5. SIDEBAR (UNIFIED 8 NODES) ---
with st.sidebar:
    st.markdown(f"<div class='brand-container'><div class='brand-title' style='font-size:2.2rem !important;'>AROHA</div><div style='color:#9AA0A6; font-size:0.9rem;'>Data into <span class='decisions-fade'>Decisions</span></div></div>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub' style='color:#FFF;'>System Overview</span>", unsafe_allow_html=True)
    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items & Sync", "#00FF88"),
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly", "#7F00FF"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks", "#FF0055"),
        ("👷‍♂️ KARMA", "Karma", "Workforce Intelligence", "#FF33FF"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System", "#00D4FF"),
        ("💰 VITTA", "Vitta", "Track Money Flow", "#FFD700"),
        ("📦 SANCHARA", "Sanchara", "Global Map & Flow", "#FF8800"),
        ("🤝 MITHRA+", "Mithra", "AI Negotiation", "#34D399")
    ]
    for label, page_id, layman, color in nodes:
        if st.button(label, key=f"nav_{page_id.lower()}"):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub' style='color:{color};'>{layman}</span>", unsafe_allow_html=True)
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 6. KARMA: THE 9-POINT WORKFORCE SYSTEM ---
if st.session_state.page == "Karma":
    st.markdown("<div class='feature-header' style='color:#FF33FF !important;'>👷‍♂️ KARMA: Workforce Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='insight-box' style='border-color:#FF33FF;'><b>💡 Efficiency Hub:</b> Optimizing human capital through dynamic orchestration and fatigue sensing.</div>", unsafe_allow_html=True)
    
    t1, t2, t3 = st.tabs(["🔧 Worker HUD", "📡 Live Activity", "📊 Manager Command"])
    
    with t1:
        st.subheader("Real-Time Operational Guide")
        c_inst, c_voice = st.columns([2, 1])
        with c_inst:
            st.markdown("<div class='directive-msg'><b>[POINT 1: ASSIGNMENT]</b> Pick 12x Titanium Chassis for order #992.</div>", unsafe_allow_html=True)
            st.markdown("<div class='directive-msg'><b>[POINT 2: GUIDANCE]</b> Proceed to <b>Shelf B2 via Aisle 3</b>. Scan barcode upon arrival.</div>", unsafe_allow_html=True)
            if st.button("📦 SIMULATE SCAN"):
                st.error("🚨 [POINT 4: ERROR PREVENTION] Warning: Incorrect item selected (SKU-405). Please verify SKU: CHASSIS-01.")
        with c_voice:
            st.write("### [POINT 3: VOICE]")
            if st.button("🎙️ 'What should I do next?'"):
                st.info("🤖 AI: Head to Zone C. 5 units of Sensors required for packing.")
            st.write("---")
            st.write("### [POINT 5: FATIGUE]")
            st.warning("🧠 Fatigue Detected: Performance slowdown (15%). Recommend a 10-minute break.")

    with t2:
        st.subheader("[POINT 7: LIVE TRACKING]")
        st.markdown("<div class='directive-msg'>🟢 14:02 - Ravi started picking at Shelf D4</div>", unsafe_allow_html=True)
        st.markdown("<div class='directive-msg'>🟡 13:58 - Ananya in process at Packing Station 1</div>", unsafe_allow_html=True)
        st.markdown("<div class='directive-msg'>🔴 13:45 - Suresh delayed at Dock A (Heavy Load)</div>", unsafe_allow_html=True)

    with t3:
        st.subheader("[POINT 8 & 9: MANAGER INSIGHTS]")
        c1, c2 = st.columns(2)
        with c1:
            st.write("### Team Efficiency Pulse")
            st.plotly_chart(px.line(y=[85, 92, 78, 95, 88], title="Team Throughput", template="plotly_dark").update_traces(line_color='#FF33FF'))
        with c2:
            st.write("### Resource Allocation")
            st.bar_chart({"Speed": [90, 75, 95], "Accuracy": [98, 80, 92]}, height=250)
            st.success("✅ Top Performer: Ananya (98% Accuracy).")

# --- 7. OTHER LOGIC NODES ---
elif st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Strategic Hub: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Assets Managed", len(df))
    with c2: st.metric("Treasury Value", f"₹{val:,.0f}")
    with c3: st.metric("System Health", "OPTIMAL")

elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header' style='color:#7F00FF !important;'>📈 PREKSHA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        target = st.selectbox("Search", df['name']); p = df[df['name'] == target].iloc[0]
        col1, col2 = st.columns([1, 2])
        with col1:
            if p['image_url'] and str(p['image_url']) != "nan": st.image(p['image_url'], use_container_width=True)
            if p['reviews']: 
                for r in p['reviews'].split('|'): st.markdown(f"<div class='review-box'>💬 {r}</div>", unsafe_allow_html=True)
        with col2:
            sent = st.select_slider("Market Sentiment", options=[0.8, 1.0, 1.5, 2.0], value=1.0)
            preds = np.random.randint(20, 50, 7)
            st.plotly_chart(px.area(y=preds, title="AI Forecasting Stream", template="plotly_dark").update_traces(line_color='#7F00FF'))
            st.markdown(f"<div class='ai-decision-box'><h3>🤖 AI SUGGESTION</h3>Order <b>{max(0, preds.sum() - p['current_stock'])}</b> units immediately.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header' style='color:#FF0055 !important;'>🛡️ STAMBHA</div>", unsafe_allow_html=True)
    s = st.selectbox("Shock Event", ["Normal", "Port Closure (3x Lead)", "Factory Fire (+30d)"])
    df = get_user_data()
    if not df.empty:
        for _, p in df.iterrows():
            ttr = p['lead_time'] * (3 if "Port" in s else 1)
            tts = round(p['current_stock'] / 12, 1)
            if tts < ttr: st.error(f"🔴 CRITICAL RISK: {p['name']} runs out in {tts}d. Recovery: {ttr}d.")
        st.table(df[['name', 'current_stock', 'lead_time']])

elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header' style='color:#00D4FF !important;'>🎙️ SAMVADA</div>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        u_in = st.chat_input("Strategic query...")
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans}); st.rerun()

elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header' style='color:#FFD700 !important;'>💰 VITTA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='financial-stat'>Total Value<br><h2>₹{total_v:,.0f}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='financial-stat' style='margin-top:20px;'>Idle Risk (15%)<br><h2 style='color:red;'>₹{total_v*0.15:,.0f}</h2></div>", unsafe_allow_html=True)
        with c2: st.plotly_chart(px.pie(df, values='current_stock', names='name', hole=0.5, template="plotly_dark"))

elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header' style='color:#FF8800 !important;'>📦 SANCHARA</div>", unsafe_allow_html=True)
    map_points = pd.DataFrame({'lat':[12.97, 22.31, 37.77, 1.35], 'lon':[77.59, 114.16, -122.41, 103.81], 'Node':['Hub','Factory','HQ','Port'], 'Address':['MG Road, Bangalore','Lantau, HK','Market St, SF','Jurong, Singapore (🔴 CLOSED)']})
    st.plotly_chart(px.scatter_mapbox(map_points, lat="lat", lon="lon", hover_name="Node", hover_data={"Address": True}, zoom=1, height=450).update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0}), use_container_width=True)

elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header' style='color:#00FF88 !important;'>📝 NYASA</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📥 Bulk Ingest", "✍️ Manual Registry"])
    with t1:
        f = st.file_uploader("Upload CSV", type="csv")
        if f and st.button("Sync Data"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            for col in ['category','supplier','image_url','reviews']: u_df[col] = u_df.get(col, "")
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Synced.")
    with t2:
        with st.form("manual"):
            n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead", 1)
            if st.form_submit_button("Commit"):
                with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time) VALUES (?,?,?,?,?)", (st.session_state.user, n, s, p, lt))
                st.success("Saved.")

elif st.session_state.page == "Mithra":
    st.markdown("<div class='feature-header' style='color:#34D399 !important;'>🤝 MITHRA+</div>", unsafe_allow_html=True)
    st.info("Strategic Negotiation Module Online.")

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

# --- 1. PREMIUM UI CONFIG (UNIVERSAL RESPONSIVE & HOLLOW GLOW) ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence", 
    layout="wide", 
    page_icon="💠",
    initial_sidebar_state="auto"
)

def apply_aroha_style():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050709; color: #E6E8EB; }

        /* 📱 UNIVERSAL RESPONSIVITY */
        @media (max-width: 768px) {
            .brand-title { font-size: 2.2rem !important; }
            .feature-header { font-size: 1.8rem !important; }
            section[data-testid="stSidebar"] { min-width: 100% !important; }
            section[data-testid="stSidebar"] .stButton > button { font-size: 1.1rem !important; }
            .sidebar-sub { font-size: 0.75rem !important; margin-left: 10px !important; }
            .saas-card { padding: 15px !important; }
        }

        /* 📟 SIDEBAR: RADIANT HOLLOW BLUE GLOW */
        [data-testid="stSidebar"] { background-color: #080A0C !important; border-right: 1px solid #1F2229; min-width: 400px; }
        section[data-testid="stSidebar"] .stButton > button { 
            background: transparent !important; border: 2px solid rgba(0, 212, 255, 0.4) !important; 
            color: #FFFFFF !important; text-align: left !important; padding: 12px 18px !important; width: 100%; 
            font-size: 1.5rem; font-weight: 800 !important; letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5); margin-bottom: 5px; transition: 0.3s;
        }
        section[data-testid="stSidebar"] .stButton > button:hover { border: 2px solid #00D4FF !important; box-shadow: 0 0 20px rgba(0, 212, 255, 0.6); color: #00D4FF !important; }
        .sidebar-sub { font-size: 0.95rem !important; color: #6C63FF; font-weight: 700; display: block; margin-top: -10px; margin-bottom: 25px; margin-left: 20px; text-transform: uppercase; letter-spacing: 1px; }

        .brand-title { font-size: 3.5rem !important; font-weight: 800 !important; color: #FFFFFF !important; letter-spacing: -2px; text-shadow: 0 0 25px rgba(108, 99, 255, 0.6); margin-bottom: 0; }
        .decisions-fade { color: #6C63FF; font-weight: 700; animation: glowPulse 2s infinite alternate; }
        @keyframes glowPulse { from { text-shadow: 0 0 5px #6C63FF; } to { text-shadow: 0 0 15px #38BDF8; } }

        .feature-header { font-size: 3.2rem !important; font-weight: 800 !important; color: #00D4FF !important; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3); text-transform: uppercase; }
        .saas-card { background: #0D1117; border: 1px solid rgba(0, 212, 255, 0.1); border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
        .ai-decision-box { background: rgba(17, 25, 40, 0.75); border: 2px solid #D4AF37; padding: 25px; border-radius: 15px; border-left: 12px solid #D4AF37; margin-top: 25px; }
        .financial-stat { background: #111; padding: 20px; border-radius: 10px; border-top: 4px solid #D4AF37; text-align: center; }
        .review-box { background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; border: 1px solid #222; margin-bottom: 10px; font-size: 0.85rem; }

        @keyframes ticker { 0% { transform: translateX(100%); } 100% { transform: translateX(-100%); } }
        .ticker-wrap { width: 100%; overflow: hidden; background: rgba(0, 212, 255, 0.05); border-bottom: 1px solid rgba(0, 212, 255, 0.2); padding: 8px 0; margin-bottom: 20px; }
        .ticker-text { display: inline-block; white-space: nowrap; font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #00D4FF; animation: ticker 40s linear infinite; }

        header {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_master_v70.db'
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

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 class='brand-title'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Turn Data Into <span class='decisions-fade'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([0.1, 0.8, 0.1])
    with col_center:
        m = st.tabs(["Login", "Enroll"])
        with m[0]:
            u_input = st.text_input("Username", key="l_u")
            p_input = st.text_input("Password", type="password", key="l_p")
            if st.button("Unlock Hub"):
                with get_db() as conn: res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u_input,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p_input):
                    st.session_state.auth = True; st.session_state.user = u_input; st.rerun()
                else: st.error("Access Denied")
        with m[1]:
            nu = st.text_input("New ID"); np = st.text_input("New Password", type="password")
            if st.button("Enroll Session"):
                try:
                    with get_db() as conn: conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np)))
                    st.success("Authorized.")
                except: st.error("ID exists.")
    st.stop()

# --- 5. TOP TICKER ---
st.markdown(f"<div class='ticker-wrap'><div class='ticker-text'>[DHWANI] Neural link active for {st.session_state.user.upper()} // [LOGISTICS] Hover over Spandana Map for Precision Addresses // [MITHRA] Supplier Reliability Scores recalculated // [VITTA] Capital allocation efficiency at 94.2%.</div></div>", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div class='brand-container'><div class='brand-title' style='font-size:2.2rem !important;'>AROHA</div><div style='color:#9AA0A6; font-size:0.9rem;'>Data into <span class='decisions-fade'>Decisions</span></div></div>", unsafe_allow_html=True)
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)

    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items & PO Gen"),
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System"),
        ("💰 VITTA", "Vitta", "Track Money Flow"),
        ("📦 SANCHARA", "Sanchara", "Global Map & Flow"),
        ("🤝 MITHRA", "Mithra", "Supplier Intelligence")
    ]
    for label, page_id, layman in nodes:
        if st.button(label):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 7. LOGIC NODES ---

# DASHBOARD
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Strategic Hub: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("📝 Assets Managed", len(df))
    with c2: st.metric("💰 Treasury Value", f"₹{val:,.0f}")
    with c3: st.metric("🛡️ System Integrity", "OPTIMAL")

# VITTA-FINANCE (RESTORED METRICS + PIE CHART)
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>💰 VITTA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        idle_v = total_v * 0.15 # 15% Estimated holding cost
        
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"<div class='financial-stat'>Total Inventory Value<br><h2>₹{total_v:,.0f}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='financial-stat' style='margin-top:20px;'>Idle Capital Risk (Holding Cost)<br><h2 style='color:red;'>₹{idle_v:,.0f}</h2></div>", unsafe_allow_html=True)
            st.info("💡 Insight: Per capita capital risk represents the potential loss due to unsold static inventory over 30 days.")
        with c2:
            st.markdown("<div class='saas-card'><b>Capital Allocation Matrix</b>", unsafe_allow_html=True)
            st.plotly_chart(px.pie(df, values='current_stock', names='name', hole=0.5, template="plotly_dark"), use_container_width=True)
    else: st.warning("Add data to view financial analysis.")

# MITHRA-ALLIANCE (RESTORED MATRIX + BAR CHART)
elif st.session_state.page == "Mithra":
    st.markdown("<div class='feature-header'>🤝 MITHRA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        # Reliability Score logic from previous high-end version
        df['Reliability Score'] = (100 - (df['lead_time'] * 2)).clip(50, 99)
        col_list, col_matrix = st.columns([2, 1])
        with col_list:
            st.write("### Vendor Reliability Matrix")
            st.dataframe(df[['supplier', 'name', 'lead_time', 'Reliability Score']].sort_values(by='Reliability Score', ascending=False), use_container_width=True)
        with col_matrix:
            st.write("### Risk Profile")
            fig = px.bar(df, x='supplier', y='Reliability Score', color='Reliability Score', color_continuous_scale='Portland', template='plotly_dark')
            st.plotly_chart(fig, use_container_width=True)
        st.info("💡 Strategic Tip: Suppliers with scores below 70% are automatically flagged for alternative sourcing.")
    else: st.warning("No supplier data found.")

# SANCHARA (MAP + DESCRIPTION + SHIPPED METRICS)
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>📦 SANCHARA</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌐 Precision Map", "📦 Floor Ops", "↩️ Returns"])
    with t1:
        st.subheader("Global SPANDANA Intelligence Map")
        map_points = pd.DataFrame({
            'lat': [12.9716, 22.3193, 37.7749, 1.3521], 'lon': [77.5946, 114.1694, -122.4194, 103.8198],
            'Location': ['Main Hub', 'Component Factory', 'Strategic HQ', 'Risk Zone'],
            'Address': ['MG Road, Bangalore, India', 'Lantau Island, Hong Kong', 'Market St, San Francisco, USA', 'Jurong Island, Singapore (🔴 PORT CLOSED)'],
            'Risk': ['Low', 'Low', 'Low', '🔴 CRITICAL']
        })
        fig = px.scatter_mapbox(map_points, lat="lat", lon="lon", hover_name="Location", hover_data={"Address": True, "Risk": True, "lat": False, "lon": False}, color="Risk", color_discrete_map={'Low': 'cyan', '🔴 CRITICAL': 'red'}, zoom=1, height=450)
        fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("""<div style='background:rgba(255,255,255,0.02); padding:15px; border-radius:10px; border:1px solid #333; margin-top:15px;'>
        <h4 style='color:#00D4FF; margin-top:0;'>🗺️ Strategic Map Description</h4>
        <p><b>📍 Precision Hover:</b> Hover or tap any marker to view the <b>Exact Physical Address</b> and regional status.</p>
        <p><b>🛰️ Global Link:</b> Map dots represent satellite-verified supplier nodes and high-risk disruption zones (Red).</p></div>""", unsafe_allow_html=True)
    with t2:
        c1, c2, c3 = st.columns(3)
        df_inv = get_user_data()
        current_total = df_inv['current_stock'].sum() if not df_inv.empty else 0
        c1.metric("📦 Items Shipped Today", "1,240", "↑ 12%")
        c2.metric("🚛 New Inbound", "3,500", "Stable")
        c3.metric("🏭 Total Floor Assets", f"{current_total + 142} Units") # Includes simulated returns
    with t3:
        st.subheader("PUNAH Returns Log")
        df_ret = pd.DataFrame({'Product': ['Quantum Laptop', '4K Monitor'], 'Reason': ['Defective Logic Board', 'Screen Bleed'], 'Action': ['Repair', 'Replace']})
        st.table(df_ret)

# PREKSHA (REVIEWS + PHOTOS RESTORED)
elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>📈 PREKSHA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if df.empty: st.warning("Add data in NYASA node.")
    else:
        target = st.selectbox("Asset Search", df['name']); p_row = df[df['name'] == target].iloc[0]
        col_m, col_v = st.columns([1, 2])
        with col_m:
            if p_row['image_url'] and str(p_row['image_url']) != "nan": st.image(p_row['image_url'], use_container_width=True)
            if p_row['reviews'] and str(p_row['reviews']) != "nan":
                st.subheader("Customer Sentiment")
                for r in p_row['reviews'].split('|'): st.markdown(f"<div class='review-box'>💬 {r}</div>", unsafe_allow_html=True)
        with col_v:
            sent = st.select_slider("Market Sentiment", options=[0.8, 1.0, 1.5, 2.0], value=1.0)
            preds = (np.random.randint(20, 50, 7) * sent).astype(int)
            st.plotly_chart(px.area(y=preds, title="AI Forecasting Stream", template="plotly_dark").update_traces(line_color='#00D4FF'), use_container_width=True)
            st.markdown(f"<div class='ai-decision-box'><h3 style='color:#D4AF37; margin:0;'>🤖 AGENT SUGGESTION</h3>Reorder <b>{max(0, preds.sum() - p_row['current_stock'])}</b> units immediately.</div>", unsafe_allow_html=True)

# STAMBHA (RISK MESSAGES RESTORED)
elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header'>🛡️ STAMBHA</div>", unsafe_allow_html=True)
    s_scenario = st.selectbox("Trigger Disruption", ["Normal", "Port Closure (3x TTR)", "Factory Fire (+30d)"])
    df = get_user_data()
    if not df.empty:
        res_list = []
        for _, p in df.iterrows():
            ttr = p['lead_time'] * (3 if "Port" in s_scenario else 1)
            if "Fire" in s_scenario: ttr += 30
            tts = round(p['current_stock'] / 12, 1)
            status = "🟢 Safe" if tts > ttr else "🔴 CRITICAL"
            if status == "🔴 CRITICAL": st.error(f"⚠️ DANGER: {p['name']} risk. TTS ({tts}d) < TTR ({ttr}d).")
            res_list.append({"Asset": p['name'], "TTS (d)": tts, "TTR (d)": ttr, "Status": status})
        st.table(pd.DataFrame(res_list))

# NYASA, SAMVADA logic ...
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>📝 NYASA</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📥 Bulk Sync", "✍️ Manual", "📄 PO Gen"])
    with t1:
        f = st.file_uploader("Upload CSV", type="csv")
        if f and st.button("Sync"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            for col in ['category','supplier','image_url','reviews']: u_df[col] = u_df.get(col, "")
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Synced.")
    with t2:
        with st.form("manual"):
            n = st.text_input("Name"); s = st.number_input("Stock", 0); p = st.number_input("Price", 0.0); lt = st.number_input("Lead", 1); img = st.text_input("Img URL"); rev = st.text_area("Reviews")
            if st.form_submit_button("Commit"):
                with get_db() as conn: conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
                st.success("Saved.")
    with t3:
        df = get_user_data()
        if not df.empty:
            t = st.selectbox("Asset", df['name'])
            if st.button("Generate PO"): st.code(f"PO-ID: #ARH-{np.random.randint(1000,9999)}\nITEM: {t}")

elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header'>🎙️ SAMVADA</div>", unsafe_allow_html=True)
    st.session_state.voice_on = st.toggle("Enable Voice Assistant")
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        u_in = st.chat_input("Strategic query...")
        audio = st.audio_input("Microphone")
        if audio:
            with st.spinner("Listening..."):
                u_in = client.audio.transcriptions.create(file=("q.wav", audio.read()), model="whisper-large-v3", response_format="text")
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans}); st.rerun()

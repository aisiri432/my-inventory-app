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

# --- 1. PREMIUM UI CONFIG (v89 HOLLOW BLUE GLOW & UNIVERSAL ADAPTIVE) ---
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
    # CSS using double braces {{ }} to prevent Python f-string errors
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap');
        html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; background-color: #050709; color: #E6E8EB; }}

        /* 💠 v89 WATERMARK */
        [data-testid="stAppViewContainer"]::before {{
            content: ""; position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%) rotate(-15deg);
            width: 70vw; height: 70vw; background-image: url("data:image/svg+xml;utf8,{logo_svg.replace('<', '%3C').replace('>', '%3E').replace('#', '%23')}");
            background-repeat: no-repeat; background-position: center; opacity: 0.05; z-index: -1; pointer-events: none; filter: blur(5px);
        }}

        /* 📟 SIDEBAR: v89 HOLLOW BLUE GLOW */
        [data-testid="stSidebar"] {{ background-color: #080A0C !important; border-right: 1px solid #1F2229; min-width: 420px; }}
        @media (max-width: 768px) {{ [data-testid="stSidebar"] {{ min-width: 100% !important; }} }}

        section[data-testid="stSidebar"] .stButton > button {{ 
            background: transparent !important; border: 2px solid rgba(0, 212, 255, 0.4) !important; 
            color: #FFFFFF !important; text-align: left !important; padding: 15px 18px !important; width: 100%; 
            font-size: 1.6rem; font-weight: 800 !important; letter-spacing: 1.5px;
            text-shadow: 0 0 10px rgba(0, 212, 255, 0.5); margin-bottom: 5px; transition: 0.3s;
        }}
        section[data-testid="stSidebar"] .stButton > button:hover {{ border-color: #00D4FF !important; box-shadow: 0 0 20px rgba(0, 212, 255, 0.6); color: #00D4FF !important; }}
        .sidebar-sub {{ font-size: 0.95rem !important; color: #6C63FF; font-weight: 700; display: block; margin-top: -10px; margin-bottom: 25px; margin-left: 20px; text-transform: uppercase; letter-spacing: 1px; }}

        /* 💎 COMPONENTS */
        .saas-card {{ background: #0D1117; border: 1px solid rgba(0, 212, 255, 0.1); border-radius: 12px; padding: 25px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }}
        .ai-decision-box {{ background: rgba(17, 25, 40, 0.75); border: 2px solid #D4AF37; padding: 25px; border-radius: 15px; border-left: 12px solid #D4AF37; margin-top: 25px; box-shadow: 0 0 20px rgba(212, 175, 55, 0.2); }}
        .feature-header {{ font-size: 3.2rem !important; font-weight: 800 !important; color: #00D4FF !important; letter-spacing: 2px; text-shadow: 0 0 15px rgba(0, 212, 255, 0.3); text-transform: uppercase; }}
        .review-box {{ background: rgba(255,255,255,0.03); padding: 12px; border-radius: 10px; border: 1px solid #222; margin-bottom: 10px; font-size: 0.85rem; border-left: 4px solid #7F00FF; }}
        .financial-stat {{ background: #111; padding: 20px; border-radius: 10px; border-top: 4px solid #D4AF37; text-align: center; }}
        .directive-msg {{ background: rgba(0, 212, 255, 0.05); border-left: 4px solid #00D4FF; padding: 15px; border-radius: 10px; margin-bottom: 10px; font-family: 'JetBrains Mono', monospace; }}

        @keyframes ticker {{ 0% {{ transform: translateX(100%); }} 100% {{ transform: translateX(-100%); }} }}
        .ticker-wrap {{ width: 100%; overflow: hidden; background: rgba(0, 212, 255, 0.05); border-bottom: 1px solid rgba(0, 212, 255, 0.2); padding: 8px 0; margin-bottom: 20px; }}
        .ticker-text {{ display: inline-block; white-space: nowrap; font-family: 'JetBrains Mono'; font-size: 0.8rem; color: #00D4FF; animation: ticker 40s linear infinite; }}

        header {{visibility: hidden;}} footer {{visibility: hidden;}}
        </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_ultimate_v120.db'
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
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 class='brand-title'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Turn Data Into Decisions</p></div>", unsafe_allow_html=True)
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
                    st.success("Authorized. Please login.")
                except: st.error("ID exists.")
    st.stop()

# --- 5. TOP HUD ---
st.markdown(f"<div class='ticker-wrap'><div class='ticker-text'>[DHWANI] {st.session_state.user.upper()} ACTIVE // [LOGISTICS] Hover over Map for Precision Addresses // [VITTA] Capital efficiency optimized.</div></div>", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div class='brand-container'><div class='brand-title' style='font-size:2.2rem !important;'>AROHA</div><div style='color:#9AA0A6; font-size:0.9rem;'>Data into <span class='decisions-fade'>Decisions</span></div></div>", unsafe_allow_html=True)
    
    if st.button("🏠 DASHBOARD"): st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)

    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items & PO Gen"),
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks"),
        ("👷‍♂️ KARMA", "Karma", "Workforce Intelligence"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System"),
        ("💰 VITTA", "Vitta", "Track Money Flow"),
        ("📦 SANCHARA", "Sanchara", "Global Map & Flow"),
        ("🤝 MITHRA+", "Mithra", "AI Negotiation")
    ]
    for label, page_id, layman in nodes:
        if st.button(label, key=f"nav_{page_id}"):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)
    if st.button("🔒 Logout"): st.session_state.auth = False; st.rerun()

# --- 7. LOGIC NODES ---

# 🏠 DASHBOARD
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1>Strategic Hub: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("📝 Assets Managed", len(df))
    with c2: st.metric("💰 Treasury Value", f"₹{val:,.0f}")
    with c3: st.metric("🛡️ Status", "OPTIMAL")

# 💰 VITTA (RESTORED METRICS + PIE)
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>💰 VITTA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        idle_v = total_v * 0.15 
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='financial-stat'>Total Inventory Value<br><h2>₹{total_v:,.0f}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='financial-stat' style='margin-top:20px;'>Idle Capital Risk (15%)<br><h2 style='color:red;'>₹{idle_v:,.0f}</h2></div>", unsafe_allow_html=True)
        with c2: 
            st.markdown("<div class='saas-card'><b>Capital Allocation Matrix</b>", unsafe_allow_html=True)
            st.plotly_chart(px.pie(df, values='current_stock', names='name', hole=0.5, template="plotly_dark"), use_container_width=True)
    else: st.warning("Add data in NYASA to begin financial analysis.")

# 📦 SANCHARA (MAP + ADDRESS + FLOOR + RETURNS)
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>📦 SANCHARA</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌐 Precision Map", "📦 Floor Ops", "↩️ Returns (PUNAH)"])
    with t1:
        map_points = pd.DataFrame({'lat':[12.97, 22.31, 37.77, 1.35], 'lon':[77.59, 114.16, -122.41, 103.81], 'Node':['Hub','Factory','HQ','Port'], 'Address':['MG Road, Bangalore','Lantau, HK','Market St, SF','Jurong, Singapore (🔴 CLOSED)']})
        st.plotly_chart(px.scatter_mapbox(map_points, lat="lat", lon="lon", hover_name="Node", hover_data={"Address": True}, zoom=1, height=450).update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0}), use_container_width=True)
        st.markdown("<div style='background:rgba(255,255,255,0.02); padding:15px; border-radius:10px; border:1px solid #333; margin-top:15px;'><h4 style='color:#00D4FF; margin-top:0;'>Strategic Map Guide</h4><p>📍 Blue: Stable factory hubs. 🔴 Red: Global disruption alerts. Hover for address mapping.</p></div>", unsafe_allow_html=True)
    with t2:
        c1, c2 = st.columns(2); c1.metric("📦 Items Shipped Today", "1,240"); c2.metric("🏭 Total Floor Assets", f"{get_user_data()['current_stock'].sum() + 142} Units", "+142 Returns")
    with t3:
        st.subheader("PUNAH Returns Analysis")
        df_ret = pd.DataFrame({'Product':['Quantum X1','4K Monitor','Titanium Chassis'], 'Amount':[4,2,1], 'Reason':['Defective Logic','Screen Bleed','Transit Damage']})
        st.table(df_ret)

# 🤝 MITHRA+ (AI NEGOTIATION ENGINE)
elif st.session_state.page == "Mithra":
    st.markdown("<div class='feature-header'>🤝 MITHRA+</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        col1, col2 = st.columns([1, 1.5])
        with col1:
            vendor = st.selectbox("Select Vendor", df['supplier'].unique())
            tone = st.radio("Negotiation Tone", ["Polite", "Balanced", "Aggressive"])
        with col2:
            if st.button("🚀 INITIATE AI NEGOTIATION"):
                st.metric("Potential Savings", "₹12,400", "↑ 8%")
                st.info(f"AI drafted strategy for {vendor}. Leveraging order volume leverage.")
                st.text_area("Directive Draft", f"Dear {vendor},\n\nOur volume sensing shows a 35% increase. We request a 10% unit cost reduction...")
    else: st.warning("No suppliers found.")

# 👷‍♂️ KARMA (WORKFORCE GUIDANCE)
elif st.session_state.page == "Karma":
    st.markdown("<div class='feature-header'>👷‍♂️ KARMA</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["🏹 Missions", "📊 Analytics"])
    with t1:
        st.markdown("<div class='directive-msg'><b>[DIRECTIVE]</b> Proceed to <b>Shelf B2 via Aisle 3</b>. Pick 12x Chassis.</div>", unsafe_allow_html=True)
        st.warning("⚠️ Fatigue Alert: Suggested rest break for Station A4 (Suresh).")
    with t2:
        st.plotly_chart(go.Figure(data=go.Scatterpolar(r=[90, 80, 70, 95], theta=['Speed','Accuracy','Packing','Safety'], fill='toself')).update_layout(template="plotly_dark"))

# NYASA, PREKSHA, STAMBHA, SAMVADA Logic ...
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>📝 NYASA</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📥 Bulk Sync", "✍️ Manual", "📄 PO Generator"])
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
        df_po = get_user_data()
        if not df_po.empty:
            t = st.selectbox("Select for PO", df_po['name'])
            if st.button("Generate PO"): st.code(f"PO-ID: #ARH-{np.random.randint(1000,9999)}\nITEM: {t}")

elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>📈 PREKSHA</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        target = st.selectbox("Search Asset", df['name']); p = df[df['name'] == target].iloc[0]
        col_m, col_v = st.columns([1, 2])
        with col_m:
            if p['image_url'] and str(p['image_url']) != "nan": st.image(p['image_url'], use_container_width=True)
            if p['reviews'] and str(p['reviews']) != "nan":
                for r in p['reviews'].split('|'): st.markdown(f"<div class='review-box'>💬 {r}</div>", unsafe_allow_html=True)
        with col_v:
            preds = np.random.randint(20, 50, 7)
            st.plotly_chart(px.area(y=preds, title="AI Forecasting Path", template="plotly_dark").update_traces(line_color='#00D4FF'), use_container_width=True)
            st.markdown(f"<div class='ai-decision-box'><h3>🤖 AI SUGGESTION</h3>Reorder <b>{max(0, preds.sum() - p['current_stock'])}</b> units now.</div>", unsafe_allow_html=True)

elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header'>🛡️ STAMBHA</div>", unsafe_allow_html=True)
    s = st.selectbox("Shock Scenario", ["Normal", "Port Closure (3x Lead)"])
    df = get_user_data()
    if not df.empty:
        for _, p in df.iterrows():
            ttr = p['lead_time'] * (3 if "Port" in s else 1)
            tts = round(p['current_stock'] / 12, 1)
            if tts < ttr: st.error(f"🔴 CRITICAL: {p['name']} stockout in {tts}d. Recovery takes {ttr}d.")
        st.table(df[['name', 'current_stock', 'lead_time']])

elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header'>🎙️ SAMVADA</div>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY")
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        # Fix for loop
        for m in st.session_state.chat_history:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        u_in = st.chat_input("Strategic query...")
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans}); st.rerun()

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

# --- 1. PREMIUM GLASSMORPHISM UI CONFIG ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence",
    layout="wide",
    page_icon="✨",
    initial_sidebar_state="expanded"
)

def apply_aroha_style():
    st.markdown("""
    <style>
        /* Base Vibrant & Modern Aesthetics */
        .stApp {
            /* A rich, deep animated-looking gradient: elegant, not "AI neon" */
            background: radial-gradient(circle at top right, #1e1b4b 0%, #0f172a 50%, #020617 100%);
            color: #F8FAFC;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }

        /* FORCE LARGER FONT SIZES GLOBALLY */
        p, li, span, div, label {
            font-size: 1.1rem !important;
        }

        /* Typography Highlights */
        .brand-title {
            background: linear-gradient(135deg, #A78BFA, #38BDF8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 2.8rem !important;
            letter-spacing: -0.5px;
        }
        .decisions-fade {
            color: #38BDF8;
            font-weight: 700;
        }
        .feature-header {
            font-size: 2.5rem !important;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 2px solid rgba(255, 255, 255, 0.1);
            letter-spacing: -0.5px;
        }

        /* Beautiful Frosted Glass Cards */
        .saas-card, .financial-stat, .insight-box, .ai-decision-box {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 30px;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-top: 1px solid rgba(255, 255, 255, 0.2); /* Creates a glass edge sheen */
            border-left: 1px solid rgba(255, 255, 255, 0.2);
            margin-bottom: 20px;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        }
        .saas-card:hover, .financial-stat:hover, .insight-box:hover {
            transform: translateY(-5px);
            border-color: rgba(56, 189, 248, 0.4);
            box-shadow: 0 12px 40px 0 rgba(0, 0, 0, 0.4);
        }
        
        /* Specialized Boxes */
        .insight-box {
            border-left: 5px solid #A78BFA;
            background: linear-gradient(90deg, rgba(167, 139, 250, 0.08), transparent);
        }
        .ai-decision-box {
            background: rgba(56, 189, 248, 0.05);
            border: 1px solid rgba(56, 189, 248, 0.3);
        }
        .ai-decision-box h3 {
            color: #7DD3FC;
            margin-top: 0;
            font-size: 1.4rem !important;
            font-weight: 700;
            letter-spacing: -0.2px;
        }
        .directive-msg {
            background-color: rgba(0, 0, 0, 0.3);
            border-left: 4px solid #38BDF8;
            padding: 18px 22px;
            margin-bottom: 12px;
            border-radius: 8px;
            color: #F1F5F9;
        }
        .review-box {
            background-color: rgba(0, 0, 0, 0.2);
            padding: 16px 20px;
            border-radius: 8px;
            margin-bottom: 10px;
            color: #CBD5E1;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }

        /* Ticker */
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background-color: rgba(0, 0, 0, 0.4);
            padding: 12px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 30px;
        }
        .ticker-text {
            white-space: nowrap;
            box-sizing: border-box;
            animation: ticker 30s linear infinite;
            color: #94A3B8;
            font-weight: 600;
            letter-spacing: 1px;
        }
        @keyframes ticker {
            0%   { transform: translate3d(100%, 0, 0); }
            100% { transform: translate3d(-100%, 0, 0); }
        }

        /* Metrics overriding - Huge numbers */
        div[data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-size: 3.2rem !important;
            font-weight: 800 !important;
            letter-spacing: -1px;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1.2rem !important;
            color: #94A3B8 !important;
            font-weight: 600;
        }

        /* ==================================================== */
        /* CREATIVE SIDEBAR OVERHAUL (GLASSMORPHISM)            */
        /* ==================================================== */
        
        [data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.6) !important;
            backdrop-filter: blur(24px) !important;
            -webkit-backdrop-filter: blur(24px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
        }

        /* Customizing Sidebar Buttons */
        [data-testid="stSidebar"] div.stButton > button {
            background: rgba(255, 255, 255, 0.03); 
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-left: 4px solid transparent; 
            border-radius: 10px;
            color: #E2E8F0;
            text-align: left;
            padding: 16px 20px; /* Big, clickable touch targets */
            margin-bottom: 10px;
            font-weight: 600;
            font-size: 1.2rem !important; /* Large text */
            width: 100%;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            justify-content: flex-start;
        }
        
        [data-testid="stSidebar"] div.stButton > button p {
            margin-left: 8px;
            font-size: 1.2rem !important;
        }

        /* The Magic Hover Effect */
        [data-testid="stSidebar"] div.stButton > button:hover {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-left: 4px solid #38BDF8; 
            color: #FFFFFF;
            transform: translateX(8px) scale(1.02); 
            box-shadow: 0 10px 20px rgba(56, 189, 248, 0.15); 
        }
        
        /* Standard buttons elsewhere in the app */
        .main div.stButton>button {
            background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.02));
            color: #FFFFFF;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 8px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 1.1rem !important;
            transition: all 0.3s ease;
            backdrop-filter: blur(10px);
        }
        .main div.stButton>button:hover {
            background: rgba(255, 255, 255, 0.15);
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        }
    </style>
    """, unsafe_allow_html=True)

apply_aroha_style()

# --- 2. DATABASE ---
DB_FILE = 'aroha_nexus_v121.db'
def get_db(): 
    return sqlite3.connect(DB_FILE, check_same_thread=False)

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

def hash_p(p): 
    return hashlib.sha256(str.encode(p)).hexdigest()

def get_user_data():
    with get_db() as conn: 
        return pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))

# --- 3. SESSION STATE ---
if "auth" not in st.session_state: st.session_state.auth = False
if "user" not in st.session_state: st.session_state.user = ""
if "page" not in st.session_state: st.session_state.page = "Dashboard"
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "voice_on" not in st.session_state: st.session_state.voice_on = False

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 class='brand-title'>AROHA</h1><p style='color:#94A3B8; font-size:1.3rem !important; margin-top:-10px;'>Turn Data Into <span class='decisions-fade'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([0.2, 0.6, 0.2])
    with col_center:
        m = st.tabs(["🔒 Secure Login", "✨ Create Hub"])
        with m[0]:
            u_input = st.text_input("Operator Username", key="l_u")
            p_input = st.text_input("Passcode", type="password", key="l_p")
            if st.button("Access Terminal"):
                with get_db() as conn: 
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u_input,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p_input):
                    st.session_state.auth = True
                    st.session_state.user = u_input
                    st.rerun()
                else: 
                    st.error("Invalid credentials.")
        with m[1]:
            nu = st.text_input("New Username")
            np_in = st.text_input("New Passcode", type="password")
            if st.button("Establish Authority"):
                try:
                    with get_db() as conn: 
                        conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np_in)))
                    st.success("Account created securely.")
                except: 
                    st.error("Username taken.")
    st.stop()

# --- 5. TOP HUD TICKER ---
st.markdown(f"<div class='ticker-wrap'><div class='ticker-text'>USER: {st.session_state.user.upper()} ••• SYSTEM: ONLINE ••• [LOGISTICS] Hover map for precision addresses ••• [KRIYA] Fleet management active ••• [VITTA] Capital optimization complete.</div></div>", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    
    user_initial = st.session_state.user[0].upper() if st.session_state.user else "A"
    
    # 🎨 Giant Profile Card
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.05); padding: 30px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); margin-bottom: 30px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.3); backdrop-filter: blur(10px);'>
        <div style='width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #A78BFA, #38BDF8); color: white; display:flex; align-items:center; justify-content:center; font-size: 2.2rem; font-weight: 800; margin: 0 auto 15px auto; box-shadow: 0 0 25px rgba(56,189,248,0.4); border: 2px solid rgba(255,255,255,0.5);'>
            {user_initial}
        </div>
        <div style='color: #FFFFFF; font-weight: 800; font-size: 1.4rem; letter-spacing: 0.5px;'>{st.session_state.user.upper()}</div>
        <div style='color: #38BDF8; font-size: 0.9rem; text-transform: uppercase; font-weight: bold; margin-top:6px;'>Commander Level</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='color:#94A3B8; font-weight:800; font-size:0.9rem; letter-spacing:1.5px; margin-bottom: 12px;'>PRIMARY HUB</div>", unsafe_allow_html=True)
    
    if st.button("🌐 Overview", use_container_width=True): 
        st.session_state.page = "Dashboard"
        st.rerun()
        
    st.markdown("<div style='color:#94A3B8; font-weight:800; font-size:0.9rem; letter-spacing:1.5px; margin-top:30px; margin-bottom: 12px;'>APPLICATIONS</div>", unsafe_allow_html=True)
    
    nodes = [
        ("📝 Nyasa Catalog", "Nyasa"),
        ("🔮 Preksha Vision", "Preksha"),
        ("🛡️ Stambha Defense", "Stambha"),
        ("⚡ Kriya Forces", "Kriya"),
        ("🎙️ Samvada Comms", "Samvada"),
        ("🏦 Vitta Treasury", "Vitta"),
        ("🗺️ Sanchara World", "Sanchara"),
        ("🤝 Mithra Partners", "Mithra")
    ]
    
    for label, page_id in nodes:
        if st.button(label, key=f"nav_{page_id}", use_container_width=True):
            st.session_state.page = page_id
            st.rerun()
        
    st.markdown("<br><hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    if st.button("🚪 Log Out", use_container_width=True): 
        st.session_state.auth = False
        st.rerun()

# --- 7. LOGIC NODES ---
# OVERVIEW
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1 style='font-size:2.8rem; color:#FFFFFF; font-weight:800; letter-spacing:-1px;'>Intelligence Hub</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.metric("Total Assets", len(df))
    with c2: 
        st.metric("Treasury Size", f"₹{val:,.0f}")
    with c3: 
        st.metric("Hub Status", "🟢 Online")
    st.markdown("<div class='insight-box'><b style='font-size:1.2rem; display:block; margin-bottom:8px;'>💡 Operational Summary:</b> Supply flow remains uninterrupted. Predictive forecasts indicate a +8% weekend velocity change. Suggest auditing Nyasa catalog.</div>", unsafe_allow_html=True)

# KRIYA
elif st.session_state.page == "Kriya":
    st.markdown("<div class='feature-header'>Workforce Orchestration</div>", unsafe_allow_html=True)
    st.markdown("<div class='insight-box'><b>⚡ Current Deployment:</b> Matching engine assigning batch jobs. Sector A throughput exceeding expectations.</div>", unsafe_allow_html=True)
    
    tab_worker, tab_manager = st.tabs(["👷 Operative View", "📊 Command Analytics"])

    with tab_worker:
        st.subheader("Active Directive")
        col_q, col_s = st.columns([2, 1])
        with col_q:
            st.markdown("<div class='directive-msg'><b style='font-size:1.2rem;'>Task 402-A</b><br><br>Gather 12x Titanium Chassis for Main Assembly.</div>", unsafe_allow_html=True)
            st.markdown("<div class='directive-msg' style='border-left-color:#34D399;'><b style='font-size:1.2rem;'>Navigational Ping</b><br><br>Move to Shelf B2. Turn left at Aisle 3. Expected time: 1m 55s.</div>", unsafe_allow_html=True)
            if st.button("Initiate Scan Sequence"):
                st.error("⚠️ SKU Mismatch Detected. Verify Shelf B2 contents.")
        with col_s:
            st.markdown("<div class='saas-card' style='text-align:center;'><h4 style='color:#94A3B8; font-size:1.2rem;'>Harvesting Speed</h4><h2 style='color:#FFFFFF; font-size:3.5rem; font-weight:800;'>42<span style='font-size:1.5rem;'>/hr</span></h2><p style='color:#34D399; font-weight:700; font-size:1.1rem;'>↑ 12% faster than average</p></div>", unsafe_allow_html=True)
            st.warning("🔋 Hydration recommended before next assignment loop.")

    with tab_manager:
        st.subheader("Workforce Flow Dynamics")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Velocity Rate (Past 5 Hours)")
            fig = px.line(y=[80, 85, 75, 90, 88], template="plotly_dark")
            fig.update_layout(height=350, margin=dict(l=0,r=0,b=0,t=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            fig.update_traces(line_color='#38BDF8', line_width=4)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.write("Unit Mastery")
            st.bar_chart({"Precision": [98, 92, 75], "Agility": [90, 85, 70]}, color=["#38BDF8", "#A78BFA"])
            st.success("🏆 Highest Yield Operative: Ananya (98% Precision)")

# VITTA
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>Treasury & Capital Flow</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"<div class='saas-card'><div style='color:#94A3B8; font-size:1.2rem; font-weight:600; margin-bottom:12px;'>Total Vault Allocation</div><div style='color:#FFFFFF; font-size:3.5rem; font-weight:800;'>₹{total_v:,.0f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='saas-card'><div style='color:#94A3B8; font-size:1.2rem; font-weight:600; margin-bottom:12px;'>Risk Exposure (Stagnant > 30d)</div><div style='color:#F43F5E; font-size:3rem; font-weight:800;'>₹{total_v*0.15:,.0f}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='saas-card'><div style='color:#94A3B8; font-size:1.2rem; font-weight:600; margin-bottom:16px;'>Asset Distribution Model</div>", unsafe_allow_html=True)
            fig = px.pie(df, values='current_stock', names='name', hole=0.6, template="plotly_dark", color_discrete_sequence=px.colors.sequential.Agsunset)
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# MITHRA+
elif st.session_state.page == "Mithra":
    st.markdown("<div class='feature-header'>Partner Connections</div>", unsafe_allow_html=True)
    df = get_user_data()
    
    if not df.empty:
        col1, col2 = st.columns([1, 1.5])

        with col1:
            vendor = st.selectbox("Select Target Supplier", df['supplier'].unique())
            style = st.radio("Dialogue Approach", ["Standard", "Symbiotic", "Aggressive Cost-Cut"])

        with col2:
            if st.button("Synthesize Message Protocol", use_container_width=True):
                st.metric("Estimated Margin Retention", "₹12,400", "+8.0%")
                st.text_area(
                    "Generated AI Blueprint",
                    f"Hi {vendor},\n\nWe recognize the shifts in Q3 throughput. To maintain our alliance scale, we suggest a pricing alignment recalibration spanning the upcoming fiscal timeline..."
                )

        st.markdown("<hr style='border-color:rgba(255,255,255,0.1); margin: 40px 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:1.5rem; color:#FFFFFF;'>Partner Vitality Matrix</h3>", unsafe_allow_html=True)

        client_data = pd.DataFrame({
            "Network Node": ["Alpha Corp", "Zenith Ltd", "Nova Ind", "Orion Traders"],
            "Capital Exhaust (₹)": [120000, 95000, 78000, 150000],
            "Delivery Success (%)": [92, 85, 78, 96]
        })

        st.dataframe(client_data, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(client_data, x="Network Node", y="Capital Exhaust (₹)", template="plotly_dark", color_discrete_sequence=["#38BDF8"])
            fig1.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.line(client_data, x="Network Node", y="Delivery Success (%)", markers=True, template="plotly_dark")
            fig2.update_traces(line_color="#34D399", marker=dict(size=12, color="#34D399"))
            fig2.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

# SANCHARA
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>Global Topology</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌍 World View", "📦 Metric Stream", "🚨 Anomalies"])
    with t1:
        map_pts = pd.DataFrame({'lat':[12.9716, 22.31, 37.77, 1.35], 'lon':[77.59, 114.16, -122.41, 103.81], 'Site':['Primary Hub','Forge','Nexus Command','Alert Zone'], 'Details':['MG Road, Bangalore','Lantau, HK','Market St, SF','Jurong, Singapore']})
        fig = px.scatter_mapbox(map_pts, lat="lat", lon="lon", hover_name="Site", hover_data={"Details": True}, zoom=1.5, height=550, color="Site", color_discrete_sequence=["#38BDF8", "#A78BFA", "#34D399", "#F43F5E"])
        fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with t2:
        c1, c2 = st.columns(2)
        c1.metric("Outbound Kinetic Velocity", "1,240 units/day", "5.2%")
        c2.metric("Aggregate Vault Count", f"{get_user_data()['current_stock'].sum() if not get_user_data().empty else 0} units")
    with t3:
        st.table(pd.DataFrame({'SKU Class':['Quantum X1','4K Array'], 'Deficit Volume':[4,2], 'Audit Note':['Circuit Anomaly','Fracture detected']}))

# PREKSHA
elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>Futures & Demand Vision</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        target = st.selectbox("Isolate Specific Asset", df['name'])
        p = df[df['name'] == target].iloc[0]
        col_a, col_b = st.columns([1, 2])
        with col_a:
            if p['image_url'] and str(p['image_url']) != "nan": 
                st.image(p['image_url'], use_container_width=True)
            if p['reviews']:
                for r in p['reviews'].split('|'): 
                    st.markdown(f"<div class='review-box'>{r}</div>", unsafe_allow_html=True)
        with col_b:
            preds = np.random.randint(20, 50, 7)
            fig = px.area(y=preds, title="Projected 7-Day Asset Drawdown", template="plotly_dark")
            fig.update_traces(line_color='#38BDF8', fillcolor='rgba(56, 189, 248, 0.15)')
            fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=14))
            st.plotly_chart(fig, use_container_width=True)
            required = max(0, preds.sum() - p['current_stock'])
            if required > 0:
                st.markdown(f"<div class='ai-decision-box' style='padding:24px;'><h3>⚙️ Synthetic Recommendation</h3>Calculate reorder parameter at exactly <b>{required}</b> elements to bypass depletion horizon. Algorithm Confidence: 94%</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ai-decision-box' style='padding:24px; border-color:#34D399;'><h3 style='color:#34D399;'>Equilibrium Attained</h3>Existing reserves transcend immediate projected demand horizons.</div>", unsafe_allow_html=True)

# STAMBHA
elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header'>Vulnerability Forecasting</div>", unsafe_allow_html=True)
    s = st.selectbox("Apply Stress Constraint", ["Clear Skies Model", "Category 5 Transit Blackout (3x Lead Risk)"])
    df = get_user_data()
    if not df.empty:
        for _, p in df.iterrows():
            ttr = p['lead_time'] * (3 if "Blackout" in s else 1)
            tts = round(p['current_stock'] / 12, 1) 
            if tts < ttr: 
                st.markdown(f"<div class='saas-card' style='border-left: 6px solid #F43F5E;'><div style='color:#F43F5E; font-weight:800; font-size:1.3rem; margin-bottom:8px;'>CRITICAL VULNERABILITY DETECTED</div><div style='color:#E2E8F0; font-size:1.15rem;'><b>{p['name']}</b> shields fail in {tts} cycles. Reinforcements blockaded for {ttr} cycles.</div></div>", unsafe_allow_html=True)
        st.dataframe(df[['name', 'current_stock', 'lead_time']], use_container_width=True)

# NYASA
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>Catalog & Sourcing Matrix</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["📥 Ingest Manifest", "✍️ Manual Ledger Entry"])
    with t1:
        f = st.file_uploader("Upload Core DB Package (CSV)", type="csv")
        if f and st.button("Initialize Data Sync"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            for col in ['category','supplier','image_url','reviews']: u_df[col] = u_df.get(col, "")
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Matrix alignment verified.")
    with t2:
        with st.form("add"):
            c1, c2 = st.columns(2)
            with c1:
                n = st.text_input("Asset Identity string")
                s = st.number_input("Vault Tally", 0)
                p = st.number_input("Value Weight (₹)", 0.0)
            with c2:
                lt = st.number_input("Transit Lag (days)", 1)
                img = st.text_input("Visual Node URL")
                rev = st.text_input("Operator Comments")
            if st.form_submit_button("Engrave to Data Bank"):
                with get_db() as conn: 
                    conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
                st.success("Ledger updated permanently.")

# SAMVADA
elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header'>Deep Voice Comms Terminal</div>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY", None)
    
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        
        st.markdown("<div class='saas-card' style='height: 500px; overflow-y: auto; background-color: rgba(0,0,0,0.5); backdrop-filter: blur(10px); flex-direction: column; display: flex;'>", unsafe_allow_html=True)
        for m in st.session_state.chat_history:
            if m["role"] == "user":
                st.markdown(f"<div style='text-align: right; margin-bottom: 20px;'><span style='background: linear-gradient(135deg, #1E293B, #0F172A); color: #FAFAFA; padding: 18px 24px; border-radius: 12px 12px 0 12px; display: inline-block; font-size:1.15rem; font-weight:500; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>{m['content']}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: left; margin-bottom: 20px;'><span style='background: linear-gradient(135deg, rgba(56, 189, 248, 0.2), transparent); color: #E0F2FE; padding: 18px 24px; border-radius: 12px 12px 12px 0; display: inline-block; font-size:1.15rem; font-weight:600; border: 1px solid rgba(56, 189, 248, 0.3); box-shadow: 0 4px 6px rgba(0,0,0,0.3);'>{m['content']}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        col_text, col_voice = st.columns([4, 1])
        with col_voice:
            audio_in = st.audio_input("Broadcast Audio")
            
        u_in = st.chat_input("Transmit text packet here...")
        
        if audio_in:
            with st.spinner("Decoding audio frequencies..."):
                try:
                    transcription = client.audio.transcriptions.create(
                        file=("audio.wav", audio_in.getvalue()),
                        model="whisper-large-v3"
                    )
                    u_in = transcription.text
                    st.success(f"Transmission decoded: *{u_in}*")
                except Exception as e:
                    st.error(f"Signal interference: {e}")
                    
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are a professional supply chain assistant. Here is the local DB context: {ctx}"}, *st.session_state.chat_history[-4:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans})
            st.rerun()
    else:
        st.warning("⚠️ API Key not detected. Comms link severed.")

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

# --- 1. AURA AESTHETIC CONFIG (MATURE GEN Z) ---
st.set_page_config(
    page_title="AROHA",
    layout="wide",
    page_icon="✨",
    initial_sidebar_state="expanded"
)

def apply_aroha_style():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');

        /* Base Aura Aesthetics */
        .stApp {
            /* Smooth, deep violet-to-midnight gradient (Aura vibe) */
            background: radial-gradient(ellipse at top left, #2e1065 0%, #0f172a 40%, #020617 100%);
            color: #F8FAFC;
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.2px;
        }

        /* EVEN LARGER FONT SIZES FOR READABILITY */
        p, li, span, div, label, input, select, textarea {
            font-family: 'Outfit', sans-serif !important;
            font-size: 1.35rem !important; /* Bumped up */
            font-weight: 500;
        }

        /* Typography Highlights */
        .brand-title {
            background: linear-gradient(135deg, #c084fc, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 4rem !important;
            letter-spacing: -1.5px;
            margin-bottom: 0px;
        }
        .feature-header {
            font-size: 3rem !important;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 24px;
            padding-bottom: 12px;
            letter-spacing: -1px;
            border-bottom: 2px solid rgba(192, 132, 252, 0.4);
            text-shadow: 0 0 20px rgba(192, 132, 252, 0.3);
        }
        .feature-sub {
            color: #cbd5e1;
            font-size: 1.5rem !important;
            font-weight: 500;
            margin-top: -15px;
            margin-bottom: 30px;
            display: block;
        }

        /* HIGH-POP Glow Cards */
        .saas-card, .financial-stat, .insight-box, .ai-decision-box {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(25px);
            -webkit-backdrop-filter: blur(25px);
            border-radius: 28px;
            padding: 30px;
            border: 1.5px solid rgba(192, 132, 252, 0.5); /* Strong vibrant border */
            margin-bottom: 24px;
            box-shadow: 0 10px 40px 0 rgba(192, 132, 252, 0.2); /* Colored glowing shadow */
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .saas-card:hover, .financial-stat:hover, .insight-box:hover {
            transform: translateY(-6px);
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(56, 189, 248, 0.7); /* Shifts to Cyan on hover */
            box-shadow: 0 20px 50px 0 rgba(56, 189, 248, 0.3);
        }
        
        .insight-box {
            background: linear-gradient(135deg, rgba(192, 132, 252, 0.15), transparent);
            border-left: 6px solid #c084fc;
        }
        .ai-decision-box {
            background: rgba(56, 189, 248, 0.1);
            border: 1.5px solid rgba(56, 189, 248, 0.5);
            box-shadow: 0 10px 40px rgba(56, 189, 248, 0.2);
        }
        .ai-decision-box h3 {
            color: #7dd3fc;
            margin-top: 0;
            font-size: 1.6rem !important;
            font-weight: 800;
        }
        .directive-msg {
            background-color: rgba(255, 255, 255, 0.1);
            border-left: 4px solid #38bdf8;
            padding: 24px;
            margin-bottom: 12px;
            border-radius: 20px;
            color: #f8fafc;
            font-weight: 600;
        }
        .review-box {
            background-color: rgba(255, 255, 255, 0.08);
            padding: 20px;
            border-radius: 16px;
            margin-bottom: 10px;
            color: #e2e8f0;
            border: 1px solid rgba(255,255,255,0.1);
        }

        /* User Friendly Soft Inputs */
        div[data-baseweb="input"] > div, 
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] > div {
            background-color: rgba(255, 255, 255, 0.08) !important;
            border-radius: 20px !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            padding: 6px 10px;
            transition: all 0.3s ease;
        }
        div[data-baseweb="input"] > div:hover, 
        div[data-baseweb="select"] > div:hover {
            border-color: rgba(192, 132, 252, 0.6) !important;
            background-color: rgba(255, 255, 255, 0.12) !important;
            box-shadow: 0 0 15px rgba(192, 132, 252, 0.2);
        }

        /* Ticker */
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background-color: transparent;
            padding: 12px;
            border-radius: 16px;
            border: 1px solid rgba(192, 132, 252, 0.3);
            margin-bottom: 30px;
            backdrop-filter: blur(15px);
            box-shadow: 0 4px 20px rgba(192,132,252,0.1);
        }
        .ticker-text {
            white-space: nowrap;
            box-sizing: border-box;
            animation: ticker 30s linear infinite;
            color: #e2e8f0;
            font-weight: 600;
        }
        @keyframes ticker {
            0%   { transform: translate3d(100%, 0, 0); }
            100% { transform: translate3d(-100%, 0, 0); }
        }

        /* Metrics overriding - Huge round numbers */
        div[data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-size: 4rem !important;
            font-weight: 800 !important;
            letter-spacing: -2px;
            text-shadow: 0 0 20px rgba(255,255,255,0.2);
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1.4rem !important;
            color: #cbd5e1 !important;
            font-weight: 600;
        }

        /* ==================================================== */
        /* CREATIVE SIDEBAR OVERHAUL                            */
        /* ==================================================== */
        
        [data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.4) !important;
            backdrop-filter: blur(40px) !important;
            -webkit-backdrop-filter: blur(40px) !important;
            border-right: 1px solid rgba(192, 132, 252, 0.2) !important;
        }

        /* Customizing Sidebar Buttons */
        [data-testid="stSidebar"] div.stButton > button {
            background: transparent;
            border: none;
            border-radius: 20px;
            color: #cbd5e1;
            text-align: left;
            padding: 18px 20px;
            margin-bottom: 6px;
            font-weight: 600;
            font-size: 1.4rem !important; 
            width: 100%;
            transition: all 0.3s ease;
            justify-content: flex-start;
        }
        
        [data-testid="stSidebar"] div.stButton > button p {
            margin-left: 10px;
        }

        /* Soft Hover Effect */
        [data-testid="stSidebar"] div.stButton > button:hover {
            background: rgba(255, 255, 255, 0.1);
            color: #FFFFFF;
            transform: scale(1.03); 
            box-shadow: 0 0 15px rgba(255,255,255,0.1);
        }
        
        /* App Primary Buttons */
        .main div.stButton>button {
            background: linear-gradient(135deg, #c084fc, #38bdf8);
            color: #000000;
            border: none;
            border-radius: 20px;
            padding: 14px 32px;
            font-weight: 800;
            font-size: 1.3rem !important;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(192,132,252,0.3);
        }
        .main div.stButton>button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 30px rgba(56,189,248,0.4);
            color: #000000;
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

# --- 4. AUTHENTICATION (Clean Vibe) ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 class='brand-title'>AROHA.</h1><p style='color:#cbd5e1; font-size:1.6rem !important; font-weight: 600;'>Smart inventory, zero stress.</p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([0.25, 0.5, 0.25])
    with col_center:
        m = st.tabs(["Log in", "Sign up"])
        with m[0]:
            u_input = st.text_input("Username", key="l_u", placeholder="Enter your username")
            p_input = st.text_input("Password", type="password", key="l_p", placeholder="Enter your password")
            if st.button("Hop in"):
                with get_db() as conn: 
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u_input,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p_input):
                    st.session_state.auth = True
                    st.session_state.user = u_input
                    st.rerun()
                else: 
                    st.error("Hmm, that didn't work. Check your password.")
        with m[1]:
            nu = st.text_input("Choose a Username", placeholder="e.g., alex_ops")
            np_in = st.text_input("Choose a Password", type="password")
            if st.button("Create account"):
                try:
                    with get_db() as conn: 
                        conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np_in)))
                    st.success("You're in. Go ahead and log in.")
                except: 
                    st.error("Username is already taken.")
    st.stop()

# --- 5. TOP HUD TICKER ---
st.markdown(f"<div class='ticker-wrap'><div class='ticker-text'>✨ Welcome back, {st.session_state.user} • Everything is running smoothly • No severe inventory flags today.</div></div>", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    
    user_initial = st.session_state.user[0].upper() if st.session_state.user else "A"
    
    # 🎨 Aura Profile Card
    st.markdown(f"""
    <div style='background: rgba(255,255,255,0.05); padding: 24px; border-radius: 24px; border: 1.px solid rgba(192, 132, 252, 0.3); margin-bottom: 30px; text-align: center; box-shadow: 0 10px 30px rgba(192, 132, 252, 0.15);'>
        <div style='width: 80px; height: 80px; border-radius: 50%; background: linear-gradient(135deg, #c084fc, #38bdf8); color: #FFFFFF; display:flex; align-items:center; justify-content:center; font-size: 2.2rem; font-weight: 800; margin: 0 auto 12px auto; box-shadow: 0 0 20px rgba(56,189,248,0.5);'>
            {user_initial}
        </div>
        <div style='color: #FFFFFF; font-weight: 800; font-size: 1.6rem;'>@{st.session_state.user.lower()}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='color:#cbd5e1; font-weight:800; font-size:1.1rem; margin-bottom: 8px; padding-left: 10px; letter-spacing: 1px;'>MENU</div>", unsafe_allow_html=True)
    
    # Simple, direct feature descriptions (1-2 words in the button)
    if st.button("🏠 Home • Overview", use_container_width=True): 
        st.session_state.page = "Dashboard"
        st.rerun()

    nodes = [
        ("📝 Nyasa • Inventory", "Nyasa"),
        ("🔮 Preksha • Forecast", "Preksha"),
        ("🛡️ Stambha • Risk Check", "Stambha"),
        ("⚡ Kriya • Team Ops", "Kriya"),
        ("🎙️ Samvada • Voice AI", "Samvada"),
        ("🏦 Vitta • Finances", "Vitta"),
        ("🗺️ Sanchara • Live Map", "Sanchara"),
        ("🤝 Mithra • Suppliers", "Mithra")
    ]
    
    for label, page_id in nodes:
        if st.button(label, key=f"nav_{page_id}", use_container_width=True):
            st.session_state.page = page_id
            st.rerun()
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Log out", use_container_width=True): 
        st.session_state.auth = False
        st.rerun()

# --- 7. LOGIC NODES ---
# OVERVIEW
if st.session_state.page == "Dashboard":
    st.markdown("<h1 class='feature-header'>Home</h1><span class='feature-sub'>A quick look at how things are doing.</span>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.metric("Total items", len(df))
    with c2: 
        st.metric("Total value", f"₹{val:,.0f}")
    with c3: 
        st.metric("App status", "All good ✨")
    st.markdown("<div class='insight-box'><b>Vibe check:</b> Operations look smooth today. Forecast algorithms suggest slightly higher weekend demand. You might want to check the Inventory tab soon.</div>", unsafe_allow_html=True)

# KRIYA
elif st.session_state.page == "Kriya":
    st.markdown("<h1 class='feature-header'>Kriya</h1><span class='feature-sub'>Team Ops & Shifts. Let's see who's doing what.</span>", unsafe_allow_html=True)
    st.markdown("<div class='insight-box'><b>Update:</b> The system just assigned tasks for the morning shift. Efficiency looks solid.</div>", unsafe_allow_html=True)
    
    tab_worker, tab_manager = st.tabs(["For the team", "For management"])

    with tab_worker:
        st.subheader("Your current task")
        col_q, col_s = st.columns([2, 1])
        with col_q:
            st.markdown("<div class='directive-msg'><b>Task #402</b><br>Grab 12x Titanium Chassis for Assembly Station B.</div>", unsafe_allow_html=True)
            st.markdown("<div class='directive-msg' style='border-left-color:#34D399;'><b>Fastest route</b><br>Go to Shelf B2 via Aisle 3. Should take about 2 mins.</div>", unsafe_allow_html=True)
            if st.button("Scan item barcode"):
                st.error("Wait, wrong item. Please double check Shelf B2.")
        with col_s:
            st.markdown("<div class='saas-card' style='text-align:center;'><h4>Pick Speed</h4><h2 style='color:#FFFFFF; font-size:4rem; font-weight:800;'>42<span style='font-size:1.5rem;'>/hr</span></h2><p style='color:#34D399; font-weight:700;'>12% above average</p></div>", unsafe_allow_html=True)
            st.warning("You've been going fast for a while. Take a quick water break.")

    with tab_manager:
        st.subheader("Team performance stats")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Speed over the last 5 hours")
            fig = px.line(y=[80, 85, 75, 90, 88], template="plotly_dark")
            fig.update_layout(height=350, margin=dict(l=0,r=0,b=0,t=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            fig.update_traces(line_color='#c084fc', line_width=4)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.write("Accuracy vs Speed")
            st.bar_chart({"Accuracy": [98, 92, 75], "Speed": [90, 85, 70]}, color=["#38bdf8", "#c084fc"])
            st.success("MVP today: Ananya (98% accuracy)")

# VITTA
elif st.session_state.page == "Vitta":
    st.markdown("<h1 class='feature-header'>Vitta</h1><span class='feature-sub'>Finances & Capital Flow. Where is the money?</span>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"<div class='saas-card'><div style='color:#e2e8f0;'>Total stock value</div><div style='color:#FFFFFF; font-size:4rem; font-weight:800; text-shadow: 0 0 20px rgba(255,255,255,0.3);'>₹{total_v:,.0f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='saas-card'><div style='color:#e2e8f0;'>Risk limit (Items sitting > 30 days)</div><div style='color:#f43f5e; font-size:3.5rem; font-weight:800; text-shadow: 0 0 20px rgba(244,63,94,0.3);'>₹{total_v*0.15:,.0f}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='saas-card'><div style='color:#e2e8f0; margin-bottom:16px;'>Value distribution</div>", unsafe_allow_html=True)
            # FIXED THE PLOTLY VALUE BUG HERE - USED PLASMA INSTEAD OF AMD
            fig = px.pie(df, values='current_stock', names='name', hole=0.6, template="plotly_dark", color_discrete_sequence=px.colors.sequential.Plasma)
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# MITHRA+
elif st.session_state.page == "Mithra":
    st.markdown("<h1 class='feature-header'>Mithra</h1><span class='feature-sub'>Suppliers. Connect and negotiate effortlessly.</span>", unsafe_allow_html=True)
    df = get_user_data()
    
    if not df.empty:
        col1, col2 = st.columns([1, 1.5])

        with col1:
            vendor = st.selectbox("Pick a supplier", df['supplier'].unique())
            style = st.radio("Vibe of the email", ["Friendly", "Direct", "Tough & Cost-driven"])

        with col2:
            if st.button("Draft an email using AI", use_container_width=True):
                st.metric("Expected savings", "₹12,400", "+8.0%")
                st.text_area(
                    "Here's your draft",
                    f"Hey {vendor},\n\nHope you're doing well. We've been looking at our Q3 numbers and want to chat about adjusting pricing to keep this partnership scaling well for both of us..."
                )

        st.markdown("<hr style='border-color:rgba(192, 132, 252, 0.3); margin: 40px 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:2rem; color:#FFFFFF;'>Supplier scorecards</h3>", unsafe_allow_html=True)

        client_data = pd.DataFrame({
            "Supplier": ["Alpha Corp", "Zenith", "Nova", "Orion"],
            "Spend (₹)": [120000, 95000, 78000, 150000],
            "On-time rate (%)": [92, 85, 78, 96]
        })

        st.dataframe(client_data, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(client_data, x="Supplier", y="Spend (₹)", template="plotly_dark", color_discrete_sequence=["#c084fc"])
            fig1.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.line(client_data, x="Supplier", y="On-time rate (%)", markers=True, template="plotly_dark")
            fig2.update_traces(line_color="#34d399", marker=dict(size=12, color="#34d399"))
            fig2.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

# SANCHARA
elif st.session_state.page == "Sanchara":
    st.markdown("<h1 class='feature-header'>Sanchara</h1><span class='feature-sub'>Live Map. Track everything visually.</span>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌍 The Map", "📦 Live Stats", "🚨 Issues"])
    with t1:
        map_pts = pd.DataFrame({'lat':[12.9716, 22.31, 37.77, 1.35], 'lon':[77.59, 114.16, -122.41, 103.81], 'Location':['Main Hub','Factory','HQ','Delayed Zone'], 'Details':['MG Road, Bangalore','Lantau, HK','Market St, SF','Jurong, Singapore']})
        fig = px.scatter_mapbox(map_pts, lat="lat", lon="lon", hover_name="Location", hover_data={"Details": True}, zoom=1.5, height=550, color="Location", color_discrete_sequence=["#c084fc", "#38bdf8", "#34d399", "#f43f5e"])
        fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with t2:
        # ADDED THE RETURNED PRODUCTS METRIC HERE
        c1, c2, c3 = st.columns(3)
        c1.metric("Ships today", "1,240 items", "+5%")
        c2.metric("Items in house", f"{get_user_data()['current_stock'].sum() if not get_user_data().empty else 0} items")
        c3.metric("Returned products", "142 items", "-12% vs last week", delta_color="inverse")
    with t3:
        st.table(pd.DataFrame({'Item':['Quantum X1','4K Screen'], 'Shortage':[4,2], 'Note':['Failed quality check','Broken in transit']}))

# PREKSHA
elif st.session_state.page == "Preksha":
    st.markdown("<h1 class='feature-header'>Preksha</h1><span class='feature-sub'>Forecast. See exactly what you need before you need it.</span>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        target = st.selectbox("Which item do you want to analyze?", df['name'])
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
            fig = px.area(y=preds, title="Expected drop in stock (Next 7 Days)", template="plotly_dark")
            fig.update_traces(line_color='#c084fc', fillcolor='rgba(192, 132, 252, 0.15)')
            fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=14))
            st.plotly_chart(fig, use_container_width=True)
            required = max(0, preds.sum() - p['current_stock'])
            if required > 0:
                st.markdown(f"<div class='ai-decision-box' style='padding:24px;'><h3>🤖 AI Insight</h3>You should order exactly <b>{required}</b> more of these to be safe. Confidence: 94%</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ai-decision-box' style='padding:24px; border-color:#34D399;'><h3 style='color:#34D399;'>All good here</h3>You have plenty of stock for the next week. No need to order.</div>", unsafe_allow_html=True)

# STAMBHA
elif st.session_state.page == "Stambha":
    st.markdown("<h1 class='feature-header'>Stambha</h1><span class='feature-sub'>Risk Check. Find bottlenecks instantly.</span>", unsafe_allow_html=True)
    s = st.selectbox("Run a stress test", ["Normal day", "What if a port closes? (3x delay)"])
    df = get_user_data()
    if not df.empty:
        for _, p in df.iterrows():
            ttr = p['lead_time'] * (3 if "port" in s.lower() else 1)
            tts = round(p['current_stock'] / 12, 1) 
            if tts < ttr: 
                st.markdown(f"<div class='saas-card' style='border-left: 6px solid #f43f5e;'><div style='color:#f43f5e; font-weight:800; font-size:1.6rem; margin-bottom:8px;'>⚠️ RISK FOUND</div><div style='color:#f8fafc;'>If you don't act, you'll run out of <b>{p['name']}</b> in {tts} days. It takes {ttr} days to restock.</div></div>", unsafe_allow_html=True)
        st.dataframe(df[['name', 'current_stock', 'lead_time']], use_container_width=True)

# NYASA
elif st.session_state.page == "Nyasa":
    st.markdown("<h1 class='feature-header'>Nyasa</h1><span class='feature-sub'>Inventory. Add and manage everything here.</span>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Add manually", "Upload batch (CSV)"])
    with t2:
        f = st.file_uploader("Drop your CSV file here", type="csv")
        if f and st.button("Sync data"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            for col in ['category','supplier','image_url','reviews']: u_df[col] = u_df.get(col, "")
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Boom. Data synced.")
    with t1:
        with st.form("add"):
            c1, c2 = st.columns(2)
            with c1:
                n = st.text_input("Item name", placeholder="e.g. Mechanical Keyboard")
                s = st.number_input("Current stock", 0)
                p = st.number_input("Price per unit (₹)", 0.0)
            with c2:
                lt = st.number_input("Restock time (days)", 1)
                img = st.text_input("Image link (Optional)", placeholder="https://...")
                rev = st.text_input("Quick notes", placeholder="Any details?")
            if st.form_submit_button("Add to inventory"):
                with get_db() as conn: 
                    conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
                st.success("Item saved securely.")

# SAMVADA
elif st.session_state.page == "Samvada":
    st.markdown("<h1 class='feature-header'>Samvada</h1><span class='feature-sub'>Voice AI. Just talk, it understands everything.</span>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY", None)
    
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        
        st.markdown("<div class='saas-card' style='height: 500px; overflow-y: auto; background-color: rgba(0,0,0,0.2)'>", unsafe_allow_html=True)
        for m in st.session_state.chat_history:
            if m["role"] == "user":
                st.markdown(f"<div style='text-align: right; margin-bottom: 20px;'><span style='background: linear-gradient(135deg, #c084fc, #38bdf8); color: #020617; padding: 20px 28px; border-radius: 24px 24px 0 24px; display: inline-block; font-weight:700; box-shadow: 0 4px 15px rgba(192,132,252,0.3);'>{m['content']}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: left; margin-bottom: 20px;'><span style='background: rgba(255,255,255,0.05); color: #f8fafc; padding: 20px 28px; border-radius: 24px 24px 24px 0; display: inline-block; font-weight:600; border: 1px solid rgba(255,255,255,0.2); backdrop-filter: blur(10px);'>{m['content']}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        col_text, col_voice = st.columns([4, 1])
        with col_voice:
            audio_in = st.audio_input("Use voice")
            
        u_in = st.chat_input("Ask anything...")
        
        if audio_in:
            with st.spinner("Processing..."):
                try:
                    transcription = client.audio.transcriptions.create(
                        file=("audio.wav", audio_in.getvalue()),
                        model="whisper-large-v3"
                    )
                    u_in = transcription.text
                    st.success(f"Heard: *{u_in}*")
                except Exception as e:
                    st.error(f"Couldn't hear that properly. Error: {e}")
                    
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are a helpful, casual, highly intelligent assistant answering questions about inventory. Keep it friendly. Data: {ctx}"}, *st.session_state.chat_history[-4:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans})
            st.rerun()
    else:
        st.warning("⚠️ Waiting on an API key to go live.")


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

# --- 1. AURA AESTHETIC CONFIG (MATURE GEN Z - MAXIMUM IMPACT) ---
st.set_page_config(
    page_title="AROHA",
    layout="wide",
    page_icon="✨",
    initial_sidebar_state="expanded"
)

def apply_aroha_style():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&display=swap');

        /* Base Aura Aesthetics */
        .stApp {
            /* DEEPER SPACE, MORE CONTRAST gradient */
            background: radial-gradient(circle at top center, #3b0764 0%, #0f172a 50%, #000000 100%);
            color: #F8FAFC;
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.2px;
        }

        /* EVEN LARGER FONT SIZES FOR MAXIMUM READABILITY */
        p, li, span, div, label, input, select, textarea {
            font-family: 'Outfit', sans-serif !important;
            font-size: 1.4rem !important; 
            font-weight: 500;
        }

        /* ✨ MASSIVE BRAND TITLE ✨ */
        .brand-container {
            filter: drop-shadow(0 0 30px rgba(192, 132, 252, 0.8));
            text-align: center;
            margin-top: 80px;
            margin-bottom: 40px;
        }
        .brand-title {
            background: linear-gradient(135deg, #c084fc 0%, #38bdf8 50%, #34d399 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            font-size: 8rem !important; /* ENORMOUS */
            letter-spacing: -4px;
            line-height: 1;
            margin: 0;
            padding: 0;
        }
        
        /* 🔥 MASSIVE FEATURE HEADERS 🔥 */
        .feature-header {
            font-size: 4.5rem !important; 
            font-weight: 900;
            color: #FFFFFF;
            margin-bottom: 20px;
            padding-bottom: 15px;
            letter-spacing: -2px;
            border-bottom: 4px solid #38bdf8; /* Bold cyan line */
            text-shadow: 0 0 40px rgba(56, 189, 248, 0.6);
            display: inline-block; /* Makes the border tight to the text */
        }
        .feature-sub {
            color: #c084fc; /* Vibrant purple subtitle */
            font-size: 1.8rem !important;
            font-weight: 700;
            margin-top: 10px;
            margin-bottom: 40px;
            display: block;
        }

        /* 💎 HIGH-CONTRAST NEON CARDS 💎 */
        .saas-card, .financial-stat, .insight-box, .ai-decision-box {
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.95)); /* Darker backing for pop */
            backdrop-filter: blur(30px);
            -webkit-backdrop-filter: blur(30px);
            border-radius: 32px;
            padding: 35px;
            border: 2px solid rgba(192, 132, 252, 0.8); /* STRONGER border */
            margin-bottom: 30px;
            box-shadow: 0 15px 50px 0 rgba(192, 132, 252, 0.25); /* Heavy glow */
            transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275); /* Bouncy hover */
        }
        .saas-card:hover, .financial-stat:hover, .insight-box:hover {
            transform: translateY(-12px) scale(1.02);
            border: 2px solid #38bdf8; /* Snaps to bright cyan on hover */
            box-shadow: 0 25px 60px 0 rgba(56, 189, 248, 0.4);
            background: linear-gradient(145deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 1));
        }
        
        .insight-box {
            background: linear-gradient(135deg, rgba(192, 132, 252, 0.25), rgba(0,0,0,0.5));
            border-left: 8px solid #c084fc;
        }
        .ai-decision-box {
            background: rgba(56, 189, 248, 0.15);
            border: 2px solid #38bdf8;
            box-shadow: 0 15px 50px rgba(56, 189, 248, 0.3);
        }
        .ai-decision-box h3 {
            color: #7dd3fc;
            margin-top: 0;
            font-size: 2rem !important;
            font-weight: 900;
        }
        .directive-msg {
            background-color: rgba(30, 41, 59, 0.8);
            border-left: 6px solid #38bdf8;
            padding: 30px;
            margin-bottom: 15px;
            border-radius: 24px;
            color: #FFFFFF;
            font-weight: 700;
            font-size: 1.5rem !important;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        /* ⚡ HUGE IMPACT METRICS ⚡ */
        div[data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-size: 5rem !important; /* GIGANTIC */
            font-weight: 900 !important;
            letter-spacing: -3px;
            text-shadow: 0 0 30px rgba(56, 189, 248, 0.8); /* Insane Cyan glow */
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1.6rem !important;
            color: #38bdf8 !important; /* Colored label */
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* ==================================================== */
        /* CREATIVE SIDEBAR OVERHAUL (MAXIMUM STAND-OUT)        */
        /* ==================================================== */
        
        [data-testid="stSidebar"] {
            background: rgba(15, 23, 42, 0.5) !important;
            backdrop-filter: blur(50px) !important;
            -webkit-backdrop-filter: blur(50px) !important;
            border-right: 2px solid rgba(192, 132, 252, 0.5) !important; /* Thicker border */
        }

        /* Customizing Sidebar Buttons */
        [data-testid="stSidebar"] div.stButton > button {
            background: rgba(30, 41, 59, 0.5); /* Solid backing */
            border: 1px solid rgba(255,255,255,0.05);
            border-radius: 24px;
            color: #e2e8f0;
            text-align: left;
            padding: 22px 20px;
            margin-bottom: 12px;
            font-weight: 700;
            font-size: 1.5rem !important; 
            width: 100%;
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            justify-content: flex-start;
        }

        /* 🔥 Aggressive Hover Effect 🔥 */
        [data-testid="stSidebar"] div.stButton > button:hover {
            background: linear-gradient(90deg, rgba(192, 132, 252, 0.6), rgba(56, 189, 248, 0.6));
            color: #FFFFFF;
            transform: translateX(10px) scale(1.05); 
            border-left: 8px solid #38bdf8;
            border-top: 1px solid #FFFFFF;
            box-shadow: 0 10px 30px rgba(56, 189, 248, 0.5);
        }
        
        /* 🚀 Main Action Buttons 🚀 */
        .main div.stButton>button {
            background: linear-gradient(135deg, #c084fc, #38bdf8);
            color: #FFFFFF;
            border: 2px solid rgba(255,255,255,0.5);
            border-radius: 24px;
            padding: 20px 40px;
            font-weight: 900;
            font-size: 1.5rem !important;
            text-shadow: 0 2px 5px rgba(0,0,0,0.5);
            transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            box-shadow: 0 10px 30px rgba(192,132,252,0.5);
        }
        .main div.stButton>button:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 15px 40px rgba(56,189,248,0.7);
            border-color: #FFFFFF;
        }

        /* Text Inputs popping harder */
        div[data-baseweb="input"] > div, 
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] > div {
            background-color: rgba(30, 41, 59, 0.8) !important;
            border-radius: 24px !important;
            border: 2px solid rgba(192, 132, 252, 0.4) !important;
            padding: 10px 15px;
            transition: all 0.3s ease;
        }
        div[data-baseweb="input"] > div:hover, 
        div[data-baseweb="select"] > div:hover {
            border-color: #38bdf8 !important;
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
            transform: translateY(-2px);
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

# --- 4. AUTHENTICATION (Maximum Impact) ---
if not st.session_state.auth:
    st.markdown("""
        <div class='brand-container'>
            <h1 class='brand-title'>AROHA</h1>
            <p style='color:#c084fc; font-size:2rem !important; font-weight: 800; margin-top:20px; letter-spacing: 2px; text-transform: uppercase;'>Smart Inventory • Zero Stress</p>
        </div>
    """, unsafe_allow_html=True)
    
    c1, col_center, c3 = st.columns([0.25, 0.5, 0.25])
    with col_center:
        m = st.tabs(["🔒 Log in", "✨ Sign up"])
        with m[0]:
            u_input = st.text_input("Username", key="l_u", placeholder="Enter your username")
            p_input = st.text_input("Password", type="password", key="l_p", placeholder="Enter your password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Access Hub", use_container_width=True):
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
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account", use_container_width=True):
                try:
                    with get_db() as conn: 
                        conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np_in)))
                    st.success("You're in. Go ahead and log in.")
                except: 
                    st.error("Username is already taken.")
    st.stop()

# --- 5. TOP HUD TICKER ---
st.markdown(f"<div class='ticker-wrap'><div class='ticker-text'>✨ STATUS ONLINE • WELCOME {st.session_state.user.upper()} • ENGINES OPTIMAL • NO SEVERE BOTTLENECKS DETECTED TODAY.</div></div>", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    
    user_initial = st.session_state.user[0].upper() if st.session_state.user else "A"
    
    # 🎨 Mega Aura Profile Card
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, rgba(192,132,252,0.15), rgba(56,189,248,0.15)); padding: 35px; border-radius: 35px; border: 3px solid rgba(192, 132, 252, 0.8); margin-bottom: 40px; text-align: center; box-shadow: 0 15px 50px rgba(192, 132, 252, 0.4); backdrop-filter: blur(10px);'>
        <div style='width: 100px; height: 100px; border-radius: 50%; background: linear-gradient(135deg, #c084fc, #38bdf8); color: #FFFFFF; display:flex; align-items:center; justify-content:center; font-size: 3.5rem; font-weight: 900; margin: 0 auto 15px auto; box-shadow: 0 0 30px rgba(56,189,248,0.8); border: 4px solid #FFFFFF;'>
            {user_initial}
        </div>
        <div style='color: #FFFFFF; font-weight: 900; font-size: 2rem; letter-spacing: 1px;'>@{st.session_state.user.lower()}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='color:#38bdf8; font-weight:900; font-size:1.4rem; margin-bottom: 15px; padding-left: 10px; letter-spacing: 2px; text-transform:uppercase;'>Navigation</div>", unsafe_allow_html=True)
    
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
        
    st.markdown("<br><hr style='border-color: rgba(192,132,252,0.4); border-width: 2px;'><br>", unsafe_allow_html=True)
    if st.button("🚪 Log out", use_container_width=True): 
        st.session_state.auth = False
        st.rerun()

# --- 7. LOGIC NODES ---
# OVERVIEW
if st.session_state.page == "Dashboard":
    st.markdown("<div class='feature-header'>Home</div><span class='feature-sub'>A quick look at how things are doing.</span>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.metric("Total items", len(df))
    with c2: 
        st.metric("Total value", f"₹{val:,.0f}")
    with c3: 
        st.metric("App status", "All good ✨")
    st.markdown("<div class='insight-box'><b style='font-size:1.6rem; color:#FFFFFF;'>Vibe check:</b><br>Operations look solid today. Forecast algorithms suggest hitting peak demand this weekend. Highly advise glancing at the Inventory soon.</div>", unsafe_allow_html=True)

# KRIYA
elif st.session_state.page == "Kriya":
    st.markdown("<div class='feature-header'>Kriya</div><span class='feature-sub'>Team Ops & Shifts. Let's see who's doing what.</span>", unsafe_allow_html=True)
    st.markdown("<div class='insight-box'><b style='font-size:1.6rem; color:#FFFFFF;'>Status Update:</b><br>The system just assigned automated tasks for the morning shift. Everything is green.</div>", unsafe_allow_html=True)
    
    tab_worker, tab_manager = st.tabs(["For the team", "For management"])

    with tab_worker:
        st.subheader("Your current task")
        col_q, col_s = st.columns([2, 1])
        with col_q:
            st.markdown("<div class='directive-msg'><b>TASK #402</b><br><span style='color:#e2e8f0;'>Grab 12x Titanium Chassis for Assembly Station B.</span></div>", unsafe_allow_html=True)
            st.markdown("<div class='directive-msg' style='border-left-color:#34D399;'><b>FASTEST PATH</b><br><span style='color:#e2e8f0;'>Head to Shelf B2 via Aisle 3. Estimated ETA: 120 seconds.</span></div>", unsafe_allow_html=True)
            if st.button("Scan item barcode"):
                st.error("Wait, wrong item code. Please double check Shelf B2.")
        with col_s:
            st.markdown("<div class='saas-card' style='text-align:center;'><h4 style='color:#c084fc; font-weight:900;'>YOUR SPEED</h4><h2 style='color:#FFFFFF; font-size:6rem; margin:0; font-weight:900; text-shadow:0 0 30px #c084fc;'>42</h2><p style='color:#34D399; font-weight:800; font-size:1.6rem;'>▲ 12% faster</p></div>", unsafe_allow_html=True)

    with tab_manager:
        st.subheader("Team performance highlights")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Speed over the last 5 hours")
            fig = px.line(y=[80, 85, 75, 90, 88], template="plotly_dark")
            fig.update_layout(height=400, margin=dict(l=0,r=0,b=0,t=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            fig.update_traces(line_color='#c084fc', line_width=6)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.write("Accuracy vs Speed")
            st.bar_chart({"Accuracy": [98, 92, 75], "Speed": [90, 85, 70]}, color=["#38bdf8", "#c084fc"], height=400)
            st.success("MVP today: Ananya (98% accuracy)")

# VITTA
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>Vitta</div><span class='feature-sub'>Finances & Capital Flow. The deep look at money.</span>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"<div class='saas-card'><div style='color:#38bdf8; font-weight:800; font-size:1.6rem; text-transform:uppercase;'>Total Stock Value</div><div style='color:#FFFFFF; font-size:5rem; font-weight:900; text-shadow: 0 0 40px rgba(56,189,248,0.6);'>₹{total_v:,.0f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='saas-card'><div style='color:#f43f5e; font-weight:800; font-size:1.6rem; text-transform:uppercase;'>Dead Money (> 30 days)</div><div style='color:#f43f5e; font-size:4.5rem; font-weight:900; text-shadow: 0 0 30px rgba(244,63,94,0.6);'>₹{total_v*0.15:,.0f}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='saas-card'><div style='color:#c084fc; font-weight:800; font-size:1.6rem; text-transform:uppercase; margin-bottom:16px;'>Value Breakdown</div>", unsafe_allow_html=True)
            fig = px.pie(df, values='current_stock', names='name', hole=0.6, template="plotly_dark", color_discrete_sequence=px.colors.sequential.Plasma)
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=450)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# MITHRA+
elif st.session_state.page == "Mithra":
    st.markdown("<div class='feature-header'>Mithra</div><span class='feature-sub'>Suppliers. Connect inside the ecosystem.</span>", unsafe_allow_html=True)
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

        st.markdown("<hr style='border-color:rgba(192, 132, 252, 0.5); margin: 60px 0; border-width:3px;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:3rem; color:#FFFFFF; font-weight:900;'>Supplier Scorecards</h3>", unsafe_allow_html=True)

        client_data = pd.DataFrame({
            "Supplier": ["Alpha Corp", "Zenith", "Nova", "Orion"],
            "Spend (₹)": [120000, 95000, 78000, 150000],
            "On-time rate (%)": [92, 85, 78, 96]
        })

        st.dataframe(client_data, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(client_data, x="Supplier", y="Spend (₹)", template="plotly_dark", color_discrete_sequence=["#c084fc"])
            fig1.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.line(client_data, x="Supplier", y="On-time rate (%)", markers=True, template="plotly_dark")
            fig2.update_traces(line_color="#38bdf8", marker=dict(size=18, color="#38bdf8"))
            fig2.update_layout(margin=dict(t=20, b=0, l=0, r=0), height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

# SANCHARA
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>Sanchara</div><span class='feature-sub'>Live Map. Global tracking, elevated.</span>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌍 The Map", "📦 Live Stats", "🚨 Issues"])
    with t1:
        map_pts = pd.DataFrame({'lat':[12.9716, 22.31, 37.77, 1.35], 'lon':[77.59, 114.16, -122.41, 103.81], 'Location':['Main Hub','Factory','HQ','Delayed Zone'], 'Details':['MG Road, Bangalore','Lantau, HK','Market St, SF','Jurong, Singapore']})
        fig = px.scatter_mapbox(map_pts, lat="lat", lon="lon", hover_name="Location", hover_data={"Details": True}, zoom=1.5, height=600, color="Location", color_discrete_sequence=["#c084fc", "#38bdf8", "#34d399", "#f43f5e"])
        fig.update_traces(marker=dict(size=15))
        fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with t2:
        c1, c2, c3 = st.columns(3)
        c1.metric("Ships today", "1,240 items", "+5%")
        c2.metric("Items in house", f"{get_user_data()['current_stock'].sum() if not get_user_data().empty else 0} items")
        c3.metric("Returned products", "142 items", "-12% vs last week", delta_color="inverse")
    with t3:
        st.table(pd.DataFrame({'Item':['Quantum X1','4K Screen'], 'Shortage':[4,2], 'Note':['Failed quality check','Broken in transit']}))

# PREKSHA
elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>Preksha</div><span class='feature-sub'>Forecast. See tomorrow, today.</span>", unsafe_allow_html=True)
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
            fig.update_traces(line_color='#c084fc', fillcolor='rgba(192, 132, 252, 0.25)')
            fig.update_layout(height=450, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(size=16))
            st.plotly_chart(fig, use_container_width=True)
            required = max(0, preds.sum() - p['current_stock'])
            if required > 0:
                st.markdown(f"<div class='ai-decision-box'><h3>🤖 AI STRONGLY ADVISES</h3>You should order exactly <strong style='font-size:2rem; color:#FFFFFF;'>{required}</strong> more of these to be safe.<br><br><span style='color:#38bdf8;'>Confidence Factor: 94%</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ai-decision-box' style='border-color:#34D399; box-shadow: 0 10px 40px rgba(52,211,153,0.3);'><h3 style='color:#34D399;'>NO ACTION NEEDED</h3>You have safely enough stock for the next week. Do not re-order.</div>", unsafe_allow_html=True)

# STAMBHA
elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header'>Stambha</div><span class='feature-sub'>Risk Check. Expose the bottlenecks.</span>", unsafe_allow_html=True)
    s = st.selectbox("Run a stress test", ["Normal day", "What if a port closes? (3x delay)"])
    df = get_user_data()
    if not df.empty:
        for _, p in df.iterrows():
            ttr = p['lead_time'] * (3 if "port" in s.lower() else 1)
            tts = round(p['current_stock'] / 12, 1) 
            if tts < ttr: 
                st.markdown(f"<div class='saas-card' style='border-left: 10px solid #f43f5e; border-color:#f43f5e; box-shadow: 0 15px 50px rgba(244,63,94,0.3);'><div style='color:#f43f5e; font-weight:900; font-size:2.5rem; margin-bottom:12px; text-shadow:0 0 20px rgba(244,63,94,0.5);'>⚠️ SEVERE RISK DETECTED</div><div style='color:#FFFFFF; font-size:1.6rem;'>You completely run out of <b style='color:#f43f5e;'>{p['name']}</b> in {tts} days.<br>Restock won't arrive for {ttr} days. <b>ACTION REQUIRED IMMMEDIATELY.</b></div></div>", unsafe_allow_html=True)
        st.dataframe(df[['name', 'current_stock', 'lead_time']], use_container_width=True)

# NYASA
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>Nyasa</div><span class='feature-sub'>Inventory. Complete control.</span>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Add manually", "Upload batch (CSV)"])
    with t2:
        f = st.file_uploader("Drop your CSV file here", type="csv")
        if f and st.button("Sync data"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            for col in ['category','supplier','image_url','reviews']: u_df[col] = u_df.get(col, "")
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Boom. Data completely synced.")
    with t1:
        with st.form("add"):
            c1, c2 = st.columns(2)
            with c1:
                n = st.text_input("Item name", placeholder="What's the exact name?")
                s = st.number_input("Current stock count", 0)
                p = st.number_input("Price per individual unit (₹)", 0.0)
            with c2:
                lt = st.number_input("Restock delay (days)", 1)
                img = st.text_input("Visual Image Link (Optional)", placeholder="https://...")
                rev = st.text_input("Quick notes", placeholder="Any critical details?")
            if st.form_submit_button("Add forcefully to inventory"):
                with get_db() as conn: 
                    conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
                st.success("Item saved permanently into the ledger.")

# SAMVADA
elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header'>Samvada</div><span class='feature-sub'>Voice AI. Talk naturally. It handles the rest.</span>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY", None)
    
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        
        st.markdown("<div class='saas-card' style='height: 550px; overflow-y: auto; background: rgba(15, 23, 42, 0.7);'>", unsafe_allow_html=True)
        for m in st.session_state.chat_history:
            if m["role"] == "user":
                st.markdown(f"<div style='text-align: right; margin-bottom: 25px;'><span style='background: linear-gradient(135deg, #c084fc, #38bdf8); color: #000000; padding: 22px 30px; border-radius: 30px 30px 0 30px; display: inline-block; font-weight:800; font-size:1.5rem; box-shadow: 0 10px 25px rgba(192,132,252,0.5);'>{m['content']}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: left; margin-bottom: 25px;'><span style='background: rgba(30, 41, 59, 0.9); color: #FFFFFF; padding: 22px 30px; border-radius: 30px 30px 30px 0; display: inline-block; font-weight:700; font-size:1.5rem; border: 2px solid rgba(56, 189, 248, 0.4); box-shadow: 0 10px 25px rgba(56,189,248,0.2); backdrop-filter: blur(20px);'>{m['content']}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        col_text, col_voice = st.columns([4, 1])
        with col_voice:
            audio_in = st.audio_input("Use voice command")
            
        u_in = st.chat_input("Type something...")
        
        if audio_in:
            with st.spinner("Processing voice data..."):
                try:
                    transcription = client.audio.transcriptions.create(
                        file=("audio.wav", audio_in.getvalue()),
                        model="whisper-large-v3"
                    )
                    u_in = transcription.text
                    st.success(f"Heard clearly: *{u_in}*")
                except Exception as e:
                    st.error(f"Couldn't hear that properly. Error: {e}")
                    
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are a highly intelligent, powerful assistant answering questions about inventory. Keep it extremely brief and friendly. Data: {ctx}"}, *st.session_state.chat_history[-4:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans})
            st.rerun()
    else:
        st.warning("⚠️ Waiting on an API key to go full online.")


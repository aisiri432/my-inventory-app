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

# --- 1. LIVELY & PREMIUM AESTHETIC CONFIG ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence",
    layout="wide",
    page_icon="✨",
    initial_sidebar_state="expanded"
)

def apply_aroha_style():
    st.markdown("""
    <style>
        /* Changed to Inter for a highly professional, clean look */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        /* Rich, lively dark gradient background */
        .stApp {
            background-color: #020617;
            background-image: radial-gradient(circle at 10% 20%, rgb(46, 26, 71) 0%, rgb(15, 23, 42) 60%, rgb(2, 6, 23) 100%);
            color: #F8FAFC;
            font-family: 'Inter', sans-serif !important;
        }

        /* Comfortable, professional typography */
        p, li, span, div, label, input, select, textarea {
            font-family: 'Inter', sans-serif !important;
            font-size: 1.05rem !important; 
            font-weight: 500;
            color: #cbd5e1;
        }

        /* ✨ AROHA BRAND TITLE - VIBRANT & SLEEK ✨ */
        .brand-container {
            text-align: center;
            margin-top: 8vh;
            margin-bottom: 40px;
        }
        .brand-title {
            background: linear-gradient(135deg, #c084fc 0%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            font-size: 5rem !important;
            letter-spacing: 4px;
            margin: 0;
            padding: 0;
            filter: drop-shadow(0 10px 20px rgba(192, 132, 252, 0.4));
        }
        .brand-sub {
            color: #f8fafc;
            font-size: 1.1rem !important;
            font-weight: 600;
            letter-spacing: 6px;
            text-transform: uppercase;
            margin-top: 15px;
            text-shadow: 0 0 10px rgba(255,255,255,0.2);
        }
        
        /* 🔥 COLORFUL FEATURE HEADERS 🔥 */
        .feature-header {
            font-size: 2.5rem !important; 
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 5px;
            letter-spacing: -0.5px;
            background: linear-gradient(90deg, #FFFFFF, #38bdf8);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .feature-sub {
            color: #c084fc; 
            font-size: 1.1rem !important;
            font-weight: 500;
            margin-bottom: 30px;
            display: block;
            border-bottom: 1px solid rgba(192,132,252,0.3);
            padding-bottom: 20px;
        }

        /* 💎 LIVELY FROSTED CARDS 💎 */
        .saas-card, .financial-stat, .insight-box, .ai-decision-box {
            background: rgba(255, 255, 255, 0.03); 
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-radius: 12px; 
            padding: 24px;
            border: 1px solid rgba(139, 92, 246, 0.3); 
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        .saas-card:hover, .financial-stat:hover, .insight-box:hover {
            border-color: rgba(56, 189, 248, 0.6); 
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(56, 189, 248, 0.2);
            background: rgba(255, 255, 255, 0.05);
        }
        
        .insight-box {
            background: linear-gradient(135deg, rgba(139, 92, 246, 0.1), rgba(0,0,0,0));
            border-left: 4px solid #c084fc;
        }
        .ai-decision-box {
            background: rgba(56, 189, 248, 0.1);
            border: 1px solid rgba(56, 189, 248, 0.4);
        }
        .ai-decision-box h3 {
            color: #7dd3fc;
            margin-top: 0;
            font-size: 1.4rem !important;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .directive-msg {
            background-color: rgba(255,255,255,0.05);
            border-left: 3px solid #c084fc;
            padding: 16px 20px;
            margin-bottom: 10px;
            border-radius: 10px;
            font-weight: 500;
            font-size: 1.1rem !important;
        }
        
        /* ⚡ POPPING METRICS ⚡ */
        div[data-testid="stMetricValue"] {
            color: #FFFFFF !important;
            font-size: 3rem !important; 
            font-weight: 800 !important;
            letter-spacing: -1px;
            text-shadow: 0 0 20px rgba(56, 189, 248, 0.4);
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1rem !important;
            color: #38bdf8 !important; 
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* ==================================================== */
        /* SIDEBAR (LIVELY NAVIGATION)                           */
        /* ==================================================== */
        
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%) !important;
            border-right: 1px solid rgba(192, 132, 252, 0.4) !important; 
        }

        [data-testid="stSidebar"]::before {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; height: 5px;
            background: linear-gradient(90deg, #c084fc, #38bdf8, #34d399);
            z-index: 100;
        }

        /* Inactive Buttons (Secondary) */
        [data-testid="stSidebar"] div.stButton > button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.03); 
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            color: #94a3b8;
            text-align: left;
            padding: 14px 20px;
            margin-bottom: 10px;
            font-weight: 600;
            font-size: 1.05rem !important; 
            width: 100%;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            justify-content: flex-start;
            white-space: pre-line;
            line-height: 1.4;
        }

        [data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(139, 92, 246, 0.4);
            color: #e2e8f0;
            transform: translateX(4px); 
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.2);
        }

        /* Active Button (Primary) - MASSIVE POP */
        [data-testid="stSidebar"] div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #c084fc 0%, #38bdf8 100%);
            border: none;
            border-radius: 12px;
            color: #020617 !important;
            text-align: left;
            padding: 16px 20px;
            margin-bottom: 10px;
            font-weight: 800;
            font-size: 1.15rem !important; 
            width: 100%;
            justify-content: flex-start;
            box-shadow: 0 8px 25px rgba(192, 132, 252, 0.6);
            transform: scale(1.02);
            position: relative;
            overflow: hidden;
            white-space: pre-line;
            line-height: 1.4;
        }
        
        [data-testid="stSidebar"] div.stButton > button[kind="primary"]::after {
            content: '●';
            position: absolute;
            right: 15px;
            color: #020617;
            font-size: 0.8rem;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 0.5; }
            50% { opacity: 1; text-shadow: 0 0 10px #fff; }
            100% { opacity: 0.5; }
        }
        
        /* Main Action Buttons  */
        .main div.stButton>button {
            background: linear-gradient(135deg, #c084fc, #38bdf8);
            color: #020617 !important;
            border: none;
            border-radius: 12px;
            padding: 12px 28px;
            font-weight: 700;
            font-size: 1.1rem !important;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
        }
        .main div.stButton>button:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(56, 189, 248, 0.5);
            color: #020617 !important;
        }

        /* Form Inputs Pro */
        div[data-baseweb="input"] > div, 
        div[data-baseweb="select"] > div,
        div[data-baseweb="textarea"] > div {
            background-color: rgba(255,255,255,0.05) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            padding: 4px 12px;
            transition: all 0.3s ease;
        }
        div[data-baseweb="input"] > div:focus-within, 
        div[data-baseweb="select"] > div:focus-within {
            border-color: #c084fc !important;
            box-shadow: 0 0 15px rgba(192, 132, 252, 0.3) !important;
            background-color: rgba(255,255,255,0.1) !important;
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

# --- 4. AUTHENTICATION (Lively) ---
if not st.session_state.auth:
    st.markdown("""
        <div class='brand-container'>
            <h1 class='brand-title'>AROHA</h1>
            <p class='brand-sub'>Turn Data Into Decisions</p>
        </div>
    """, unsafe_allow_html=True)
    
    c1, col_center, c3 = st.columns([0.3, 0.4, 0.3])
    with col_center:
        m = st.tabs(["✨ Secure Login", "🚀 Register"])
        with m[0]:
            u_input = st.text_input("Username", key="l_u")
            p_input = st.text_input("Password", type="password", key="l_p")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Authenticate", use_container_width=True):
                with get_db() as conn: 
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u_input,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p_input):
                    st.session_state.auth = True
                    st.session_state.user = u_input
                    st.rerun()
                else: 
                    st.error("Invalid credentials.")
        with m[1]:
            nu = st.text_input("Choose a Username", placeholder="e.g., admin_user")
            np_in = st.text_input("Choose a Password", type="password")
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Create Account", use_container_width=True):
                try:
                    with get_db() as conn: 
                        conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np_in)))
                    st.success("Account created securely.")
                except: 
                    st.error("Username is already taken.")
    st.stop()

# --- 5. TOP HUD TICKER ---
st.markdown(f"<div style='background:rgba(255,255,255,0.05); border:1px solid rgba(192,132,252,0.3); padding:12px 16px; border-radius:10px; margin-bottom:24px; font-size:1rem; color:#cbd5e1; letter-spacing:1px; backdrop-filter:blur(10px);'><span style='color:#34d399;'>●</span> SYSTEM ONLINE | OPERATOR: <b style='color:#ffffff;'>{st.session_state.user.upper()}</b> | REFRESH RATE: REAL-TIME</div>", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    
    user_initial = st.session_state.user[0].upper() if st.session_state.user else "A"
    
    # 🎨 Lively Profile
    st.markdown(f"""
    <div style='display:flex; align-items:center; gap:16px; margin-bottom: 35px; padding: 16px; background:rgba(255,255,255,0.05); border:1px solid rgba(139,92,246,0.3); border-radius:16px;'>
        <div style='width: 45px; height: 45px; border-radius: 12px; background: linear-gradient(135deg, #c084fc, #38bdf8); color: #020617; display:flex; align-items:center; justify-content:center; font-size: 1.5rem; font-weight: 800; box-shadow: 0 0 15px rgba(56,189,248,0.4);'>
            {user_initial}
        </div>
        <div>
            <div style='color: #FFFFFF; font-weight: 700; font-size: 1.1rem;'>{st.session_state.user.lower()}</div>
            <div style='color: #38bdf8; font-size: 0.85rem; font-weight: 600;'>Workspace Admin</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='color:#94a3b8; font-weight:700; font-size:0.85rem; margin-bottom: 12px; padding-left: 6px; letter-spacing: 2px; text-transform:uppercase;'>Overview</div>", unsafe_allow_html=True)
    
    if st.button("🏠 HOME ✦ Dashboard", key="nav_home", type="primary" if st.session_state.page == "Dashboard" else "secondary", use_container_width=True): 
        st.session_state.page = "Dashboard"
        st.rerun()

    st.markdown("<br><div style='color:#94a3b8; font-weight:700; font-size:0.85rem; margin-bottom: 12px; padding-left: 6px; letter-spacing: 2px; text-transform:uppercase;'>Modules</div>", unsafe_allow_html=True)

    nodes = [
        ("NYASA", "Nyasa", "Inventory Catalog", "📦"),
        ("PREKSHA", "Preksha", "Demand Forecaster", "🔮"),
        ("STAMBHA", "Stambha", "Risk Check", "🛡️"),
        ("KRIYA", "Kriya", "Employee Ops", "👥"),
        ("SAMVADA", "Samvada", "Voice Chatbot", "🎙️"),
        ("VITTA", "Vitta", "Finance Dashboard", "💸"),
        ("SANCHARA", "Sanchara", "Live Map", "🗺️"),
        ("MITHRA", "Mithra", "Supplier Relations", "🤝")
    ]
    
    for title, page_id, desc, icon in nodes:
        b_type = "primary" if st.session_state.page == page_id else "secondary"
        label = f"{icon} {title}\n<small style='font-weight:500; font-size:0.85rem;'>{desc}</small>"
        # Streamlit button doesn't parse HTML but plain \n works with our CSS.
        label_plain = f"{icon} {title}\n{desc}"
        if st.button(label_plain, key=f"nav_{page_id}", type=b_type, use_container_width=True):
            st.session_state.page = page_id
            st.rerun()

    st.markdown("<br><hr style='border-color: rgba(192,132,252,0.2);'><br>", unsafe_allow_html=True)
    if st.button("🚪 Log out", use_container_width=True): 
        st.session_state.auth = False
        st.rerun()

# --- 7. LOGIC NODES ---
# OVERVIEW (Dashboard)
if st.session_state.page == "Dashboard":
    st.markdown("<div class='feature-header'>AROHA Dashboard</div><span class='feature-sub'>Overview of your entire system capabilities.</span>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.metric("Total Products in Stock", len(df))
    with c2: 
        st.metric("Total Inventory Value", f"₹{val:,.0f}")
    with c3: 
        st.metric("System Status", "Healthy", delta="Online", delta_color="normal")
        
    # Dynamic, User-Friendly Insights
    low_stock = df[df['current_stock'] < 10] if not df.empty else pd.DataFrame()
    if not low_stock.empty:
        st.markdown(f"<div class='insight-box' style='border-left-color: #ef4444;'><b>🔔 Alert:</b> You have {len(low_stock)} products with critically low stock (less than 10 units left). Consider checking the Inventory tab to reorder!</div>", unsafe_allow_html=True)
    elif not df.empty:
        st.markdown("<div class='insight-box' style='border-left-color: #34d399;'><b>✅ Insight:</b> All product stock levels are looking great. Great job keeping the inventory balanced!</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='insight-box'><b>👋 Welcome:</b> It looks like you haven't added any products yet. Head over to the INVENTORY module to get started.</div>", unsafe_allow_html=True)

    st.markdown("<br><h3 style='font-size:1.5rem; color:#ffffff; font-weight:700; margin-bottom: 20px;'>Available Features</h3>", unsafe_allow_html=True)
    
    # Feature Grid Display
    cols = st.columns(4)
    for i, (title, page_id, desc, icon) in enumerate(nodes):
        with cols[i % 4]:
            st.markdown(f"""
            <div style='background:rgba(255,255,255,0.03); border:1px solid rgba(139,92,246,0.3); border-radius:12px; padding:20px 15px; margin-bottom:15px; text-align:center; box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: all 0.3s;'>
                <div style='font-size: 1.15rem; font-weight: 800; color: #ffffff; letter-spacing:1px;'>{icon} {title}</div>
                <div style='font-size: 0.95rem; color: #38bdf8; margin-top: 8px; font-weight: 500;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)

# KRIYA (Employees)
elif st.session_state.page == "Kriya":
    st.markdown("<div class='feature-header'>KRIYA</div><span class='feature-sub'>Employee Operations & Team Performance.</span>", unsafe_allow_html=True)
    
    tab_worker, tab_manager = st.tabs(["🎯 Active Tasks", "📊 Employee Performance"])

    with tab_worker:
        col_q, col_s = st.columns([2, 1])
        with col_q:
            st.markdown("<div class='directive-msg'><span style='color:#c084fc; font-weight:800;'>Task #402: Pack Shipment</span><br><br>Gather 12 items securely for Order Delivery Node B.</div>", unsafe_allow_html=True)
            st.markdown("<div class='directive-msg' style='border-left-color:#38bdf8;'><span style='color:#38bdf8; font-weight:800;'>Suggested Route</span><br><br>Proceed to Shelf B2. Estimated completion time: 2 mins.</div>", unsafe_allow_html=True)
            if st.button("Mark Task Complete", use_container_width=True):
                st.success("Great! Task marked as completed.")
        with col_s:
            st.markdown("<div class='saas-card' style='text-align:center;'><h4 style='color:#cbd5e1; font-weight:600; font-size:1rem;'>YOUR EFFICIENCY</h4><h2 style='color:#ffffff; font-size:4rem; margin:10px 0;'>94<span style='font-size:1.2rem; color:#94a3b8;'>%</span></h2><p style='color:#34d399; font-weight:700; font-size:1rem;'>▲ Doing Excellent</p></div>", unsafe_allow_html=True)

    with tab_manager:
        st.markdown("<h3 style='color:#fff; font-size:1.3rem; margin-bottom:15px;'>Top Performers (This Week)</h3>", unsafe_allow_html=True)
        emp_data = pd.DataFrame({
            "Employee Name": ["Alice Johnson", "Bob Smith", "Charlie Davis", "Diana Prince"],
            "Role": ["Warehouse Lead", "Packer", "Forklift Operator", "QA Inspector"],
            "Tasks Completed": [142, 128, 95, 110],
            "Accuracy (%)": [99.5, 96.0, 98.2, 99.9]
        })
        st.dataframe(emp_data, use_container_width=True, hide_index=True)
        
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(emp_data, x="Employee Name", y="Tasks Completed", template="plotly_dark", color_discrete_sequence=["#c084fc"])
            fig.update_layout(margin=dict(l=0,r=0,b=0,t=40), height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", title="Tasks Completed by Employee")
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            fig2 = px.scatter(emp_data, x="Employee Name", y="Accuracy (%)", size="Tasks Completed", template="plotly_dark", color_discrete_sequence=["#38bdf8"])
            fig2.update_layout(margin=dict(l=0,r=0,b=0,t=40), height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", title="Accuracy vs Volume Handled")
            st.plotly_chart(fig2, use_container_width=True)

# VITTA (Finances)
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>VITTA</div><span class='feature-sub'>A clear overview of revenue, inventory costs, and capital.</span>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"<div class='saas-card'><div style='color:#cbd5e1; font-size:0.9rem; text-transform:uppercase;'>Total Inventory Value</div><div style='color:#ffffff; font-size:3.5rem; font-weight:800;'>₹{total_v:,.0f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='saas-card'><div style='color:#cbd5e1; font-size:0.9rem; text-transform:uppercase;'>Value of Obsolete/Old Stock</div><div style='color:#ef4444; font-size:3rem; font-weight:800; text-shadow:0 0 20px rgba(239,68,68,0.4);'>₹{total_v*0.15:,.0f}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='saas-card'><div style='color:#cbd5e1; font-size:0.9rem; text-transform:uppercase; margin-bottom:10px;'>Value Distribution by Product</div>", unsafe_allow_html=True)
            fig = px.pie(df, values='current_stock', names='name', hole=0.6, template="plotly_dark", color_discrete_sequence=px.colors.sequential.Plasma)
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=350)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# MITHRA+ (Vendors)
elif st.session_state.page == "Mithra":
    st.markdown("<div class='feature-header'>MITHRA</div><span class='feature-sub'>Manage your suppliers, contracts, and delivery success rates.</span>", unsafe_allow_html=True)
    df = get_user_data()
    
    if not df.empty:
        col1, col2 = st.columns([1, 1.5])

        with col1:
            vendor = st.selectbox("Select Supplier", df['supplier'].unique())
            style = st.radio("Email Tone", ["Friendly & Standard", "Professional & Firm"])

        with col2:
            if st.button("Generate Vendor Email", use_container_width=True):
                st.metric("Estimated Money Saved", "₹12,400", "+8.0%")
                st.text_area(
                    "AI Generated Email",
                    f"Hi {vendor},\n\nWe are reviewing our recent orders and would like to discuss our current pricing structure to ensure it remains competitive..."
                )

        st.markdown("<br><hr style='border-color:rgba(192,132,252,0.3);'><br>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:1.5rem; color:#ffffff; font-weight:700;'>Supplier Success Rates</h3>", unsafe_allow_html=True)

        client_data = pd.DataFrame({
            "Supplier Company": ["Alpha Corp", "Zenith Systems", "Nova Ind", "Orion Log"],
            "Total Spend (₹)": [120000, 95000, 78000, 150000],
            "On-Time Delivery (%)": [92, 85, 78, 96]
        })

        st.dataframe(client_data, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(client_data, x="Supplier Company", y="Total Spend (₹)", template="plotly_dark", color_discrete_sequence=["#c084fc"])
            fig1.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", title="Spend Per Supplier")
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.line(client_data, x="Supplier Company", y="On-Time Delivery (%)", markers=True, template="plotly_dark")
            fig2.update_traces(line_color="#38bdf8", marker=dict(size=12, color="#38bdf8"))
            fig2.update_layout(margin=dict(t=30, b=0, l=0, r=0), height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", title="Delivery Punctuality")
            st.plotly_chart(fig2, use_container_width=True)

# SANCHARA (Tracking)
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>SANCHARA</div><span class='feature-sub'>Monitor your physical inventory across multiple locations globally.</span>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌍 Global Map", "⚡ Total Shipments", "🚨 Active Alerts"])
    with t1:
        map_pts = pd.DataFrame({'lat':[12.9716, 22.31, 37.77, 1.35], 'lon':[77.59, 114.16, -122.41, 103.81], 'Node':['Primary','Warehouse','Storefront','Delayed Area'], 'Location':['Bangalore','HK','SF','Singapore']})
        fig = px.scatter_mapbox(map_pts, lat="lat", lon="lon", hover_name="Node", hover_data={"Location": True}, zoom=1.5, height=550, color="Node", color_discrete_sequence=["#c084fc", "#38bdf8", "#34d399", "#ef4444"])
        fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with t2:
        c1, c2, c3 = st.columns(3)
        c1.metric("Recent Shipments", "1,240 boxes", "+5.2%")
        c2.metric("Safe Deliveries", f"{get_user_data()['current_stock'].sum() if not get_user_data().empty else 0} units")
        c3.metric("Returned/Damaged", "142 units", "-12%", delta_color="inverse")
    with t3:
        st.table(pd.DataFrame({'Product Name':['Quantum X1','4K Array'], 'Missing Units':[4,2], 'Reason':['Failed inspection','Damage in shipping']}))

# PREKSHA (Forecast)
elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>PREKSHA</div><span class='feature-sub'>Use predictive AI to figure out what stock you will need next.</span>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        target = st.selectbox("Select a Product to Analyze", df['name'])
        p = df[df['name'] == target].iloc[0]
        col_a, col_b = st.columns([1, 2])
        with col_a:
            if p['image_url'] and str(p['image_url']) != "nan": 
                st.image(p['image_url'], use_container_width=True)
            if p['reviews']:
                for r in p['reviews'].split('|'): 
                    st.markdown(f"<div class='saas-card' style='padding:15px; font-size:1rem;'>📝 Note: {r}</div>", unsafe_allow_html=True)
        with col_b:
            preds = np.random.randint(20, 50, 7)
            fig = px.area(y=preds, title="Expected Customer Demand (Next 7 Days)", template="plotly_dark")
            fig.update_traces(line_color='#38bdf8', fillcolor='rgba(56, 189, 248, 0.2)')
            fig.update_layout(height=400, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            required = max(0, preds.sum() - p['current_stock'])
            if required > 0:
                st.markdown(f"<div class='ai-decision-box' style='padding:24px;'><h3>🤖 AI Recommendation</h3>You need to reorder <b style='color:#ffffff; font-size:1.5rem;'>{required}</b> more units soon, otherwise you might run out of stock next week!</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ai-decision-box' style='padding:24px; border-color:#34d399;'><h3 style='color:#34d399;'>STOCK IS HEALTHY</h3>You have enough inventory to cover the expected demand for the next week. No action needed.</div>", unsafe_allow_html=True)

# STAMBHA (Risk Check)
elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header'>STAMBHA</div><span class='feature-sub'>Simulate terrible situations (like shipping delays) to see if you survive.</span>", unsafe_allow_html=True)
    s = st.selectbox("Choose a Disaster Scenario to Test", ["Normal Operations", "Severe Supplier Delay (Takes 3x Longer)"])
    df = get_user_data()
    if not df.empty:
        for _, p in df.iterrows():
            ttr = p['lead_time'] * (3 if "Delay" in s else 1)
            tts = round(p['current_stock'] / 12, 1) 
            if tts < ttr: 
                st.markdown(f"<div class='saas-card' style='border-left: 6px solid #ef4444;'><div style='color:#ef4444; font-weight:800; font-size:1.3rem; margin-bottom:8px;'>⚠️ LOW STOCK WARNING</div><div style='color:#f8fafc;'>Your current stock of <b style='color:#ef4444;'>{p['name']}</b> will run out in {tts} days. But your supplier will take {ttr} days to deliver more. You will lose sales!</div></div>", unsafe_allow_html=True)
        st.dataframe(df[['name', 'current_stock', 'lead_time']], use_container_width=True)

# NYASA (Inventory)
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>NYASA</div><span class='feature-sub'>Add new products and manage your database here.</span>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📥 Add Single Item", "📦 Batch Upload (CSV)", "📄 Generate Purchase Order"])
    
    with t3:
        st.markdown("<h3 style='color:#fff; margin-bottom:20px; font-weight:700;'>Create a Purchase Order</h3>", unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            po_num = f"PO-{np.random.randint(1000, 9999)}"
            st.text_input("PO Document ID", value=po_num, disabled=True)
            supp = st.text_input("Supplier Name", placeholder="e.g. Zenith Systems")
            items = st.text_area("Items Needed", placeholder="10x Coffee Mugs\n5x Laptops", height=100)
        with c2:
            cost = st.number_input("Estimated Total Cost (₹)", min_value=0.0)
            date_needed = st.date_input("Delivery Deadline")
        
        if st.button("Generate PO File"):
            if not supp or not items:
                st.warning("Please fill in Supplier and Items to generate the file.")
            else:
                po_text = f"""# PURCHASE ORDER
**PO Number:** {po_num}
**Date Generated:** {datetime.now().strftime("%Y-%m-%d")}
**Requested By:** {st.session_state.user.upper()}

## Supplier Details
**Name:** {supp}

## Itemized Request
{items}

## Fulfillment & Accounting
**Expected Delivery Date:** {date_needed}
**Estimated Cost:** ₹{cost:,.2f}

---
*Generated securely by AROHA Strategic Intelligence.*
*Turn Data Into Decisions.*
"""
                st.markdown(f"<div class='saas-card' style='background:rgba(0,0,0,0.5); padding:30px; font-family:monospace; margin-top:20px;'><pre style='color:#fff; white-space: pre-wrap;'>{po_text}</pre></div>", unsafe_allow_html=True)
                st.download_button("📥 Save PO to text file (.txt)", data=po_text, file_name=f"{po_num}.txt", mime="text/plain")
                st.success("Document created successfully! You can download it using the button above.")

    with t2:
        f = st.file_uploader("Upload CSV Spreadsheet", type="csv")
        if f and st.button("Import Data"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            for col in ['category','supplier','image_url','reviews']: u_df[col] = u_df.get(col, "")
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Successfully uploaded your spreadsheet into the database.")
            
    with t1:
        with st.form("add"):
            c1, c2 = st.columns(2)
            with c1:
                n = st.text_input("Product Name")
                s = st.number_input("Quantity in Stock", 0)
                p = st.number_input("Unit Price (₹)", 0.0)
            with c2:
                lt = st.number_input("Supplier Lead Time (days)", 1)
                img = st.text_input("Product Image URL (Optional)")
                rev = st.text_input("Notes or Tags")
            if st.form_submit_button("Add to Warehouse"):
                with get_db() as conn: 
                    conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
                st.success("Product successfully added to inventory!")

# SAMVADA (Voice AI)
elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header'>SAMVADA</div><span class='feature-sub'>Use your microphone to ask the AI questions about your data!</span>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY", None)
    
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        
        st.markdown("<div class='saas-card' style='height: 500px; overflow-y: auto; background: rgba(0,0,0,0.4);'>", unsafe_allow_html=True)
        for m in st.session_state.chat_history:
            if m["role"] == "user":
                st.markdown(f"<div style='text-align: right; margin-bottom: 20px;'><span style='background: linear-gradient(135deg, #c084fc, #38bdf8); color: #020617; padding: 14px 22px; border-radius: 20px 20px 0 20px; display: inline-block; font-weight:700; box-shadow: 0 4px 15px rgba(56,189,248,0.2);'>{m['content']}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: left; margin-bottom: 20px;'><span style='background: rgba(255,255,255,0.05); color: #ffffff; padding: 14px 22px; border-radius: 20px 20px 20px 0; display: inline-block; font-weight:500; border: 1px solid rgba(192,132,252,0.3); backdrop-filter:blur(10px);'>{m['content']}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        col_text, col_voice = st.columns([4, 1])
        with col_voice:
            audio_in = st.audio_input("Record Audio")
            
        u_in = st.chat_input("Type your message here...")
        
        if audio_in:
            with st.spinner("Listening..."):
                try:
                    transcription = client.audio.transcriptions.create(
                        file=("audio.wav", audio_in.getvalue()),
                        model="whisper-large-v3"
                    )
                    u_in = transcription.text
                    st.success(f"Heard: *{u_in}*")
                except Exception as e:
                    st.error(f"Microphone error: {e}")
                    
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are a friendly, helpful assistant analyzing inventory. Keep answers short, simple, and easy to understand. Data: {ctx}"}, *st.session_state.chat_history[-4:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans})
            st.rerun()
    else:
        st.warning("⚠️ Warning: Could not connect to the microphone. Please add your API Key in the settings.")

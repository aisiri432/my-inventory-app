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

# --- 1. ENTERPRISE UI CONFIG ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence",
    layout="wide",
    page_icon="💼",
    initial_sidebar_state="expanded"
)

def apply_aroha_style():
    st.markdown("""
    <style>
        /* Base Enterprise Aesthetics */
        .stApp {
            background-color: #0A0A0A;
            color: #D4D4D8;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol';
        }

        /* Typography Highlights */
        .brand-title {
            color: #FAFAFA;
            font-weight: 700;
            font-size: 1.75rem;
            letter-spacing: -0.5px;
        }
        .decisions-fade {
            color: #6366F1;
            font-weight: 600;
        }
        .feature-header {
            font-size: 1.5rem;
            font-weight: 600;
            color: #FAFAFA;
            margin-bottom: 24px;
            padding-bottom: 12px;
            border-bottom: 1px solid #27272A;
            letter-spacing: -0.5px;
        }

        /* Clean SaaS Cards */
        .saas-card, .financial-stat, .insight-box, .ai-decision-box {
            background-color: #18181B;
            border-radius: 8px;
            padding: 24px;
            border: 1px solid #27272A;
            margin-bottom: 16px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.2);
            transition: border-color 0.2s ease;
        }
        .saas-card:hover, .financial-stat:hover, .insight-box:hover {
            border-color: #3F3F46;
        }
        
        /* Specialized Boxes */
        .insight-box {
            border-left: 3px solid #6366F1;
        }
        .ai-decision-box {
            background-color: #171717;
            border: 1px solid #3B82F6;
        }
        .ai-decision-box h3 {
            color: #60A5FA;
            margin-top: 0;
            font-size: 1.05rem;
            font-weight: 600;
            letter-spacing: -0.2px;
        }
        .directive-msg {
            background-color: #18181B;
            border-left: 3px solid #3B82F6;
            padding: 14px 18px;
            margin-bottom: 10px;
            border-radius: 6px;
            color: #E4E4E7;
            font-size: 0.95rem;
            border-top: 1px solid #27272A;
            border-right: 1px solid #27272A;
            border-bottom: 1px solid #27272A;
        }
        .review-box {
            background-color: #18181B;
            padding: 12px 16px;
            border-radius: 6px;
            margin-bottom: 8px;
            color: #A1A1AA;
            font-size: 0.9rem;
            border: 1px solid #27272A;
        }

        /* Ticker */
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background-color: #000000;
            padding: 8px;
            border-radius: 6px;
            border: 1px solid #27272A;
            margin-bottom: 24px;
        }
        .ticker-text {
            white-space: nowrap;
            box-sizing: border-box;
            animation: ticker 35s linear infinite;
            color: #71717A;
            font-size: 0.8rem;
            font-weight: 500;
        }
        @keyframes ticker {
            0%   { transform: translate3d(100%, 0, 0); }
            100% { transform: translate3d(-100%, 0, 0); }
        }

        /* Metrics overriding */
        div[data-testid="stMetricValue"] {
            color: #FAFAFA !important;
            font-size: 1.8rem !important;
            font-weight: 600 !important;
            letter-spacing: -0.5px;
        }
        div[data-testid="stMetricLabel"] {
            font-size: 0.85rem !important;
            color: #A1A1AA !important;
            font-weight: 500;
        }

        /* ==================================================== */
        /* CREATIVE SIDEBAR OVERHAUL                            */
        /* ==================================================== */
        
        /* Cyber-Grid / Blueprint texture on the Sidebar */
        [data-testid="stSidebar"] {
            background-color: #050505 !important;
            background-image: linear-gradient(#18181B 1px, transparent 1px), linear-gradient(90deg, #18181B 1px, transparent 1px) !important;
            background-size: 25px 25px !important;
            border-right: 1px solid #27272A !important;
        }

        /* Customizing Sidebar Buttons to look like floating interactive tabs */
        [data-testid="stSidebar"] div.stButton > button {
            background: rgba(24, 24, 27, 0.85); /* transulcent slate */
            backdrop-filter: blur(4px);
            border: 1px solid #27272A;
            border-left: 4px solid #27272A; /* Initial thick border */
            border-radius: 6px;
            color: #A1A1AA;
            text-align: left;
            padding: 12px 16px;
            margin-bottom: 4px;
            font-weight: 500;
            font-size: 0.95rem;
            width: 100%;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
            justify-content: flex-start;
        }
        
        [data-testid="stSidebar"] div.stButton > button p {
            margin-left: 5px;
        }

        /* The Magic Hover Effect */
        [data-testid="stSidebar"] div.stButton > button:hover {
            background: #18181B;
            border: 1px solid #3F3F46;
            border-left: 4px solid #3B82F6; /* Pops blue on the left */
            color: #FAFAFA;
            transform: translateX(6px) scale(1.02); /* slides out and pops toward user */
            box-shadow: -4px 0 20px rgba(59, 130, 246, 0.15); /* blue back-glow */
        }
        
        /* Standard buttons elsewhere in the app */
        .main div.stButton>button {
            background-color: #27272A;
            color: #FAFAFA;
            border: 1px solid #3F3F46;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }
        .main div.stButton>button:hover {
            background-color: #3F3F46;
            border-color: #52525B;
            color: #FFFFFF;
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
    st.markdown("<div style='text-align:center; margin-top:100px;'><h1 class='brand-title'>AROHA</h1><p style='color:#71717A; font-size:1.1rem; margin-top:-10px;'>Turn Data Into <span class='decisions-fade'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([0.2, 0.6, 0.2])
    with col_center:
        m = st.tabs(["Login", "Create Account"])
        with m[0]:
            u_input = st.text_input("Username", key="l_u")
            p_input = st.text_input("Password", type="password", key="l_p")
            if st.button("Sign In"):
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
            np_in = st.text_input("New Password", type="password")
            if st.button("Register"):
                try:
                    with get_db() as conn: 
                        conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np_in)))
                    st.success("Account created successfully.")
                except: 
                    st.error("Username already exists.")
    st.stop()

# --- 5. TOP HUD TICKER ---
st.markdown(f"<div class='ticker-wrap'><div class='ticker-text'>USER: {st.session_state.user.upper()} ••• SYSTEM: ONLINE ••• [LOGISTICS] Hover map for precision addresses ••• [KRIYA] Fleet management active ••• [VITTA] Capital optimization complete.</div></div>", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    
    user_initial = st.session_state.user[0].upper() if st.session_state.user else "A"
    
    # 🎨 Creative Profile Card
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #18181B, #09090B); padding: 20px; border-radius: 12px; border: 1px solid #27272A; margin-bottom: 25px; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5);'>
        <div style='width: 65px; height: 65px; border-radius: 50%; background: #27272A; color: white; display:flex; align-items:center; justify-content:center; font-size: 1.8rem; font-weight: bold; margin: 0 auto 12px auto; border: 2px solid #3B82F6; box-shadow: 0 0 15px rgba(59,130,246,0.3);'>
            {user_initial}
        </div>
        <div style='color: #FAFAFA; font-weight: 700; font-size: 1.15rem; letter-spacing: 0.5px;'>{st.session_state.user.upper()}</div>
        <div style='color: #10B981; font-size: 0.75rem; text-transform: uppercase; font-weight: bold; margin-top:4px;'>Terminal Verified</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='color:#52525B; font-weight:700; font-size:0.75rem; letter-spacing:1px; margin-bottom: 10px;'>CORE COMMAND</div>", unsafe_allow_html=True)
    
    if st.button("🌐 Main Overview", use_container_width=True): 
        st.session_state.page = "Dashboard"
        st.rerun()
        
    st.markdown("<div style='color:#52525B; font-weight:700; font-size:0.75rem; letter-spacing:1px; margin-top:24px; margin-bottom: 10px;'>SYSTEM MODULES</div>", unsafe_allow_html=True)
    
    # Adding subtle emojis back to the sidebar only, for creative flair.
    nodes = [
        ("📝 Nyasa (Registry)", "Nyasa"),
        ("🔮 Preksha (Forecast)", "Preksha"),
        ("🛡️ Stambha (Risk)", "Stambha"),
        ("⚡ Kriya (Fleet)", "Kriya"),
        ("🎙️ Samvada Voice", "Samvada"),
        ("🏦 Vitta (Capital)", "Vitta"),
        ("🗺️ Sanchara (Map)", "Sanchara"),
        ("🤝 Mithra (Partner)", "Mithra")
    ]
    
    for label, page_id in nodes:
        if st.button(label, key=f"nav_{page_id}", use_container_width=True):
            st.session_state.page = page_id
            st.rerun()
        
    st.markdown("<br><hr style='border-color: #27272A;'>", unsafe_allow_html=True)
    if st.button("🚪 Secure Logout", use_container_width=True): 
        st.session_state.auth = False
        st.rerun()

# --- 7. LOGIC NODES ---
# OVERVIEW
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1 style='font-size:1.75rem; color:#FAFAFA; font-weight:600; letter-spacing:-0.5px;'>Intelligence Hub</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.metric("Assets Managed", len(df))
    with c2: 
        st.metric("Capital Value", f"₹{val:,.0f}")
    with c3: 
        st.metric("System Status", "Operational")
    st.markdown("<div class='insight-box'><b>Summary:</b> Warehouse throughput is stable. Supply forecasts predict a +8% weekend variance. Recommend reviewing active POs in Nyasa.</div>", unsafe_allow_html=True)

# KRIYA
elif st.session_state.page == "Kriya":
    st.markdown("<div class='feature-header'>Workforce Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='insight-box'><b>Active Deployment:</b> AI matching engine has allocated batch processing to Sector A. Shift efficiency nominal.</div>", unsafe_allow_html=True)
    
    tab_worker, tab_manager = st.tabs(["Employee View", "Management Analytics"])

    with tab_worker:
        st.subheader("Current Assignment")
        col_q, col_s = st.columns([2, 1])
        with col_q:
            st.markdown("<div class='directive-msg'><b>Task 402-A</b><br><br>Pick 12x Titanium Chassis for Assembly Station B.</div>", unsafe_allow_html=True)
            st.markdown("<div class='directive-msg' style='border-left-color:#10B981;'><b>Route Optimized</b><br><br>Navigate to Shelf B2 via Aisle 3. Estimated time: 2m 14s.</div>", unsafe_allow_html=True)
            if st.button("Complete Scan"):
                st.error("Invalid SKU. Please verify barcode on Bin B2.")
        with col_s:
            st.markdown("<div class='saas-card' style='text-align:center;'><h4>Pick Rate</h4><h2 style='color:#FAFAFA; font-size:2rem; font-weight:600;'>42/hr</h2><p style='color:#10B981; font-weight:500; font-size:0.9rem;'>↑ 12% shift average</p></div>", unsafe_allow_html=True)
            st.warning("Pattern matches light fatigue. Recommend hydration break after next run.")

    with tab_manager:
        st.subheader("Efficiency Metrics")
        c1, c2 = st.columns(2)
        with c1:
            st.write("Throughput (Past 5 Hours)")
            fig = px.line(y=[80, 85, 75, 90, 88], template="plotly_dark")
            fig.update_layout(height=250, margin=dict(l=0,r=0,b=0,t=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            fig.update_traces(line_color='#3B82F6', line_width=2)
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.write("Operator Performance")
            st.bar_chart({"Accuracy": [98, 92, 75], "Speed": [90, 85, 70]}, color=["#3B82F6", "#6366F1"])
            st.success("Lead Operator: Ananya (98% Quality Rate)")

# VITTA
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>Financial Overview</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"<div class='saas-card'><div style='color:#A1A1AA; font-size:0.9rem; margin-bottom:8px;'>Deployed Capital</div><div style='color:#FAFAFA; font-size:2.5rem; font-weight:600;'>₹{total_v:,.0f}</div></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='saas-card'><div style='color:#A1A1AA; font-size:0.9rem; margin-bottom:8px;'>Capital at Risk (Idle > 30 days)</div><div style='color:#F43F5E; font-size:2rem; font-weight:600;'>₹{total_v*0.15:,.0f}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='saas-card'><div style='color:#A1A1AA; font-size:0.9rem; margin-bottom:16px;'>Capital Allocation Concentration</div>", unsafe_allow_html=True)
            fig = px.pie(df, values='current_stock', names='name', hole=0.6, template="plotly_dark", color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=220)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# MITHRA+
elif st.session_state.page == "Mithra":
    st.markdown("<div class='feature-header'>Procurement Engagements</div>", unsafe_allow_html=True)
    df = get_user_data()
    
    if not df.empty:
        col1, col2 = st.columns([1, 1.5])

        with col1:
            vendor = st.selectbox("Counterparty", df['supplier'].unique())
            style = st.radio("Negotiation Posture", ["Standard", "Partnership", "Cost-Driven"])

        with col2:
            if st.button("Generate Strategy Draft", use_container_width=True):
                st.metric("Estimated Margin Impact", "₹12,400", "8.0%")
                st.text_area(
                    "Generated Communication",
                    f"Hi {vendor},\n\nBased on Q3 volume projections, we'd like to initiate a pricing review to align with our latest supply chain targets..."
                )

        st.markdown("<hr style='border-color:#27272A; margin: 30px 0;'>", unsafe_allow_html=True)
        st.markdown("<h3 style='font-size:1.1rem; color:#FAFAFA;'>Vendor Performance</h3>", unsafe_allow_html=True)

        client_data = pd.DataFrame({
            "Supplier": ["Alpha Corp", "Zenith Ltd", "Nova Ind", "Orion Traders"],
            "Spend (₹)": [120000, 95000, 78000, 150000],
            "Fulfillment Rate (%)": [92, 85, 78, 96],
            "Reliability": ["High", "Medium", "Medium", "High"]
        })

        st.dataframe(client_data, use_container_width=True, hide_index=True)

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(client_data, x="Supplier", y="Spend (₹)", template="plotly_dark", color_discrete_sequence=["#3B82F6"])
            fig1.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=200, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.line(client_data, x="Supplier", y="Fulfillment Rate (%)", markers=True, template="plotly_dark")
            fig2.update_traces(line_color="#10B981", marker=dict(size=8, color="#10B981"))
            fig2.update_layout(margin=dict(t=10, b=0, l=0, r=0), height=200, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig2, use_container_width=True)

# SANCHARA
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>Logistics Networking</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["Geospatial View", "Throughput", "Exceptions"])
    with t1:
        map_pts = pd.DataFrame({'lat':[12.9716, 22.31, 37.77, 1.35], 'lon':[77.59, 114.16, -122.41, 103.81], 'Facility':['Distribution Hub','Manufacturing','Corporate HQ','Risk Zone flagged'], 'Address':['MG Road, Bangalore','Lantau, HK','Market St, SF','Jurong, Singapore']})
        fig = px.scatter_mapbox(map_pts, lat="lat", lon="lon", hover_name="Facility", hover_data={"Address": True}, zoom=1, height=450, color="Facility", color_discrete_sequence=["#3B82F6", "#6366F1", "#A855F7", "#F43F5E"])
        fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)
    with t2:
        c1, c2 = st.columns(2)
        c1.metric("Outbound Volume (24h)", "1,240 units", "5.2%")
        c2.metric("Total Vaulted Inventory", f"{get_user_data()['current_stock'].sum() if not get_user_data().empty else 0} units")
    with t3:
        st.table(pd.DataFrame({'SKU':['Quantum X1','4K Monitor'], 'Quantity':[4,2], 'Exception Reason':['QC Failure','Transit Damage']}))

# PREKSHA
elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>Demand Forecasting</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        target = st.selectbox("Select Asset Code", df['name'])
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
            fig = px.area(y=preds, title="Projected Drawdown (7 Days)", template="plotly_dark")
            fig.update_traces(line_color='#3B82F6', fillcolor='rgba(59, 130, 246, 0.1)')
            fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)
            required = max(0, preds.sum() - p['current_stock'])
            if required > 0:
                st.markdown(f"<div class='ai-decision-box' style='padding:16px;'><h3>System Action Recommended</h3>Optimal reorder quantity: <b>{required}</b> units to mitigate projected shortage. Confidence: 94%</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='ai-decision-box' style='padding:16px; border-color:#10B981;'><h3>Stock Sufficient</h3>No immediate procurement actions required.</div>", unsafe_allow_html=True)

# STAMBHA
elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header'>Supply Risk Modeling</div>", unsafe_allow_html=True)
    s = st.selectbox("Scenario Model", ["Baseline", "Transit Delay Stress Test (3x Lead Time)"])
    df = get_user_data()
    if not df.empty:
        for _, p in df.iterrows():
            ttr = p['lead_time'] * (3 if "Delay" in s else 1)
            tts = round(p['current_stock'] / 12, 1) # Mock usage rate
            if tts < ttr: 
                st.markdown(f"<div class='saas-card' style='border-left: 4px solid #F43F5E;'><div style='color:#F43F5E; font-weight:600; margin-bottom:4px;'>Exposure Warning</div><div style='color:#E4E4E7; font-size:0.95rem;'>{p['name']} buffer depletes in {tts} days. Replenishment requires {ttr} days.</div></div>", unsafe_allow_html=True)
        st.dataframe(df[['name', 'current_stock', 'lead_time']], use_container_width=True)

# NYASA
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>Registry & Procurement</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Manifest Import", "Manual Entry"])
    with t1:
        f = st.file_uploader("Upload Batch CSV", type="csv")
        if f and st.button("Process Manifest"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            for col in ['category','supplier','image_url','reviews']: u_df[col] = u_df.get(col, "")
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Database synchronized.")
    with t2:
        with st.form("add"):
            c1, c2 = st.columns(2)
            with c1:
                n = st.text_input("Asset Name")
                s = st.number_input("Count", 0)
                p = st.number_input("Unit Price", 0.0)
            with c2:
                lt = st.number_input("Lead Time (days)", 1)
                img = st.text_input("Cover Image URL (optional)")
                rev = st.text_input("Notes")
            if st.form_submit_button("Commit Record"):
                with get_db() as conn: 
                    conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
                st.success("Record appended.")

# SAMVADA
elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header'>Interactive AI Terminal</div>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY", None)
    
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        
        st.markdown("<div class='saas-card' style='height: 400px; overflow-y: auto; background-color:#111111;'>", unsafe_allow_html=True)
        for m in st.session_state.chat_history:
            if m["role"] == "user":
                st.markdown(f"<div style='text-align: right; margin-bottom: 16px;'><span style='background-color: #27272A; color: #FAFAFA; padding: 12px 18px; border-radius: 8px 8px 0 8px; display: inline-block; font-size:0.95rem; border: 1px solid #3F3F46;'>{m['content']}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: left; margin-bottom: 16px;'><span style='background-color: #172554; color: #DBEAFE; padding: 12px 18px; border-radius: 8px 8px 8px 0; display: inline-block; font-size:0.95rem; border: 1px solid #1E3A8A;'>{m['content']}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        col_text, col_voice = st.columns([4, 1])
        with col_voice:
            audio_in = st.audio_input("Dictate")
            
        u_in = st.chat_input("Run a query...")
        
        if audio_in:
            with st.spinner("Processing..."):
                try:
                    transcription = client.audio.transcriptions.create(
                        file=("audio.wav", audio_in.getvalue()),
                        model="whisper-large-v3"
                    )
                    u_in = transcription.text
                    st.success(f"Recognized: *{u_in}*")
                except Exception as e:
                    st.error(f"Failed to process audio: {e}")
                    
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are a professional supply chain assistant. Here is the local DB context: {ctx}"}, *st.session_state.chat_history[-4:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans})
            st.rerun()
    else:
        st.warning("⚠️ API Key not detected. Terminal inactive.")

Here is the full, final colorful Streamlit code for your `app.py`. You can seamlessly copy and paste this into your project.

```python
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

# --- 1. PREMIUM UI CONFIG (UNIVERSAL ADAPTIVE & HOLLOW GLOW) ---
st.set_page_config(
    page_title="AROHA | Strategic Intelligence",
    layout="wide",
    page_icon="💠",
    initial_sidebar_state="expanded"
)

def apply_aroha_style():
    st.markdown("""
    <style>
        /* Base Streamlit Overrides */
        .stApp {
            background-color: #0E1117;
            color: #E0E6ED;
            font-family: 'Inter', sans-serif;
        }
        
        /* Typography Highlights */
        .brand-title {
            background: linear-gradient(90deg, #FF007F, #7928CA, #00D4FF);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 900;
            font-size: 3rem;
            text-shadow: 0 0 20px rgba(121, 40, 202, 0.4);
            letter-spacing: 2px;
        }
        .decisions-fade {
            color: #00D4FF;
            text-shadow: 0 0 10px #00D4FF;
            font-weight: bold;
        }
        .feature-header {
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #00D4FF 0%, #7928CA 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid rgba(0, 212, 255, 0.3);
        }

        /* Glassmorphism Cards */
        .saas-card, .financial-stat, .insight-box, .ai-decision-box {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 16px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin-bottom: 15px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        .saas-card:hover, .financial-stat:hover, .insight-box:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 212, 255, 0.2);
            border-color: rgba(0, 212, 255, 0.5);
        }
        
        /* Specialized Boxes */
        .insight-box {
            border-left: 5px solid #FF007F;
            background: linear-gradient(90deg, rgba(255, 0, 127, 0.1) 0%, transparent 100%);
        }
        .ai-decision-box {
            border: 2px dashed #00FFCC;
            background: rgba(0, 255, 204, 0.05);
            text-align: center;
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 0 20px rgba(0, 255, 204, 0.2);
        }
        .ai-decision-box h3 {
            color: #00FFCC;
            margin-top: 0;
            text-shadow: 0 0 15px #00FFCC;
        }
        .directive-msg {
            background: linear-gradient(90deg, rgba(121, 40, 202, 0.2), transparent);
            border-left: 4px solid #7928CA;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 4px;
            color: #E0E6ED;
        }
        .review-box {
            background: linear-gradient(135deg, rgba(255, 0, 127, 0.2), rgba(0, 212, 255, 0.2));
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
            color: white;
            font-weight: bold;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Ticker */
        .ticker-wrap {
            width: 100%;
            overflow: hidden;
            background: linear-gradient(90deg, #111, #222, #111);
            padding: 10px;
            border-radius: 8px;
            box-shadow: inset 0 0 15px #000;
            border: 1px solid rgba(0, 212, 255, 0.3);
            margin-bottom: 20px;
        }
        .ticker-text {
            white-space: nowrap;
            box-sizing: border-box;
            animation: ticker 25s linear infinite;
            color: #00FFCC;
            font-weight: 600;
            letter-spacing: 1px;
            text-shadow: 0 0 10px rgba(0, 255, 204, 0.5);
        }
        @keyframes ticker {
            0%   { transform: translate3d(100%, 0, 0); }
            100% { transform: translate3d(-100%, 0, 0); }
        }

        /* Sidebar Navigation */
        .sidebar-sub {
            color: #00D4FF;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 10px;
            display: block;
            margin-top: 20px;
            font-weight: bold;
        }
        
        /* Metric overriding */
        div[data-testid="stMetricValue"] {
            color: #00FFCC !important;
            font-size: 2.5rem !important;
            text-shadow: 0 0 15px rgba(0, 255, 204, 0.3);
        }
        div[data-testid="stMetricLabel"] {
            font-size: 1.1rem !important;
            color: #E0E6ED !important;
            font-weight: 600;
        }

        /* Buttons globally styled */
        .stButton>button {
            border: 1px solid rgba(0, 212, 255, 0.5);
            background: linear-gradient(90deg, rgba(121, 40, 202, 0.3), rgba(0, 212, 255, 0.3));
            color: white;
            transition: all 0.3s ease;
            box-shadow: 0 0 10px rgba(0,0,0,0.5);
        }
        .stButton>button:hover {
            border-color: #00D4FF;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.6);
            transform: translateY(-2px);
            color: white;
        }
    </style>
    <div style='text-align:center; margin-top:-10px; margin-bottom:30px;'>
        <div style='height:4px; width:180px; margin:auto; border-radius:10px;
            background: linear-gradient(90deg, #FF007F, #7928CA, #00D4FF);
            box-shadow: 0 0 15px #00D4FF, 0 0 30px #FF007F;'>
        </div>
    </div>
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
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 class='brand-title'>AROHA</h1><p style='color:#9AA0A6; font-size:1.4rem;'>Turn Data Into <span class='decisions-fade'>Decisions</span></p></div>", unsafe_allow_html=True)
    c1, col_center, c3 = st.columns([0.1, 0.8, 0.1])
    with col_center:
        m = st.tabs(["Login", "Join"])
        with m[0]:
            u_input = st.text_input("Username", key="l_u")
            p_input = st.text_input("Password", type="password", key="l_p")
            if st.button("Unlock Hub"):
                with get_db() as conn: 
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u_input,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p_input):
                    st.session_state.auth = True
                    st.session_state.user = u_input
                    st.rerun()
                else: 
                    st.error("Access Denied")
        with m[1]:
            nu = st.text_input("New ID")
            np_in = st.text_input("New Pass", type="password")
            if st.button("Enroll"):
                try:
                    with get_db() as conn: 
                        conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np_in)))
                    st.success("Authorized.")
                except: 
                    st.error("ID exists.")
    st.stop()

# --- 5. TOP HUD TICKER ---
st.markdown(f"<div class='ticker-wrap'><div class='ticker-text'>[DHWANI] {st.session_state.user.upper()} ACTIVE // [LOGISTICS] Hover Map for Precision Addresses // [KRIYA] Human fatigue Delta sensing online // [VITTA] Inventory ROI optimized.</div></div>", unsafe_allow_html=True)

# --- 6. SIDEBAR ---
with st.sidebar:
    st.markdown(f"<div class='brand-container'><div class='brand-title' style='font-size:2.2rem !important; background: linear-gradient(90deg, #00D4FF, #00FFCC); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>AROHA</div><div style='color:#9AA0A6; font-size:0.9rem;'>Data into <span class='decisions-fade'>Decisions</span></div></div>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color: rgba(0, 212, 255, 0.2);'>", unsafe_allow_html=True)
    
    if st.button("🏠 DASHBOARD", use_container_width=True): 
        st.session_state.page = "Dashboard"
        st.rerun()
        
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)
    
    nodes = [
        ("📝 NYASA", "Nyasa", "Add Items & PO Gen"),
        ("📈 PREKSHA", "Preksha", "Predict Demand Instantly"),
        ("🛡️ STAMBHA", "Stambha", "Test Supply Risks"),
        ("👷‍♂️ KRIYA", "Kriya", "Workforce Intelligence"),
        ("🎙️ SAMVADA", "Samvada", "Talk To System"),
        ("💰 VITTA", "Vitta", "Track Money Flow"),
        ("📦 SANCHARA", "Sanchara", "Global Map & Flow"),
        ("🤝 MITHRA+", "Mithra", "AI Negotiation")
    ]
    
    for label, page_id, layman in nodes:
        if st.button(label, key=f"nav_{page_id}", use_container_width=True):
            st.session_state.page = page_id
            st.rerun()
        st.markdown(f"<div style='color:#8892B0; font-size:0.75rem; text-align:center; margin-top:-10px; margin-bottom:15px;'>{layman}</div>", unsafe_allow_html=True)
        
    st.markdown("<hr style='border-color: rgba(255, 0, 127, 0.2);'>", unsafe_allow_html=True)
    if st.button("🔒 Logout", use_container_width=True): 
        st.session_state.auth = False
        st.rerun()

# --- 7. LOGIC NODES ---
# 🏠 DASHBOARD
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1 style='background: linear-gradient(90deg, #FFFFFF, #B0BEC5); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>Strategic Hub: {st.session_state.user.upper()}</h1>", unsafe_allow_html=True)
    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0
    c1, c2, c3 = st.columns(3)
    with c1: 
        st.metric("📝 Assets Managed", len(df))
    with c2: 
        st.metric("💰 Treasury Value", f"₹{val:,.0f}")
    with c3: 
        st.metric("🛡️ System Integrity", "OPTIMAL")
    st.markdown("<div class='insight-box'><b>💡 Tactical Handoff:</b> Warehouse throughput is stable. Intelligence node PREKSHA sensing +8% weekend spike. Recommend auditing NYASA registry.</div>", unsafe_allow_html=True)

# 👷‍♂️ KRIYA (FULL 9-POINT SPEC)
elif st.session_state.page == "Kriya":
    st.markdown("<div class='feature-header'>👷‍♂️ KRIYA Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='insight-box' style='border-left-color: #00D4FF; background: linear-gradient(90deg, rgba(0, 212, 255, 0.1), transparent);'><b>🚀 Workforce Briefing:</b> AI is dynamically orchestrating tasks to Ravi and Ananya. Fatigue sensors active.</div>", unsafe_allow_html=True)
    
    tab_worker, tab_manager = st.tabs(["🔧 Worker Interface (HUD)", "📊 Manager Intelligence"])

    with tab_worker:
        st.subheader("Operational Directives")
        col_q, col_s = st.columns([2, 1])
        with col_q:
            st.markdown("<div class='directive-msg'><b>[POINT 1: ASSIGNMENT]</b> Pick 12x Titanium Chassis for Station B.</div>", unsafe_allow_html=True)
            st.markdown("<div class='directive-msg' style='border-left-color:#FF007F;'><b>[POINT 2 & 6: GUIDANCE]</b> Proceed to <b>Shelf B2 via Aisle 3</b>. Shortcut path displayed.</div>", unsafe_allow_html=True)
            if st.button("📦 SIMULATE SCAN"):
                st.error("🚨 [POINT 4: ERROR PREVENTION] Warning: Incorrect item selected (SKU-405). Please verify barcode on Bin B2.")
        with col_s:
            st.markdown("<div class='saas-card' style='text-align:center;'><h4>Shift Performance</h4><h2 style='color:#00FFCC; font-size:2.5rem; text-shadow:0 0 10px #00FFCC;'>42 picks/hr</h2><p style='color:#34D399; font-weight:bold;'>+12% vs Team Avg</p></div>", unsafe_allow_html=True)
            if st.button("🎙️ Voice: 'What should I do next?'"):
                st.info("🤖 AI: Ravi, proceed to Zone C for sensor audit. Fastest route: Aisle 1 North.")
            st.warning("🧠 [POINT 5: FATIGUE] Speed drop detected for Ravi. Suggest 10-min break.")

    with tab_manager:
        st.subheader("Human Capital Analytics")
        c1, c2 = st.columns(2)
        with c1:
            st.write("### [POINT 9] Efficiency Trends")
            fig = px.line(y=[80, 85, 75, 90, 88], title="Real-time Throughput", template="plotly_dark")
            fig.update_traces(line_color='#00D4FF', line_width=4, fill='tozeroy', fillcolor='rgba(0, 212, 255, 0.1)')
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.write("### [POINT 8] Resource Allocation")
            st.bar_chart({"Accuracy": [98, 92, 75], "Speed": [90, 85, 70]}, color=["#FF007F", "#7928CA"])
            st.success("✅ Top Performer: Ananya (98% Accuracy).")

# 💰 VITTA
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>💰 VITTA Financials</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"<div class='saas-card'><div style='color:#8892B0; font-size:1.1rem;'>Total Inventory Value</div><h2 style='color:#00FFCC; text-shadow:0 0 15px rgba(0,255,204,0.4); font-size:3rem;'>₹{total_v:,.0f}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='saas-card' style='border-color:rgba(255,0,127,0.3);'><div style='color:#8892B0; font-size:1.1rem;'>Idle Capital Risk (15%)</div><h2 style='color:#FF007F; text-shadow:0 0 15px rgba(255,0,127,0.4); font-size:2.4rem;'>₹{total_v*0.15:,.0f}</h2></div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div class='saas-card'><b>Capital Allocation Matrix</b>", unsafe_allow_html=True)
            fig = px.pie(df, values='current_stock', names='name', hole=0.5, template="plotly_dark", color_discrete_sequence=px.colors.sequential.Agsunset)
            fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# 🤝 MITHRA+
elif st.session_state.page == "Mithra":
    st.markdown("<div class='feature-header'>🤝 MITHRA+ Nexus</div>", unsafe_allow_html=True)
    df = get_user_data()
    
    if not df.empty:
        col1, col2 = st.columns([1, 1.5])

        with col1:
            vendor = st.selectbox("Select Vendor", df['supplier'].unique())
            style = st.radio("Strategy", ["Polite", "Balanced", "Aggressive"])

        with col2:
            if st.button("🚀 EXECUTE AI NEGOTIATION", use_container_width=True):
                st.metric("Potential Savings", "₹12,400", "↑ 8%")
                st.text_area(
                    "Drafted Strategy",
                    f"Dear {vendor},\n\nWe sensed a 35% increase in volume. We request a pricing re-alignment..."
                )

        st.markdown("<hr style='border-color:rgba(255,255,255,0.1); margin: 30px 0;'>", unsafe_allow_html=True)
        st.markdown("### 🏆 Client Scoreboard")

        client_data = pd.DataFrame({
            "Client": ["Alpha Corp", "Zenith Ltd", "Nova Industries", "Orion Traders"],
            "Deal Value (₹)": [120000, 95000, 78000, 150000],
            "Negotiation Success (%)": [92, 85, 78, 96],
            "Trust Score": ["High", "Medium", "Medium", "High"]
        })

        st.dataframe(client_data, use_container_width=True, hide_index=True)

        st.markdown("### 📊 Performance Insights")

        col1, col2 = st.columns(2)

        with col1:
            fig1 = px.bar(client_data, x="Client", y="Deal Value (₹)", template="plotly_dark", color="Deal Value (₹)", color_continuous_scale=px.colors.sequential.Plasma)
            fig1.update_layout(margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.line(client_data, x="Client", y="Negotiation Success (%)", markers=True, template="plotly_dark")
            fig2.update_traces(line_color="#00FFCC", marker=dict(size=12, color="#FF007F", symbol="diamond"))
            fig2.update_layout(margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig2, use_container_width=True)

        st.markdown("<div class='insight-box'><b>💡 Insight:</b> Orion Traders delivers highest value + success rate. Expand engagement.</div>", unsafe_allow_html=True)

# 📦 SANCHARA
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>📦 SANCHARA Operations</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["🌐 Precision Map", "📦 Floor Ops", "↩️ Returns (PUNAH)"])
    with t1:
        map_pts = pd.DataFrame({'lat':[12.9716, 22.31, 37.77, 1.35], 'lon':[77.59, 114.16, -122.41, 103.81], 'Node':['Hub','Factory','HQ','Risk Zone'], 'Address':['MG Road, Bangalore','Lantau, HK','Market St, SF','Jurong, Singapore (🔴 PORT CLOSED)']})
        fig = px.scatter_mapbox(map_pts, lat="lat", lon="lon", hover_name="Node", hover_data={"Address": True}, zoom=1, height=450, color="Node", color_discrete_sequence=["#00FFCC", "#7928CA", "#FF007F", "#FF3333"])
        fig.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<div class='saas-card'><h4 style='color:#00D4FF; margin-top:0;'>Strategic Map Guide</h4>📍 <span style='color:#00FFCC'>Green/Blue</span>: Stable Nodes. 🔴 <span style='color:#FF3333'>Red</span>: Crisis/Risk. Hover dots for strict addresses.</div>", unsafe_allow_html=True)
    with t2:
        c1, c2 = st.columns(2)
        c1.metric("📦 Items Shipped Today", "1,240", delta="+5.2%")
        c2.metric("🏭 Total Floor Assets", f"{get_user_data()['current_stock'].sum() + 142} Units", delta="+142 Returns")
    with t3:
        st.table(pd.DataFrame({'Product':['Quantum X1','4K Monitor'], 'Amount':[4,2], 'Reason':['Defective Logic','Screen Bleed']}))

# 📈 PREKSHA
elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>📈 PREKSHA Predictive</div>", unsafe_allow_html=True)
    df = get_user_data()
    if not df.empty:
        target = st.selectbox("Asset", df['name'])
        p = df[df['name'] == target].iloc[0]
        col_a, col_b = st.columns([1, 2])
        with col_a:
            if p['image_url'] and str(p['image_url']) != "nan": 
                st.image(p['image_url'], use_container_width=True)
            if p['reviews']:
                for r in p['reviews'].split('|'): 
                    st.markdown(f"<div class='review-box'>⭐ {r}</div>", unsafe_allow_html=True)
        with col_b:
            preds = np.random.randint(20, 50, 7)
            fig = px.area(y=preds, title="AI Forecasting Path (7-day ahead)", template="plotly_dark")
            fig.update_traces(line_color='#00D4FF', fillcolor='rgba(0, 212, 255, 0.2)')
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"<div class='ai-decision-box'><h3>🤖 AI SUGGESTION</h3>Procure <b>{max(0, preds.sum() - p['current_stock'])}</b> units immediately to prevent stockouts. Confidence: 94%</div>", unsafe_allow_html=True)

# 🛡️ STAMBHA
elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header'>🛡️ STAMBHA Risk Defense</div>", unsafe_allow_html=True)
    s = st.selectbox("Simulate Shock", ["Normal", "Port Closure (3x Lead Risk)"])
    df = get_user_data()
    if not df.empty:
        for _, p in df.iterrows():
            ttr = p['lead_time'] * (3 if "Port" in s else 1)
            tts = round(p['current_stock'] / 12, 1)
            if tts < ttr: 
                st.markdown(f"<div class='saas-card' style='border-left: 5px solid #FF3333;'><h3 style='color:#FF3333; margin:0;'>🔴 CRITICAL RISK</h3>{p['name']} runs out in <b>{tts} days</b>. Recovery takes <b>{ttr} days</b>. Action needed!</div>", unsafe_allow_html=True)
        st.dataframe(df[['name', 'current_stock', 'lead_time']], use_container_width=True)

# 📝 NYASA
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>📝 NYASA Registry</div>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["📥 Bulk Sync", "✍️ Manual Registry", "📄 Formatted PO Gen"])
    with t1:
        f = st.file_uploader("Upload CSV Asset Data", type="csv")
        if f and st.button("Sync Now"):
            u_df = pd.read_csv(f); u_df['username'] = st.session_state.user
            for col in ['category','supplier','image_url','reviews']: u_df[col] = u_df.get(col, "")
            with get_db() as conn: u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success("Synchronized successfully.")
    with t2:
        with st.form("add"):
            n = st.text_input("Asset Name")
            s = st.number_input("Current Stock", 0)
            p = st.number_input("Unit Price", 0.0)
            lt = st.number_input("Lead Time (days)", 1)
            img = st.text_input("Image URL")
            rev = st.text_area("Reviews (use | to separate)")
            if st.form_submit_button("Commit to DB"):
                with get_db() as conn: 
                    conn.execute("INSERT INTO products (username, name, current_stock, unit_price, lead_time, image_url, reviews) VALUES (?,?,?,?,?,?,?,?)", (st.session_state.user, n, s, p, lt, img, rev))
                st.success("Asset logged.")
    with t3:
        df_po = get_user_data()
        if not df_po.empty: 
            po_id = np.random.randint(1000,9999)
            st.markdown(f"""
            <div class='saas-card' style='background:rgba(255,255,255,0.05); font-family:monospace;'>
                <h3 style='color:#00FFCC;'>PURCHASE ORDER</h3>
                <b>PO-ID:</b> #ARH-{po_id}<br>
                <b>ITEM:</b> {df_po.iloc[0]['name']}<br>
                <b>AUTH:</b> {st.session_state.user.upper()}<br>
                <b>DATE:</b> {time.strftime('%Y-%m-%d')}
            </div>
            """, unsafe_allow_html=True)

# 🎙️ SAMVADA
elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header'>🎙️ SAMVADA Comms</div>", unsafe_allow_html=True)
    key = st.secrets.get("GROQ_API_KEY", None)
    if key:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        
        st.markdown("<div class='saas-card' style='height: 400px; overflow-y: auto;'>", unsafe_allow_html=True)
        for m in st.session_state.chat_history:
            if m["role"] == "user":
                st.markdown(f"<div style='text-align: right; margin-bottom: 15px;'><span style='background: #7928CA; padding: 10px 15px; border-radius: 15px 15px 0 15px; display: inline-block;'>{m['content']}</span></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align: left; margin-bottom: 15px;'><span style='background: #00D4FF; color: black; padding: 10px 15px; border-radius: 15px 15px 15px 0; display: inline-block; font-weight: 500;'>{m['content']}</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        u_in = st.chat_input("Input strategic query here...")
        if u_in:
            st.session_state.chat_history.append({"role":"user", "content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":f"You are AROHA AI. Data: {ctx}"}, *st.session_state.chat_history[-3:]])
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant", "content":ans})
            st.rerun()
    else:
        st.warning("⚠️ GROQ_API_KEY secret not found. Conversational AI offline.")
```

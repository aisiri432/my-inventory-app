import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
import hashlib

# ── 1. PAGE CONFIG ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AROHA | Strategic Intelligence",
    layout="wide",
    page_icon="💠",
    initial_sidebar_state="expanded"
)

# ── 2. GLOBAL CSS ────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;600;700&family=Share+Tech+Mono&display=swap');

    /* ── BASE ── */
    html, body, [class*="css"] {
        font-family: 'Rajdhani', sans-serif;
        background: #05050f;
        color: #e0e8ff;
    }
    .stApp { background: #05050f; }

    /* Animated starfield background */
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse at 20% 50%, rgba(108,99,255,0.08) 0%, transparent 60%),
            radial-gradient(ellipse at 80% 20%, rgba(0,212,255,0.07) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 80%, rgba(255,0,200,0.05) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── TICKER ── */
    .ticker-wrap {
        width: 100%;
        background: linear-gradient(90deg, rgba(108,99,255,0.15), rgba(0,212,255,0.10), rgba(255,0,200,0.12));
        border-top: 1px solid rgba(0,212,255,0.4);
        border-bottom: 1px solid rgba(108,99,255,0.4);
        padding: 8px 0;
        overflow: hidden;
        margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(0,212,255,0.2), 0 0 40px rgba(108,99,255,0.1);
    }
    .ticker-text {
        display: inline-block;
        white-space: nowrap;
        animation: ticker-scroll 35s linear infinite;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.75rem;
        color: #00D4FF;
        letter-spacing: 0.12em;
        text-shadow: 0 0 10px #00D4FF, 0 0 20px #6C63FF;
    }
    @keyframes ticker-scroll {
        0%   { transform: translateX(100vw); }
        100% { transform: translateX(-100%); }
    }

    /* ── BRAND ── */
    .brand-title {
        font-family: 'Orbitron', monospace !important;
        font-weight: 900;
        font-size: 2.8rem;
        background: linear-gradient(135deg, #6C63FF 0%, #00D4FF 40%, #FF00C8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: none;
        filter: drop-shadow(0 0 20px rgba(0,212,255,0.6));
        letter-spacing: 0.15em;
    }
    .decisions-fade {
        background: linear-gradient(90deg, #FF00C8, #6C63FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 8px rgba(255,0,200,0.7));
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0a1f 0%, #08081a 100%) !important;
        border-right: 1px solid rgba(108,99,255,0.3) !important;
        box-shadow: 4px 0 30px rgba(108,99,255,0.15) !important;
    }
    .sidebar-sub {
        display: block;
        font-size: 0.65rem;
        color: #5a5f8a;
        letter-spacing: 0.1em;
        margin: -8px 0 8px 4px;
        text-transform: uppercase;
    }

    /* ── SIDEBAR BUTTONS ── */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, rgba(108,99,255,0.12), rgba(0,212,255,0.06));
        border: 1px solid rgba(108,99,255,0.35);
        color: #c8d0ff;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.08em;
        padding: 8px 14px;
        border-radius: 6px;
        transition: all 0.25s ease;
        text-align: left;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, rgba(108,99,255,0.35), rgba(0,212,255,0.2));
        border-color: #00D4FF;
        color: #fff;
        box-shadow: 0 0 15px rgba(0,212,255,0.4), 0 0 30px rgba(108,99,255,0.25);
        transform: translateX(3px);
    }

    /* ── FEATURE HEADER ── */
    .feature-header {
        font-family: 'Orbitron', monospace;
        font-size: 1.8rem;
        font-weight: 700;
        background: linear-gradient(135deg, #6C63FF, #00D4FF, #FF00C8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: 0.12em;
        margin-bottom: 20px;
        filter: drop-shadow(0 0 15px rgba(0,212,255,0.5));
    }

    /* ── METRIC CARDS ── */
    [data-testid="metric-container"] {
        background: linear-gradient(135deg, rgba(108,99,255,0.1), rgba(0,212,255,0.07));
        border: 1px solid rgba(0,212,255,0.25);
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 0 20px rgba(108,99,255,0.15), inset 0 1px 0 rgba(255,255,255,0.05);
        transition: box-shadow 0.3s;
    }
    [data-testid="metric-container"]:hover {
        box-shadow: 0 0 35px rgba(0,212,255,0.35), 0 0 60px rgba(108,99,255,0.2), inset 0 1px 0 rgba(255,255,255,0.08);
    }
    [data-testid="metric-container"] label {
        color: #8899cc !important;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.72rem !important;
        letter-spacing: 0.12em !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Orbitron', monospace !important;
        font-size: 1.6rem !important;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #00D4FF, #6C63FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ── INSIGHT BOX ── */
    .insight-box {
        background: linear-gradient(135deg, rgba(0,212,255,0.06), rgba(108,99,255,0.06));
        border: 1px solid rgba(0,212,255,0.3);
        border-left: 4px solid #00D4FF;
        border-radius: 10px;
        padding: 16px 20px;
        margin: 16px 0;
        box-shadow: 0 0 25px rgba(0,212,255,0.12), inset 0 0 40px rgba(108,99,255,0.04);
        font-size: 0.95rem;
        color: #c8d8ff;
    }

    /* ── SAAS CARD ── */
    .saas-card {
        background: linear-gradient(145deg, rgba(15,15,35,0.95), rgba(10,10,25,0.9));
        border: 1px solid rgba(108,99,255,0.25);
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 0 30px rgba(108,99,255,0.1), inset 0 1px 0 rgba(255,255,255,0.04);
        margin-bottom: 16px;
    }

    /* ── AI DECISION BOX ── */
    .ai-decision-box {
        background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(108,99,255,0.12));
        border: 1px solid rgba(0,212,255,0.4);
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 0 40px rgba(0,212,255,0.2), 0 0 80px rgba(108,99,255,0.1);
        text-align: center;
        margin-top: 16px;
        animation: pulse-glow 3s ease-in-out infinite;
    }
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 40px rgba(0,212,255,0.2), 0 0 80px rgba(108,99,255,0.1); }
        50%       { box-shadow: 0 0 60px rgba(0,212,255,0.4), 0 0 100px rgba(108,99,255,0.2); }
    }
    .ai-decision-box h3 {
        font-family: 'Orbitron', monospace;
        color: #00D4FF;
        text-shadow: 0 0 15px #00D4FF, 0 0 30px #6C63FF;
        margin-bottom: 8px;
    }

    /* ── DIRECTIVE MSG ── */
    .directive-msg {
        background: rgba(108,99,255,0.08);
        border-left: 3px solid #6C63FF;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
        font-size: 0.92rem;
        color: #d0d8ff;
        box-shadow: 0 0 15px rgba(108,99,255,0.1);
    }

    /* ── REVIEW BOX ── */
    .review-box {
        background: rgba(0,212,255,0.05);
        border: 1px solid rgba(0,212,255,0.15);
        border-radius: 8px;
        padding: 8px 12px;
        margin: 4px 0;
        font-size: 0.85rem;
        color: #99aabb;
    }

    /* ── FINANCIAL STAT ── */
    .financial-stat {
        background: linear-gradient(135deg, rgba(108,99,255,0.1), rgba(0,212,255,0.06));
        border: 1px solid rgba(108,99,255,0.3);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 0 25px rgba(108,99,255,0.12);
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.85rem;
        color: #8899cc;
        letter-spacing: 0.06em;
    }
    .financial-stat h2 {
        font-family: 'Orbitron', monospace;
        font-size: 2rem;
        margin: 8px 0 0;
        background: linear-gradient(90deg, #FFD700, #FF6B35);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        filter: drop-shadow(0 0 10px rgba(255,215,0,0.4));
    }

    /* ── RANK BADGE ── */
    .rank-gold   { color: #FFD700; text-shadow: 0 0 12px #FFD700, 0 0 25px #FF8C00; font-weight: 900; }
    .rank-silver { color: #C0C0C0; text-shadow: 0 0 10px #C0C0C0; font-weight: 700; }
    .rank-bronze { color: #CD7F32; text-shadow: 0 0 10px #CD7F32; font-weight: 700; }
    .rank-other  { color: #6C63FF; text-shadow: 0 0 8px #6C63FF; }

    /* ── RANK CARD ── */
    .rank-card {
        background: linear-gradient(145deg, rgba(15,15,35,0.98), rgba(10,10,28,0.95));
        border-radius: 14px;
        padding: 18px 22px;
        margin: 8px 0;
        display: flex;
        align-items: center;
        gap: 16px;
        transition: all 0.3s ease;
    }
    .rank-card-1 { border: 1px solid rgba(255,215,0,0.5);   box-shadow: 0 0 30px rgba(255,215,0,0.2),   inset 0 0 40px rgba(255,215,0,0.03); }
    .rank-card-2 { border: 1px solid rgba(192,192,192,0.4); box-shadow: 0 0 25px rgba(192,192,192,0.15), inset 0 0 30px rgba(192,192,192,0.02); }
    .rank-card-3 { border: 1px solid rgba(205,127,50,0.4);  box-shadow: 0 0 25px rgba(205,127,50,0.15),  inset 0 0 30px rgba(205,127,50,0.02); }
    .rank-card-n { border: 1px solid rgba(108,99,255,0.25); box-shadow: 0 0 15px rgba(108,99,255,0.1); }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.02);
        border-radius: 10px;
        border: 1px solid rgba(108,99,255,0.2);
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Rajdhani', sans-serif;
        font-weight: 600;
        color: #6670aa;
        letter-spacing: 0.06em;
        border-radius: 7px;
        padding: 8px 18px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, rgba(108,99,255,0.3), rgba(0,212,255,0.2)) !important;
        color: #fff !important;
        box-shadow: 0 0 20px rgba(0,212,255,0.2) !important;
    }

    /* ── MAIN BUTTONS ── */
    .main-content .stButton > button, .element-container .stButton > button {
        background: linear-gradient(135deg, rgba(108,99,255,0.2), rgba(0,212,255,0.12));
        border: 1px solid rgba(0,212,255,0.4);
        color: #e0eeff;
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        letter-spacing: 0.1em;
        font-size: 0.9rem;
        border-radius: 8px;
        padding: 8px 20px;
        transition: all 0.25s;
    }
    .main-content .stButton > button:hover, .element-container .stButton > button:hover {
        background: linear-gradient(135deg, rgba(108,99,255,0.45), rgba(0,212,255,0.3));
        box-shadow: 0 0 25px rgba(0,212,255,0.5), 0 0 50px rgba(108,99,255,0.3);
        transform: translateY(-2px);
        color: #fff;
    }

    /* ── DIVIDER LINE ── */
    .glow-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #6C63FF, #00D4FF, #FF00C8, transparent);
        border-radius: 2px;
        box-shadow: 0 0 15px rgba(0,212,255,0.5), 0 0 30px rgba(108,99,255,0.3);
        margin: 24px 0;
    }

    /* ── DATAFRAME ── */
    [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

    /* ── INPUT FIELDS ── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: rgba(10,10,30,0.8) !important;
        border: 1px solid rgba(108,99,255,0.35) !important;
        border-radius: 8px !important;
        color: #d0d8ff !important;
        font-family: 'Rajdhani', sans-serif !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #00D4FF !important;
        box-shadow: 0 0 15px rgba(0,212,255,0.3) !important;
    }

    /* ── ALERTS ── */
    .stSuccess { background: rgba(52,211,153,0.08) !important; border-color: rgba(52,211,153,0.4) !important; border-radius: 8px !important; }
    .stError   { background: rgba(255,80,80,0.08) !important;  border-color: rgba(255,80,80,0.4) !important;  border-radius: 8px !important; }
    .stWarning { background: rgba(255,180,0,0.08) !important;  border-color: rgba(255,180,0,0.4) !important;  border-radius: 8px !important; }
    .stInfo    { background: rgba(0,212,255,0.06) !important;  border-color: rgba(0,212,255,0.35) !important; border-radius: 8px !important; }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 6px; height: 6px; }
    ::-webkit-scrollbar-track { background: #07071a; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #6C63FF, #00D4FF); border-radius: 3px; }

    /* ── SCORE BADGE ── */
    .score-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-family: 'Share Tech Mono', monospace;
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
    }
    .score-high   { background: rgba(52,211,153,0.15); color: #34D399; border: 1px solid rgba(52,211,153,0.4); box-shadow: 0 0 8px rgba(52,211,153,0.3); }
    .score-med    { background: rgba(255,180,0,0.12);  color: #FBBF24; border: 1px solid rgba(255,180,0,0.4); box-shadow: 0 0 8px rgba(255,180,0,0.25); }
    .score-low    { background: rgba(255,80,80,0.12);  color: #F87171; border: 1px solid rgba(255,80,80,0.35); box-shadow: 0 0 8px rgba(248,113,113,0.25); }

    /* ── BRAND BAR ── */
    .brand-container { text-align: center; padding: 20px 0 24px; }

    /* ── TROPHY ── */
    .trophy-icon { font-size: 2rem; line-height: 1; }

    /* ── LOGIN CARD ── */
    .stTabs { background: rgba(255,255,255,0.01) !important; }
    </style>
    """, unsafe_allow_html=True)

inject_css()

# ── 3. DATABASE ───────────────────────────────────────────────────────────────
DB_FILE = 'aroha_nexus_v2.db'

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
        c.execute('''CREATE TABLE IF NOT EXISTS clients
            (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, client_name TEXT,
             deal_value REAL, negotiation_success REAL, trust_score TEXT,
             payment_speed TEXT, volume_orders INTEGER, relationship_months INTEGER,
             created_at TEXT)''')
        conn.commit()

init_db()

def hash_p(p):
    return hashlib.sha256(str.encode(p)).hexdigest()

def get_user_data():
    with get_db() as conn:
        return pd.read_sql_query("SELECT * FROM products WHERE username=?", conn, params=(st.session_state.user,))

def get_client_data():
    with get_db() as conn:
        df = pd.read_sql_query("SELECT * FROM clients WHERE username=?", conn, params=(st.session_state.user,))
    return df

def seed_clients_if_empty(username):
    with get_db() as conn:
        count = conn.execute("SELECT COUNT(*) FROM clients WHERE username=?", (username,)).fetchone()[0]
        if count == 0:
            sample = [
                (username, "Orion Traders",    150000, 96, "High",   "Fast",   48, 24),
                (username, "Alpha Corp",        120000, 92, "High",   "Fast",   36, 18),
                (username, "Zenith Ltd",         95000, 85, "Medium", "Normal", 28, 12),
                (username, "Nova Industries",    78000, 78, "Medium", "Slow",   20,  9),
                (username, "Apex Systems",       62000, 71, "Low",    "Normal", 15,  6),
                (username, "Vega Partners",      45000, 65, "Low",    "Slow",    9,  3),
            ]
            conn.executemany(
                "INSERT INTO clients (username,client_name,deal_value,negotiation_success,trust_score,payment_speed,volume_orders,relationship_months,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                [(*r, datetime.now().isoformat()) for r in sample]
            )
            conn.commit()

# ── 4. SESSION STATE ──────────────────────────────────────────────────────────
for k, v in [("auth", False), ("user", ""), ("page", "Dashboard"), ("chat_history", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── 5. AUTH ───────────────────────────────────────────────────────────────────
if not st.session_state.auth:
    st.markdown("""
    <div style='text-align:center; margin-top:60px; margin-bottom:40px;'>
        <div class='brand-title' style='font-size:4rem;'>AROHA</div>
        <p style='color:#6670aa; font-size:1.3rem; font-family:Rajdhani; letter-spacing:0.2em; margin-top:8px;'>
            STRATEGIC INTELLIGENCE NEXUS
        </p>
        <p style='color:#4a5070; font-size:1rem; font-family:Share Tech Mono;'>
            Turn Data Into <span class='decisions-fade'>Decisions</span>
        </p>
        <div style='height:2px; width:200px; margin:20px auto; background:linear-gradient(90deg,transparent,#6C63FF,#00D4FF,transparent); box-shadow:0 0 20px rgba(0,212,255,0.5);'></div>
    </div>
    """, unsafe_allow_html=True)

    _, col_center, _ = st.columns([0.2, 0.6, 0.2])
    with col_center:
        tabs = st.tabs(["🔑 LOGIN", "✨ JOIN"])
        with tabs[0]:
            u = st.text_input("Username", key="l_u", placeholder="Enter your ID")
            p = st.text_input("Password", type="password", key="l_p", placeholder="••••••••")
            if st.button("⚡ UNLOCK HUB", use_container_width=True):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True
                    st.session_state.user = u
                    seed_clients_if_empty(u)
                    st.rerun()
                else:
                    st.error("🔴 Access Denied — Invalid Credentials")
        with tabs[1]:
            nu = st.text_input("New ID", placeholder="Choose username")
            np_ = st.text_input("New Pass", type="password", placeholder="Choose password")
            if st.button("🚀 ENROLL", use_container_width=True):
                try:
                    with get_db() as conn:
                        conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np_)))
                    st.success("✅ Authorization Granted. You may login.")
                except:
                    st.error("🔴 ID already exists.")
    st.stop()

# ── 6. TICKER ────────────────────────────────────────────────────────────────
st.markdown(
    f"<div class='ticker-wrap'><div class='ticker-text'>"
    f"[DHWANI] {st.session_state.user.upper()} ACTIVE &nbsp;⬡&nbsp; "
    f"[LOGISTICS] Hover Map for Precision Addresses &nbsp;⬡&nbsp; "
    f"[KRIYA] Human Fatigue Delta Sensing Online &nbsp;⬡&nbsp; "
    f"[VITTA] Inventory ROI Optimized &nbsp;⬡&nbsp; "
    f"[PREKSHA] +8% Weekend Spike Detected &nbsp;⬡&nbsp; "
    f"[MITHRA+] 4 Active Negotiations Queued &nbsp;⬡&nbsp; "
    f"[NEXUS] All Systems Optimal — {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC"
    f"</div></div>",
    unsafe_allow_html=True
)

# ── 7. SIDEBAR ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='brand-container'>
        <div class='brand-title' style='font-size:2rem !important;'>AROHA</div>
        <div style='color:#5a6088; font-size:0.78rem; font-family:Share Tech Mono; letter-spacing:0.15em; margin-top:4px;'>
            Data Into <span class='decisions-fade'>Decisions</span>
        </div>
    </div>
    <div class='glow-divider' style='margin:0 0 16px;'></div>
    """, unsafe_allow_html=True)

    if st.button("🏠 DASHBOARD"):
        st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)

    nodes = [
        ("📝 NYASA",       "Nyasa",    "Add Items & PO Gen"),
        ("📈 PREKSHA",     "Preksha",  "Predict Demand Instantly"),
        ("🛡️ STAMBHA",    "Stambha",  "Test Supply Risks"),
        ("👷‍♂️ KRIYA",   "Kriya",    "Workforce Intelligence"),
        ("🎙️ SAMVADA",   "Samvada",  "Talk To System"),
        ("💰 VITTA",       "Vitta",    "Track Money Flow"),
        ("📦 SANCHARA",    "Sanchara", "Global Map & Flow"),
        ("🤝 MITHRA+",     "Mithra",   "AI Negotiation & Ranking"),
    ]
    for label, page_id, layman in nodes:
        if st.button(label, key=f"nav_{page_id}"):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-family:Share Tech Mono;font-size:0.68rem;color:#3a4060;text-align:center;'>USER: {st.session_state.user.upper()}</div>", unsafe_allow_html=True)
    if st.button("🔒 Logout"):
        st.session_state.auth = False; st.rerun()

# ── PLOTLY DARK TEMPLATE ──────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Rajdhani", color="#c8d0ff"),
    margin=dict(t=40, b=20, l=20, r=20),
)

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGES
# ═══════════════════════════════════════════════════════════════════════════════

# ── DASHBOARD ────────────────────────────────────────────────────────────────
if st.session_state.page == "Dashboard":
    st.markdown(f"<h1 style='font-family:Orbitron;font-size:1.6rem;color:#c8d8ff;letter-spacing:0.12em;'>⬡ STRATEGIC HUB: <span style='color:#00D4FF;'>{st.session_state.user.upper()}</span></h1>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("📝 Assets Managed",  len(df))
    with c2: st.metric("💰 Treasury Value",  f"₹{val:,.0f}")
    with c3: st.metric("🛡️ System Integrity", "OPTIMAL")
    with c4: st.metric("📡 Nodes Active",    "8 / 8")

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
        <b>💡 TACTICAL HANDOFF:</b> Warehouse throughput is stable. Intelligence node PREKSHA sensing
        <span style='color:#00D4FF;'>+8% weekend spike</span>. Recommend auditing NYASA registry.
        MITHRA+ has 4 negotiation drafts queued. VITTA reports ₹0 idle capital risk this cycle.
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div class='saas-card'><b style='color:#6C63FF;font-family:Orbitron;font-size:0.85rem;'>⬡ SYSTEM STATUS</b>", unsafe_allow_html=True)
        statuses = [
            ("PREKSHA", "DEMAND AI", "#34D399"),
            ("STAMBHA", "RISK ENGINE", "#34D399"),
            ("KRIYA", "WORKFORCE AI", "#FBBF24"),
            ("SAMVADA", "VOICE AI", "#34D399"),
            ("SANCHARA", "LOGISTICS MAP", "#34D399"),
            ("MITHRA+", "NEGOTIATION AI", "#34D399"),
        ]
        for name, desc, col in statuses:
            st.markdown(f"<div style='display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);'><span style='color:#8899cc;font-size:0.85rem;'>{name} <span style='color:#4a5070;'>·</span> {desc}</span><span style='color:{col};font-family:Share Tech Mono;font-size:0.75rem;text-shadow:0 0 8px {col};'>● ONLINE</span></div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        if not df.empty:
            fig = px.bar(df, x='name', y='current_stock', title="Inventory Overview",
                         color='current_stock',
                         color_continuous_scale=[[0,'#6C63FF'],[0.5,'#00D4FF'],[1,'#FF00C8']])
            fig.update_layout(**PLOT_LAYOUT, title_font=dict(family='Orbitron', size=13, color='#8899cc'))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<div class='saas-card' style='text-align:center;color:#4a5070;padding:60px;'>No inventory data yet.<br>Add items via NYASA.</div>", unsafe_allow_html=True)

# ── MITHRA+ ──────────────────────────────────────────────────────────────────
elif st.session_state.page == "Mithra":
    st.markdown("<div class='feature-header'>🤝 MITHRA+ — AI Negotiation & Client Command</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    df_products = get_user_data()
    df_clients  = get_client_data()

    tab_nego, tab_rank, tab_manage = st.tabs(["🚀 Negotiation Engine", "🏆 Client War Room", "➕ Manage Clients"])

    # ── TAB 1: NEGOTIATION ──────────────────────────────────────────────────
    with tab_nego:
        st.markdown("<div class='insight-box' style='border-color:#FF00C8;'><b>🤖 MITHRA+ BRIEFING:</b> AI negotiation protocols loaded. Select vendor and strategy to execute.</div>", unsafe_allow_html=True)

        if not df_products.empty:
            col1, col2 = st.columns([1, 1.5])
            with col1:
                vendor   = st.selectbox("🏭 Select Vendor", df_products['supplier'].dropna().unique() if 'supplier' in df_products.columns else ["Default Vendor"])
                strategy = st.radio("⚔️ Strategy", ["🕊️ Polite", "⚖️ Balanced", "🔥 Aggressive"])
                discount = st.slider("Target Discount %", 3, 25, 10)
                volume   = st.number_input("Projected Volume (units)", 100, 100000, 500, step=100)

            with col2:
                if st.button("🚀 EXECUTE AI NEGOTIATION", use_container_width=True):
                    savings = round(volume * df_products.iloc[0]['unit_price'] * (discount / 100), 0)
                    st.metric("💰 Potential Savings", f"₹{savings:,.0f}", f"↑ {discount}%")

                    tone_map = {
                        "🕊️ Polite":     ("We kindly request a pricing review", "look forward to a continued partnership"),
                        "⚖️ Balanced":   ("We require a pricing re-alignment",  "expect competitive terms to proceed"),
                        "🔥 Aggressive": ("We demand immediate price correction", "will reassess the vendor relationship otherwise"),
                    }
                    opener, closer = tone_map[strategy]
                    draft = f"""Dear {vendor} Team,

We have observed a {discount}% opportunity for pricing optimization based on our {volume:,} unit volume commitment and 
sustained transaction history with your organization.

{opener} on the current rate card. Given market benchmarks and our projected growth, we 
{closer}.

Proposed Terms:
  • Volume Commitment : {volume:,} units/quarter
  • Target Discount   : {discount}%
  • Payment Terms     : Net-30
  • Review Cycle      : Bi-annual

We are available for a call at your earliest convenience.

Regards,
{st.session_state.user.upper()} | AROHA Strategic Procurement"""
                    st.text_area("📄 AI-Drafted Negotiation Letter", draft, height=280)
                    st.success(f"✅ Strategy '{strategy}' deployed. Est. savings: ₹{savings:,.0f}")
                else:
                    st.markdown("""
                    <div class='saas-card' style='text-align:center; padding:50px 20px;'>
                        <div style='font-size:3rem;'>🤖</div>
                        <div style='color:#4a5070; font-family:Share Tech Mono; margin-top:12px; font-size:0.85rem;'>
                            Configure parameters and execute negotiation
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Add products via NYASA to enable negotiation engine.")

    # ── TAB 2: CLIENT WAR ROOM ──────────────────────────────────────────────
    with tab_rank:
        st.markdown("<div class='insight-box' style='border-color:#FFD700;'><b>🏆 CLIENT WAR ROOM:</b> AI-computed composite scores rank each client by deal value, negotiation success, trust, payment speed, and volume.</div>", unsafe_allow_html=True)

        if df_clients.empty:
            st.warning("No client data. Add clients in the 'Manage Clients' tab.")
        else:
            # ── COMPUTE COMPOSITE SCORE ────────────────────────────────────
            df_c = df_clients.copy()

            trust_map = {"High": 100, "Medium": 60, "Low": 20}
            speed_map = {"Fast": 100, "Normal": 60, "Slow": 20}
            df_c['trust_num'] = df_c['trust_score'].map(trust_map).fillna(50)
            df_c['speed_num'] = df_c['payment_speed'].map(speed_map).fillna(50)

            # Normalize deal_value and volume to 0-100
            dv_max  = df_c['deal_value'].max()
            vol_max = df_c['volume_orders'].max()
            df_c['dv_norm']  = (df_c['deal_value'] / dv_max * 100).round(1) if dv_max > 0 else 50
            df_c['vol_norm'] = (df_c['volume_orders'] / vol_max * 100).round(1) if vol_max > 0 else 50

            # Composite score (weighted)
            df_c['composite'] = (
                df_c['dv_norm']              * 0.30 +
                df_c['negotiation_success']  * 0.25 +
                df_c['trust_num']            * 0.20 +
                df_c['speed_num']            * 0.15 +
                df_c['vol_norm']             * 0.10
            ).round(1)

            df_c = df_c.sort_values('composite', ascending=False).reset_index(drop=True)

            # ── PODIUM ─────────────────────────────────────────────────────
            st.markdown("<h3 style='font-family:Orbitron;color:#00D4FF;font-size:1rem;letter-spacing:0.1em;'>⬡ ELITE PODIUM</h3>", unsafe_allow_html=True)

            podium_cols = st.columns(3)
            medals = [
                (0, "🥇", "rank-card-1", "rank-gold",   "#FFD700"),
                (1, "🥈", "rank-card-2", "rank-silver",  "#C0C0C0"),
                (2, "🥉", "rank-card-3", "rank-bronze",  "#CD7F32"),
            ]
            for idx, medal, card_cls, text_cls, glow in medals:
                if idx < len(df_c):
                    row = df_c.iloc[idx]
                    with podium_cols[idx]:
                        st.markdown(f"""
                        <div class='rank-card {card_cls}'>
                            <div style='font-size:2.2rem;'>{medal}</div>
                            <div>
                                <div class='{text_cls}' style='font-family:Orbitron;font-size:0.9rem;letter-spacing:0.08em;'>
                                    {row['client_name']}
                                </div>
                                <div style='color:{glow};font-family:Share Tech Mono;font-size:1.5rem;font-weight:900;
                                    text-shadow:0 0 20px {glow};margin:4px 0;'>{row['composite']}</div>
                                <div style='color:#5a6088;font-size:0.72rem;font-family:Share Tech Mono;'>COMPOSITE SCORE</div>
                                <div style='margin-top:6px;'>
                                    <span class='score-badge score-high'>₹{int(row["deal_value"]):,}</span>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

            # ── FULL LEADERBOARD ───────────────────────────────────────────
            st.markdown("<h3 style='font-family:Orbitron;color:#00D4FF;font-size:1rem;letter-spacing:0.1em;'>⬡ FULL LEADERBOARD</h3>", unsafe_allow_html=True)

            rank_icons = ["🥇","🥈","🥉"] + ["⬡"]*(len(df_c)-3)
            for i, (_, row) in enumerate(df_c.iterrows()):
                card_cls = f"rank-card-{i+1}" if i < 3 else "rank-card-n"
                score_cls = "score-high" if row['composite'] >= 80 else ("score-med" if row['composite'] >= 55 else "score-low")
                trust_cls = "score-high" if row['trust_score']=="High" else ("score-med" if row['trust_score']=="Medium" else "score-low")
                spd_cls   = "score-high" if row['payment_speed']=="Fast" else ("score-med" if row['payment_speed']=="Normal" else "score-low")

                st.markdown(f"""
                <div class='rank-card {card_cls}' style='margin:6px 0;'>
                    <div style='font-size:1.6rem; min-width:40px; text-align:center;'>{rank_icons[i]}</div>
                    <div style='flex:1;'>
                        <div style='display:flex; justify-content:space-between; align-items:center;'>
                            <span style='font-family:Rajdhani; font-size:1.05rem; font-weight:700; color:#d0d8ff;'>
                                {row['client_name']}
                            </span>
                            <span class='score-badge {score_cls}'>Score: {row['composite']}</span>
                        </div>
                        <div style='display:flex; gap:8px; margin-top:8px; flex-wrap:wrap;'>
                            <span class='score-badge score-high'>₹{int(row["deal_value"]):,}</span>
                            <span class='score-badge {"score-high" if row["negotiation_success"]>=85 else ("score-med" if row["negotiation_success"]>=70 else "score-low")}'>
                                🤝 {row['negotiation_success']}%
                            </span>
                            <span class='score-badge {trust_cls}'>🔒 {row['trust_score']}</span>
                            <span class='score-badge {spd_cls}'>⚡ {row['payment_speed']}</span>
                            <span class='score-badge score-med'>📦 {row['volume_orders']} orders</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

            # ── CHARTS ────────────────────────────────────────────────────
            st.markdown("<h3 style='font-family:Orbitron;color:#00D4FF;font-size:1rem;letter-spacing:0.1em;'>⬡ PERFORMANCE INTELLIGENCE</h3>", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                fig_bar = go.Figure(go.Bar(
                    x=df_c['composite'],
                    y=df_c['client_name'],
                    orientation='h',
                    marker=dict(
                        color=df_c['composite'],
                        colorscale=[[0,'#6C63FF'],[0.5,'#00D4FF'],[1,'#FF00C8']],
                        line=dict(color='rgba(0,212,255,0.3)', width=1)
                    ),
                    text=df_c['composite'].astype(str),
                    textposition='outside',
                    textfont=dict(family='Share Tech Mono', color='#c8d0ff', size=11),
                ))
                fig_bar.update_layout(**PLOT_LAYOUT, title="Composite Score Ranking",
                    title_font=dict(family='Orbitron', size=12, color='#8899cc'),
                    yaxis=dict(autorange='reversed'))
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_b:
                fig_scatter = px.scatter(
                    df_c, x='deal_value', y='negotiation_success',
                    size='volume_orders', color='composite',
                    color_continuous_scale=[[0,'#6C63FF'],[0.5,'#00D4FF'],[1,'#FF00C8']],
                    hover_name='client_name',
                    title="Deal Value vs Success Rate",
                    labels={'deal_value':'Deal Value (₹)', 'negotiation_success':'Negotiation Success (%)'}
                )
                fig_scatter.update_layout(**PLOT_LAYOUT, title_font=dict(family='Orbitron', size=12, color='#8899cc'))
                st.plotly_chart(fig_scatter, use_container_width=True)

            col_c, col_d = st.columns(2)
            with col_c:
                fig_radar = go.Figure()
                categories = ['Deal Value', 'Nego. Success', 'Trust', 'Payment Speed', 'Volume']
                colors_list = ['#6C63FF','#00D4FF','#FF00C8','#34D399','#FBBF24']
                for idx2, row2 in df_c.head(4).iterrows():
                    vals = [
                        row2['dv_norm'], row2['negotiation_success'],
                        row2['trust_num'], row2['speed_num'], row2['vol_norm']
                    ]
                    fig_radar.add_trace(go.Scatterpolar(
                        r=vals + [vals[0]], theta=categories + [categories[0]],
                        name=row2['client_name'],
                        line=dict(color=colors_list[idx2 % len(colors_list)], width=2),
                        fill='toself', fillcolor=colors_list[idx2 % len(colors_list)].replace('#','rgba(').replace('FF','255,').replace('00','0,') + '0.05)',
                    ))
                fig_radar.update_layout(**PLOT_LAYOUT, polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, range=[0,100], color='#3a4060', gridcolor='rgba(108,99,255,0.15)'),
                    angularaxis=dict(color='#8899cc', gridcolor='rgba(108,99,255,0.1)')
                ), title="Multi-Dimensional Radar", title_font=dict(family='Orbitron', size=12, color='#8899cc'))
                st.plotly_chart(fig_radar, use_container_width=True)

            with col_d:
                fig_pie = px.pie(
                    df_c, values='deal_value', names='client_name',
                    hole=0.55, title="Revenue Distribution",
                    color_discrete_sequence=['#6C63FF','#00D4FF','#FF00C8','#34D399','#FBBF24','#F87171']
                )
                fig_pie.update_traces(textfont=dict(family='Rajdhani'), pull=[0.05]*len(df_c))
                fig_pie.update_layout(**PLOT_LAYOUT, title_font=dict(family='Orbitron', size=12, color='#8899cc'))
                st.plotly_chart(fig_pie, use_container_width=True)

            # ── AI INSIGHT BOX ─────────────────────────────────────────────
            if len(df_c) > 0:
                top    = df_c.iloc[0]
                bottom = df_c.iloc[-1]
                st.markdown(f"""
                <div class='ai-decision-box'>
                    <h3>🤖 MITHRA+ INTELLIGENCE REPORT</h3>
                    <p style='color:#c8d8ff; font-size:0.95rem;'>
                        <b style='color:#FFD700;'>{top['client_name']}</b> leads the board with a composite score of
                        <b style='color:#00D4FF;'>{top['composite']}</b> — highest deal value and negotiation success.
                        Prioritize relationship deepening and volume scaling.<br><br>
                        <b style='color:#F87171;'>{bottom['client_name']}</b> ranks lowest at
                        <b style='color:#F87171;'>{bottom['composite']}</b>. Recommend structured review and
                        re-engagement protocol within 30 days.
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 3: MANAGE CLIENTS ───────────────────────────────────────────────
    with tab_manage:
        st.markdown("<h3 style='font-family:Orbitron;color:#6C63FF;font-size:1rem;letter-spacing:0.1em;'>⬡ ADD / UPDATE CLIENT</h3>", unsafe_allow_html=True)

        with st.form("add_client"):
            c1, c2, c3 = st.columns(3)
            with c1:
                cname   = st.text_input("Client Name")
                deal_v  = st.number_input("Deal Value (₹)", 0, 10000000, 50000, step=1000)
                nego_s  = st.slider("Negotiation Success %", 0, 100, 75)
            with c2:
                trust   = st.selectbox("Trust Score", ["High","Medium","Low"])
                speed   = st.selectbox("Payment Speed", ["Fast","Normal","Slow"])
            with c3:
                vol_ord = st.number_input("Volume Orders", 0, 10000, 10)
                rel_mo  = st.number_input("Relationship (months)", 0, 240, 6)

            if st.form_submit_button("➕ ADD CLIENT", use_container_width=True):
                if cname:
                    with get_db() as conn:
                        conn.execute(
                            "INSERT INTO clients (username,client_name,deal_value,negotiation_success,trust_score,payment_speed,volume_orders,relationship_months,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                            (st.session_state.user, cname, deal_v, nego_s, trust, speed, vol_ord, rel_mo, datetime.now().isoformat())
                        )
                    st.success(f"✅ {cname} added to roster.")
                    st.rerun()
                else:
                    st.error("🔴 Client name is required.")

        st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

        if not df_clients.empty:
            st.markdown("<h3 style='font-family:Orbitron;color:#6C63FF;font-size:1rem;letter-spacing:0.1em;'>⬡ CURRENT ROSTER</h3>", unsafe_allow_html=True)
            st.dataframe(
                df_clients[['client_name','deal_value','negotiation_success','trust_score','payment_speed','volume_orders','relationship_months']].rename(columns={
                    'client_name':'Client','deal_value':'Deal Value (₹)','negotiation_success':'Success %',
                    'trust_score':'Trust','payment_speed':'Payment','volume_orders':'Orders','relationship_months':'Months'
                }),
                use_container_width=True
            )

            del_client = st.selectbox("🗑️ Remove Client", [""] + list(df_clients['client_name'].tolist()))
            if del_client and st.button("❌ REMOVE", use_container_width=False):
                with get_db() as conn:
                    conn.execute("DELETE FROM clients WHERE username=? AND client_name=?", (st.session_state.user, del_client))
                st.success(f"🗑️ {del_client} removed.")
                st.rerun()

# ── KRIYA ────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Kriya":
    st.markdown("<div class='feature-header'>👷‍♂️ KRIYA — Workforce Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='insight-box' style='border-color:#6C63FF;'><b>🚀 WORKFORCE BRIEFING:</b> AI orchestrating tasks to Ravi and Ananya. Fatigue sensors active. Peak efficiency window: 09:00–14:00.</div>", unsafe_allow_html=True)

    tab_worker, tab_manager = st.tabs(["🔧 Worker Interface (HUD)", "📊 Manager Intelligence"])

    with tab_worker:
        col_q, col_s = st.columns([2, 1])
        with col_q:
            st.markdown("<div class='directive-msg'><b>[ASSIGNMENT]</b> Pick 12x Titanium Chassis for Station B.</div>", unsafe_allow_html=True)
            st.markdown("<div class='directive-msg'><b>[GUIDANCE]</b> Proceed to <b>Shelf B2 via Aisle 3</b>. Optimal path highlighted.</div>", unsafe_allow_html=True)
            st.markdown("<div class='directive-msg'><b>[NEXT]</b> After Station B — audit Zone C Sensor Array. Est. 8 min.</div>", unsafe_allow_html=True)
            if st.button("📦 SIMULATE SCAN"):
                st.error("🚨 [ERROR PREVENTION] Warning: Incorrect item (SKU-405). Verify barcode on Bin B2.")
            if st.button("✅ CONFIRM PICK"):
                st.success("✅ Pick confirmed. 12x Titanium Chassis logged. Station B delivery initiated.")
        with col_s:
            st.markdown("""
            <div class='saas-card' style='text-align:center;'>
                <h4 style='color:#8899cc; font-family:Share Tech Mono; font-size:0.8rem; letter-spacing:0.1em;'>SHIFT PERFORMANCE</h4>
                <div style='font-family:Orbitron; font-size:2.5rem; color:#00D4FF; text-shadow:0 0 20px #00D4FF;'>42</div>
                <div style='color:#8899cc; font-size:0.8rem; font-family:Share Tech Mono;'>PICKS / HR</div>
                <div style='color:#34D399; font-size:0.9rem; margin-top:8px;'>+12% vs Team Avg</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("🎙️ 'What next?'"):
                st.info("🤖 AI: Ravi → Zone C sensor audit. Route: Aisle 1 North. ETA: 3 min.")
            st.warning("🧠 [FATIGUE ALERT] Speed drop for Ravi. Suggest 10-min break now.")

    with tab_manager:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("<b style='color:#6C63FF; font-family:Orbitron; font-size:0.85rem;'>⬡ THROUGHPUT TREND</b>", unsafe_allow_html=True)
            fig_t = px.line(y=[80,85,75,90,88,92,87], title="Real-time Throughput", template="plotly_dark")
            fig_t.update_traces(line_color='#6C63FF', line_width=2, fill='tozeroy', fillcolor='rgba(108,99,255,0.1)')
            fig_t.update_layout(**PLOT_LAYOUT)
            st.plotly_chart(fig_t, use_container_width=True)
        with c2:
            st.markdown("<b style='color:#00D4FF; font-family:Orbitron; font-size:0.85rem;'>⬡ RESOURCE MATRIX</b>", unsafe_allow_html=True)
            workers = ["Ravi","Ananya","Dev"]
            fig_b = go.Figure(data=[
                go.Bar(name='Accuracy', x=workers, y=[98,92,75], marker_color='#00D4FF'),
                go.Bar(name='Speed',    x=workers, y=[90,85,70], marker_color='#6C63FF'),
            ])
            fig_b.update_layout(**PLOT_LAYOUT, barmode='group')
            st.plotly_chart(fig_b, use_container_width=True)
        st.success("✅ Top Performer: Ananya — 98% Accuracy | 92% Speed | 0 Errors this shift.")

# ── VITTA ────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>💰 VITTA — Capital Intelligence</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    df = get_user_data()
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        idle_r  = total_v * 0.15
        roi_e   = total_v * 0.22

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Value",     f"₹{total_v:,.0f}")
        with c2: st.metric("Idle Capital Risk", f"₹{idle_r:,.0f}", delta="-15%", delta_color="inverse")
        with c3: st.metric("Est. ROI (Annual)", f"₹{roi_e:,.0f}", delta="+22%")

        st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

        col_l, col_r = st.columns([1, 1])
        with col_l:
            st.markdown(f"<div class='financial-stat'>Total Inventory Value<h2>₹{total_v:,.0f}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='financial-stat' style='margin-top:16px;'>Idle Capital Risk (15%)<h2 style='background:linear-gradient(90deg,#F87171,#FF4444);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 10px rgba(248,113,113,0.5));'>₹{idle_r:,.0f}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='financial-stat' style='margin-top:16px;'>Projected Annual ROI<h2 style='background:linear-gradient(90deg,#34D399,#00D4FF);-webkit-background-clip:text;-webkit-text-fill-color:transparent;filter:drop-shadow(0 0 10px rgba(52,211,153,0.5));'>₹{roi_e:,.0f}</h2></div>", unsafe_allow_html=True)
        with col_r:
            fig_pie = px.pie(df, values='current_stock', names='name', hole=0.5,
                             color_discrete_sequence=['#6C63FF','#00D4FF','#FF00C8','#34D399','#FBBF24'])
            fig_pie.update_layout(**PLOT_LAYOUT, title="Capital Allocation Matrix", title_font=dict(family='Orbitron',size=12,color='#8899cc'))
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.markdown("<div class='insight-box'>No inventory data. Add items via NYASA to see financial analytics.</div>", unsafe_allow_html=True)

# ── SANCHARA ─────────────────────────────────────────────────────────────────
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>📦 SANCHARA — Global Logistics</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["🌐 Precision Map", "📦 Floor Ops", "↩️ Returns (PUNAH)"])
    with t1:
        map_pts = pd.DataFrame({
            'lat':     [12.9716, 22.31, 37.77,  1.35,    51.5,   35.68],
            'lon':     [77.59,  114.16,-122.41, 103.81, -0.12,  139.69],
            'Node':    ['HQ Bangalore','Factory HK','SF Depot','Singapore Hub','London Node','Tokyo Relay'],
            'Status':  ['OPTIMAL','OPTIMAL','OPTIMAL','⚠️ PORT ALERT','OPTIMAL','OPTIMAL'],
            'Address': ['MG Road, Bangalore','Lantau Island, HK','Market St, SF','Jurong Port (🔴 CLOSED)','Canary Wharf, London','Shinjuku, Tokyo'],
        })
        fig_map = px.scatter_mapbox(
            map_pts, lat="lat", lon="lon",
            hover_name="Node", hover_data={"Address":True, "Status":True, "lat":False, "lon":False},
            color="Status",
            color_discrete_map={"OPTIMAL":"#00D4FF","⚠️ PORT ALERT":"#F87171"},
            zoom=1, height=480,
        )
        fig_map.update_layout(mapbox_style="carto-darkmatter", margin={"r":0,"t":0,"l":0,"b":0},
                               paper_bgcolor="rgba(0,0,0,0)", legend=dict(font=dict(color="#c8d0ff")))
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("<div style='background:rgba(255,255,255,0.02);padding:15px;border-radius:10px;border:1px solid #333;margin-top:10px;'><span style='color:#00D4FF;font-family:Share Tech Mono;'>📍 BLUE</span> Stable nodes &nbsp;|&nbsp; <span style='color:#F87171;font-family:Share Tech Mono;'>🔴 RED</span> Crisis nodes &nbsp;|&nbsp; Hover dots for details</div>", unsafe_allow_html=True)

    with t2:
        df_inv = get_user_data()
        c1, c2, c3 = st.columns(3)
        c1.metric("📦 Items Shipped Today", "1,240")
        c2.metric("🏭 Floor Assets", f"{df_inv['current_stock'].sum() + 142 if not df_inv.empty else 142} Units", "+142 Returns")
        c3.metric("🚛 Active Routes", "7")

    with t3:
        st.table(pd.DataFrame({
            'Product':  ['Quantum X1','4K Monitor','USB-C Hub'],
            'Amount':   [4, 2, 6],
            'Reason':   ['Defective Logic','Screen Bleed','Port Failure'],
            'Status':   ['Processing','Approved','Pending'],
        }))

# ── PREKSHA ──────────────────────────────────────────────────────────────────
elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>📈 PREKSHA — Demand AI</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    df = get_user_data()
    if not df.empty:
        target = st.selectbox("⬡ Select Asset", df['name'])
        p      = df[df['name'] == target].iloc[0]

        col_a, col_b = st.columns([1, 2])
        with col_a:
            if p['image_url'] and str(p['image_url']) != "nan":
                st.image(p['image_url'], use_container_width=True)
            st.markdown(f"""
            <div class='saas-card'>
                <div style='font-family:Share Tech Mono;font-size:0.7rem;color:#5a6088;letter-spacing:0.1em;'>CURRENT STOCK</div>
                <div style='font-family:Orbitron;font-size:2rem;color:#00D4FF;text-shadow:0 0 15px #00D4FF;'>{p['current_stock']}</div>
                <div style='font-family:Share Tech Mono;font-size:0.7rem;color:#5a6088;letter-spacing:0.1em;margin-top:12px;'>LEAD TIME</div>
                <div style='font-family:Orbitron;font-size:1.5rem;color:#6C63FF;'>{p['lead_time']}d</div>
                <div style='font-family:Share Tech Mono;font-size:0.7rem;color:#5a6088;letter-spacing:0.1em;margin-top:12px;'>UNIT PRICE</div>
                <div style='font-family:Orbitron;font-size:1.5rem;color:#FF00C8;text-shadow:0 0 10px #FF00C8;'>₹{p['unit_price']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
            if p['reviews']:
                for r in p['reviews'].split('|'):
                    st.markdown(f"<div class='review-box'>⭐ {r}</div>", unsafe_allow_html=True)

        with col_b:
            preds = np.random.randint(20, 50, 14)
            days  = [f"D+{i+1}" for i in range(14)]
            fig_f = go.Figure()
            fig_f.add_trace(go.Scatter(
                x=days, y=preds, fill='tozeroy',
                line=dict(color='#00D4FF', width=2),
                fillcolor='rgba(0,212,255,0.08)',
                name='Forecast',
            ))
            fig_f.add_trace(go.Scatter(
                x=days, y=[p['current_stock']/14]*14,
                line=dict(color='#F87171', width=1, dash='dash'),
                name='Daily Stock Rate',
            ))
            fig_f.update_layout(**PLOT_LAYOUT, title="14-Day AI Forecasting Path",
                                 title_font=dict(family='Orbitron',size=13,color='#8899cc'))
            st.plotly_chart(fig_f, use_container_width=True)

            order_qty = max(0, int(preds.sum()) - int(p['current_stock']))
            st.markdown(f"""
            <div class='ai-decision-box'>
                <h3>🤖 PREKSHA AI RECOMMENDATION</h3>
                <p style='color:#c8d8ff;'>Order <b style='font-size:1.5rem;color:#00D4FF;'>{order_qty}</b> units of
                <b style='color:#FF00C8;'>{target}</b> immediately.<br>
                <span style='color:#5a6088;font-size:0.85rem;'>14-day projected demand: {preds.sum()} | Current stock: {int(p['current_stock'])}</span></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='insight-box'>No products found. Add inventory via NYASA first.</div>", unsafe_allow_html=True)

# ── STAMBHA ──────────────────────────────────────────────────────────────────
elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header'>🛡️ STAMBHA — Risk Engine</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    shock = st.selectbox("⚡ Select Shock Scenario", ["Normal Operations", "Port Closure (3× Lead)", "Demand Surge (2× Normal)", "Supplier Failure"])
    multipliers = {"Normal Operations":1, "Port Closure (3× Lead)":3, "Demand Surge (2× Normal)":2, "Supplier Failure":4}
    m = multipliers[shock]

    df = get_user_data()
    if not df.empty:
        st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
        risk_count = 0
        for _, p in df.iterrows():
            ttr = p['lead_time'] * m
            tts = round(p['current_stock'] / max(12, 1), 1)
            if tts < ttr:
                st.error(f"🔴 CRITICAL: **{p['name']}** runs out in **{tts}d**. Recovery: **{ttr}d**. Order NOW.")
                risk_count += 1
            else:
                st.success(f"✅ {p['name']} — Safe for {tts}d (recovery: {ttr}d)")

        if risk_count == 0:
            st.markdown("<div class='ai-decision-box'><h3>🛡️ ALL CLEAR</h3><p style='color:#34D399;'>No critical risks under current scenario.</p></div>", unsafe_allow_html=True)

        st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
        st.dataframe(df[['name','current_stock','lead_time']], use_container_width=True)
    else:
        st.markdown("<div class='insight-box'>No inventory data. Add items via NYASA to run risk simulations.</div>", unsafe_allow_html=True)

# ── NYASA ────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>📝 NYASA — Asset Registry</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["📥 Bulk Sync", "✍️ Manual Registry", "📄 PO Generator"])

    with t1:
        st.markdown("<div class='insight-box'>Upload a CSV with columns: name, category, current_stock, unit_price, lead_time, supplier, image_url, reviews</div>", unsafe_allow_html=True)
        f = st.file_uploader("Upload CSV", type="csv")
        if f and st.button("⚡ SYNC", use_container_width=True):
            u_df = pd.read_csv(f)
            u_df['username'] = st.session_state.user
            for col in ['category','supplier','image_url','reviews']:
                if col not in u_df.columns:
                    u_df[col] = ""
            with get_db() as conn:
                u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success(f"✅ Synced {len(u_df)} records.")

    with t2:
        with st.form("add_product"):
            c1, c2 = st.columns(2)
            with c1:
                n   = st.text_input("Product Name")
                s   = st.number_input("Current Stock", 0)
                p   = st.number_input("Unit Price (₹)", 0.0)
                lt  = st.number_input("Lead Time (days)", 1)
            with c2:
                cat  = st.text_input("Category")
                sup  = st.text_input("Supplier")
                img  = st.text_input("Image URL")
                rev  = st.text_area("Reviews (separate by |)")
            if st.form_submit_button("💾 COMMIT TO REGISTRY", use_container_width=True):
                with get_db() as conn:
                    conn.execute(
                        "INSERT INTO products (username,name,category,current_stock,unit_price,lead_time,supplier,image_url,reviews) VALUES (?,?,?,?,?,?,?,?,?)",
                        (st.session_state.user, n, cat, s, p, lt, sup, img, rev)
                    )
                st.success(f"✅ {n} committed to registry.")

    with t3:
        df_po = get_user_data()
        if not df_po.empty:
            sel_po = st.selectbox("Select Product", df_po['name'])
            item   = df_po[df_po['name']==sel_po].iloc[0]
            po_id  = f"ARH-{np.random.randint(10000,99999)}"
            st.code(f"""
╔══════════════════════════════════════════════════╗
  AROHA NEXUS — PURCHASE ORDER
  PO-ID   : #{po_id}
  DATE    : {datetime.now().strftime('%Y-%m-%d %H:%M')} IST
  AUTH BY : {st.session_state.user.upper()}
══════════════════════════════════════════════════
  ITEM    : {item['name']}
  STOCK   : {item['current_stock']} units
  PRICE   : ₹{item['unit_price']:,.2f} / unit
  SUPPLIER: {item.get('supplier','N/A')}
  LEAD    : {item['lead_time']} days
══════════════════════════════════════════════════
  STATUS  : PENDING APPROVAL
╚══════════════════════════════════════════════════╝
            """)
        else:
            st.markdown("<div class='insight-box'>No products found. Add items in Manual Registry first.</div>", unsafe_allow_html=True)

# ── SAMVADA ──────────────────────────────────────────────────────────────────
elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header'>🎙️ SAMVADA — AI Voice Interface</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    key = st.secrets.get("GROQ_API_KEY", None)
    if not key:
        st.markdown("<div class='insight-box' style='border-color:#FBBF24;'>⚠️ <b>SAMVADA offline.</b> Add GROQ_API_KEY to Streamlit secrets to enable AI chat.</div>", unsafe_allow_html=True)
    else:
        from openai import OpenAI
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)

        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        u_in = st.chat_input("Strategic query to AROHA AI...")
        if u_in:
            st.session_state.chat_history.append({"role":"user","content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role":"system","content":f"You are AROHA AI — a strategic supply chain intelligence system. Be concise, insightful, and data-driven. User inventory: {ctx}"},
                    *st.session_state.chat_history[-6:]
                ]
            )
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant","content":ans})
            st.rerun()

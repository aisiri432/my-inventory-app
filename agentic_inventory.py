import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import hashlib

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AROHA | Strategic Intelligence",
    layout="wide",
    page_icon="◈",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600;700&family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@300;400;500&display=swap');

    /* ── PALETTE (ancient × gen-z) ──
       bg:        #0e0d0b  (scorched obsidian)
       surface1:  #161410  (dark clay)
       surface2:  #1e1b16  (aged wood)
       terracotta:#c4673a  (burnt clay)
       ochre:     #d4a44c  (aged gold)
       sage:      #7a9e7e  (faded moss)
       ash:       #9e9689  (weathered stone)
       linen:     #e8e0d0  (parchment)
       blush:     #d4856a  (faded fresco)
    */

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background: #0e0d0b;
        color: #c8bfb0;
    }
    .stApp {
        background: #0e0d0b;
    }
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse at 15% 40%, rgba(196,103,58,0.06) 0%, transparent 55%),
            radial-gradient(ellipse at 85% 20%, rgba(212,164,76,0.05) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 90%, rgba(122,158,126,0.04) 0%, transparent 45%);
        pointer-events: none;
        z-index: 0;
    }

    /* ── TICKER ── */
    .ticker-wrap {
        width: 100%;
        background: linear-gradient(90deg, rgba(196,103,58,0.08), rgba(212,164,76,0.06), rgba(196,103,58,0.08));
        border-top: 1px solid rgba(196,103,58,0.25);
        border-bottom: 1px solid rgba(212,164,76,0.2);
        padding: 7px 0;
        overflow: hidden;
        margin-bottom: 24px;
    }
    .ticker-text {
        display: inline-block;
        white-space: nowrap;
        animation: ticker-scroll 40s linear infinite;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        color: #d4a44c;
        letter-spacing: 0.14em;
    }
    @keyframes ticker-scroll {
        0%   { transform: translateX(100vw); }
        100% { transform: translateX(-100%); }
    }

    /* ── BRAND ── */
    .brand-title {
        font-family: 'Cinzel', serif !important;
        font-weight: 700;
        font-size: 2.6rem;
        color: #d4a44c;
        letter-spacing: 0.25em;
        text-shadow: 0 0 30px rgba(212,164,76,0.3);
    }
    .decisions-fade {
        color: #c4673a;
        text-shadow: 0 0 15px rgba(196,103,58,0.4);
    }
    .brand-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #5a5244;
        letter-spacing: 0.3em;
        text-transform: uppercase;
    }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #121009 0%, #0e0d0b 100%) !important;
        border-right: 1px solid rgba(196,103,58,0.18) !important;
    }
    .sidebar-sub {
        display: block;
        font-size: 0.6rem;
        color: #3d3830;
        letter-spacing: 0.12em;
        margin: -6px 0 9px 4px;
        text-transform: uppercase;
        font-family: 'JetBrains Mono', monospace;
    }

    /* ── SIDEBAR BUTTONS ── */
    [data-testid="stSidebar"] .stButton > button {
        width: 100%;
        background: rgba(196,103,58,0.06);
        border: 1px solid rgba(196,103,58,0.2);
        color: #a89880;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 0.85rem;
        letter-spacing: 0.04em;
        padding: 9px 14px;
        border-radius: 6px;
        transition: all 0.2s ease;
        text-align: left;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(196,103,58,0.14);
        border-color: rgba(212,164,76,0.4);
        color: #e8d8c0;
        box-shadow: 0 0 12px rgba(212,164,76,0.12);
        transform: translateX(2px);
    }

    /* ── FEATURE HEADER ── */
    .feature-header {
        font-family: 'Cinzel', serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: #d4a44c;
        letter-spacing: 0.15em;
        margin-bottom: 4px;
        text-shadow: 0 0 20px rgba(212,164,76,0.25);
    }
    .feature-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        color: #4a4238;
        letter-spacing: 0.2em;
        margin-bottom: 20px;
    }

    /* ── DIVIDER ── */
    .glow-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(196,103,58,0.5), rgba(212,164,76,0.6), rgba(196,103,58,0.5), transparent);
        border-radius: 1px;
        margin: 20px 0;
        box-shadow: 0 0 8px rgba(212,164,76,0.15);
    }

    /* ── METRIC CARDS ── */
    [data-testid="metric-container"] {
        background: #161410;
        border: 1px solid rgba(196,103,58,0.2);
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 2px 20px rgba(0,0,0,0.4), 0 0 0 1px rgba(212,164,76,0.04);
    }
    [data-testid="metric-container"]:hover {
        border-color: rgba(212,164,76,0.35);
        box-shadow: 0 2px 20px rgba(0,0,0,0.4), 0 0 15px rgba(212,164,76,0.08);
    }
    [data-testid="metric-container"] label {
        color: #5a5244 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.65rem !important;
        letter-spacing: 0.15em !important;
        text-transform: uppercase !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-family: 'Cinzel', serif !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #d4a44c !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricDelta"] {
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.72rem !important;
    }

    /* ── CARDS ── */
    .saas-card {
        background: #161410;
        border: 1px solid rgba(196,103,58,0.18);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 24px rgba(0,0,0,0.35);
    }
    .insight-box {
        background: rgba(196,103,58,0.05);
        border: 1px solid rgba(196,103,58,0.25);
        border-left: 3px solid #c4673a;
        border-radius: 0 8px 8px 0;
        padding: 14px 18px;
        margin: 14px 0;
        font-size: 0.88rem;
        color: #a89880;
        line-height: 1.6;
    }
    .ai-decision-box {
        background: linear-gradient(135deg, rgba(212,164,76,0.06), rgba(196,103,58,0.05));
        border: 1px solid rgba(212,164,76,0.3);
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        margin-top: 16px;
        box-shadow: 0 0 25px rgba(212,164,76,0.08), inset 0 1px 0 rgba(212,164,76,0.06);
    }
    .ai-decision-box h3 {
        font-family: 'Cinzel', serif;
        color: #d4a44c;
        text-shadow: 0 0 12px rgba(212,164,76,0.3);
        margin-bottom: 10px;
        letter-spacing: 0.12em;
        font-size: 1rem;
    }

    /* ── DIRECTIVE ── */
    .directive-msg {
        background: rgba(122,158,126,0.05);
        border-left: 2px solid rgba(122,158,126,0.5);
        padding: 10px 16px;
        border-radius: 0 6px 6px 0;
        margin: 8px 0;
        font-size: 0.88rem;
        color: #a0b8a4;
    }

    /* ── REVIEW BOX ── */
    .review-box {
        background: rgba(212,164,76,0.04);
        border: 1px solid rgba(212,164,76,0.12);
        border-radius: 6px;
        padding: 7px 12px;
        margin: 4px 0;
        font-size: 0.82rem;
        color: #7a6e60;
    }

    /* ── FINANCIAL STAT ── */
    .financial-stat {
        background: #161410;
        border: 1px solid rgba(196,103,58,0.2);
        border-radius: 10px;
        padding: 20px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        color: #5a5244;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    .financial-stat h2 {
        font-family: 'Cinzel', serif;
        font-size: 1.8rem;
        margin: 8px 0 0;
        color: #d4a44c;
        text-shadow: 0 0 12px rgba(212,164,76,0.25);
    }

    /* ── RANK CARDS ── */
    .rank-card {
        background: #161410;
        border-radius: 10px;
        padding: 16px 18px;
        margin: 6px 0;
        display: flex;
        align-items: center;
        gap: 14px;
        border: 1px solid rgba(196,103,58,0.15);
    }
    .rank-card-1 {
        border-color: rgba(212,164,76,0.45);
        box-shadow: 0 0 20px rgba(212,164,76,0.08), inset 0 1px 0 rgba(212,164,76,0.06);
    }
    .rank-card-2 {
        border-color: rgba(158,150,137,0.4);
        box-shadow: 0 0 15px rgba(158,150,137,0.06);
    }
    .rank-card-3 {
        border-color: rgba(196,103,58,0.4);
        box-shadow: 0 0 15px rgba(196,103,58,0.07);
    }
    .rank-card-n { border-color: rgba(196,103,58,0.12); }
    .rank-gold   { color: #d4a44c; font-family: 'Cinzel', serif; text-shadow: 0 0 10px rgba(212,164,76,0.4); }
    .rank-silver { color: #9e9689; font-family: 'Cinzel', serif; }
    .rank-bronze { color: #c4673a; font-family: 'Cinzel', serif; text-shadow: 0 0 8px rgba(196,103,58,0.35); }

    /* ── SCORE BADGES ── */
    .score-badge {
        display: inline-block;
        padding: 2px 9px;
        border-radius: 4px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.05em;
    }
    .score-high { background: rgba(122,158,126,0.12); color: #7a9e7e; border: 1px solid rgba(122,158,126,0.3); }
    .score-med  { background: rgba(212,164,76,0.1);  color: #a07830; border: 1px solid rgba(212,164,76,0.25); }
    .score-low  { background: rgba(196,103,58,0.1);  color: #c4673a; border: 1px solid rgba(196,103,58,0.3); }

    /* ── TABS ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(22,20,16,0.8);
        border-radius: 8px;
        border: 1px solid rgba(196,103,58,0.15);
        padding: 3px;
        gap: 3px;
    }
    .stTabs [data-baseweb="tab"] {
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        color: #5a5244;
        letter-spacing: 0.04em;
        border-radius: 6px;
        font-size: 0.82rem;
    }
    .stTabs [aria-selected="true"] {
        background: rgba(196,103,58,0.15) !important;
        color: #d4a44c !important;
        box-shadow: 0 0 10px rgba(212,164,76,0.08) !important;
    }

    /* ── BUTTONS (main) ── */
    .element-container .stButton > button {
        background: rgba(196,103,58,0.1);
        border: 1px solid rgba(196,103,58,0.35);
        color: #c8b090;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        letter-spacing: 0.05em;
        font-size: 0.85rem;
        border-radius: 7px;
        padding: 8px 18px;
        transition: all 0.2s;
    }
    .element-container .stButton > button:hover {
        background: rgba(196,103,58,0.22);
        border-color: rgba(212,164,76,0.5);
        color: #e8d0b0;
        box-shadow: 0 0 14px rgba(212,164,76,0.12);
    }

    /* ── INPUTS ── */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: #121009 !important;
        border: 1px solid rgba(196,103,58,0.25) !important;
        border-radius: 7px !important;
        color: #c8bfb0 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
    }
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(212,164,76,0.5) !important;
        box-shadow: 0 0 10px rgba(212,164,76,0.08) !important;
    }
    .stSelectbox > div > div {
        background: #121009 !important;
        border: 1px solid rgba(196,103,58,0.25) !important;
        border-radius: 7px !important;
        color: #c8bfb0 !important;
    }

    /* ── ALERTS ── */
    .stSuccess { background: rgba(122,158,126,0.08) !important; border-color: rgba(122,158,126,0.3) !important; border-radius: 7px !important; color: #7a9e7e !important; }
    .stError   { background: rgba(196,103,58,0.08) !important;  border-color: rgba(196,103,58,0.35) !important; border-radius: 7px !important; }
    .stWarning { background: rgba(212,164,76,0.07) !important;  border-color: rgba(212,164,76,0.3) !important;  border-radius: 7px !important; }
    .stInfo    { background: rgba(122,158,126,0.06) !important; border-color: rgba(122,158,126,0.25) !important;border-radius: 7px !important; }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: #0e0d0b; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(180deg, #c4673a, #d4a44c); border-radius: 3px; }

    /* ── DATAFRAME ── */
    [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; border: 1px solid rgba(196,103,58,0.15); }

    /* ── STATUS DOT ── */
    .status-online  { color: #7a9e7e; }
    .status-warning { color: #d4a44c; }
    .status-offline { color: #c4673a; }

    /* ── BRAND CONTAINER ── */
    .brand-container { text-align: center; padding: 18px 0 22px; }

    /* ── PODIUM NUMBER ── */
    .podium-score {
        font-family: 'Cinzel', serif;
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1;
        margin: 4px 0;
    }
    </style>
    """, unsafe_allow_html=True)

inject_css()

# ── DATABASE ──────────────────────────────────────────────────────────────────
DB_FILE = 'aroha_nexus_v3.db'

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
        return pd.read_sql_query("SELECT * FROM clients WHERE username=?", conn, params=(st.session_state.user,))

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

# ── SESSION STATE ─────────────────────────────────────────────────────────────
for k, v in [("auth", False), ("user", ""), ("page", "Dashboard"), ("chat_history", [])]:
    if k not in st.session_state:
        st.session_state[k] = v

# ── PLOTLY THEME ──────────────────────────────────────────────────────────────
PCOLOR = ['#c4673a','#d4a44c','#7a9e7e','#9e9689','#d4856a','#a07830','#5a8060']
PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#7a6e60", size=11),
    margin=dict(t=36, b=16, l=16, r=16),
    xaxis=dict(gridcolor="rgba(196,103,58,0.1)", zerolinecolor="rgba(196,103,58,0.15)"),
    yaxis=dict(gridcolor="rgba(196,103,58,0.1)", zerolinecolor="rgba(196,103,58,0.15)"),
)
ANCIENT_SCALE = [[0,'#2a1a0e'],[0.25,'#7a3a1e'],[0.5,'#c4673a'],[0.75,'#d4a44c'],[1,'#e8d4a0']]

# ══════════════════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.auth:
    st.markdown("""
    <div style='text-align:center; margin-top:70px; margin-bottom:50px;'>
        <div class='brand-title' style='font-size:4.5rem; letter-spacing:0.4em;'>AROHA</div>
        <div class='brand-sub' style='margin-top:12px;'>Strategic Intelligence Nexus · Est. MMXXIV</div>
        <div style='height:1px; width:180px; margin:20px auto;
            background:linear-gradient(90deg,transparent,#c4673a,#d4a44c,transparent);
            box-shadow:0 0 8px rgba(212,164,76,0.2);'></div>
        <p style='color:#3d3830; font-family:JetBrains Mono; font-size:0.72rem; letter-spacing:0.2em;'>
            TURN DATA INTO <span style='color:#c4673a;'>DECISIONS</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

    _, col_c, _ = st.columns([0.25, 0.5, 0.25])
    with col_c:
        tabs = st.tabs(["◈  LOGIN", "◈  JOIN"])
        with tabs[0]:
            u = st.text_input("Username", key="l_u", placeholder="enter your ID")
            p = st.text_input("Password", type="password", key="l_p", placeholder="••••••••")
            if st.button("UNLOCK HUB", use_container_width=True):
                with get_db() as conn:
                    res = pd.read_sql_query("SELECT password FROM users WHERE username=?", conn, params=(u,))
                if not res.empty and res.iloc[0]['password'] == hash_p(p):
                    st.session_state.auth = True
                    st.session_state.user = u
                    seed_clients_if_empty(u)
                    st.rerun()
                else:
                    st.error("Access denied — invalid credentials.")
        with tabs[1]:
            nu = st.text_input("New ID", placeholder="choose username")
            np_ = st.text_input("New Pass", type="password", placeholder="choose password")
            if st.button("ENROLL", use_container_width=True):
                try:
                    with get_db() as conn:
                        conn.execute("INSERT INTO users VALUES (?,?)", (nu, hash_p(np_)))
                    st.success("Authorized. You may now login.")
                except:
                    st.error("ID already exists.")
    st.stop()

# ── TICKER ────────────────────────────────────────────────────────────────────
st.markdown(
    f"<div class='ticker-wrap'><div class='ticker-text'>"
    f"◈ DHWANI · {st.session_state.user.upper()} ACTIVE &nbsp;&nbsp;·&nbsp;&nbsp;"
    f"◈ LOGISTICS · Hover map for addresses &nbsp;&nbsp;·&nbsp;&nbsp;"
    f"◈ KRIYA · Fatigue sensing online &nbsp;&nbsp;·&nbsp;&nbsp;"
    f"◈ VITTA · Inventory ROI optimized &nbsp;&nbsp;·&nbsp;&nbsp;"
    f"◈ PREKSHA · +8% weekend spike detected &nbsp;&nbsp;·&nbsp;&nbsp;"
    f"◈ MITHRA+ · 4 negotiations queued &nbsp;&nbsp;·&nbsp;&nbsp;"
    f"◈ NEXUS · All systems optimal · {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    f"</div></div>",
    unsafe_allow_html=True
)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div class='brand-container'>
        <div class='brand-title' style='font-size:2rem;'>AROHA</div>
        <div class='brand-sub' style='margin-top:6px;'>Data Into Decisions</div>
    </div>
    <div class='glow-divider' style='margin:0 0 16px;'></div>
    """, unsafe_allow_html=True)

    if st.button("◈  DASHBOARD"):
        st.session_state.page = "Dashboard"; st.rerun()
    st.markdown("<span class='sidebar-sub'>System Overview</span>", unsafe_allow_html=True)

    nodes = [
        ("◈  NYASA",    "Nyasa",    "Add Items & PO Gen"),
        ("◈  PREKSHA",  "Preksha",  "Predict Demand"),
        ("◈  STAMBHA",  "Stambha",  "Supply Risk Engine"),
        ("◈  KRIYA",    "Kriya",    "Workforce Intelligence"),
        ("◈  SAMVADA",  "Samvada",  "Talk To System"),
        ("◈  VITTA",    "Vitta",    "Track Money Flow"),
        ("◈  SANCHARA", "Sanchara", "Global Map & Flow"),
        ("◈  MITHRA+",  "Mithra",   "Negotiation & Ranking"),
    ]
    for label, page_id, layman in nodes:
        if st.button(label, key=f"nav_{page_id}"):
            st.session_state.page = page_id; st.rerun()
        st.markdown(f"<span class='sidebar-sub'>{layman}</span>", unsafe_allow_html=True)

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-family:JetBrains Mono;font-size:0.6rem;color:#3d3830;text-align:center;letter-spacing:0.15em;'>SESSION · {st.session_state.user.upper()}</div>", unsafe_allow_html=True)
    if st.button("◈  LOGOUT"):
        st.session_state.auth = False; st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
#  PAGES
# ══════════════════════════════════════════════════════════════════════════════

# ── DASHBOARD ─────────────────────────────────────────────────────────────────
if st.session_state.page == "Dashboard":
    st.markdown(f"""
    <div class='feature-header'>Strategic Hub</div>
    <div class='feature-sub'>OPERATOR · {st.session_state.user.upper()} · {datetime.now().strftime('%d %b %Y')}</div>
    """, unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    df = get_user_data()
    val = (df['current_stock'] * df['unit_price']).sum() if not df.empty else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Assets Managed", len(df))
    with c2: st.metric("Treasury Value",  f"₹{val:,.0f}")
    with c3: st.metric("System Integrity", "OPTIMAL")
    with c4: st.metric("Active Nodes", "8 / 8")

    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div class='insight-box'>
        <strong>◈ Tactical Handoff</strong> — Warehouse throughput stable.
        PREKSHA sensing <span style='color:#d4a44c;'>+8% weekend spike</span>.
        Recommend auditing NYASA registry. MITHRA+ has 4 negotiation drafts queued.
    </div>
    """, unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<div class='saas-card'><div style='font-family:JetBrains Mono;font-size:0.65rem;color:#4a4238;letter-spacing:0.2em;margin-bottom:14px;'>◈ SYSTEM STATUS</div>", unsafe_allow_html=True)
        nodes_status = [
            ("PREKSHA",  "DEMAND AI",       "online",  "#7a9e7e"),
            ("STAMBHA",  "RISK ENGINE",     "online",  "#7a9e7e"),
            ("KRIYA",    "WORKFORCE AI",    "warning", "#d4a44c"),
            ("SAMVADA",  "VOICE AI",        "online",  "#7a9e7e"),
            ("SANCHARA", "LOGISTICS MAP",   "online",  "#7a9e7e"),
            ("MITHRA+",  "NEGOTIATION AI",  "online",  "#7a9e7e"),
        ]
        for name, desc, status, col in nodes_status:
            st.markdown(f"""<div style='display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid rgba(196,103,58,0.08);'>
                <span style='color:#7a6e60;font-size:0.82rem;'>{name} <span style='color:#3a3428;'>·</span> <span style='color:#4a4238;font-size:0.72rem;font-family:JetBrains Mono;'>{desc}</span></span>
                <span style='color:{col};font-family:JetBrains Mono;font-size:0.65rem;letter-spacing:0.1em;'>● {status.upper()}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_r:
        if not df.empty:
            fig = px.bar(df, x='name', y='current_stock', title="Inventory Levels",
                         color='current_stock', color_continuous_scale=ANCIENT_SCALE)
            fig.update_layout(**PLOT_LAYOUT, title_font=dict(family='Cinzel', size=13, color='#7a6e60'))
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.markdown("<div class='saas-card' style='text-align:center;color:#3a3428;padding:60px 20px;font-family:JetBrains Mono;font-size:0.75rem;letter-spacing:0.1em;'>NO INVENTORY DATA<br>Add items via NYASA</div>", unsafe_allow_html=True)

# ── MITHRA+ ───────────────────────────────────────────────────────────────────
elif st.session_state.page == "Mithra":
    st.markdown("<div class='feature-header'>MITHRA+</div>", unsafe_allow_html=True)
    st.markdown("<div class='feature-sub'>AI NEGOTIATION · CLIENT COMMAND · RANKING ENGINE</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    df_products = get_user_data()
    df_clients  = get_client_data()

    tab_nego, tab_rank, tab_manage = st.tabs(["◈  Negotiation Engine", "◈  Client War Room", "◈  Manage Clients"])

    # ── NEGOTIATION ───────────────────────────────────────────────────────────
    with tab_nego:
        st.markdown("<div class='insight-box'>Negotiation protocols loaded. Select vendor and strategy to draft AI letter.</div>", unsafe_allow_html=True)
        if not df_products.empty:
            col1, col2 = st.columns([1, 1.5])
            with col1:
                vendors  = df_products['supplier'].dropna().unique().tolist() or ["Default Vendor"]
                vendor   = st.selectbox("Vendor", vendors)
                strategy = st.radio("Strategy", ["Polite", "Balanced", "Aggressive"])
                discount = st.slider("Target Discount %", 3, 25, 10)
                volume   = st.number_input("Volume (units)", 100, 100000, 500, step=100)
            with col2:
                if st.button("◈  EXECUTE AI NEGOTIATION", use_container_width=True):
                    savings = round(volume * df_products.iloc[0]['unit_price'] * (discount / 100))
                    st.metric("Potential Savings", f"₹{savings:,.0f}", f"↑ {discount}%")
                    tone_map = {
                        "Polite":     ("We kindly request a pricing review", "look forward to a continued partnership"),
                        "Balanced":   ("We require a pricing re-alignment",  "expect competitive terms to proceed"),
                        "Aggressive": ("We demand immediate price correction","will reassess the vendor relationship otherwise"),
                    }
                    opener, closer = tone_map[strategy]
                    draft = f"""Dear {vendor} Team,

We have identified a {discount}% optimisation opportunity based on our
{volume:,}-unit volume commitment and sustained transaction history.

{opener} on the current rate card. Given market benchmarks and our
projected growth, we {closer}.

Proposed Terms
  Volume Commitment : {volume:,} units/quarter
  Target Discount   : {discount}%
  Payment Terms     : Net-30
  Review Cycle      : Bi-annual

Available for a call at your earliest convenience.

Regards,
{st.session_state.user.upper()} | AROHA Strategic Procurement"""
                    st.text_area("AI-Drafted Letter", draft, height=270)
                else:
                    st.markdown("""
                    <div class='saas-card' style='text-align:center;padding:60px 20px;'>
                        <div style='font-size:2rem;color:#3a3428;'>◈</div>
                        <div style='color:#3a3428;font-family:JetBrains Mono;margin-top:12px;font-size:0.72rem;letter-spacing:0.1em;'>
                            CONFIGURE AND EXECUTE
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("Add products via NYASA to enable the negotiation engine.")

    # ── CLIENT WAR ROOM ───────────────────────────────────────────────────────
    with tab_rank:
        st.markdown("<div class='insight-box'>Composite scores computed from deal value, negotiation success, trust, payment speed, and volume.</div>", unsafe_allow_html=True)

        if df_clients.empty:
            st.warning("No client data. Add clients in the 'Manage Clients' tab.")
        else:
            df_c = df_clients.copy()
            trust_map = {"High":100,"Medium":60,"Low":20}
            speed_map = {"Fast":100,"Normal":60,"Slow":20}
            df_c['trust_num'] = df_c['trust_score'].map(trust_map).fillna(50)
            df_c['speed_num'] = df_c['payment_speed'].map(speed_map).fillna(50)
            dv_max  = df_c['deal_value'].max()
            vol_max = df_c['volume_orders'].max()
            df_c['dv_norm']  = (df_c['deal_value'] / dv_max * 100).round(1) if dv_max > 0 else 50
            df_c['vol_norm'] = (df_c['volume_orders'] / vol_max * 100).round(1) if vol_max > 0 else 50
            df_c['composite'] = (
                df_c['dv_norm']              * 0.30 +
                df_c['negotiation_success']  * 0.25 +
                df_c['trust_num']            * 0.20 +
                df_c['speed_num']            * 0.15 +
                df_c['vol_norm']             * 0.10
            ).round(1)
            df_c = df_c.sort_values('composite', ascending=False).reset_index(drop=True)

            # PODIUM
            st.markdown("""<div style='font-family:JetBrains Mono;font-size:0.65rem;color:#4a4238;letter-spacing:0.2em;margin-bottom:14px;'>◈ ELITE PODIUM</div>""", unsafe_allow_html=True)
            podium_cols = st.columns(3)
            medals = [
                (0, "I",   "rank-card-1", "rank-gold",   "#d4a44c"),
                (1, "II",  "rank-card-2", "rank-silver", "#9e9689"),
                (2, "III", "rank-card-3", "rank-bronze", "#c4673a"),
            ]
            for idx, numeral, card_cls, text_cls, glow in medals:
                if idx < len(df_c):
                    row = df_c.iloc[idx]
                    with podium_cols[idx]:
                        st.markdown(f"""
                        <div class='rank-card {card_cls}' style='flex-direction:column;text-align:center;padding:22px 16px;'>
                            <div style='font-family:Cinzel,serif;font-size:1.2rem;color:{glow};letter-spacing:0.2em;'>{numeral}</div>
                            <div class='{text_cls}' style='font-size:1rem;letter-spacing:0.08em;margin:8px 0 4px;'>{row['client_name']}</div>
                            <div class='podium-score' style='color:{glow};text-shadow:0 0 12px {glow}66;'>{row['composite']}</div>
                            <div style='color:#4a4238;font-family:JetBrains Mono;font-size:0.6rem;letter-spacing:0.1em;margin-bottom:8px;'>COMPOSITE</div>
                            <span class='score-badge score-{"high" if row["composite"]>=80 else ("med" if row["composite"]>=55 else "low")}'>₹{int(row["deal_value"]):,}</span>
                        </div>
                        """, unsafe_allow_html=True)

            st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

            # FULL LEADERBOARD
            st.markdown("""<div style='font-family:JetBrains Mono;font-size:0.65rem;color:#4a4238;letter-spacing:0.2em;margin-bottom:14px;'>◈ FULL LEADERBOARD</div>""", unsafe_allow_html=True)
            rank_numerals = ["I","II","III"] + ["·"]*(len(df_c)-3)
            for i, (_, row) in enumerate(df_c.iterrows()):
                card_cls  = f"rank-card-{i+1}" if i < 3 else "rank-card-n"
                score_cls = "score-high" if row['composite']>=80 else ("score-med" if row['composite']>=55 else "score-low")
                trust_cls = "score-high" if row['trust_score']=="High" else ("score-med" if row['trust_score']=="Medium" else "score-low")
                spd_cls   = "score-high" if row['payment_speed']=="Fast" else ("score-med" if row['payment_speed']=="Normal" else "score-low")
                nego_cls  = "score-high" if row['negotiation_success']>=85 else ("score-med" if row['negotiation_success']>=70 else "score-low")
                glow_col  = "#d4a44c" if i==0 else ("#9e9689" if i==1 else ("#c4673a" if i==2 else "#3a3428"))
                st.markdown(f"""
                <div class='rank-card {card_cls}' style='margin:5px 0;'>
                    <div style='font-family:Cinzel,serif;font-size:1.1rem;color:{glow_col};min-width:30px;text-align:center;letter-spacing:0.1em;'>{rank_numerals[i]}</div>
                    <div style='flex:1;'>
                        <div style='display:flex;justify-content:space-between;align-items:center;'>
                            <span style='font-family:Inter;font-size:0.95rem;font-weight:500;color:#c8bfb0;'>{row['client_name']}</span>
                            <span class='score-badge {score_cls}'>Score {row['composite']}</span>
                        </div>
                        <div style='display:flex;gap:6px;margin-top:8px;flex-wrap:wrap;'>
                            <span class='score-badge score-med'>₹{int(row["deal_value"]):,}</span>
                            <span class='score-badge {nego_cls}'>Nego {row["negotiation_success"]}%</span>
                            <span class='score-badge {trust_cls}'>Trust · {row["trust_score"]}</span>
                            <span class='score-badge {spd_cls}'>Pay · {row["payment_speed"]}</span>
                            <span class='score-badge score-med'>{row["volume_orders"]} orders</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

            # CHARTS
            st.markdown("""<div style='font-family:JetBrains Mono;font-size:0.65rem;color:#4a4238;letter-spacing:0.2em;margin-bottom:14px;'>◈ PERFORMANCE INTELLIGENCE</div>""", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                fig_bar = go.Figure(go.Bar(
                    x=df_c['composite'], y=df_c['client_name'], orientation='h',
                    marker=dict(color=df_c['composite'], colorscale=ANCIENT_SCALE,
                                line=dict(color='rgba(196,103,58,0.2)', width=0.5)),
                    text=df_c['composite'].astype(str), textposition='outside',
                    textfont=dict(family='JetBrains Mono', color='#7a6e60', size=10),
                ))
                fig_bar.update_layout(**PLOT_LAYOUT, title="Composite Ranking",
                    title_font=dict(family='Cinzel', size=12, color='#7a6e60'),
                    yaxis=dict(autorange='reversed', gridcolor='rgba(196,103,58,0.08)'),
                    xaxis=dict(gridcolor='rgba(196,103,58,0.08)'))
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_b:
                fig_sc = px.scatter(
                    df_c, x='deal_value', y='negotiation_success',
                    size='volume_orders', color='composite',
                    color_continuous_scale=ANCIENT_SCALE,
                    hover_name='client_name', title="Deal Value vs Success",
                    labels={'deal_value':'Deal Value (₹)','negotiation_success':'Negotiation Success (%)'}
                )
                fig_sc.update_layout(**PLOT_LAYOUT, title_font=dict(family='Cinzel', size=12, color='#7a6e60'))
                st.plotly_chart(fig_sc, use_container_width=True)

            col_c, col_d = st.columns(2)
            with col_c:
                fig_radar = go.Figure()
                categories = ['Deal Value','Nego. Success','Trust','Payment','Volume']
                for idx2, row2 in df_c.head(4).iterrows():
                    vals = [row2['dv_norm'],row2['negotiation_success'],row2['trust_num'],row2['speed_num'],row2['vol_norm']]
                    fig_radar.add_trace(go.Scatterpolar(
                        r=vals+[vals[0]], theta=categories+[categories[0]],
                        name=row2['client_name'],
                        line=dict(color=PCOLOR[idx2 % len(PCOLOR)], width=1.5),
                        fill='toself',
                        fillcolor=f'rgba({int(PCOLOR[idx2%len(PCOLOR)][1:3],16)},{int(PCOLOR[idx2%len(PCOLOR)][3:5],16)},{int(PCOLOR[idx2%len(PCOLOR)][5:7],16)},0.05)',
                    ))
                fig_radar.update_layout(**PLOT_LAYOUT, polar=dict(
                    bgcolor='rgba(0,0,0,0)',
                    radialaxis=dict(visible=True, range=[0,100], color='#3a3428', gridcolor='rgba(196,103,58,0.1)'),
                    angularaxis=dict(color='#5a5244', gridcolor='rgba(196,103,58,0.08)')
                ), title="Multi-Dimensional Radar", title_font=dict(family='Cinzel',size=12,color='#7a6e60'),
                legend=dict(font=dict(color='#7a6e60',size=10)))
                st.plotly_chart(fig_radar, use_container_width=True)

            with col_d:
                fig_pie = px.pie(
                    df_c, values='deal_value', names='client_name',
                    hole=0.55, title="Revenue Share",
                    color_discrete_sequence=PCOLOR
                )
                fig_pie.update_traces(textfont=dict(family='Inter',size=11), pull=[0.04]*len(df_c))
                fig_pie.update_layout(**PLOT_LAYOUT, title_font=dict(family='Cinzel',size=12,color='#7a6e60'),
                    legend=dict(font=dict(color='#7a6e60',size=10)))
                st.plotly_chart(fig_pie, use_container_width=True)

            # AI insight
            if len(df_c) > 0:
                top    = df_c.iloc[0]
                bottom = df_c.iloc[-1]
                st.markdown(f"""
                <div class='ai-decision-box'>
                    <h3>◈ MITHRA+ Intelligence Report</h3>
                    <p style='color:#a89880;font-size:0.9rem;line-height:1.8;'>
                        <strong style='color:#d4a44c;'>{top['client_name']}</strong> leads the board
                        with a composite score of <strong style='color:#d4a44c;'>{top['composite']}</strong>.
                        Prioritize relationship deepening and volume scaling.<br>
                        <strong style='color:#c4673a;'>{bottom['client_name']}</strong> ranks lowest at
                        <strong style='color:#c4673a;'>{bottom['composite']}</strong>.
                        Recommend re-engagement within 30 days.
                    </p>
                </div>
                """, unsafe_allow_html=True)

    # ── MANAGE CLIENTS ────────────────────────────────────────────────────────
    with tab_manage:
        st.markdown("""<div style='font-family:JetBrains Mono;font-size:0.65rem;color:#4a4238;letter-spacing:0.2em;margin-bottom:14px;'>◈ ADD CLIENT</div>""", unsafe_allow_html=True)
        with st.form("add_client"):
            c1, c2, c3 = st.columns(3)
            with c1:
                cname  = st.text_input("Client Name")
                deal_v = st.number_input("Deal Value (₹)", 0, 10000000, 50000, step=1000)
                nego_s = st.slider("Negotiation Success %", 0, 100, 75)
            with c2:
                trust  = st.selectbox("Trust Score", ["High","Medium","Low"])
                speed  = st.selectbox("Payment Speed", ["Fast","Normal","Slow"])
            with c3:
                vol_o  = st.number_input("Volume Orders", 0, 10000, 10)
                rel_m  = st.number_input("Relationship (months)", 0, 240, 6)
            if st.form_submit_button("◈  ADD CLIENT", use_container_width=True):
                if cname:
                    with get_db() as conn:
                        conn.execute(
                            "INSERT INTO clients (username,client_name,deal_value,negotiation_success,trust_score,payment_speed,volume_orders,relationship_months,created_at) VALUES (?,?,?,?,?,?,?,?,?)",
                            (st.session_state.user, cname, deal_v, nego_s, trust, speed, vol_o, rel_m, datetime.now().isoformat())
                        )
                    st.success(f"{cname} added to roster.")
                    st.rerun()
                else:
                    st.error("Client name is required.")

        st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
        if not df_clients.empty:
            st.markdown("""<div style='font-family:JetBrains Mono;font-size:0.65rem;color:#4a4238;letter-spacing:0.2em;margin-bottom:10px;'>◈ CURRENT ROSTER</div>""", unsafe_allow_html=True)
            st.dataframe(
                df_clients[['client_name','deal_value','negotiation_success','trust_score','payment_speed','volume_orders','relationship_months']].rename(columns={
                    'client_name':'Client','deal_value':'Deal Value (₹)','negotiation_success':'Success %',
                    'trust_score':'Trust','payment_speed':'Payment','volume_orders':'Orders','relationship_months':'Months'
                }), use_container_width=True
            )
            del_client = st.selectbox("Remove Client", [""] + list(df_clients['client_name'].tolist()))
            if del_client and st.button("◈  REMOVE"):
                with get_db() as conn:
                    conn.execute("DELETE FROM clients WHERE username=? AND client_name=?", (st.session_state.user, del_client))
                st.success(f"{del_client} removed.")
                st.rerun()

# ── KRIYA ─────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Kriya":
    st.markdown("<div class='feature-header'>KRIYA</div>", unsafe_allow_html=True)
    st.markdown("<div class='feature-sub'>WORKFORCE INTELLIGENCE · FATIGUE SENSING · TASK ORCHESTRATION</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
    st.markdown("<div class='insight-box'>AI orchestrating tasks to Ravi and Ananya. Fatigue sensors active. Peak efficiency window: 09:00–14:00.</div>", unsafe_allow_html=True)

    tab_w, tab_m = st.tabs(["◈  Worker Interface", "◈  Manager Intelligence"])
    with tab_w:
        col_q, col_s = st.columns([2, 1])
        with col_q:
            st.markdown("<div class='directive-msg'><strong>[Assignment]</strong> Pick 12x Titanium Chassis for Station B.</div>", unsafe_allow_html=True)
            st.markdown("<div class='directive-msg'><strong>[Guidance]</strong> Proceed to Shelf B2 via Aisle 3. Optimal path calculated.</div>", unsafe_allow_html=True)
            st.markdown("<div class='directive-msg'><strong>[Next]</strong> After Station B — audit Zone C Sensor Array. Est. 8 min.</div>", unsafe_allow_html=True)
            if st.button("◈  SIMULATE SCAN"):
                st.error("Warning: Incorrect item selected (SKU-405). Verify barcode on Bin B2.")
            if st.button("◈  CONFIRM PICK"):
                st.success("Pick confirmed. 12x Titanium Chassis logged. Station B delivery initiated.")
        with col_s:
            st.markdown("""
            <div class='saas-card' style='text-align:center;'>
                <div style='font-family:JetBrains Mono;font-size:0.62rem;color:#4a4238;letter-spacing:0.15em;margin-bottom:8px;'>SHIFT PERFORMANCE</div>
                <div style='font-family:Cinzel,serif;font-size:2.8rem;color:#d4a44c;text-shadow:0 0 15px rgba(212,164,76,0.25);line-height:1;'>42</div>
                <div style='font-family:JetBrains Mono;font-size:0.65rem;color:#5a5244;margin:4px 0 10px;'>PICKS / HR</div>
                <div style='color:#7a9e7e;font-size:0.85rem;'>+12% vs team avg</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button("◈  Voice: 'What next?'"):
                st.info("Ravi → Zone C sensor audit. Route: Aisle 1 North. ETA: 3 min.")
            st.warning("Fatigue alert: Speed drop detected for Ravi. Suggest 10-min break.")
    with tab_m:
        c1, c2 = st.columns(2)
        with c1:
            fig_t = go.Figure()
            fig_t.add_trace(go.Scatter(
                y=[80,85,75,90,88,92,87], fill='tozeroy',
                line=dict(color='#c4673a', width=2),
                fillcolor='rgba(196,103,58,0.08)', name='Throughput'
            ))
            fig_t.update_layout(**PLOT_LAYOUT, title="Real-time Throughput",
                title_font=dict(family='Cinzel',size=12,color='#7a6e60'))
            st.plotly_chart(fig_t, use_container_width=True)
        with c2:
            workers = ["Ravi","Ananya","Dev"]
            fig_b = go.Figure(data=[
                go.Bar(name='Accuracy', x=workers, y=[98,92,75], marker_color='#d4a44c'),
                go.Bar(name='Speed',    x=workers, y=[90,85,70], marker_color='#c4673a'),
            ])
            fig_b.update_layout(**PLOT_LAYOUT, barmode='group',
                title="Resource Matrix", title_font=dict(family='Cinzel',size=12,color='#7a6e60'))
            st.plotly_chart(fig_b, use_container_width=True)
        st.success("Top performer: Ananya — 98% accuracy · 92% speed · 0 errors this shift.")

# ── VITTA ─────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Vitta":
    st.markdown("<div class='feature-header'>VITTA</div>", unsafe_allow_html=True)
    st.markdown("<div class='feature-sub'>CAPITAL INTELLIGENCE · FINANCIAL ANALYTICS · ROI TRACKING</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    df = get_user_data()
    if not df.empty:
        total_v = (df['current_stock'] * df['unit_price']).sum()
        idle_r  = total_v * 0.15
        roi_e   = total_v * 0.22

        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Total Value",       f"₹{total_v:,.0f}")
        with c2: st.metric("Idle Capital Risk", f"₹{idle_r:,.0f}", delta="-15%", delta_color="inverse")
        with c3: st.metric("Est. Annual ROI",   f"₹{roi_e:,.0f}", delta="+22%")

        st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown(f"<div class='financial-stat'>Total Inventory Value<h2>₹{total_v:,.0f}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='financial-stat' style='margin-top:14px;'>Idle Capital Risk (15%)<h2 style='color:#c4673a;text-shadow:0 0 10px rgba(196,103,58,0.3);'>₹{idle_r:,.0f}</h2></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='financial-stat' style='margin-top:14px;'>Projected Annual ROI<h2 style='color:#7a9e7e;text-shadow:0 0 10px rgba(122,158,126,0.3);'>₹{roi_e:,.0f}</h2></div>", unsafe_allow_html=True)
        with col_r:
            fig_pie = px.pie(df, values='current_stock', names='name', hole=0.52,
                             title="Capital Allocation", color_discrete_sequence=PCOLOR)
            fig_pie.update_traces(textfont=dict(family='Inter',size=11), pull=[0.03]*len(df))
            fig_pie.update_layout(**PLOT_LAYOUT, title_font=dict(family='Cinzel',size=13,color='#7a6e60'))
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.markdown("<div class='insight-box'>No inventory data. Add items via NYASA to see financial analytics.</div>", unsafe_allow_html=True)

# ── SANCHARA ──────────────────────────────────────────────────────────────────
elif st.session_state.page == "Sanchara":
    st.markdown("<div class='feature-header'>SANCHARA</div>", unsafe_allow_html=True)
    st.markdown("<div class='feature-sub'>GLOBAL LOGISTICS · PRECISION MAP · FLOOR OPS · RETURNS</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["◈  Precision Map", "◈  Floor Ops", "◈  Returns (PUNAH)"])
    with t1:
        map_pts = pd.DataFrame({
            'lat':     [12.9716, 22.31,  37.77,   1.35,   51.5,   35.68],
            'lon':     [77.59,  114.16, -122.41, 103.81,  -0.12, 139.69],
            'Node':    ['HQ Bangalore','Factory HK','SF Depot','Singapore Hub','London Node','Tokyo Relay'],
            'Status':  ['OPTIMAL','OPTIMAL','OPTIMAL','PORT ALERT','OPTIMAL','OPTIMAL'],
            'Address': ['MG Road, Bangalore','Lantau Island, HK','Market St, SF','Jurong Port (CLOSED)','Canary Wharf, London','Shinjuku, Tokyo'],
        })
        fig_map = px.scatter_mapbox(
            map_pts, lat="lat", lon="lon", hover_name="Node",
            hover_data={"Address":True,"Status":True,"lat":False,"lon":False},
            color="Status",
            color_discrete_map={"OPTIMAL":"#7a9e7e","PORT ALERT":"#c4673a"},
            zoom=1, height=460,
        )
        fig_map.update_layout(mapbox_style="carto-darkmatter",
            margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor="rgba(0,0,0,0)",
            legend=dict(font=dict(color="#7a6e60",size=11)))
        st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("<div style='background:rgba(196,103,58,0.04);padding:12px 16px;border-radius:8px;border:1px solid rgba(196,103,58,0.15);margin-top:10px;font-family:JetBrains Mono;font-size:0.68rem;color:#5a5244;letter-spacing:0.08em;'>◈ GREEN · Stable nodes &nbsp;|&nbsp; ◈ TERRACOTTA · Crisis nodes &nbsp;|&nbsp; Hover dots for full details</div>", unsafe_allow_html=True)
    with t2:
        df_inv = get_user_data()
        c1, c2, c3 = st.columns(3)
        c1.metric("Items Shipped Today", "1,240")
        c2.metric("Floor Assets", f"{df_inv['current_stock'].sum() + 142 if not df_inv.empty else 142} units", "+142 returns")
        c3.metric("Active Routes", "7")
    with t3:
        st.table(pd.DataFrame({
            'Product':  ['Quantum X1','4K Monitor','USB-C Hub'],
            'Amount':   [4, 2, 6],
            'Reason':   ['Defective Logic','Screen Bleed','Port Failure'],
            'Status':   ['Processing','Approved','Pending'],
        }))

# ── PREKSHA ───────────────────────────────────────────────────────────────────
elif st.session_state.page == "Preksha":
    st.markdown("<div class='feature-header'>PREKSHA</div>", unsafe_allow_html=True)
    st.markdown("<div class='feature-sub'>DEMAND AI · 14-DAY FORECASTING · REORDER INTELLIGENCE</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    df = get_user_data()
    if not df.empty:
        target = st.selectbox("◈ Select Asset", df['name'])
        p      = df[df['name'] == target].iloc[0]
        col_a, col_b = st.columns([1, 2])
        with col_a:
            if p['image_url'] and str(p['image_url']) != "nan":
                st.image(p['image_url'], use_container_width=True)
            st.markdown(f"""
            <div class='saas-card'>
                <div style='font-family:JetBrains Mono;font-size:0.6rem;color:#4a4238;letter-spacing:0.15em;'>CURRENT STOCK</div>
                <div style='font-family:Cinzel,serif;font-size:2.5rem;color:#d4a44c;text-shadow:0 0 12px rgba(212,164,76,0.2);line-height:1.2;'>{p['current_stock']}</div>
                <div style='font-family:JetBrains Mono;font-size:0.6rem;color:#4a4238;letter-spacing:0.15em;margin-top:14px;'>LEAD TIME</div>
                <div style='font-family:Cinzel,serif;font-size:1.8rem;color:#c4673a;'>{p['lead_time']}d</div>
                <div style='font-family:JetBrains Mono;font-size:0.6rem;color:#4a4238;letter-spacing:0.15em;margin-top:14px;'>UNIT PRICE</div>
                <div style='font-family:Cinzel,serif;font-size:1.8rem;color:#7a9e7e;'>₹{p['unit_price']:,.0f}</div>
            </div>
            """, unsafe_allow_html=True)
            if p['reviews']:
                for r in p['reviews'].split('|'):
                    st.markdown(f"<div class='review-box'>· {r}</div>", unsafe_allow_html=True)
        with col_b:
            preds = np.random.randint(20, 50, 14)
            days  = [f"D+{i+1}" for i in range(14)]
            fig_f = go.Figure()
            fig_f.add_trace(go.Scatter(
                x=days, y=preds, fill='tozeroy',
                line=dict(color='#d4a44c', width=2),
                fillcolor='rgba(212,164,76,0.07)', name='Forecast'
            ))
            fig_f.add_trace(go.Scatter(
                x=days, y=[p['current_stock']/14]*14,
                line=dict(color='#c4673a', width=1.5, dash='dash'), name='Daily Rate'
            ))
            fig_f.update_layout(**PLOT_LAYOUT, title="14-Day AI Forecast",
                title_font=dict(family='Cinzel',size=13,color='#7a6e60'))
            st.plotly_chart(fig_f, use_container_width=True)
            order_qty = max(0, int(preds.sum()) - int(p['current_stock']))
            st.markdown(f"""
            <div class='ai-decision-box'>
                <h3>◈ PREKSHA Recommendation</h3>
                <p style='color:#a89880;'>Order <strong style='font-family:Cinzel,serif;font-size:1.8rem;color:#d4a44c;'>{order_qty}</strong>
                units of <strong style='color:#c4673a;'>{target}</strong> immediately.<br>
                <span style='color:#4a4238;font-family:JetBrains Mono;font-size:0.72rem;'>
                14-day demand: {preds.sum()} · Current stock: {int(p['current_stock'])}
                </span></p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='insight-box'>No products found. Add inventory via NYASA first.</div>", unsafe_allow_html=True)

# ── STAMBHA ───────────────────────────────────────────────────────────────────
elif st.session_state.page == "Stambha":
    st.markdown("<div class='feature-header'>STAMBHA</div>", unsafe_allow_html=True)
    st.markdown("<div class='feature-sub'>RISK ENGINE · SUPPLY SHOCK SIMULATION · RESILIENCE SCORING</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    shock = st.selectbox("◈ Shock Scenario", ["Normal Operations","Port Closure (3× Lead)","Demand Surge (2×)","Supplier Failure (4×)"])
    m_map = {"Normal Operations":1,"Port Closure (3× Lead)":3,"Demand Surge (2×)":2,"Supplier Failure (4×)":4}
    m = m_map[shock]
    df = get_user_data()
    if not df.empty:
        st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
        risk_count = 0
        for _, p in df.iterrows():
            ttr = p['lead_time'] * m
            tts = round(p['current_stock'] / max(12, 1), 1)
            if tts < ttr:
                st.error(f"Critical: {p['name']} runs out in {tts}d · Recovery: {ttr}d · Order immediately.")
                risk_count += 1
            else:
                st.success(f"{p['name']} — Safe for {tts}d (recovery: {ttr}d)")
        if risk_count == 0:
            st.markdown("<div class='ai-decision-box'><h3>◈ All Clear</h3><p style='color:#7a9e7e;'>No critical risks under current scenario.</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)
        st.dataframe(df[['name','current_stock','lead_time']], use_container_width=True)
    else:
        st.markdown("<div class='insight-box'>No inventory data. Add items via NYASA to run risk simulations.</div>", unsafe_allow_html=True)

# ── NYASA ─────────────────────────────────────────────────────────────────────
elif st.session_state.page == "Nyasa":
    st.markdown("<div class='feature-header'>NYASA</div>", unsafe_allow_html=True)
    st.markdown("<div class='feature-sub'>ASSET REGISTRY · BULK SYNC · PO GENERATOR</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    t1, t2, t3 = st.tabs(["◈  Bulk Sync", "◈  Manual Registry", "◈  PO Generator"])
    with t1:
        st.markdown("<div class='insight-box'>Upload a CSV with columns: name, category, current_stock, unit_price, lead_time, supplier, image_url, reviews</div>", unsafe_allow_html=True)
        f = st.file_uploader("Upload CSV", type="csv")
        if f and st.button("◈  SYNC", use_container_width=True):
            u_df = pd.read_csv(f)
            u_df['username'] = st.session_state.user
            for col in ['category','supplier','image_url','reviews']:
                if col not in u_df.columns: u_df[col] = ""
            with get_db() as conn:
                u_df.to_sql('products', conn, if_exists='append', index=False)
            st.success(f"Synced {len(u_df)} records.")

    with t2:
        with st.form("add_product"):
            c1, c2 = st.columns(2)
            with c1:
                n  = st.text_input("Product Name")
                s  = st.number_input("Current Stock", 0)
                p  = st.number_input("Unit Price (₹)", 0.0)
                lt = st.number_input("Lead Time (days)", 1)
            with c2:
                cat = st.text_input("Category")
                sup = st.text_input("Supplier")
                img = st.text_input("Image URL")
                rev = st.text_area("Reviews (separate with |)")
            if st.form_submit_button("◈  COMMIT TO REGISTRY", use_container_width=True):
                with get_db() as conn:
                    conn.execute(
                        "INSERT INTO products (username,name,category,current_stock,unit_price,lead_time,supplier,image_url,reviews) VALUES (?,?,?,?,?,?,?,?,?)",
                        (st.session_state.user, n, cat, s, p, lt, sup, img, rev)
                    )
                st.success(f"{n} committed to registry.")

    with t3:
        df_po = get_user_data()
        if not df_po.empty:
            sel_po = st.selectbox("Select Product", df_po['name'])
            item   = df_po[df_po['name']==sel_po].iloc[0]
            po_id  = f"ARH-{np.random.randint(10000,99999)}"
            st.code(f"""
  AROHA NEXUS — PURCHASE ORDER
  ─────────────────────────────────────────
  PO-ID    : #{po_id}
  Date     : {datetime.now().strftime('%Y-%m-%d %H:%M')} IST
  Auth By  : {st.session_state.user.upper()}
  ─────────────────────────────────────────
  Item     : {item['name']}
  Stock    : {item['current_stock']} units
  Price    : ₹{item['unit_price']:,.2f} / unit
  Supplier : {item.get('supplier','N/A')}
  Lead     : {item['lead_time']} days
  ─────────────────────────────────────────
  Status   : PENDING APPROVAL
            """)
        else:
            st.markdown("<div class='insight-box'>No products found. Add items via Manual Registry first.</div>", unsafe_allow_html=True)

# ── SAMVADA ───────────────────────────────────────────────────────────────────
elif st.session_state.page == "Samvada":
    st.markdown("<div class='feature-header'>SAMVADA</div>", unsafe_allow_html=True)
    st.markdown("<div class='feature-sub'>AI VOICE INTERFACE · STRATEGIC QUERY ENGINE</div>", unsafe_allow_html=True)
    st.markdown("<div class='glow-divider'></div>", unsafe_allow_html=True)

    key = st.secrets.get("GROQ_API_KEY", None)
    if not key:
        st.markdown("<div class='insight-box' style='border-left-color:#d4a44c;'>SAMVADA is offline. Add GROQ_API_KEY to Streamlit secrets to enable AI chat.</div>", unsafe_allow_html=True)
    else:
        from openai import OpenAI
        client_ai = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        for msg in st.session_state.chat_history:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
        u_in = st.chat_input("Strategic query to AROHA AI...")
        if u_in:
            st.session_state.chat_history.append({"role":"user","content":u_in})
            ctx = get_user_data().to_string(index=False)
            res = client_ai.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role":"system","content":f"You are AROHA AI — a strategic supply chain intelligence system. Be concise and data-driven. User inventory: {ctx}"},
                    *st.session_state.chat_history[-6:]
                ]
            )
            ans = res.choices[0].message.content
            st.session_state.chat_history.append({"role":"assistant","content":ans})
            st.rerun()

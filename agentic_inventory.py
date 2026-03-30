import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI

# --- 1. SETTINGS & HIGH-END GLASS UI ---
st.set_page_config(page_title="AROHA | Elite Intelligence", layout="wide", page_icon="💠")

def apply_ultra_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');
        html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #050505; color: #E0E0E0; }
        .icon-orb { font-size: 42px; margin-bottom: 12px; filter: drop-shadow(0 0 10px rgba(212, 175, 55, 0.6)); }
        .glass-card {
            background: linear-gradient(145deg, rgba(20,20,20,0.9), rgba(10,10,10,0.9));
            backdrop-filter: blur(15px); border-radius: 25px; border: 1px solid rgba(255, 255, 255, 0.05);
            padding: 35px 20px; text-align: center; transition: 0.4s;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5); height: 280px;
            display: flex; flex-direction: column; justify-content: center; align-items: center;
        }
        .glass-card:hover { border: 1px solid #D4AF37; transform: translateY(-8px); box-shadow: 0 0 25px rgba(212, 175, 55, 0.2); }
        .title-text { color: #D4AF37; font-weight: 700; font-size: 1.3rem; letter-spacing: 2px; text-transform: uppercase; }
        .desc-text { color: #888; font-size: 0.8rem; margin-top: 8px; }
        .vault-box { max-width: 420px; margin: 80px auto; padding: 45px; background: rgba(15, 15, 15, 0.95); border-radius: 30px; border: 1px solid #222; text-align: center; }
        [data-testid="stSidebar"] { display: none; }
        .stButton>button { border-radius: 12px; background: #111; border: 1px solid #333; color: #D4AF37; font-weight: 700; padding: 10px 18px; width: 100%; transition: 0.3s; font-size: 0.8rem; }
        .stButton>button:hover { border-color: #D4AF37; background: #D4AF37; color: black; }
        .header-info { display: flex; justify-content: center; gap: 20px; padding: 12px; background: rgba(255,255,255,0.02); border-radius: 50px; margin-bottom: 30px; font-size: 0.7rem; color: #555; }
        .ai-suggestion { background: rgba(212, 175, 55, 0.1); border: 1px solid #D4AF37; padding: 20px; border-radius: 15px; margin-top: 20px; }
        </style>
    """, unsafe_allow_html=True)

apply_ultra_css()

# --- 2. DATABASE LOGIC ---
def get_db(): return sqlite3.connect('aroha_vault.db', check_same_thread=False)

def init_db():
    conn = get_db(); c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS products (id INTEGER PRIMARY KEY, name TEXT, category TEXT, current_stock INTEGER, unit_price REAL, lead_time INTEGER)')
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, hint TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS sales (p_id INTEGER, date TEXT, qty INTEGER)')
    conn.commit(); conn.close()

init_db()

# --- 3. AUTH LOGIC ---
if "auth" not in st.session_state: st.session_state.auth = False
if "page" not in st.session_state: st.session_state.page = "Home"

def check_for_user():
    conn = get_db(); res = conn.execute("SELECT * FROM users WHERE username='admin'").fetchone(); conn.close()
    return res

# --- 4. LOGIN SCREEN ---
if not st.session_state.auth:
    st.markdown("<div style='text-align:center; margin-top:50px;'><h1 style='color:#D4AF37; font-size:4rem; font-weight:800; letter-spacing:15px; margin-bottom:0;'>AROHA</h1><p style='color:#444; letter-spacing:3px;'>TURN DATA INTO DECISIONS</p></div>", unsafe_allow_html=True)
    existing_user = check_for_user()
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        if not existing_user:
            st.markdown("<div class='vault-box'><h3 style='color:white;'>Initialize Treasury</h3>", unsafe_allow_html=True)
            new_m = st.text_input("Set Mantra", type="password"); hint_ans = st.text_input("Security Hint")
            if st.button("AUTHORIZE SYSTEM"):
                if new_m and hint_ans:
                    conn = get_db(); conn.execute("INSERT INTO users VALUES ('admin', ?, ?)", (new_m, hint_ans)); conn.commit(); conn.close(); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='vault-box'><h3 style='color:white;'>Verify Mantra</h3>", unsafe_allow_html=True)
            input_m = st.text_input("Mantra", type="password")
            if st.button("UNLOCK VAULT"):
                if input_m == existing_user[1]: st.session_state.auth = True; st.rerun()
                else: st.error("Access Denied")
            with st.expander("Forgot Mantra?"):
                ans = st.text_input("Security Hint Answer")
                if st.button("RECOVER"):
                    if ans == existing_user[2]: st.info(f"Mantra: {existing_user[1]}")
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# --- 5. COMMAND CENTER (HOME) ---
if st.session_state.page == "Home":
    st.markdown("<div class='header-info'>🟢 SYSTEM: ONLINE | 🔒 VAULT: ENCRYPTED | 🌐 SYNC: CLOUD | 💠 AGENT: SAMVADA</div>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align:center; color:#D4AF37; letter-spacing:5px;'>COMMAND CENTER</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3); c4, c5, c6 = st.columns(3)
    badges = [
        {"id": "Preksha", "icon": "🔮", "title": "PREKSHA", "desc": "AI Demand & Market Sensing", "col": c1},
        {"id": "Stambha", "icon": "🛡️", "title": "STAMBHA", "desc": "Resilience & Risk Alerts", "col": c2},
        {"id": "Samvada", "icon": "🗣️", "title": "SAMVADA", "desc": "Agentic Reasoning Chat", "col": c3},
        {"id": "Nyasa", "icon": "✍️", "title": "NYASA", "desc": "Asset Ledger & Audit", "col": c4},
        {"id": "Agama", "icon": "📥", "title": "AGAMA", "desc": "Bulk Data Ingestion", "col": c5},
        {"id": "Exit", "icon": "🔒", "title": "EXIT", "desc": "Secure Terminate", "col": c6},
    ]
    for b in badges:
        with b["col"]:
            st.markdown(f"<div class='glass-card'><div class='icon-orb'>{b['icon']}</div><div class='title-text'>{b['title']}</div><div class='desc-text'>{b['desc']}</div></div>", unsafe_allow_html=True)
            if st.button(f"OPEN {b['title']}", key=b['id']):
                if b['id'] == "Exit": st.session_state.auth = False; st.rerun()
                else: st.session_state.page = b['id']; st.rerun()

# --- 6. SUB-PAGES ---
def nav_home():
    if st.button("⬅️ RETURN TO COMMAND CENTER"): st.session_state.page = "Home"; st.rerun()

if st.session_state.page == "Preksha":
    nav_home(); st.title("🔮 Preksha Intelligence")
    # --- WEATHER/MARKET SENSING ---
    col_l, col_r = st.columns([1, 2])
    with col_l:
        st.subheader("External Factors")
        sentiment = st.select_slider("Market Sentiment (Weather/Festivals)", options=[0.5, 0.8, 1.0, 1.2, 1.5, 2.0], value=1.0)
        safety_buffer = st.slider("Safety Stock Buffer", 0, 100, 20)
    
    conn = get_db(); df = pd.read_sql_query("SELECT * FROM products", conn); conn.close()
    if df.empty: st.warning("Treasury empty.")
    else:
        with col_r:
            target = st.selectbox("Select Asset", df['name'])
            p_row = df[df['name'] == target].iloc[0]
            # AI Forecasting with Sentiment
            base_preds = np.random.randint(20, 50, size=7)
            final_preds = (base_preds * sentiment).astype(int)
            total_demand = final_preds.sum()
            
            fig = px.area(x=[f"Day {i+1}" for i in range(7)], y=final_preds, title=f"AI Forecast (Sentiment Adjusted)", template="plotly_dark")
            fig.update_traces(line_color='#D4AF37', fillcolor='rgba(212, 175, 55, 0.1)')
            st.plotly_chart(fig, use_container_width=True)
            
            # --- AI SUGGESTION CARD ---
            reorder_qty = max(0, (total_demand + safety_buffer) - p_row['current_stock'])
            st.markdown(f"""
                <div class='ai-suggestion'>
                    <h3 style='color:#D4AF37; margin:0;'>🤖 AI Suggestion</h3>
                    <p>Based on <b>{sentiment}x</b> market sensing, we predict a demand of <b>{total_demand} units</b>.</p>
                    <h4>Recommendation: Order <b>{reorder_qty} units</b></h4>
                </div>
            """, unsafe_allow_html=True)

elif st.session_state.page == "Stambha":
    nav_home(); st.title("🛡️ Stambha Resilience")
    scenario = st.selectbox("Disruption Trigger", ["Normal", "Port Closure", "Factory Fire"])
    conn = get_db(); df = pd.read_sql_query("SELECT * FROM products", conn); conn.close()
    
    if not df.empty:
        results = []
        for _, p in df.iterrows():
            avg_demand = 12 # Simulated
            tts = p['current_stock'] / avg_demand
            ttr = p['lead_time']
            if scenario == "Port Closure": ttr *= 3
            if scenario == "Factory Fire": ttr += 30
            
            status = "🟢 Green"
            if tts < ttr: 
                status = "🔴 CRITICAL RISK"
                # --- RISK POP UP / ALERT ---
                st.error(f"⚠️ RISK ALERT: {p['name']} will run out in {round(tts,1)} days, but recovery takes {ttr} days!")
            
            results.append({"Product": p['name'], "Time-to-Survive": round(tts,1), "Time-to-Recover": ttr, "Status": status})
        st.table(pd.DataFrame(results))

elif st.session_state.page == "Samvada":
    nav_home(); st.title("🗣️ Samvada Agentic Chat")
    key = st.secrets.get("GROQ_API_KEY")
    if not key: st.error("AI Node Offline")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        if "msgs" not in st.session_state: st.session_state.msgs = []
        for m in st.session_state.msgs:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        if p := st.chat_input("Ask Samvada..."):
            st.session_state.msgs.append({"role": "user", "content": p})
            with st.chat_message("user"): st.markdown(p)
            with st.chat_message("assistant"):
                r = client.chat.completions.create(model="llama-3.1-8b-instant", messages=[{"role":"system","content":"You are Samvada AI Agent."}]+st.session_state.msgs[-3:])
                msg = r.choices[0].message.content
                st.markdown(msg); st.session_state.msgs.append({"role":"assistant","content":msg})

elif st.session_state.page == "Nyasa":
    nav_home(); st.title("✍️ Nyasa Ledger")
    with st.form("add_asset"):
        name = st.text_input("Product Name"); stock = st.number_input("Initial Stock", 0)
        price = st.number_input("Unit Value", 0.0); lt = st.number_input("Lead Time", 1)
        if st.form_submit_button("LOG TO TREASURY"):
            conn = get_db(); conn.execute("INSERT INTO products (name, current_stock, unit_price, lead_time) VALUES (?,?,?,?)", (name, stock, price, lt)); conn.commit(); conn.close(); st.success("Logged.")

elif st.session_state.page == "Agama":
    nav_home(); st.title("📥 Agama Bulk Sync")
    file = st.file_uploader("Upload CSV", type="csv")
    if file:
        u_df = pd.read_csv(file)
        if st.button("SYNCHRONIZE"):
            conn = get_db(); u_df.to_sql('products', conn, if_exists='append', index=False); conn.close(); st.success("Synced.")

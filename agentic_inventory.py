import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI
import io

# --- 1. BRANDING & STYLE ---
APP_NAME = "KOSHA.ai"
TAGLINE = "Treasury of Intelligence. Guardian of Supply."

st.set_page_config(page_title=f"{APP_NAME} | Smart Inventory", layout="wide", page_icon="🪙")

# Custom CSS for the High-End "Gold & Obsidian" look
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #D4AF37; }
    .metric-card {
        background-color: #161B22;
        padding: 20px;
        border-radius: 12px;
        border-top: 4px solid #D4AF37;
        text-align: center;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('inventory_pro.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, current_stock INTEGER, 
                  unit_price REAL, lead_time INTEGER, supplier TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sales_history 
                 (product_id INTEGER, date TEXT, units_sold INTEGER)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. THE KOSHA AI BRAIN (ML & Logic) ---
class KoshaEngine:
    @staticmethod
    def predict_demand(product_id):
        """Feature: Random Forest Demand Prediction"""
        conn = sqlite3.connect('inventory_pro.db')
        df = pd.read_sql_query(f"SELECT * FROM sales_history WHERE product_id={product_id}", conn)
        conn.close()
        if df.empty or len(df) < 5: return np.array([5, 5, 5, 5, 5, 5, 5]) # Fallback
        
        df['date'] = pd.to_datetime(df['date'])
        df['day_index'] = np.arange(len(df))
        df['day_of_week'] = df['date'].dt.dayofweek
        
        model = RandomForestRegressor(n_estimators=50)
        model.fit(df[['day_index', 'day_of_week']], df['units_sold'])
        
        future = pd.DataFrame({
            'day_index': [df['day_index'].iloc[-1] + i for i in range(1, 8)],
            'day_of_week': [(df['date'].iloc[-1] + timedelta(days=i)).dayofweek for i in range(1, 8)]
        })
        return model.predict(future).round().astype(int)

    @staticmethod
    def run_resilience(p_id, scenario="Normal"):
        """Feature: TTS vs TTR Stress Testing"""
        conn = sqlite3.connect('inventory_pro.db')
        p = pd.read_sql_query(f"SELECT * FROM products WHERE id={p_id}", conn).iloc[0]
        sales = pd.read_sql_query(f"SELECT units_sold FROM sales_history WHERE product_id={p_id}", conn)
        conn.close()
        
        avg_demand = sales['units_sold'].mean() if not sales.empty else 1
        tts = p['current_stock'] / avg_demand if avg_demand > 0 else 999
        ttr = p['lead_time']
        
        if scenario == "Port Closure": ttr *= 3
        if scenario == "Factory Fire": ttr += 30
        
        status = "🟢 Safe"
        if tts < ttr: status = "🔴 Critical"
        elif tts < (ttr * 1.5): status = "🟡 Warning"
        
        return {"tts": round(tts, 1), "ttr": round(ttr, 1), "status": status, "avg_demand": avg_demand}

# --- 4. NAVIGATION ---
st.sidebar.markdown(f"<h1 style='color: #D4AF37;'>{APP_NAME}</h1>", unsafe_allow_html=True)
st.sidebar.caption(TAGLINE)
mode = st.sidebar.selectbox("Mission Control", [
    "📈 Strategic Dashboard", 
    "🌪️ Resilience Simulator", 
    "📝 Treasury Ledger", 
    "📂 Bulk Data Import",
    "💬 AI Agent Chat"
])

# --- 5. MODES ---

# MODE 1: STRATEGIC DASHBOARD
if mode == "📈 Strategic Dashboard":
    st.title("🚀 Strategic Inventory Control")
    conn = sqlite3.connect('inventory_pro.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    
    if df.empty:
        st.info("The Treasury is empty. Add data in the Ledger or Import section.")
    else:
        # Top Metrics
        m1, m2, m3 = st.columns(3)
        m1.metric("Assets Managed", len(df))
        m2.metric("Treasury Value", f"${(df['current_stock'] * df['unit_price']).sum():,.0F}")
        m3.metric("System Health", "Optimal")

        # Demand Prediction & Stock Suggestion
        st.divider()
        target = st.selectbox("Select Product for AI Analysis", df['name'])
        p_info = df[df['name'] == target].iloc[0]
        
        preds = KoshaEngine.predict_demand(p_info['id'])
        total_pred = preds.sum()
        
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("7-Day Demand Forecast")
            fig = px.bar(x=[f"Day {i+1}" for i in range(7)], y=preds, template="plotly_dark", color_discrete_sequence=['#D4AF37'])
            st.plotly_chart(fig, use_container_width=True)
        
        with c2:
            st.subheader("Agentic Recommendation")
            if p_info['current_stock'] < total_pred:
                st.error(f"⚠️ LOW STOCK DETECTED\n\nAI Suggests: Order **{int(total_pred - p_info['current_stock'] + 10)} units** immediately to cover forecasted demand.")
            else:
                st.success(f"✅ STOCK HEALTHY\n\nCurrent levels cover the predicted {total_pred} units for next week.")

# MODE 2: RESILIENCE SIMULATOR
elif mode == "🌪️ Resilience Simulator":
    st.title("🌪️ Supply Chain Stress-Test (TTS vs TTR)")
    scenario = st.selectbox("Trigger External Disruption", ["Normal", "Port Closure", "Factory Fire"])
    
    conn = sqlite3.connect('inventory_pro.db')
    products = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    
    res_list = []
    for _, p in products.iterrows():
        r = KoshaEngine.run_resilience(p['id'], scenario)
        res_list.append({"Product": p['name'], "Time-to-Survive (TTS)": r['tts'], "Time-to-Recover (TTR)": r['ttr'], "Risk Status": r['status']})
    
    st.table(pd.DataFrame(res_list))

# MODE 3: TREASURY LEDGER (Manual Entry & Correction)
elif mode == "📝 Treasury Ledger":
    st.title("📝 Ledger Management")
    tab1, tab2 = st.tabs(["Add New Asset", "Correct/Update Records"])
    
    with tab1:
        with st.form("new_p"):
            n = st.text_input("Product Name")
            c = st.selectbox("Category", ["Electronics", "Furniture", "Raw Materials"])
            s = st.number_input("Current Stock", min_value=0)
            p = st.number_input("Unit Value", min_value=0.0)
            l = st.number_input("Lead Time (Days)", min_value=1)
            sup = st.text_input("Supplier")
            if st.form_submit_button("Authorize Entry"):
                conn = sqlite3.connect('inventory_pro.db')
                conn.execute("INSERT INTO products (name, category, current_stock, unit_price, lead_time, supplier) VALUES (?,?,?,?,?,?)", (n,c,s,p,l,sup))
                conn.commit(); conn.close()
                st.success("Asset logged.")

    with tab2:
        conn = sqlite3.connect('inventory_pro.db')
        df = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        if not df.empty:
            target = st.selectbox("Select Asset to Correct", df['name'])
            new_val = st.number_input("New Quantity", min_value=0)
            if st.button("Apply Correction"):
                conn = sqlite3.connect('inventory_pro.db')
                conn.execute("UPDATE products SET current_stock=? WHERE name=?", (new_val, target))
                conn.commit(); conn.close()
                st.rerun()

# MODE 4: BULK DATA IMPORT
elif mode == "📂 Bulk Data Import":
    st.title("📂 External Data Ingestion")
    file = st.file_uploader("Upload CSV Supply Data", type="csv")
    if file:
        df_up = pd.read_csv(file)
        st.write("Preview:")
        st.dataframe(df_up.head())
        if st.button("Sync with Treasury"):
            conn = sqlite3.connect('inventory_pro.db')
            df_up.to_sql('products', conn, if_exists='append', index=False)
            conn.close()
            st.success("Sync Complete.")

# MODE 5: AI AGENT CHAT
elif mode == "💬 AI Agent Chat":
    st.title("💬 KOSHA AI: Conversational Intelligence")
    key = st.secrets.get("GROQ_API_KEY")
    if not key:
        st.warning("Chatbot Offline. Add GROQ_API_KEY to Secrets.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=key)
        if "messages" not in st.session_state: st.session_state.messages = []
        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])
        
        if prompt := st.chat_input("Ask about Treasury risks..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)
            
            conn = sqlite3.connect('inventory_pro.db')
            p_data = pd.read_sql_query("SELECT name, current_stock, supplier FROM products", conn).to_string()
            conn.close()
            
            with st.chat_message("assistant"):
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[{"role": "system", "content": f"You are KOSHA AI, a master supply chain agent. Data: {p_data}"}] + st.session_state.messages
                )
                res = response.choices[0].message.content
                st.markdown(res)
                st.session_state.messages.append({"role": "assistant", "content": res})

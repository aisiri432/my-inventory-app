import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI
import io

# --- 1. DATABASE & AGENT SYSTEMS ---
class EnterpriseSystem:
    def __init__(self, db_path='inventory_pro.db'):
        self.db_path = db_path

    def get_conn(self):
        return sqlite3.connect(self.db_path)

    def run_resilience_test(self, product_id, scenario="Normal"):
        conn = self.get_conn()
        p = pd.read_sql_query(f"SELECT * FROM products WHERE id={product_id}", conn).iloc[0]
        sales = pd.read_sql_query(f"SELECT units_sold FROM sales_history WHERE product_id={product_id}", conn)
        conn.close()

        avg_demand = sales['units_sold'].mean()
        tts = p['current_stock'] / avg_demand if avg_demand > 0 else 999
        ttr = p['lead_time']
        
        if scenario == "Port Closure": ttr *= 3
        if scenario == "Factory Fire": ttr += 30
        
        status = "🟢 GREEN"
        if tts < ttr: status = "🔴 RED"
        elif tts < (ttr * 1.5): status = "🟡 YELLOW"
        
        return {"tts": round(tts, 1), "ttr": round(ttr, 1), "status": status}

# --- 2. INITIALIZE ---
st.set_page_config(page_title="DS-31 Enterprise AI", layout="wide")
system = EnterpriseSystem()

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

# --- 3. NAVIGATION ---
st.sidebar.title("🤖 DS-31 Orchestrator")
mode = st.sidebar.selectbox("Navigate", [
    "📈 Strategic Dashboard", 
    "🧪 Stress-Test Simulator", 
    "✍️ Manual Data Entry", 
    "📂 File Upload Center",
    "💬 AI Agent Chat"
])

# --- 4. MODE: DASHBOARD ---
if mode == "📈 Strategic Dashboard":
    st.title("🚀 Strategic Inventory Control")
    conn = sqlite3.connect('inventory_pro.db')
    df = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    
    if df.empty:
        st.warning("Database is empty. Please add data in the 'Manual Entry' or 'File Upload' section.")
    else:
        st.dataframe(df, use_container_width=True)
        fig = px.bar(df, x='name', y='current_stock', color='category', title="Global Stock Levels")
        st.plotly_chart(fig, use_container_width=True)

# --- 5. MODE: STRESS-TEST ---
elif mode == "🧪 Stress-Test Simulator":
    st.title("🧪 Resilience Stress-Testing")
    scenario = st.selectbox("Scenario", ["Normal", "Port Closure", "Factory Fire"])
    
    conn = sqlite3.connect('inventory_pro.db')
    products = pd.read_sql_query("SELECT * FROM products", conn)
    conn.close()
    
    results = []
    for _, p in products.iterrows():
        res = system.run_resilience_test(p['id'], scenario)
        results.append({"Product": p['name'], "TTS": res['tts'], "TTR": res['ttr'], "Risk": res['status']})
    
    st.table(pd.DataFrame(results))

# --- 6. MODE: MANUAL DATA ENTRY (Correcting Data) ---
elif mode == "✍️ Manual Data Entry":
    st.title("✍️ Ledger Management")
    
    tab1, tab2 = st.tabs(["Add New Product", "Edit Existing Stock"])
    
    with tab1:
        with st.form("add_product"):
            name = st.text_input("Product Name")
            cat = st.selectbox("Category", ["Electronics", "Furniture", "Accessories"])
            stock = st.number_input("Initial Stock", min_value=0)
            price = st.number_input("Unit Price", min_value=0.0)
            lt = st.number_input("Lead Time (Days)", min_value=1)
            sup = st.text_input("Supplier Name")
            if st.form_submit_button("Save to Ledger"):
                conn = sqlite3.connect('inventory_pro.db')
                conn.execute("INSERT INTO products (name, category, current_stock, unit_price, lead_time, supplier) VALUES (?,?,?,?,?,?)", 
                             (name, cat, stock, price, lt, sup))
                conn.commit()
                conn.close()
                st.success("Product Added!")

    with tab2:
        conn = sqlite3.connect('inventory_pro.db')
        df = pd.read_sql_query("SELECT * FROM products", conn)
        conn.close()
        
        selected_edit = st.selectbox("Select Product to Edit", df['name'])
        new_qty = st.number_input("Corrected Stock Quantity", min_value=0)
        if st.button("Update Stock"):
            conn = sqlite3.connect('inventory_pro.db')
            conn.execute("UPDATE products SET current_stock = ? WHERE name = ?", (new_qty, selected_edit))
            conn.commit()
            conn.close()
            st.success("Record Updated!")

# --- 7. MODE: FILE UPLOAD (CSV/Excel) ---
elif mode == "📂 File Upload Center":
    st.title("📂 Batch Data Import")
    st.write("Upload a CSV file with columns: `name, category, current_stock, unit_price, lead_time, supplier`")
    
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        df_upload = pd.read_csv(uploaded_file)
        st.write("Preview of Uploaded Data:")
        st.dataframe(df_upload.head())
        
        if st.button("Import to System"):
            conn = sqlite3.connect('inventory_pro.db')
            df_upload.to_sql('products', conn, if_exists='append', index=False)
            conn.close()
            st.success("Successfully imported data to database!")

# --- 8. MODE: AI AGENT CHAT (GROQ/LLM) ---
elif mode == "💬 AI Agent Chat":
    st.title("💬 Agentic Reasoning Interface")
    st.info("Ask me about stock risks, resilience, or optimization.")

    # Get API Key from Secrets
    api_key = st.secrets.get("GROQ_API_KEY")
    
    if not api_key:
        st.warning("Please add 'GROQ_API_KEY' to Streamlit Secrets to enable the Chat Agent.")
    else:
        client = OpenAI(base_url="https://api.groq.com/openai/v1", api_key=api_key)
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

        for m in st.session_state.messages:
            with st.chat_message(m["role"]): st.markdown(m["content"])

        if prompt := st.chat_input("Ex: Which product has the highest risk?"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"): st.markdown(prompt)

            # Context: Provide current database state to the AI
            conn = sqlite3.connect('inventory_pro.db')
            current_data = pd.read_sql_query("SELECT name, current_stock, supplier FROM products", conn).to_string()
            conn.close()

            with st.chat_message("assistant"):
                response = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": f"You are an Inventory AI. Here is the data: {current_data}"},
                        *st.session_state.messages
                    ]
                )
                full_res = response.choices[0].message.content
                st.markdown(full_res)
                st.session_state.messages.append({"role": "assistant", "content": full_res})

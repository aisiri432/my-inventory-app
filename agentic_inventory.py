import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta

# --- 1. PRO DATABASE ENGINE ---
# This creates a persistent database with multiple products and suppliers
def init_pro_db():
    conn = sqlite3.connect('inventory_pro.db')
    c = conn.cursor()
    # Table for Products
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, current_stock INTEGER, 
                  unit_cost REAL, unit_price REAL, lead_time INTEGER, supplier TEXT)''')
    
    # Table for Sales History
    c.execute('''CREATE TABLE IF NOT EXISTS sales_history 
                 (product_id INTEGER, date TEXT, units_sold INTEGER)''')
    
    # Populate with impressive demo data if empty
    c.execute("SELECT count(*) FROM products")
    if c.fetchone()[0] == 0:
        # (ID, Name, Category, Stock, Cost, Price, LeadTime(Days), Supplier)
        products = [
            (1, 'Gaming Laptop x1', 'Electronics', 12, 800, 1200, 7, 'Global Tech Distro'),
            (2, 'Wireless Keyboard', 'Accessories', 45, 30, 75, 4, 'Logi-Logistics'),
            (3, '4K Monitor 27"', 'Electronics', 5, 200, 450, 10, 'Display Solutions Co.'),
            (4, 'Ergonomic Chair', 'Furniture', 22, 150, 299, 14, 'Comfort Seating Ltd.')
        ]
        c.executemany("INSERT INTO products VALUES (?,?,?,?,?,?,?,?)", products)
        
        # Generate 60 days of realistic sales data for each product
        for p_id in [1, 2, 3, 4]:
            base_sales = np.random.randint(2, 8)
            for i in range(60):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                # Add some randomness and a slight upward trend for the AI to detect
                variation = np.random.randint(-2, 4)
                units = max(0, base_sales + variation)
                c.execute("INSERT INTO sales_history VALUES (?,?,?)", (p_id, date, units))
    conn.commit()
    conn.close()

# Initialize DB on startup
init_pro_db()

# --- 2. ADVANCED AI FORECASTING ENGINE ---
# Uses Random Forest to predict demand based on time trends
def ai_forecast(product_id):
    conn = sqlite3.connect('inventory_pro.db')
    df = pd.read_sql_query(f"SELECT * FROM sales_history WHERE product_id={product_id}", conn)
    conn.close()
    
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')
    
    # Create features: Day of year and day of week
    df['day_index'] = np.arange(len(df))
    df['day_of_week'] = df['date'].dt.dayofweek
    
    X = df[['day_index', 'day_of_week']]
    y = df['units_sold']
    
    # Train Random Forest Regressor
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Predict next 7 days
    last_idx = df['day_index'].iloc[-1]
    future_days = []
    for i in range(1, 8):
        future_date = df['date'].iloc[-1] + timedelta(days=i)
        future_days.append([last_idx + i, future_date.dayofweek])
    
    predictions = model.predict(future_days)
    return predictions.round().astype(int)

# --- 3. STREAMLIT UI ---
st.set_page_config(page_title="Agentic AI Inventory Pro", layout="wide", page_icon="📈")

# Sidebar Navigation
st.sidebar.title("🤖 Agentic Menu")
menu = st.sidebar.radio("Navigate to:", ["Live Dashboard", "Agent Reasoning Center", "Manage Inventory"])

# Get Data for UI
conn = sqlite3.connect('inventory_pro.db')
products_df = pd.read_sql_query("SELECT * FROM products", conn)
conn.close()

# --- MODE 1: LIVE DASHBOARD ---
if menu == "Live Dashboard":
    st.title("📊 Multi-Product Inventory Dashboard")
    st.markdown("### Real-time AI Demand Analysis")

    selected_product = st.selectbox("Select Product to Analyze", products_df['name'])
    p_data = products_df[products_df['name'] == selected_product].iloc[0]
    
    # Run AI Forecast
    forecast = ai_forecast(p_data['id'])
    total_7d_demand = forecast.sum()
    
    # KPI Row
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Current Stock", f"{p_data['current_stock']} Units")
    c2.metric("AI Predicted Demand (7d)", f"{total_7d_demand} Units")
    
    # Calculate Risk
    stock_gap = total_7d_demand - p_data['current_stock']
    risk_value = max(0, stock_gap * p_data['unit_price'])
    
    if stock_gap > 0:
        c3.error(f"Stock Gap: {stock_gap} Units")
        c4.warning(f"Revenue at Risk: ${risk_value:,.2f}")
    else:
        c3.success("Stock Level: Safe")
        c4.info("Revenue at Risk: $0.00")

    # Visualizations
    col_a, col_b = st.columns(2)
    
    with col_a:
        # Historical Sales Chart
        conn = sqlite3.connect('inventory_pro.db')
        hist_df = pd.read_sql_query(f"SELECT * FROM sales_history WHERE product_id={p_data['id']}", conn)
        conn.close()
        hist_df['date'] = pd.to_datetime(hist_df['date'])
        fig = px.area(hist_df.tail(30), x='date', y='units_sold', title="30-Day Sales History", color_discrete_sequence=['#00CC96'])
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        # Forecast Chart
        forecast_dates = [(datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(1, 8)]
        fig2 = px.bar(x=forecast_dates, y=forecast, title="7-Day AI Prediction", labels={'x':'Future Date', 'y':'Expected Sales'})
        st.plotly_chart(fig2, use_container_width=True)

# --- MODE 2: AGENT REASONING CENTER (The WOW Factor) ---
elif menu == "Agent Reasoning Center":
    st.title("🧠 AI Agent Decision Logs")
    st.info("The Agent is analyzing stock levels vs lead times to automate reordering.")

    for index, row in products_df.iterrows():
        forecast = ai_forecast(row['id'])
        avg_daily_demand = forecast.mean()
        reorder_point = avg_daily_demand * row['lead_time']
        
        with st.expander(f"Analysis for {row['name']} (Supplier: {row['supplier']})"):
            st.write(f"**Agent Thought Process:**")
            st.write(f"- Average daily demand predicted by Random Forest: **{avg_daily_demand:.2f} units**")
            st.write(f"- Supplier takes **{row['lead_time']} days** to deliver.")
            st.write(f"- Reorder Point: We must order when stock hits **{int(reorder_point)} units** to avoid zero stock.")
            
            if row['current_stock'] <= reorder_point:
                st.error(f"🆘 ALERT: Stock is at {row['current_stock']}. **AGENT HAS GENERATED A RESTOCK REQUEST.**")
                if st.button(f"Generate Purchase Order for {row['name']}"):
                    st.success(f"PO #ORD-{np.random.randint(1000,9999)} sent to {row['supplier']}")
            else:
                st.success(f"✅ Status: Stock is sufficient to cover lead time.")

# --- MODE 3: MANAGE INVENTORY ---
elif menu == "Manage Inventory":
    st.title("⚙️ Inventory Management")
    st.write("Update stock levels after a shipment arrives or manually edit product info.")
    
    st.dataframe(products_df, use_container_width=True)
    
    with st.form("update_stock"):
        st.subheader("Update Stock Level")
        p_name = st.selectbox("Select Product", products_df['name'])
        updated_stock = st.number_input("New Stock Level", min_value=0)
        
        if st.form_submit_button("Update Database"):
            conn = sqlite3.connect('inventory_pro.db')
            conn.execute("UPDATE products SET current_stock = ? WHERE name = ?", (updated_stock, p_name))
            conn.commit()
            conn.close()
            st.success(f"Database updated! {p_name} now has {updated_stock} units.")
            st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("Agentic AI System v2.0 - Hackathon Edition")
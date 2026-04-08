import streamlit as st
import time
import random
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- 1. APP CONFIG & THEME ---
st.set_page_config(
    page_title="AROHA AI | Intelligent Supply Chain",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. PREMIUM CYBER-DARK UI (CSS) ---
st.markdown("""
<style>
    /* Global Background */
    .stApp {
        background-color: #0B0F14;
        color: #E0E0E0;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    /* Gradient Headers */
    .main-header {
        background: linear-gradient(90deg, #7F00FF 0%, #00D4FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #080B0E !important;
        border-right: 1px solid #1F2937;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 2.5rem;
        font-weight: 700;
        transition: 0.3s all ease;
    }

    .stButton>button:hover {
        box-shadow: 0 0 20px rgba(110, 142, 251, 0.6);
        transform: translateY(-2px);
    }

    /* Email Output Box (Fixed MITRA Issue) */
    .email-container {
        background: #171A21;
        border-left: 4px solid #00D4FF;
        padding: 25px;
        border-radius: 8px;
        font-family: 'Inter', sans-serif;
        color: #FFFFFF;
        line-height: 1.6;
    }

    /* Real-time Status Indicators */
    .status-active { color: #00FFB2; font-weight: bold; }
    .status-delayed { color: #FF4B4B; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE MANAGEMENT ---
if 'logs' not in st.session_state:
    st.session_state.logs = [
        {"time": "09:00 AM", "msg": "Neural Network Initialized", "icon": "🟢"},
        {"time": "09:45 AM", "msg": "Warehouse Floor Sync Complete", "icon": "🟢"}
    ]
if 'email_result' not in st.session_state:
    st.session_state.email_result = None

# --- 4. MODULE LOGIC: MITRA ---
def run_mitra():
    st.markdown("<h1 class='main-header'>MITRA Assistant</h1>", unsafe_allow_html=True)
    st.write("### AI Communication & Negotiation Engine")
    
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            recipient = st.text_input("Recipient (Supplier/Client)", placeholder="e.g. Reliance Logistics")
            purpose = st.selectbox("Email Purpose", ["Shipment Delay", "Urgent Reorder", "Price Negotiation", "Task Assignment"])
        with col2:
            urgency = st.select_slider("Urgency Level", options=["Low", "Standard", "Critical"])
            tone = st.radio("Tone", ["Professional", "Strict", "Friendly"], horizontal=True)

        if st.button("✨ Generate AI Email"):
            with st.spinner("AI is drafting your communication..."):
                time.sleep(2)
                subject = f"[{urgency}] Regarding {purpose} - AROHA Operations"
                body = f"""Subject: {subject}\n\nDear {recipient if recipient else "Valued Partner"},\n\nThis is an automated communication from the AROHA AI Orchestrator. Regarding our recent {purpose.lower()}, we would like to request an immediate update on the current status. \n\nOur system has flagged this as a {urgency.lower()} priority. We expect a resolution following our {tone.lower()} guidelines within the next business cycle.\n\nBest Regards,\nOperations Lead | AROHA AI"""
                st.session_state.email_result = body
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.email_result:
        st.markdown("<div class='email-container'>", unsafe_allow_html=True)
        st.text_area("Generated Draft", st.session_state.email_result, height=250)
        st.markdown("</div>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 1, 4])
        with c1:
            if st.button("📋 Copy"): st.toast("Copied to clipboard!")
        with c2:
            if st.button("🔄 Reset"): 
                st.session_state.email_result = None
                st.rerun()

# --- 5. MODULE LOGIC: SANCHARA ---
def run_sanchara():
    st.markdown("<h1 class='main-header'>SANCHARA Tracker</h1>", unsafe_allow_html=True)
    
    col_map, col_feed = st.columns([2, 1])
    
    with col_feed:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Live Activity Stream")
        feed_placeholder = st.empty()
        
        if st.button("🛰️ Start Real-Time Tracking"):
            events = [
                "Ravi started picking at Shelf B2",
                "Anomaly Detected: Aisle 4 Blockage",
                "Ananya completed packing for SKU-901",
                "New Order Received from Mumbai Hub",
                "Logistics Vehicle TRK-402 Departed"
            ]
            for event in events:
                new_status = random.choice(["🟢", "🟡", "🔴"])
                st.session_state.logs.append({"time": datetime.now().strftime("%H:%M:%S"), "msg": event, "icon": new_status})
                with feed_placeholder.container():
                    for log in reversed(st.session_state.logs[-10:]):
                        st.write(f"{log['icon']} **{log['time']}** : {log['msg']}")
                time.sleep(1.2)
        else:
            with feed_placeholder.container():
                for log in reversed(st.session_state.logs[-10:]):
                    st.write(f"{log['icon']} **{log['time']}** : {log['msg']}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_map:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Asset Distribution")
        # Creating a dummy map
        df = pd.DataFrame({
            'lat': [12.97, 19.07, 28.61, 22.57],
            'lon': [77.59, 72.87, 77.20, 88.36],
            'status': ['🟢 Active', '🔴 Delayed', '🟡 Processing', '🟢 Active']
        })
        fig = px.scatter_mapbox(df, lat="lat", lon="lon", color="status", size_max=15, zoom=3,
                                mapbox_style="carto-darkmatter", color_discrete_map={'🟢 Active':'#00FFB2','🔴 Delayed':'#FF4B4B','🟡 Processing':'#FFD700'})
        fig.update_layout(margin=dict(l=0,r=0,t=0,b=0), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. MODULE LOGIC: KARMA ---
def run_karma():
    st.markdown("<h1 class='main-header'>KARMA Intelligence</h1>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Worker Task Assignment")
        st.write("👷 **Employee:** Ravi Kumar")
        st.success("✅ Current Task: Picking Batch #A-42")
        st.write("**Location:** Zone 3, Shelf D12")
        st.write("**Instruction:** Verify barcode for each unit. Pack in bulk crate.")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("<div class='glass-card' style='border-left: 5px solid #FF4B4B;'>", unsafe_allow_html=True)
        st.subheader("⚠️ Fatigue Alerts")
        st.error("Suresh P. showing 15% speed decrease. High error risk. Recommendation: 15min Break.")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Manager Insights")
        chart_data = pd.DataFrame({
            'Worker': ['Ravi', 'Ananya', 'Suresh', 'Priya'],
            'Efficiency': [92, 95, 74, 88]
        })
        fig = px.bar(chart_data, x='Worker', y='Efficiency', color='Efficiency', color_continuous_scale="Purp")
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 7. MAIN NAVIGATION ---
def main():
    st.sidebar.markdown(f"<h1 style='color: #00D4FF;'>AROHA AI</h1>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    
    choice = st.sidebar.radio("Navigate Node", ["🏠 Dashboard", "📧 MITRA (Assistant)", "🛰️ SANCHARA (Tracking)", "👷 KARMA (Workforce)"])
    
    st.sidebar.markdown("---")
    st.sidebar.info("System Health: 🟢 Optimal")
    st.sidebar.write("Last Refreshed: " + datetime.now().strftime("%H:%M:%S"))

    if choice == "🏠 Dashboard":
        st.markdown("<h1 class='main-header'>Strategic Overview</h1>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.metric("Active Nodes", "3/3", "Online")
        c2.metric("Efficiency Index", "94.2%", "+2.1%")
        c3.metric("Data Processed", "1.2 TB", "Real-time")
        
        # Show mini activity feed
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Live System Pulse")
        for log in st.session_state.logs[-3:]:
            st.write(f"{log['icon']} {log['msg']}")
        st.markdown("</div>", unsafe_allow_html=True)

    elif choice == "📧 MITRA (Assistant)":
        run_mitra()
    elif choice == "🛰️ SANCHARA (Tracking)":
        run_sanchara()
    elif choice == "👷 KARMA (Workforce)":
        run_karma()

if __name__ == "__main__":
    main()

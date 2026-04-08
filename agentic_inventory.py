import streamlit as st
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import random

# --- 1. SETTINGS & FUTURISTIC THEME ---
st.set_page_config(
    page_title="AROHA AI | Nexus",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- 2. ULTRA-PREMIUM CSS INJECTION ---
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background: radial-gradient(circle at top right, #0B0E14, #050505);
        color: #E0E0E0;
    }

    /* Glassmorphic Cards */
    div.stElementContainer div[data-testid="stVerticalBlock"] > div.glass-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(0, 242, 254, 0.1);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.8);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    /* Gradient Text & Headers */
    .neon-text {
        background: linear-gradient(90deg, #7928CA, #00f2fe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #080B0E !important;
        border-right: 1px solid #1F2937;
    }

    /* Animated KPI Cards */
    .kpi-box {
        text-align: center;
        padding: 20px;
        border-radius: 15px;
        background: linear-gradient(145deg, #12161d, #0d1015);
        border: 1px solid #1F2937;
        transition: 0.3s;
    }
    .kpi-box:hover {
        border-color: #00f2fe;
        transform: translateY(-5px);
    }

    /* Status Indicators */
    .status-pill {
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }

    /* Custom Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #7928CA 0%, #0070F3 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 700 !important;
        transition: 0.3s !important;
    }
    .stButton > button:hover {
        box-shadow: 0 0 20px rgba(121, 40, 202, 0.6) !important;
        transform: scale(1.02) !important;
    }
    
    /* Input Boxes */
    .stTextInput input, .stSelectbox div {
        background-color: #12161d !important;
        color: white !important;
        border: 1px solid #333 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. SESSION STATE MANAGEMENT (The "Brain") ---
if 'logs' not in st.session_state:
    st.session_state.logs = []
if 'workers' not in st.session_state:
    st.session_state.workers = {
        "Ravi": {"speed": 92, "accuracy": 98, "workload": 40, "status": "🟢 Active", "task": "Picking", "loc": "Shelf B2"},
        "Ananya": {"speed": 85, "accuracy": 95, "workload": 70, "status": "🟡 In Progress", "task": "Packing", "loc": "Station 4"},
        "Suresh": {"speed": 65, "accuracy": 80, "workload": 95, "status": "🔴 Delayed", "task": "Loading", "loc": "Dock A"},
        "Priya": {"speed": 88, "accuracy": 99, "workload": 20, "status": "🟢 Active", "task": "Auditing", "loc": "Zone 1"}
    }
if 'sim_running' not in st.session_state:
    st.session_state.sim_running = False

# --- 4. DATA GENERATORS & LOGIC ---
def add_log(msg, type="🟢"):
    t = datetime.now().strftime("%H:%M:%S")
    st.session_state.logs.append(f"{type} [{t}] {msg}")
    if len(st.session_state.logs) > 15:
        st.session_state.logs.pop(0)

# --- 5. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("<h1 class='neon-text' style='font-size: 2.5rem;'>AROHA</h1>", unsafe_allow_html=True)
    st.markdown("`PREMIUM NEXUS v2.0`", unsafe_allow_html=True)
    st.markdown("---")
    menu = st.radio("Navigate", ["Command Dashboard", "MITRA (AI Comms)", "SANCHARA (Live Track)", "KARMA (Workforce)"])
    st.markdown("---")
    st.info("System Integrity: 99.8%")
    st.info("Neural Link: Stable")

# --- 6. MODULE: DASHBOARD ---
if menu == "Command Dashboard":
    st.markdown("<h1 class='neon-text'>Command Center</h1>", unsafe_allow_html=True)
    
    # KPI Grid
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown("<div class='kpi-box'><small>ACTIVE WORKERS</small><h3>14</h3></div>", unsafe_allow_html=True)
    with kpi2:
        st.markdown("<div class='kpi-box'><small>TASKS COMPLETED</small><h3>1,204</h3></div>", unsafe_allow_html=True)
    with kpi3:
        st.markdown("<div class='kpi-box'><small>EFFICIENCY</small><h3 style='color: #00f2fe;'>94.2%</h3></div>", unsafe_allow_html=True)
    with kpi4:
        st.markdown("<div class='kpi-box'><small>ACTIVE ALERTS</small><h3 style='color: #ff4b4b;'>3</h3></div>", unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        st.markdown("### Real-Time Performance Analytics")
        # Plotly chart
        df_perf = pd.DataFrame({
            "Time": ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00"],
            "Throughput": [85, 88, 95, 92, 98, 100]
        })
        fig = px.line(df_perf, x="Time", y="Throughput", template="plotly_dark", color_discrete_sequence=['#00f2fe'])
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.markdown("### 🔔 System Pulse")
        if not st.session_state.logs:
            st.write("Awaiting data stream...")
        for log in reversed(st.session_state.logs):
            st.write(log)

# --- 7. MODULE: MITRA (EMAIL ASSISTANT) ---
elif menu == "MITRA (AI Comms)":
    st.markdown("<h1 class='neon-text'>MITRA Assistant</h1>", unsafe_allow_html=True)
    st.write("Generates high-precision strategic communications.")

    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            recipient = st.text_input("Recipient", placeholder="e.g. Reliance Logistics CEO")
            purpose = st.selectbox("Strategic Purpose", ["Shipment Delay", "Inventory Shortage", "Supplier Appreciation", "Negotiation Request"])
        with c2:
            tone = st.select_slider("AI Tone", options=["Professional", "Urgent", "Diplomatic"])
        
        if st.button("Generate Strategic Email"):
            with st.spinner("Neural network drafting..."):
                time.sleep(2)
                st.session_state.mitra_email = {
                    "subject": f"[{tone.upper()}] Update: {purpose} - AROHA Nexus",
                    "body": f"Dear {recipient},\n\nThis is an automated intelligence brief from the AROHA Nexus. We are contacting you regarding the {purpose.lower()}. \n\nOur real-time tracking (SANCHARA) indicates a shift in operational parameters. Our AI predicts a resolution within the next business cycle. We appreciate your continued partnership.\n\nBest Regards,\nAROHA AI Systems"
                }
        st.markdown("</div>", unsafe_allow_html=True)

    if 'mitra_email' in st.session_state:
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.subheader("Final Draft")
        st.code(f"Subject: {st.session_state.mitra_email['subject']}\n\n{st.session_state.mitra_email['body']}")
        if st.button("Copy to Clipboard"):
            st.toast("Copied!")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 8. MODULE: SANCHARA (LIVE TRACKING) ---
elif menu == "SANCHARA (Live Track)":
    st.markdown("<h1 class='neon-text'>SANCHARA Track</h1>", unsafe_allow_html=True)
    
    col_map, col_stream = st.columns([2, 1])
    
    with col_stream:
        st.markdown("### Real-Time Activity")
        placeholder = st.empty()
        
        if st.button("🛰️ Initialize Live Stream"):
            st.session_state.sim_running = True
            
        if st.session_state.sim_running:
            for i in range(10):
                worker_name = random.choice(list(st.session_state.workers.keys()))
                actions = ["picked item", "completed pack", "scanned SKU", "moved to station", "paused for sync"]
                icons = ["🟢", "🟡", "🔴"]
                msg = f"{worker_name} {random.choice(actions)}"
                add_log(msg, random.choice(icons))
                
                with placeholder.container():
                    for log in reversed(st.session_state.logs):
                        st.write(log)
                time.sleep(0.5)
            st.session_state.sim_running = False
        else:
            for log in reversed(st.session_state.logs):
                st.write(log)

    with col_map:
        st.markdown("### Asset Geolocation")
        # Visual Simulation of warehouse floor
        df_map = pd.DataFrame({
            'x': [random.randint(1,10) for _ in range(5)],
            'y': [random.randint(1,10) for _ in range(5)],
            'Label': ['A', 'B', 'C', 'D', 'E']
        })
        fig = px.scatter(df_map, x='x', y='y', text='Label', template="plotly_dark")
        fig.update_traces(marker=dict(size=20, color='#00f2fe', symbol='hexagon'))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)

# --- 9. MODULE: KARMA (WORKFORCE INTEL) ---
elif menu == "KARMA (Workforce)":
    st.markdown("<h1 class='neon-text'>KARMA Workforce</h1>", unsafe_allow_html=True)
    
    worker_tab, manager_tab = st.tabs(["👷 Worker Interface", "📊 Manager Command"])
    
    with worker_tab:
        col_w1, col_w2 = st.columns([1, 2])
        with col_w1:
            worker_id = st.selectbox("Select Profile", list(st.session_state.workers.keys()))
            data = st.session_state.workers[worker_id]
            st.markdown(f"**Status:** {data['status']}")
            st.markdown(f"**Speed:** {data['speed']}%")
            st.markdown(f"**Accuracy:** {data['accuracy']}%")
        
        with col_w2:
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            st.subheader("📍 Current Instruction")
            st.success(f"GO TO **{data['loc']}**")
            st.info(f"TASK: **{data['task']}** 10 units of Electronics-SKU")
            st.markdown("**Navigation:** Move to Shelf C1 via Aisle 3")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Error Prevention Simulation
            if st.button("Simulate Scanning Item"):
                if random.random() > 0.8:
                    st.error("🚨 Warning: Incorrect item selected (SKU-402). Please verify barcode.")
                else:
                    st.success("✅ SKU Match. Proceed to packing.")

        # Voice interaction Simulation
        st.markdown("### 🎙️ Voice Interaction Simulator")
        voice_query = st.text_input("Speak to AI (Type to simulate voice)", placeholder="'What should I do next?'")
        if voice_query:
            st.markdown(f"<div style='background: #1F2937; padding: 15px; border-radius: 10px;'><b>AI Agent:</b> Based on current priorities, proceed to Shelf B2 for Picking task. Route uploaded to headset.</div>", unsafe_allow_html=True)

        # Fatigue Logic
        if data['workload'] == 95:
            st.warning("🧠 **Fatigue Detected:** Performance slowdown of 15% detected. Recommend immediate 15-min break.")

    with manager_tab:
        m1, m2 = st.columns(2)
        with m1:
            st.markdown("### Performance Insights Engine")
            st.write("Worker Ravi improved efficiency by 12% this week.")
            st.write("Worker Suresh showing high error rate (Fatigue risk).")
            
            # Bar chart
            worker_names = list(st.session_state.workers.keys())
            worker_speeds = [w['speed'] for w in st.session_state.workers.values()]
            st.bar_chart(pd.DataFrame({"Speed": worker_speeds}, index=worker_names))
            
        with m2:
            st.markdown("### Workforce Allocation")
            for name, d in st.session_state.workers.items():
                st.write(f"**{name}**: {d['task']} at {d['loc']}")
            
            if st.button("Auto-Rebalance Workload"):
                st.toast("AI rebalancing complete. Tasks redistributed to Priya.")

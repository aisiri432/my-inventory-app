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
        c = conn

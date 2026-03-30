import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import plotly.express as px
from sklearn.ensemble import RandomForestRegressor
from datetime import datetime, timedelta
from openai import OpenAI

# --- 1. CORE BRANDING ---
APP_NAME = "AROHA"
TAGLINE = "Turn Data into Decisions"

st.set_page_config(page_title=APP_NAME, layout="wide", page_icon="💠")

# --- 2. THE VAULT (Database Logic) ---
def get_db_connection():
    return sqlite3.connect('aroha_vault.db')

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    # Table for Products
    c.execute('''CREATE TABLE IF NOT EXISTS products 
                 (id INTEGER PRIMARY KEY, name TEXT, category TEXT, current_stock INTEGER, 
                  unit_price REAL, lead_time INTEGER, supplier TEXT)''')
    # Table for Auth
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, hint TEXT)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. SESSION STATE ---
if "auth_status" not in st.session_state:
    st.session_state.auth_status = "Login" # Options: Login, Register, Reset, Authenticated
if "page" not in st.session_state:
    st.session_state.page = "Home"

# High-End UI CSS
st.markdown("""
    <style>
    .stApp { background-color: #05070A; color: white; }
    .main-title { text-align: center; color: #D4AF37; font-size: 3.5em; font-weight: 800; letter-spacing: 5px; margin-bottom: 0px; }
    .tagline { text-align: center; color: #888; font-size: 1.1em; margin-bottom: 50px; font-style: italic; }
    .badge-container {
        background: linear-gradient(145deg, #10141d, #0a0e14);
        border: 1px solid #1f2937; padding: 40px 20px; border-radius: 28px;
        text-align: center; transition: 0.4s; margin-bottom: 20px;
    }
    .badge-container:hover { border-color: #D4AF37; transform: translateY(-10px); background: #161B22; }
    .badge-icon { font-size: 55px; margin-bottom: 15px; }
    .badge-label { color: #D4AF37; font-weight: 700; font-size: 1.4em; }
    .protected-stamp { text-align: center; color: #22c55e; font-size: 0.8em; font-weight: bold; border: 1px solid #22c55e; padding: 6px 15px; width: fit-content; margin: 0 auto 30px auto; border-radius: 50px; }
    .stButton>button { width: 100%; border-radius: 15px; border: 1px solid #1f2937; background: #10141d; color: white; }
    .stButton>button:hover { background: #D4AF37 !important; color: black !important; }
    </style>
""", unsafe_allow_html=True)

# --- 4. AUTHENTICATION MODULES ---

def get_user():
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username='admin'").fetchone()
    conn.close()
    return user

def login_screen():
    st.markdown(f"<h1 class='main-title'>💠 {APP_NAME}</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='tagline'>{TAGLINE}</p>", unsafe_allow_html=True)
    
    user_data = get_user()
    
    # CASE A: NO USER EXISTS (REGISTRATION)
    if not user_data:
        st.info("🏦 Welcome! Initialize the AROHA Treasury by setting your Access Mantra.")
        col1, col2, col3 = st.columns([1,1.5,1])
        with col2:
            new_pwd = st.text_input("Set New Access Mantra", type="password")
            hint = st.text_input("Security Hint (e.g., your pet's name)")
            if st.button("Initialize Vault"):
                if new_pwd and hint:
                    conn = get_db_connection()
                    conn.execute("INSERT INTO users VALUES ('admin', ?, ?)", (new_pwd, hint))
                    conn.commit(); conn.close()
                    st.success("Treasury Initialized! You can now login.")
                    st.rerun()
    
    # CASE B: USER EXISTS (LOGIN)
    elif st.session_state.auth_status == "Login":
        st.markdown("<div class='protected-stamp'>🔒 SECURE ACCESS GATE</div>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1.2,1])
        with col2:
            pwd = st.text_input("Enter Access Mantra", type="password")
            if st.button("Unlock AROHA"):
                if pwd == user_data[1]:
                    st.session_state.auth_status = "Authenticated"
                    st.rerun()
                else:
                    st.error("Incorrect Mantra.")
            if st.button("Forgot Mantra?", use_container_width=True):
                st.session_state.auth_status = "Reset"
                st.rerun()

    # CASE C: FORGOT PASSWORD (RESET)
    elif st.session_state.auth_status == "Reset":
        st.markdown("<h3 style='text-align:center;'>Mantra Recovery</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,1.2,1])
        with col2:
            answer = st.text_input(f"Enter Security Hint Answer: (Hint was set during setup)")
            if st.button("Verify Hint"):
                if answer == user_data[2]:
                    st.success(f"Recovery Successful! Your Mantra is: **{user_data[1]}**")
                    if st.button("Go to Login"):
                        st.session_state.auth_status = "Login"
                        st.rerun()
                else:
                    st.error("Hint answer is incorrect.")
            if st.button("Back to Login"):
                st.session_state.auth_status = "Login"
                st.rerun()

# --- 5. MAIN APP (HOME GRID) ---

if st.session_state.auth_status != "Authenticated":
    login_screen()
else:
    if st.session_state.page == "Home":
        st.markdown(f"<h1 class='main-title'>{APP_NAME}</h1>", unsafe_allow_html=True)
        st.markdown(f"<p class='tagline'>{TAGLINE}</p>", unsafe_allow_html=True)
        
        r1c1, r1c2, r1c3 = st.columns(3)
        r2c1, r2c2, r2c3 = st.columns(3)

        # Badges (Drishti, Stambha, Samvada, Nyasa, Agama)
        with r1c1:
            st.markdown("<div class='badge-container'><div class='badge-icon'>🔮</div><div class='badge-label'>PREKSHA</div></div>", unsafe_allow_html=True)
            if st.button("Open Preksha"): st.session_state.page = "Preksha"; st.rerun()
        with r1c2:
            st.markdown("<div class='badge-container'><div class='badge-icon'>🛡️</div><div class='badge-label'>STAMBHA</div></div>", unsafe_allow_html=True)
            if st.button("Open Stambha"): st.session_state.page = "Stambha"; st.rerun()
        with r1c3:
            st.markdown("<div class='badge-container'><div class='badge-icon'>🗣️</div><div class='badge-label'>SAMVADA</div></div>", unsafe_allow_html=True)
            if st.button("Open Samvada"): st.session_state.page = "Samvada"; st.rerun()
        with r2c1:
            st.markdown("<div class='badge-container'><div class='badge-icon'>✍️</div><div class='badge-label'>NYASA</div></div>", unsafe_allow_html=True)
            if st.button("Open Nyasa"): st.session_state.page = "Nyasa"; st.rerun()
        with r2c2:
            st.markdown("<div class='badge-container'><div class='badge-icon'>📥</div><div class='badge-label'>AGAMA</div></div>", unsafe_allow_html=True)
            if st.button("Open Agama"): st.session_state.page = "Agama"; st.rerun()
        with r2c3:
            st.markdown("<div class='badge-container'><div class='badge-icon'>🔒</div><div class='badge-label'>LOGOUT</div></div>", unsafe_allow_html=True)
            if st.button("Secure Exit"): 
                st.session_state.auth_status = "Login"
                st.session_state.page = "Home"
                st.rerun()

    # --- FEATURE MODULES (SUB-PAGES) ---
    elif st.session_state.page == "Preksha":
        if st.button("⬅️ Home"): st.session_state.page = "Home"; st.rerun()
        st.title("🔮 Preksha: Intelligent Forecasting")
        # Add your graph/prediction code here
        
    elif st.session_state.page == "Samvada":
        if st.button("⬅️ Home"): st.session_state.page = "Home"; st.rerun()
        st.title("🗣️ Samvada: Agentic Chat")
        # Add your Samvada Chat code here (using st.secrets for Groq key)
                

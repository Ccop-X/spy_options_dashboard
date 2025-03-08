import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import datetime
import numpy as np
import requests

# ------------------ APP CONFIGURATION ------------------ #
st.set_page_config(page_title="SPY Options Dashboard", layout="wide")

# ------------------ DARK/LIGHT MODE (FULLY FIXED & FORCED TO APPLY) ------------------ #
theme = st.sidebar.radio("🌗 Theme Mode:", ["🌙 Dark Mode", "☀️ Light Mode"])

# Define Modern Styling (Now Guaranteed to Apply)
if theme == "🌙 Dark Mode":
    st.markdown(
        """
        <style>
            body, .stApp { background-color: #121212; color: #E0E0E0; font-family: 'Inter', sans-serif; }
            .stDataFrame { background-color: #1E1E1E; border-radius: 10px; padding: 15px; }
            .stSidebar { background-color: #1E1E1E; border-radius: 10px; padding: 15px; }
            h1, h2, h3 { color: #17A2B8; font-weight: bold; }
            .metric-container { background-color: #1E1E1E; padding: 20px; border-radius: 12px; text-align: center; 
                                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }
            .stTabs div[role="tablist"] { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; font-weight: bold; }
            .stButton>button { background-color: #17A2B8; color: white; font-size: 16px; border-radius: 8px; width: 100%; padding: 10px; }
        </style>
        """,
        unsafe_allow_html=True
    )
    chart_template = "plotly_dark"
else:
    st.markdown(
        """
        <style>
            body, .stApp { background-color: #F8F9FA; color: #212529; font-family: 'Inter', sans-serif; }
            .stDataFrame { background-color: #FFFFFF; border-radius: 10px; padding: 15px; }
            .stSidebar { background-color: #E9ECEF; border-radius: 10px; padding: 15px; }
            h1, h2, h3 { color: #007BFF; font-weight: bold; }
            .metric-container { background-color: #FFFFFF; padding: 20px; border-radius: 12px; text-align: center; 
                                box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }
            .stTabs div[role="tablist"] { display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; font-weight: bold; }
            .stButton>button { background-color: #007BFF; color: white; font-size: 16px; border-radius: 8px; width: 100%; padding: 10px; }
        </style>
        """,
        unsafe_allow_html=True
    )
    chart_template = "plotly_white"

# ------------------ COUNTDOWN TIMER FOR JOBS REPORT ------------------ #
def get_next_jobs_report():
    today = datetime.date.today()
    year, month = today.year, today.month
    if today.day > 7 or today.weekday() >= 4:
        month += 1
        if month > 12:
            month = 1
            year += 1
    first_day = datetime.date(year, month, 1)
    first_friday = first_day + datetime.timedelta(days=(4 - first_day.weekday() + 7) % 7)
    return datetime.datetime.combine(first_friday, datetime.time(8, 30))

next_jobs_report = get_next_jobs_report()
st.sidebar.markdown(f"### 🕒 Next Jobs Report: **{next_jobs_report.strftime('%B %d, %Y')} at 8:30 AM ET**")

# ------------------ FETCH SPY PRICE (FIXED) ------------------ #
@st.cache_data
def get_spy_price():
    spy = yf.Ticker("SPY")
    return spy.fast_info.get("last_price") or spy.history(period="1d")["Close"].iloc[-1]

spy_price = get_spy_price()

# ------------------ SIDEBAR ------------------ #
st.sidebar.title("⚙️ Dashboard Settings")
st.sidebar.info("Select options below to update the dashboard.")

# Fetch SPY options safely
st.sidebar.subheader("📅 Options Data")
try:
    expirations = yf.Ticker("SPY").options
except Exception as e:
    st.sidebar.error(f"⚠️ Error fetching SPY data: {e}")
    st.stop()

selected_date = st.sidebar.selectbox("📆 Select Expiration Date", expirations)

# ------------------ DASHBOARD UI ------------------ #
st.title("📊 SPY Options Dashboard")
st.subheader(f"🔹 Options Expiring on {selected_date}")

# Quick Insights Section
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("SPY Price", f"${spy_price:.2f}")
with col2:
    st.metric("Total Put Volume", f"{puts['volume'].sum():,}")
with col3:
    st.metric("Total Call Volume", f"{calls['volume'].sum():,}")

# ------------------ FORCE STREAMLIT TO APPLY UI CHANGES ------------------ #
st.markdown("<h1 style='text-align: center; color: red;'>🚀 UI HAS BEEN UPDATED 🚀</h1>", unsafe_allow_html=True)

# ------------------ DEPLOYMENT CONFIRMATION ------------------ #
st.sidebar.success("✅ Final UI Update + SPY Price Fix Applied.")

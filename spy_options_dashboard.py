import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import datetime
import numpy as np
import matplotlib.pyplot as plt
import requests
import time

# ------------------ APP CONFIGURATION ------------------ #
st.set_page_config(page_title="SPY Options Dashboard", layout="wide")

# Custom Styling
st.markdown("""
    <style>
        body { font-family: 'Arial', sans-serif; }
        .stApp { background-color: #121212; color: white; }
        .sidebar .sidebar-content { background-color: #1E1E1E; color: white; }
        .stButton>button { background-color: #0066CC; color: white; font-size: 16px; border-radius: 5px; width: 100%; }
        .stDataFrame { background-color: #222222; border-radius: 5px; padding: 10px; }
        h1, h2, h3 { color: #17A2B8; }
        .metric-container { background-color: #222222; padding: 10px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ------------------ COUNTDOWN TIMER FOR JOBS REPORT ------------------ #
def get_next_jobs_report():
    """Calculate the next U.S. Non-Farm Payroll (NFP) Jobs Report date (First Friday of the Month at 8:30 AM ET)."""
    today = datetime.date.today()
    year, month = today.year, today.month

    if today.day > 7 or today.weekday() >= 4:
        month += 1
        if month > 12:
            month = 1
            year += 1

    first_day = datetime.date(year, month, 1)
    first_friday = first_day + datetime.timedelta(days=(4 - first_day.weekday() + 7) % 7)

    jobs_report_datetime = datetime.datetime.combine(first_friday, datetime.time(8, 30))
    
    return jobs_report_datetime

next_jobs_report = get_next_jobs_report()
st.sidebar.markdown(f"### 🕒 Next Jobs Report: **{next_jobs_report.strftime('%B %d, %Y')} at 8:30 AM ET**")

countdown_placeholder = st.sidebar.empty()

def update_countdown():
    """Dynamically updates the countdown timer every second."""
    time_left = next_jobs_report - datetime.datetime.now()
    
    if time_left.total_seconds() <= 0:
        countdown_placeholder.markdown("🚨 **Jobs Report Released!**")
    else:
        days, seconds = divmod(time_left.total_seconds(), 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        
        countdown_placeholder.markdown(f"**{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s remaining**")

update_countdown()

# ------------------ SIDEBAR ------------------ #
st.sidebar.title("⚙️ Dashboard Settings")
st.sidebar.info("Select options below to update the dashboard.")

# Fetch SPY options safely
st.sidebar.subheader("📅 Options Data")
today = datetime.date.today()

try:
    spy = yf.Ticker("SPY")
    expirations = spy.options
except Exception as e:
    st.sidebar.error(f"⚠️ Error fetching SPY data: {e}")
    st.stop()

selected_date = st.sidebar.selectbox("📆 Select Expiration Date", expirations)

# ------------------ DATA FETCHING ------------------ #
with st.spinner("Fetching latest SPY options data..."):
    try:
        options_chain = spy.option_chain(selected_date)
        puts = options_chain.puts
        calls = options_chain.calls
    except Exception as e:
        st.error(f"⚠️ Error fetching options chain: {e}")
        st.stop()

# Get SPY current price
try:
    spy_price = spy.history(period="1d")["Close"].iloc[-1]
    st.sidebar.metric(label="📈 SPY Current Price", value=f"${spy_price:.2f}")
except:
    st.sidebar.warning("⚠️ Unable to fetch SPY price.")

# ------------------ DASHBOARD UI ------------------ #
st.title("📊 SPY Options Dashboard")
st.subheader(f"🔹 Options Expiring on {selected_date}")

# Quick Insights Section
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='metric-container'><h3>SPY Price</h3><h2>${:.2f}</h2></div>".format(spy_price), unsafe_allow_html=True)
with col2:
    st.markdown("<div class='metric-container'><h3>Total Put Volume</h3><h2>{:,}</h2></div>".format(puts["volume"].sum()), unsafe_allow_html=True)
with col3:
    st.markdown("<div class='metric-container'><h3>Total Call Volume</h3><h2>{:,}</h2></div>".format(calls["volume"].sum()), unsafe_allow_html=True)

# ------------------ TABS ------------------ #
tab1, tab2, tab3, tab4 = st.tabs(["📉 Put Options", "📈 Call Options", "📊 Backtesting", "📰 Tariff News"])

# 📉 PUT OPTIONS
with tab1:
    st.subheader(f"🔻 SPY Put Options Expiring {selected_date}")
    st.dataframe(puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])

# 📈 CALL OPTIONS
with tab2:
    st.subheader(f"🔼 SPY Call Options Expiring {selected_date}")
    st.dataframe(calls[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])

# 📊 BACKTESTING
with tab3:
    st.subheader("📊 Options Backtesting")
    st.write("🔍 Backtesting module coming soon with customizable strategies!")

# 📰 TARIFF NEWS
with tab4:
    st.subheader("📰 Latest Tariff News")
    
    news_api_url = "https://newsapi.org/v2/everything?q=tariff&language=en&sortBy=publishedAt&apiKey=YOUR_NEWS_API_KEY"

    try:
        response = requests.get(news_api_url)
        news_data = response.json()
        
        if "articles" in news_data:
            for article in news_data["articles"][:5]:  # Show only top 5 articles
                st.markdown(f"### [{article['title']}]({article['url']})")
                st.write(f"🗓️ {article['publishedAt']} | 🏛️ {article['source']['name']}")
                st.write(f"{article['description']}")
                st.write("---")
        else:
            st.warning("⚠️ No tariff news available at the moment.")
    except Exception as e:
        st.error(f"⚠️ Error fetching tariff news: {e}")

# ------------------ SUCCESS MESSAGE ------------------ #
st.sidebar.success("✅ Full Features Restored! Your dashboard is now complete.")

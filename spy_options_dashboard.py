import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import datetime
import numpy as np
import requests

# ------------------ APP CONFIGURATION ------------------ #
st.set_page_config(page_title="SPY Options Dashboard V2", layout="wide")

# ------------------ DARK/LIGHT MODE (FULLY FIXED) ------------------ #
theme = st.sidebar.radio("🌗 Theme Mode:", ["🌙 Dark Mode", "☀️ Light Mode"])

# Define Modern Styling
if theme == "🌙 Dark Mode":
    primary_bg = "#121212"
    text_color = "#E0E0E0"
    accent_color = "#17A2B8"
    table_bg = "#1E1E1E"
    sidebar_bg = "#1E1E1E"
    chart_template = "plotly_dark"
else:
    primary_bg = "#F4F4F4"
    text_color = "#212529"
    accent_color = "#007BFF"
    table_bg = "#FFFFFF"
    sidebar_bg = "#E9ECEF"
    chart_template = "plotly_white"

# Apply Styling (Fully Fixed)
st.markdown(f"""
    <style>
        body, .stApp {{ background-color: {primary_bg}; color: {text_color}; font-family: 'Inter', sans-serif; }}
        .stDataFrame {{ background-color: {table_bg}; border-radius: 10px; padding: 15px; }}
        .stSidebar {{ background-color: {sidebar_bg}; border-radius: 10px; padding: 15px; }}
        h1, h2, h3 {{ color: {accent_color}; font-weight: bold; }}
        .metric-container {{ background-color: {table_bg}; padding: 20px; border-radius: 12px; text-align: center; 
                            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1); }}
        .stTabs div[role="tablist"] {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 15px; font-weight: bold; }}
        .stButton>button {{ background-color: {accent_color}; color: white; font-size: 16px; border-radius: 8px; width: 100%; padding: 10px; }}
    </style>
""", unsafe_allow_html=True)

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
    st.markdown(f"<div class='metric-container'><h3>SPY Price</h3><h2>${spy_price:.2f}</h2></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-container'><h3>Total Put Volume</h3><h2>{puts['volume'].sum():,}</h2></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-container'><h3>Total Call Volume</h3><h2>{calls['volume'].sum():,}</h2></div>", unsafe_allow_html=True)

# ------------------ TABS (Fixed Layout) ------------------ #
tab1, tab2, tab3, tab4 = st.tabs(["📉 Puts", "📈 Calls", "📊 Backtesting", "📰 Tariff News"])

# 📉 PUT OPTIONS
with tab1:
    st.subheader(f"🔻 SPY Put Options Expiring {selected_date}")
    st.dataframe(puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])
    fig_puts = px.line(puts, x='strike', y='impliedVolatility', title="📉 Implied Volatility vs Strike Price (Puts)",
                        labels={'strike': "Strike Price", 'impliedVolatility': "Implied Volatility"},
                        template=chart_template)
    st.plotly_chart(fig_puts, use_container_width=True)

# 📈 CALL OPTIONS
with tab2:
    st.subheader(f"🔼 SPY Call Options Expiring {selected_date}")
    st.dataframe(calls[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])
    fig_calls = px.line(calls, x='strike', y='impliedVolatility', title="📈 Implied Volatility vs Strike Price (Calls)",
                        labels={'strike': "Strike Price", 'impliedVolatility': "Implied Volatility"},
                        template=chart_template)
    st.plotly_chart(fig_calls, use_container_width=True)

# 📊 BACKTESTING
with tab3:
    st.subheader("📊 Options Backtesting")
    st.write("🔍 Backtesting module coming soon with customizable strategies!")

# 📰 TARIFF NEWS
with tab4:
    st.subheader("📰 Latest Tariff News")
    
    api_key = "6c293f797122483d8a71858ab2619844"
    news_api_url = f"https://newsapi.org/v2/everything?q=tariff&language=en&sortBy=publishedAt&apiKey={api_key}"

    try:
        response = requests.get(news_api_url)
        news_data = response.json()
        if "articles" in news_data:
            for article in news_data["articles"][:5]:
                st.markdown(f"### [{article['title']}]({article['url']})")
                st.write(f"🗓️ {article['publishedAt']} | 🏛️ {article['source']['name']}")
                st.write(f"{article['description']}")
                st.write("---")
        else:
            st.warning("⚠️ No tariff news available.")
    except Exception as e:
        st.error(f"⚠️ Error fetching tariff news: {e}")

st.sidebar.success("✅ Final UI Overhaul Complete! Looks like a Real Trading App.")

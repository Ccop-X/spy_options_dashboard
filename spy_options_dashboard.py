import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import datetime

# Set page title and layout
st.set_page_config(page_title="SPY Options Dashboard", layout="wide")

# Sidebar - Select date range
st.sidebar.header("Options Data Settings")
today = datetime.date.today()

# Fetch SPY options chain
st.sidebar.subheader("Fetching Options Data...")
spy = yf.Ticker("SPY")
expirations = spy.options

# Expiration date selection
selected_date = st.sidebar.selectbox("Select Expiration Date", expirations)

# Load options data
options_chain = spy.option_chain(selected_date)
puts = options_chain.puts
calls = options_chain.calls

# Display live SPY price
spy_price = spy.history(period="1d")["Close"].iloc[-1]
st.sidebar.metric(label="SPY Current Price", value=f"${spy_price:.2f}")

# Tabs for different data views
tab1, tab2 = st.tabs(["📉 Put Options", "📈 Call Options"])

# Put Options Table
with tab1:
    st.subheader(f"SPY Put Options Expiring {selected_date}")
    st.dataframe(puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])

    # Plot Implied Volatility vs Strike Price
    fig_puts = px.line(puts, x='strike', y='impliedVolatility',
                        title="Implied Volatility vs Strike Price (Puts)",
                        labels={'strike': "Strike Price", 'impliedVolatility': "Implied Volatility"})
    st.plotly_chart(fig_puts, use_container_width=True)

# Call Options Table
with tab2:
    st.subheader(f"SPY Call Options Expiring {selected_date}")
    st.dataframe(calls[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])

    # Plot Implied Volatility vs Strike Price
    fig_calls = px.line(calls, x='strike', y='impliedVolatility',
                        title="Implied Volatility vs Strike Price (Calls)",
                        labels={'strike': "Strike Price", 'impliedVolatility': "Implied Volatility"})
    st.plotly_chart(fig_calls, use_container_width=True)

st.sidebar.info("This dashboard fetches real-time SPY options data using Yahoo Finance.")

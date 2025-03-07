import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import datetime

# Set up Streamlit page configuration
st.set_page_config(page_title="SPY Options Dashboard", layout="wide")

# Custom CSS for a better UI
st.markdown("""
    <style>
        .big-font { font-size:20px !important; }
        .stDataFrame { background-color: #f9f9f9; border-radius: 5px; padding: 10px; }
    </style>
""", unsafe_allow_html=True)

# Sidebar header
st.sidebar.header("Options Data Settings")

# Get today's date
today = datetime.date.today()

# Fetch SPY options chain safely
try:
    spy = yf.Ticker("SPY")
    expirations = spy.options
except Exception as e:
    st.sidebar.error(f"Error fetching SPY options data: {e}")
    st.stop()

# Dropdown for expiration date selection
selected_date = st.sidebar.selectbox("Select Expiration Date", expirations)

# Fetch options chain safely
try:
    options_chain = spy.option_chain(selected_date)
    puts = options_chain.puts
    calls = options_chain.calls
except Exception as e:
    st.sidebar.error(f"Error fetching options chain: {e}")
    st.stop()

# Get SPY current price
try:
    spy_price = spy.history(period="1d")["Close"].iloc[-1]
    st.sidebar.metric(label="SPY Current Price", value=f"${spy_price:.2f}")
except:
    st.sidebar.warning("Unable to fetch SPY price.")

# Create tabs for Calls and Puts
tab1, tab2 = st.tabs(["📉 Put Options", "📈 Call Options"])

# Display Put Options
with tab1:
    st.subheader(f"SPY Put Options Expiring {selected_date}")
    st.dataframe(puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])

    # Plot Implied Volatility vs Strike Price
    fig_puts = px.line(puts, x='strike', y='impliedVolatility',
                        title="Implied Volatility vs Strike Price (Puts)",
                        labels={'strike': "Strike Price", 'impliedVolatility': "Implied Volatility"})
    st.plotly_chart(fig_puts, use_container_width=True)

# Display Call Options
with tab2:
    st.subheader(f"SPY Call Options Expiring {selected_date}")
    st.dataframe(calls[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])

    # Plot Implied Volatility vs Strike Price
    fig_calls = px.line(calls, x='strike', y='impliedVolatility',
                        title="Implied Volatility vs Strike Price (Calls)",
                        labels={'strike': "Strike Price", 'impliedVolatility': "Implied Volatility"})
    st.plotly_chart(fig_calls, use_container_width=True)

# Display completion message
st.sidebar.success("Dashboard is now live! 🎯")

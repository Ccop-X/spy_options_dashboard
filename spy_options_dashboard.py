import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import datetime

# ------------------ APP CONFIGURATION ------------------ #
st.set_page_config(page_title="SPY Options Dashboard", layout="wide")

# Custom CSS for styling
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
        }
        .stApp {
            background-color: #f5f5f5;
        }
        .sidebar .sidebar-content {
            background-color: #2E4053;
            color: white;
        }
        .stButton>button {
            background-color: #007BFF;
            color: white;
            font-size: 16px;
            border-radius: 5px;
            width: 100%;
        }
        .stDataFrame {
            background-color: #ffffff;
            border-radius: 5px;
            padding: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# ------------------ SIDEBAR CONFIGURATION ------------------ #
st.sidebar.header("⚙️ Settings")
theme = st.sidebar.radio("Select Theme", ["Light", "Dark"])

# Apply Theme
if theme == "Dark":
    st.markdown("""
        <style>
            .stApp { background-color: #1E1E1E; color: white; }
            .stDataFrame { background-color: #2E2E2E; color: white; }
            .stButton>button { background-color: #17A589; }
        </style>
    """, unsafe_allow_html=True)

# Fetch SPY data safely
st.sidebar.subheader("📅 Options Data")
today = datetime.date.today()

try:
    spy = yf.Ticker("SPY")
    expirations = spy.options
except Exception as e:
    st.sidebar.error(f"Error fetching SPY data: {e}")
    st.stop()

selected_date = st.sidebar.selectbox("📆 Select Expiration Date", expirations)

# ------------------ DATA FETCHING & LOADING INDICATOR ------------------ #
with st.spinner("Fetching options data..."):
    try:
        options_chain = spy.option_chain(selected_date)
        puts = options_chain.puts
        calls = options_chain.calls
    except Exception as e:
        st.error(f"Error fetching options chain: {e}")
        st.stop()

# Get SPY current price
try:
    spy_price = spy.history(period="1d")["Close"].iloc[-1]
    st.sidebar.metric(label="📈 SPY Current Price", value=f"${spy_price:.2f}")
except:
    st.sidebar.warning("Unable to fetch SPY price.")

# ------------------ TABS FOR CALLS & PUTS ------------------ #
st.title("📊 SPY Options Dashboard")
tab1, tab2 = st.tabs(["📉 Put Options", "📈 Call Options"])

# Display Put Options
with tab1:
    st.subheader(f"🔻 SPY Put Options Expiring {selected_date}")
    with st.expander("📋 View Data Table"):
        st.dataframe(puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])

    # Plot Implied Volatility vs Strike Price
    fig_puts = px.line(puts, x='strike', y='impliedVolatility',
                        title="📉 Implied Volatility vs Strike Price (Puts)",
                        labels={'strike': "Strike Price", 'impliedVolatility': "Implied Volatility"},
                        template="plotly_dark" if theme == "Dark" else "plotly_white")
    st.plotly_chart(fig_puts, use_container_width=True)

# Display Call Options
with tab2:
    st.subheader(f"🔼 SPY Call Options Expiring {selected_date}")
    with st.expander("📋 View Data Table"):
        st.dataframe(calls[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])

    # Plot Implied Volatility vs Strike Price
    fig_calls = px.line(calls, x='strike', y='impliedVolatility',
                        title="📈 Implied Volatility vs Strike Price (Calls)",
                        labels={'strike': "Strike Price", 'impliedVolatility': "Implied Volatility"},
                        template="plotly_dark" if theme == "Dark" else "plotly_white")
    st.plotly_chart(fig_calls, use_container_width=True)

# ------------------ SUCCESS MESSAGE ------------------ #
st.sidebar.success("✅ Dashboard Ready!")

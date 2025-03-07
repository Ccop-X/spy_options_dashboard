import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
import datetime

# ------------------ APP CONFIGURATION ------------------ #
st.set_page_config(page_title="SPY Options Dashboard", layout="wide")

# Custom CSS for sleek design
st.markdown("""
    <style>
        body {
            font-family: 'Arial', sans-serif;
        }
        .stApp {
            background-color: #121212;
            color: white;
        }
        .sidebar .sidebar-content {
            background-color: #1E1E1E;
            color: white;
        }
        .stButton>button {
            background-color: #0066CC;
            color: white;
            font-size: 16px;
            border-radius: 5px;
            width: 100%;
        }
        .stDataFrame {
            background-color: #222222;
            border-radius: 5px;
            padding: 10px;
        }
        h1, h2, h3 {
            color: #17A2B8;
        }
        .metric-container {
            background-color: #222222;
            padding: 10px;
            border-radius: 10px;
            text-align: center;
        }
    </style>
""", unsafe_allow_html=True)

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

# Create a metric container for quick insights
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='metric-container'><h3>SPY Price</h3><h2>${:.2f}</h2></div>".format(spy_price), unsafe_allow_html=True)
with col2:
    st.markdown("<div class='metric-container'><h3>Total Put Volume</h3><h2>{:,}</h2></div>".format(puts["volume"].sum()), unsafe_allow_html=True)
with col3:
    st.markdown("<div class='metric-container'><h3>Total Call Volume</h3><h2>{:,}</h2></div>".format(calls["volume"].sum()), unsafe_allow_html=True)

# ------------------ OPTIONS DATA & VISUALS ------------------ #
tab1, tab2 = st.tabs(["📉 Put Options", "📈 Call Options"])

# Display Put Options
with tab1:
    st.subheader(f"🔻 SPY Put Options Expiring {selected_date}")
    st.dataframe(puts[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])
    # Plot Implied Volatility vs Strike Price
    fig_puts = px.line(puts, x='strike', y='impliedVolatility',
                        title="📉 Implied Volatility vs Strike Price (Puts)",
                        labels={'strike': "Strike Price", 'impliedVolatility': "Implied Volatility"},
                        template="plotly_dark")
    st.plotly_chart(fig_puts, use_container_width=True)

# Display Call Options
with tab2:
    st.subheader(f"🔼 SPY Call Options Expiring {selected_date}")
    st.dataframe(calls[['strike', 'lastPrice', 'bid', 'ask', 'volume', 'openInterest', 'impliedVolatility']])
    # Plot Implied Volatility vs Strike Price
    fig_calls = px.line(calls, x='strike', y='impliedVolatility',
                        title="📈 Implied Volatility vs Strike Price (Calls)",
                        labels={'strike': "Strike Price", 'impliedVolatility': "Implied Volatility"},
                        template="plotly_dark")
    st.plotly_chart(fig_calls, use_container_width=True)

# ------------------ SUCCESS MESSAGE ------------------ #
st.sidebar.success("✅ Dashboard is now optimized & ready to use!")

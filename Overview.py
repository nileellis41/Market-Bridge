import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fredapi import Fred
from datetime import datetime

# Sidebar for API Key Input
st.sidebar.title("API Key Input")
fred_api_key = st.sidebar.text_input("Enter your FRED API Key:", type="password")

# Initialize FRED API
if fred_api_key:
    fred = Fred(api_key=fred_api_key)
    st.sidebar.success("FRED API Key successfully added!")
else:
    fred = None
    st.sidebar.warning("Please enter a valid FRED API Key.")

# Helper Functions
@st.cache_data
def fetch_fred_data(indicator_id, start_date):
    """Fetch data from FRED API."""
    if fred:
        try:
            data = fred.get_series(indicator_id, start=start_date)
            return data
        except Exception as e:
            return f"Error fetching data for {indicator_id}: {e}"
    else:
        return "FRED API Key not set."

@st.cache_data
def get_yfinance_data(ticker, start_date, end_date):
    """Fetch data from Yahoo Finance."""
    ticker_data = yf.Ticker(ticker)
    return ticker_data.history(start=start_date, end=end_date)

# At-a-Glance Summary Section
st.title("📊 Market Overview: Economic Indicators and Indices")
st.markdown("Stay updated with key economic trends and market indices.")

# Date Range Selector
st.sidebar.markdown("### Date Range Selector")
start_date = st.sidebar.date_input("Start Date", value=datetime(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", value=datetime.today())

# Tabs for better navigation
tabs = st.tabs(["At-a-Glance Summary", "Economic Indicators", "Market Indices"])

# Tab 1: At-a-Glance Summary
with tabs[0]:
    st.subheader("📈 Overview of Key Metrics")
    indicators = {
        "Unemployment Rate": "UNRATE",
        "CPI (Inflation)": "CPIAUCSL",
        "GDP Growth": "GDPC1",
        "Federal Funds Rate": "FEDFUNDS"
    }
    indicator_changes = {}
    for name, fred_id in indicators.items():
        data = fetch_fred_data(fred_id, start_date=start_date)
        if isinstance(data, pd.Series) and not data.empty:
            change = ((data[-1] - data[-2]) / data[-2]) * 100 if len(data) > 1 else 0
            indicator_changes[name] = (data[-1], change)
        else:
            indicator_changes[name] = ("Data unavailable", None)

    if indicator_changes:
        st.markdown("### Economic Indicators")
        for name, (latest, change) in indicator_changes.items():
            delta = f"{change:.2f}%" if change is not None else "N/A"
            st.metric(label=name, value=f"{latest:.2f}" if isinstance(latest, (int, float)) else latest, delta=delta)

# Tab 2: Economic Indicators
with tabs[1]:
    st.subheader("📊 Key Economic Indicators")
    explanations = {
        "Unemployment Rate": """
            Tracks the percentage of the labor force that is unemployed. 
            **Current Impact**: A lower rate suggests economic growth but can signal inflationary pressure.
        """,
        "CPI (Inflation)": """
            Measures the average change in prices paid by consumers for goods and services.
            **Current Impact**: Rising inflation can lead to tighter monetary policies, affecting borrowing costs.
        """,
        "GDP Growth": """
            Represents the total value of goods and services produced over a specific time period.
            **Current Impact**: High GDP growth suggests economic expansion, boosting markets, while contractions may indicate recessions.
        """,
        "Federal Funds Rate": """
            The interest rate at which banks lend to each other overnight.
            **Current Impact**: Higher rates can cool inflation but may dampen market liquidity and borrowing.
        """
    }
    for name, fred_id in indicators.items():
        data = fetch_fred_data(fred_id, start_date=start_date)
        if isinstance(data, pd.Series) and not data.empty:
            fig = px.line(data_frame=data.reset_index(), x="index", y=0, labels={"index": "Date", 0: name})
            fig.update_layout(title=name, template="plotly_dark")
            st.plotly_chart(fig)
            st.markdown(f"**Explanation:** {explanations.get(name, 'No explanation available.')}")
        else:
            st.write(f"Data for {name} is unavailable.")

# Tab 3: Market Indices
with tabs[2]:
    st.subheader("📈 Market Indices and Volatility")
    indices = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "Dow Jones": "^DJI"
    }
    for name, ticker in indices.items():
        index_data = get_yfinance_data(ticker, start_date=start_date, end_date=end_date)
        if not index_data.empty:
            fig = go.Figure(data=[go.Candlestick(
                x=index_data.index,
                open=index_data["Open"],
                high=index_data["High"],
                low=index_data["Low"],
                close=index_data["Close"]
            )])
            fig.update_layout(title=name, template="plotly_dark", xaxis_title="Date", yaxis_title="Price")
            st.plotly_chart(fig)
        else:
            st.write(f"Data for {name} is unavailable.")

    # Add VIX Analysis
    st.subheader("📉 Volatility Index (VIX)")
    vix_data = get_yfinance_data("^VIX", start_date=start_date, end_date=end_date)
    if not vix_data.empty:
        fig = px.line(
            vix_data.reset_index(), x="Date", y="Close",
            labels={"Date": "Date", "Close": "VIX Value"}
        )
        fig.update_layout(title="VIX: Market Volatility Index", template="plotly_dark")
        st.plotly_chart(fig)
        st.markdown("""
            **Explanation**: The VIX measures market volatility. 
            A high VIX value indicates increased uncertainty and risk aversion in the market, while a low VIX suggests stability.
        """)
    else:
        st.write("Data for VIX is unavailable.")
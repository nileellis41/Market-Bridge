import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from fredapi import Fred
from datetime import datetime
plt.style.use('dark_background')

# Streamlit App Layout
st.set_page_config(page_title="MarketBridge", layout="wide")
st.title("MarketBridge")
st.markdown("## Sector Insights Home Page")

# Sidebar for API Key Input and Date Range
st.sidebar.title("API Key Input and Date Range")
fred_api_key = st.sidebar.text_input("Enter your FRED API Key:", type="password")
start_date = st.sidebar.date_input("Start Date", value=datetime(2020, 1, 1))
end_date = st.sidebar.date_input("End Date", value=datetime.today())

# Initialize FRED API
if fred_api_key:
    fred = Fred(api_key=fred_api_key)
    st.sidebar.success("FRED API Key successfully added!")
else:
    fred = None
    st.sidebar.warning("Please enter a valid FRED API Key.")

# Helper Functions
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

def fetch_sector_performance(ticker, start_date, end_date):
    """Fetch historical data for sector ETFs."""
    try:
        return yf.Ticker(ticker).history(start=start_date, end=end_date)
    except Exception as e:
        return f"Error fetching data for {ticker}: {e}"

# Heatmap Section
st.subheader("Sector Heatmap")
sector_etfs = ["XLE", "XLF", "XLK", "XLV", "XLY"]
performance_data = {}

# Pull performance data within the selected date range
for etf in sector_etfs:
    hist = fetch_sector_performance(etf, start_date, end_date)
    if isinstance(hist, pd.DataFrame):
        daily_change = ((hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2]) * 100
        weekly_change = ((hist["Close"].iloc[-1] - hist["Close"].iloc[-6]) / hist["Close"].iloc[-6]) * 100
        ytd_change = ((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0]) * 100
        performance_data[etf] = {
            "Daily Change (%)": daily_change,
            "Weekly Change (%)": weekly_change,
            "YTD Change (%)": ytd_change,
        }

# Convert performance data to DataFrame
performance_df = pd.DataFrame(performance_data).T

# Plot Heatmap
if not performance_df.empty:
    st.write("### Daily Sector Performance Heatmap")
    plt.figure(figsize=(6, 3))
    sns.heatmap(performance_df[["Daily Change (%)"]], annot=True, cmap="RdYlGn", center=0, fmt=".2f")
    plt.title("Sector Daily Performance Heatmap (%)")
    plt.xlabel("")
    plt.ylabel("Sector ETFs")
    st.pyplot(plt)

# Performance Table with Conditional Formatting
st.write("### Performance Metrics (Daily, Weekly, YTD)")

def style_table(dataframe):
    def color_value(val):
        color = "green" if val > 0 else "red" if val < 0 else "black"
        return f"color: {color}"

    return dataframe.style.applymap(color_value, subset=["Daily Change (%)", "Weekly Change (%)", "YTD Change (%)"])

if not performance_df.empty:
    performance_df.reset_index(inplace=True)
    performance_df.rename(columns={"index": "Sector ETF"}, inplace=True)
    st.dataframe(style_table(performance_df))

# Sector Analysis Tabs
st.markdown("---")
st.markdown("### Sector Analysis")

sector_tabs = st.tabs(sector_etfs)
sector_indicators = {
    "XLE": {"Crude Oil Prices": "DCOILWTICO", "Natural Gas Prices": "MHHNGSP"},
    "XLF": {"Federal Funds Rate": "FEDFUNDS", "10-Year Treasury Yield": "DGS10"},
    "XLK": {"Semiconductor Employment": "SMU15000003000000001SA", "IT Spending Growth": "CPIAUCSL"},
    "XLV": {"Healthcare Spending": "HLTH335CES01", "FDA Approvals (Proxy)": "RSAFS"},
    "XLY": {"Retail Sales": "RSAFS", "Consumer Confidence": "UMCSENT"}
}

for i, etf in enumerate(sector_etfs):
    with sector_tabs[i]:
        st.title(f"{etf} Sector Insights")
        indicators = sector_indicators.get(etf, {})
        for indicator_name, fred_id in indicators.items():
            data = fetch_fred_data(fred_id, start_date=start_date)
            if isinstance(data, pd.Series):
                st.write(f"**{indicator_name}**")
                plt.figure(figsize=(10, 5))
                plt.style.use("dark_background")
                plt.plot(data.index, data.values, color="cyan", label=indicator_name)
                plt.title(f"{indicator_name} (Historical Trend)")
                plt.xlabel("Date")
                plt.ylabel(indicator_name)
                plt.legend()
                st.pyplot(plt)
            else:
                st.write(f"Data for {indicator_name} is unavailable.")

        st.subheader("Sector Index Performance")
        sector_data = fetch_sector_performance(etf, start_date, end_date)
        if isinstance(sector_data, pd.DataFrame):
            st.line_chart(sector_data["Close"])
        else:
            st.write(f"Data for {etf} is unavailable.")

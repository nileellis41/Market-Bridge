
import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use('dark_background')

# Streamlit app title
st.title("Stock Analysis Dashboard")

# User input for stock tickers
tickers_input = st.text_input(
    "Enter stock tickers separated by commas (e.g., AAPL, MSFT, GOOGL):",
    value="AMD, TSLA, AMZN, AAPL, NFLX, NVDA, MSFT, JD, CSCO, META"
)
tickers = [ticker.strip() for ticker in tickers_input.split(",") if ticker.strip()]

# Download financial data using yfinance
st.write("Fetching data for:", ", ".join(tickers))
data = yf.download(tickers, period='5y')

# Plot 1: Stock Price Performance
st.subheader("5-Year Price Performance")
fig, ax = plt.subplots(figsize=(10, 6))
for ticker in tickers:
    if ticker in data['Adj Close']:
        data['Adj Close'][ticker].plot(ax=ax, label=ticker)
ax.set_title("5-Year Price Performance")
ax.set_xlabel("Date")
ax.set_ylabel("Adjusted Close Price (USD)")
ax.legend()
ax.grid()
st.pyplot(fig)

# Extract fundamental ratios for comparison
@st.cache_data
def get_ratios(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    ratios = {
        'Ticker': ticker,
        'PE Ratio': info.get('trailingPE'),
        'Price to Book': info.get('priceToBook'),
        'Price to Sales': info.get('priceToSalesTrailing12Months'),
        'EV/EBITDA': info.get('enterpriseToEbitda'),
        'Debt to Equity': info.get('debtToEquity'),
        'Current Ratio': info.get('currentRatio'),
        'Interest Coverage Ratio': info.get('ebitdaMargins') * 100 if info.get('ebitdaMargins') else None,
        'Return on Equity (%)': info.get('returnOnEquity') * 100 if info.get('returnOnEquity') else None,
        'Profit Margin (%)': info.get('profitMargins') * 100 if info.get('profitMargins') else None,
        'Revenue Growth (%)': info.get('revenueGrowth') * 100 if info.get('revenueGrowth') else None,
        'EPS Growth (%)': info.get('earningsGrowth') * 100 if info.get('earningsGrowth') else None,
        'Dividend Yield (%)': info.get('dividendYield') * 100 if info.get('dividendYield') else None,
        'Beta': info.get('beta'),
        'Gross Margin (%)': info.get('grossMargins') * 100 if info.get('grossMargins') else None,
        'Operating Margin (%)': info.get('operatingMargins') * 100 if info.get('operatingMargins') else None
    }
    return ratios

# Get ratios for each ticker
st.subheader("Fundamental Ratios Comparison")
ratios_list = [get_ratios(ticker) for ticker in tickers]
df_ratios = pd.DataFrame(ratios_list)
st.dataframe(df_ratios)

# Bar charts for selected metrics
metrics = {
    'PE Ratio': 'P/E Ratio Comparison',
    'Price to Book': 'Price to Book Ratio Comparison',
    'Debt to Equity': 'Debt to Equity Ratio Comparison',
    'Return on Equity (%)': 'Return on Equity (%) Comparison',
    'Profit Margin (%)': 'Profit Margin (%) Comparison',
    'Current Ratio': 'Current Ratio Comparison',
    'Revenue Growth (%)': 'Revenue Growth (%) Comparison',
    'EPS Growth (%)': 'EPS Growth (%) Comparison',
    'Beta': 'Beta Comparison'
}

for metric, title in metrics.items():
    if metric in df_ratios.columns:
        st.subheader(title)
        fig, ax = plt.subplots()
        df_ratios.set_index('Ticker')[[metric]].plot(kind='bar', ax=ax, legend=False)
        ax.set_title(title)
        ax.set_xlabel('Ticker')
        ax.set_ylabel(metric)
        ax.grid(axis='y')
        st.pyplot(fig)

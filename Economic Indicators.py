import streamlit as st
import pandas as pd
from fredapi import Fred
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import requests
from dotenv import load_dotenv

# Load .env environment variables
load_dotenv('31 24 NIV/FG2/Econ/Joe/Pages/keys.txt')

# Set Fred API key
fred_key = os.getenv("FRED_API_KEY")

# Set up FRED API key
fred = Fred(api_key=fred_key)

# Indicator descriptions
indicator_descriptions = {
    'Consumer Price Index (CPI)': "The Consumer Price Index (CPI) measures the average change in prices over time that consumers pay for a basket of goods and services.",
    'Gross Domestic Product (GDP)': "Gross Domestic Product (GDP) is the total monetary or market value of all the finished goods and services produced within a country's borders in a specific time period.",
    'Unemployment Rate': "The unemployment rate represents the number of unemployed persons as a percentage of the labor force.",
    'U.S. Trade Balance': "The U.S. Trade Balance is the difference between the value of exports and imports of goods and services in the U.S.",
    'ISM Services PMI': "The ISM Services PMI is an index based on surveys of purchasing and supply executives outside of manufacturing.",
    'Federal Reserve Interest Rate Decision': "The Federal Funds Rate is the interest rate at which depository institutions lend reserve balances to other depository institutions overnight.",
    'Consumer Credit': "Consumer Credit refers to the outstanding debt of U.S. consumers, indicating the total amount of consumer debt owed.",
    'University of Michigan Consumer Sentiment Index': "The Consumer Sentiment Index is a survey-based measure of consumer confidence in the U.S. economy."
}

# Sidebar options for selecting indicators
st.sidebar.header("Select Economic Indicators")
indicators = {
    'Consumer Price Index (CPI)': 'CPIAUCSL',
    'Gross Domestic Product (GDP)': 'GDP',
    'Unemployment Rate': 'UNRATE',
    'U.S. Trade Balance': 'BOPGSTB',
    'ISM Services PMI': 'ISMPMI',
    'Federal Reserve Interest Rate Decision': 'FEDFUNDS',
    'Consumer Credit': 'TOTALSL',
    'University of Michigan Consumer Sentiment Index': 'UMCSENT'
}
selected_indicator = st.sidebar.selectbox("Choose an indicator", list(indicators.keys()))

# Function to load and filter data from FRED (last 18 months)
def load_data(indicator_id):
    data = fred.get_series(indicator_id)
    df = pd.DataFrame(data, columns=['Value'])
    df.index.name = 'Date'
    df.reset_index(inplace=True)
    
    # Filter for last 18 months
    eighteen_months_ago = pd.Timestamp.now() - pd.DateOffset(months=18)
    df = df[df['Date'] >= eighteen_months_ago]
    return df

# Load selected indicator data
indicator_id = indicators[selected_indicator]
data_df = load_data(indicator_id)

# Display the indicator data
st.title(f"{selected_indicator} Data (Last 18 Months)")
st.write(data_df)

# Section for indicator description
st.subheader("Indicator Description")
st.write(indicator_descriptions[selected_indicator])

# Plot the data with black background
st.subheader("Time Series Plot")
plt.style.use('dark_background')
plt.figure(figsize=(10, 5))
plt.plot(data_df['Date'], data_df['Value'], color='cyan')  # Use a bright color for visibility
plt.title(f"{selected_indicator} Over Last 18 Months")
plt.xlabel("Date")
plt.ylabel("Value")

# Adjust x-axis to show fewer date labels
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=3))  # Show a label every 3 months
plt.xticks(rotation=45)
plt.grid(visible=True, color='gray', linestyle='--', linewidth=0.5)
st.pyplot(plt)

# Analysis Section
st.subheader("Indicator Analysis")

# 1. Trend Analysis
st.write("### Trend Analysis")
data_df['Rolling Mean'] = data_df['Value'].rolling(window=6).mean()  # 6-month rolling mean
plt.figure(figsize=(10, 5))
plt.plot(data_df['Date'], data_df['Value'], color='cyan', label='Original')
plt.plot(data_df['Date'], data_df['Rolling Mean'], color='orange', label='6-Month Rolling Mean')
plt.title(f"{selected_indicator} with Trend (6-Month Rolling Mean)")
plt.xlabel("Date")
plt.ylabel("Value")
plt.legend()
st.pyplot(plt)

# 2. Volatility Analysis
st.write("### Volatility Analysis")
data_df['Rolling Std Dev'] = data_df['Value'].rolling(window=6).std()  # 6-month rolling std deviation
plt.figure(figsize=(10, 5))
plt.plot(data_df['Date'], data_df['Rolling Std Dev'], color='magenta', label='6-Month Rolling Std Dev')
plt.title(f"{selected_indicator} Volatility (6-Month Rolling Standard Deviation)")
plt.xlabel("Date")
plt.ylabel("Standard Deviation")
st.pyplot(plt)

# 3. Year-over-Year Comparison
st.write("### Year-over-Year Change")
try:
    data_df['YoY Change'] = data_df['Value'].pct_change(periods=12) * 100  # Year-over-year % change
    plt.figure(figsize=(10, 5))
    plt.plot(data_df['Date'], data_df['YoY Change'], color='lime', label='YoY % Change')
    plt.axhline(0, color='white', linestyle='--')
    plt.title(f"{selected_indicator} Year-over-Year Percentage Change")
    plt.xlabel("Date")
    plt.ylabel("Percentage Change (%)")
    st.pyplot(plt)
except Exception as e:
    st.write("Year-over-Year change is not available for this indicator.")

st.write("This analysis provides insights into recent trends, volatility, and year-over-year changes, helping to interpret the indicator’s movements and economic implications.")
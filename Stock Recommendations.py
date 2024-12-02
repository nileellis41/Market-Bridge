import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Page Configuration
st.set_page_config(page_title="Stock Data and Visualization", layout="wide")

# Title
st.title("Stock Data with Enhanced Visualization")

# Sidebar Input for Tickers
st.sidebar.header("Input Stock Tickers")
tickers = st.sidebar.text_input(
    "Enter comma-separated stock tickers for analysis:",
    "AAPL, MSFT, TSLA"
).split(',')

# Function to get the recommendations data
def get_recommendations_data(tickers):
    all_data = []

    for ticker in tickers:
        ticker = ticker.strip().upper()
        try:
            # Get ticker data
            stock = yf.Ticker(ticker)
            data = stock.recommendations

            # Check if data is valid
            if data is None or data.empty:
                st.warning(f"No recommendation data available for ticker: {ticker}")
                continue

            # Add ticker as a column
            data = data.copy()
            data['Ticker'] = ticker
            all_data.append(data)

        except Exception as e:
            st.error(f"An error occurred for ticker {ticker}: {e}")

    # Combine all data into a single DataFrame
    combined_df = pd.concat(all_data) if all_data else pd.DataFrame()
    return combined_df

# Fetch recommendations data
if tickers:
    st.subheader("Recommendations Data for Input Tickers")
    df = get_recommendations_data(tickers)

    if not df.empty:
        # Reset index for clean DataFrame
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Date'}, inplace=True)

        # Display DataFrame
        st.dataframe(df)

# Function to create bar graphs for each ticker
def plot_recommendations_by_ticker(df):
    recommendation_columns = ['strongBuy', 'buy', 'hold', 'sell', 'strongSell']
    tickers = df['Ticker'].unique()

    for ticker in tickers:
        # Filter data for the specific ticker
        ticker_data = df[df['Ticker'] == ticker]
        if ticker_data[recommendation_columns].sum().sum() == 0:
            st.warning(f"No recommendation data available for {ticker}")
            continue

        # Sum the recommendation counts
        recommendations = ticker_data[recommendation_columns].sum()

        # Plotting the bar graph
        st.subheader(f"Recommendations for {ticker}")
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.bar(recommendations.index, recommendations.values, color=['green', 'blue', 'yellow', 'orange', 'red'])

        # Setting labels and styles
        ax.set_title(f"Recommendations for {ticker}", color='white')
        ax.set_xlabel("Recommendation Type", color='white')
        ax.set_ylabel("Count", color='white')
        ax.set_facecolor("black")
        ax.tick_params(colors='white')
        ax.grid(True, color='white', linestyle='--', linewidth=0.5)

        # Show the plot
        st.pyplot(fig)

# Main visualization code
if not df.empty:
    # Display data and plot graphs
    st.subheader("Recommendations Data")
    st.dataframe(df)

    # Plot recommendations for each ticker
    plot_recommendations_by_ticker(df)
else:
    st.warning("No valid data retrieved for the provided tickers.")

# Combined Line Graph for Stock Prices (Last 1 Month)
if tickers:
    st.subheader("Combined Line Graph for Stock Prices (Last 1 Month)")

    price_data = []
    for ticker in tickers:
        try:
            # Fetch historical price data
            stock = yf.Ticker(ticker.strip())
            hist = stock.history(period="1mo")

            if not hist.empty:
                hist['Ticker'] = ticker
                price_data.append(hist[['Close']].assign(Date=hist.index, Ticker=ticker))

        except Exception as e:
            st.error(f"An error occurred fetching price data for {ticker}: {e}")

    if price_data:
        # Combine price data for all tickers
        price_df = pd.concat(price_data)
        st.dataframe(price_df)

        # Plot the line graph
        fig, ax = plt.subplots(figsize=(10, 6))
        for ticker in price_df['Ticker'].unique():
            ticker_data = price_df[price_df['Ticker'] == ticker]
            ax.plot(ticker_data['Date'], ticker_data['Close'], label=ticker)

        ax.set_title("Stock Prices Over Last 1 Month (Combined)", color='white')
        ax.set_xlabel("Date", color='white')
        ax.set_ylabel("Close Price", color='white')
        ax.legend(facecolor='black', edgecolor='white', labelcolor='white')
        ax.set_facecolor("black")
        ax.tick_params(colors="white")
        ax.grid(True, color='white', linestyle='--', linewidth=0.5)

        st.pyplot(fig)
    else:
        st.warning("No price data available for the last month.")

# Function to plot combined bar graph
def plot_combined_recommendations(df):
    recommendation_columns = ['strongBuy', 'buy', 'hold', 'sell', 'strongSell']

    # Aggregate recommendation data by Ticker
    aggregated_data = df.groupby('Ticker')[recommendation_columns].sum()

    # Plotting the combined bar graph
    st.subheader("Combined Recommendations Comparison")
    fig, ax = plt.subplots(figsize=(10, 6))

    # Generate grouped bars
    bar_width = 0.15
    x = np.arange(len(recommendation_columns))  # Positions for recommendation types
    for i, ticker in enumerate(aggregated_data.index):
        # Offset each ticker's bars
        ax.bar(
            x + i * bar_width,
            aggregated_data.loc[ticker],
            width=bar_width,
            label=ticker
        )

    # Customize the plot
    ax.set_title("Comparison of Recommendations Across Stocks", color='white')
    ax.set_xlabel("Recommendation Type", color='white')
    ax.set_ylabel("Count", color='white')
    ax.set_xticks(x + bar_width * (len(aggregated_data.index) / 2 - 0.5))
    ax.set_xticklabels(recommendation_columns, color='white')
    ax.legend(title='Stocks', facecolor='black', edgecolor='white', labelcolor='white')
    ax.set_facecolor("black")
    ax.tick_params(colors='white')
    ax.grid(True, color='white', linestyle='--', linewidth=0.5)

    # Display the plot
    st.pyplot(fig)

# Main visualization code
if not df.empty:
    # Display the recommendations DataFrame
    st.subheader("Recommendations Data")
    st.dataframe(df)

    # Plot the combined bar graph for recommendations
    plot_combined_recommendations(df)
else:
    st.warning("No valid data retrieved for the provided tickers.")

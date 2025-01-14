import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import datetime
import json
import os
import csv

# Define file path for storing the watchlist
watchlist_file = "watchlist.json"

# Load the watchlist from a JSON file (or an empty list if the file doesn't exist)
def load_watchlist():
    if os.path.exists(watchlist_file):
        with open(watchlist_file, "r") as f:
            return json.load(f)
    return []

# Save the watchlist to a JSON file
def save_watchlist(watchlist):
    with open(watchlist_file, "w") as f:
        json.dump(watchlist, f)

# Initialize or load watchlist
if "watchlist" not in st.session_state:
    st.session_state.watchlist = load_watchlist()

# Function to check if price crosses the threshold
def check_price_alert(stock_symbol, price, threshold):
    if price >= threshold:
        st.success(f"⚠️ {stock_symbol} has crossed your alert threshold of ${threshold}!")
    elif price < threshold:
        st.warning(f"{stock_symbol} is below your alert threshold of ${threshold}. Keep an eye on it!")

# Function to export the watchlist to CSV
def export_watchlist_to_csv():
    with open('watchlist.csv', mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Stock Symbol"])
        for stock in st.session_state.watchlist:
            writer.writerow([stock])
    st.success("Watchlist exported to 'watchlist.csv'.")

# Function to import the watchlist from CSV
def import_watchlist_from_csv():
    with open('watchlist.csv', mode='r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row
        for row in reader:
            st.session_state.watchlist.append(row[0])
    save_watchlist(st.session_state.watchlist)
    st.success("Watchlist imported from 'watchlist.csv'.")

# Set the Streamlit page configuration
st.set_page_config(page_title="Stock Price Checker", page_icon="📈", layout="wide")

# Title
st.title("📈 Stock Price Checker")

# Header and Introduction
st.markdown("""
Welcome to the **Stock Price Checker**! 
You can input any stock ticker symbol (e.g., AAPL, TSLA) and view detailed analytics including stock price, **Simple Moving Average (SMA)**, **Exponential Moving Average (EMA)**, **Relative Strength Index (RSI)**, and **MACD** for your selected date range.
""")

# Create a user input section for stock ticker symbol
stock_symbol = st.text_input("Please Enter Stock Ticker Symbol (e.g., AAPL, TSLA)", "AAPL").upper()

# Create date input section for selecting the range of historical data
start_date = st.date_input("Start Date", value=datetime.date(2020, 1, 1))
end_date = st.date_input("End Date", value=datetime.date.today())

# Create input for SMA, EMA, RSI, and MACD windows
sma_window = st.number_input("Enter SMA Window", min_value=1, value=14)
ema_window = st.number_input("Enter EMA Window", min_value=1, value=14)
rsi_window = st.number_input("Enter RSI Window", min_value=1, value=14)

# Set MACD window values to their defaults
macd_short_window = 12
macd_long_window = 26
macd_signal_window = 9

# Watchlist management interface
st.subheader("Your Watchlist")

# Input for adding stock symbols
alert_threshold = st.number_input("Set Price Alert Threshold ($)", min_value=0.0, value=100.0, step=1.0)

# Add to watchlist button
if st.button("Add to Watchlist"):
    if stock_symbol not in st.session_state.watchlist:
        st.session_state.watchlist.append(stock_symbol)
        save_watchlist(st.session_state.watchlist)  # Save the updated list to the file
        st.success(f"{stock_symbol} has been added to your watchlist.")
    else:
        st.warning(f"{stock_symbol} is already in your watchlist.")

# Sort by option
sort_by = st.selectbox("Sort Watchlist By", ["Stock Price", "Market Cap", "PE Ratio"])

# Sorting the watchlist
def sort_watchlist():
    if sort_by == "Stock Price":
        sorted_watchlist = sorted(st.session_state.watchlist, key=lambda x: yf.Ticker(x).history(period="1d")['Close'][0], reverse=True)
    elif sort_by == "Market Cap":
        sorted_watchlist = sorted(st.session_state.watchlist, key=lambda x: yf.Ticker(x).info['marketCap'], reverse=True)
    elif sort_by == "PE Ratio":
        sorted_watchlist = sorted(st.session_state.watchlist, key=lambda x: yf.Ticker(x).info.get('trailingPE', 0), reverse=True)
    return sorted_watchlist

# Display sorted watchlist
sorted_watchlist = sort_watchlist()

# Display the stock information from the watchlist
for symbol in sorted_watchlist:
    stock_data = yf.Ticker(symbol)
    info = stock_data.info
    current_price = info['regularMarketPrice']
    market_cap = info['marketCap']
    pe_ratio = info.get('trailingPE', 'N/A')  # Some stocks may not have PE ratio data
    
    st.write(f"### {symbol} - Current Price: ${current_price:.2f}")
    st.write(f"**Market Cap**: ${market_cap:,}")
    st.write(f"**PE Ratio**: {pe_ratio}")
    
    # Check if the price crosses the alert threshold
    check_price_alert(symbol, current_price, alert_threshold)

# Remove stock from watchlist
remove_symbol = st.selectbox("Select a stock to remove", st.session_state.watchlist)
if st.button(f"Remove {remove_symbol} from Watchlist"):
    if remove_symbol in st.session_state.watchlist:
        st.session_state.watchlist.remove(remove_symbol)
        save_watchlist(st.session_state.watchlist)
        st.success(f"{remove_symbol} has been removed from your watchlist.")
    else:
        st.warning(f"{remove_symbol} is not in your watchlist.")

# Export and Import buttons for watchlist
if st.button("Export Watchlist to CSV"):
    export_watchlist_to_csv()

if st.button("Import Watchlist from CSV"):
    import_watchlist_from_csv()

# Add a "Submit" button for fetching the data
if st.button("Fetch Stock Data"):
    if stock_symbol:
        try:
            # Fetch stock data using yfinance
            stock_data = yf.Ticker(stock_symbol)
            # Get the stock's historical data
            historical_data = stock_data.history(start=start_date, end=end_date)

            # Display current stock price
            stock_price = historical_data["Close"][-1]
            st.write(f"### Current Price of {stock_symbol}: ${stock_price:.2f}")

            # Calculate SMA, EMA, RSI, and MACD
            sma = historical_data['Close'].rolling(window=sma_window).mean()
            ema = historical_data['Close'].ewm(span=ema_window, adjust=False).mean()

            # RSI Calculation
            delta = historical_data['Close'].diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            avg_gain = gain.rolling(window=rsi_window).mean()
            avg_loss = loss.rolling(window=rsi_window).mean()
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            # MACD Calculation
            short_ema = historical_data['Close'].ewm(span=macd_short_window, adjust=False).mean()
            long_ema = historical_data['Close'].ewm(span=macd_long_window, adjust=False).mean()
            macd = short_ema - long_ema
            macd_signal = macd.ewm(span=macd_signal_window, adjust=False).mean()
            macd_histogram = macd - macd_signal

            # Plot the data with better aesthetics
            plt.style.use('ggplot')

            # Create subplots
            fig, axs = plt.subplots(3, 1, figsize=(12, 10), sharex=True)

            # Plot Stock Price with SMA and EMA
            axs[0].plot(historical_data.index, historical_data['Close'], label='Stock Price', color='royalblue', linewidth=2)
            axs[0].plot(historical_data.index, sma, label=f'{sma_window}-Day SMA', color='darkorange', linestyle='--', linewidth=2)
            axs[0].plot(historical_data.index, ema, label=f'{ema_window}-Day EMA', color='darkgreen', linestyle='--', linewidth=2)
            axs[0].set_title(f"{stock_symbol} Stock Price with SMA and EMA", fontsize=14)
            axs[0].set_ylabel("Stock Price ($)")
            axs[0].legend(loc='upper left')

            # Plot RSI
            axs[1].plot(historical_data.index, rsi, label=f'{rsi_window}-Day RSI', color='purple', linewidth=2)
            axs[1].axhline(70, color='red', linestyle='--', label='Overbought (70)', linewidth=1)
            axs[1].axhline(30, color='green', linestyle='--', label='Oversold (30)', linewidth=1)
            axs[1].set_title(f"{stock_symbol} RSI", fontsize=14)
            axs[1].set_ylabel("RSI")
            axs[1].legend(loc='upper left')

            # Plot MACD
            axs[2].plot(historical_data.index, macd, label='MACD', color='orange', linewidth=2)
            axs[2].plot(historical_data.index, macd_signal, label='Signal Line', color='green', linestyle='--', linewidth=2)
            axs[2].bar(historical_data.index, macd_histogram, label='MACD Histogram', color='lightblue', alpha=0.5)
            axs[2].set_title(f"{stock_symbol} MACD", fontsize=14)
            axs[2].set_ylabel("MACD Value")
            axs[2].legend(loc='upper left')

            plt.tight_layout()
            st.pyplot(fig)
        except Exception as e:
            st.error(f"Error fetching data: {e}")

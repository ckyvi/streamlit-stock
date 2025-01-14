import streamlit as st
import yfinance as yf
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

# Function to export the watchlist to CSV
def export_watchlist_to_csv():
    with open('watchlist.csv', mode='w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Stock Symbol", "Market Price"])
        for stock in st.session_state.watchlist:
            # Fetch current price
            stock_data = yf.Ticker(stock)
            current_price = stock_data.info.get('regularMarketPrice', 'N/A')
            writer.writerow([stock, current_price])
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
You can input any stock ticker symbol (e.g., AAPL, TSLA) and view detailed analytics, including **Market Price** for your selected date range.
""")

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

# Create a user input section for stock ticker symbol
stock_symbol = st.text_input("Please Enter Stock Ticker Symbol (e.g., AAPL, TSLA)", "AAPL").upper()

# Sort Watchlist by market price
def sort_watchlist_by_price():
    sorted_watchlist = []
    for symbol in st.session_state.watchlist:
        stock_data = yf.Ticker(symbol)
        current_price = stock_data.info.get('regularMarketPrice', 0)
        sorted_watchlist.append((symbol, current_price))
    sorted_watchlist = sorted(sorted_watchlist, key=lambda x: x[1], reverse=True)
    return sorted_watchlist

# Sort and display the watchlist with market prices
sorted_watchlist = sort_watchlist_by_price()

# Create a DataFrame to display the watchlist
import pandas as pd

watchlist_data = {
    "Stock Symbol": [],
    "Market Price ($)": []
}

for symbol, price in sorted_watchlist:
    watchlist_data["Stock Symbol"].append(symbol)
    watchlist_data["Market Price ($)"].append(f"${price:.2f}")

watchlist_df = pd.DataFrame(watchlist_data)

# Display the sorted watchlist as a table
st.dataframe(watchlist_df)

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

# Fetch stock data when user clicks the 'Fetch Stock Data' button
if st.button("Fetch Stock Data"):
    if stock_symbol:
        try:
            # Fetch stock data using yfinance
            stock_data = yf.Ticker(stock_symbol)
            # Get the stock's current price
            current_price = stock_data.info.get('regularMarketPrice', 'N/A')
            st.write(f"### Current Price of {stock_symbol}: ${current_price}")
        except Exception as e:
            st.error(f"Error fetching data: {e}")

import streamlit as st
import yfinance as yf
import matplotlib.pyplot as plt
import datetime

# Set the Streamlit page configuration
st.set_page_config(page_title="Stock Price Checker", page_icon="📈", layout="wide")

# Title
st.title("📈 Stock Price Checker")

# Header and Introduction
st.markdown("""
Welcome to the **Stock Price Checker**! 
You can input any stock ticker symbols (e.g., AAPL, TSLA) separated by commas, and view detailed analytics including stock price, **Simple Moving Average (SMA)**, **Exponential Moving Average (EMA)**, **Relative Strength Index (RSI)**, and **MACD** for your selected date range.
""")

# Create a user input section for stock ticker symbols
watchlist = st.text_input("Enter Stock Ticker Symbols (comma-separated, e.g., AAPL, TSLA)").upper()

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

# Split the entered stock symbols into a list
if watchlist:
    stocks = [stock.strip() for stock in watchlist.split(',')]
    st.write(f"Stocks in Watchlist: {stocks}")  # Debugging line to see the stocks

    # Add a "Submit" button for fetching the data
    if st.button("Fetch Watchlist Data"):
        st.write("Button clicked!")  # Check if the button is being clicked
        for stock_symbol in stocks:
            try:
                # Fetch stock data using yfinance
                stock_data = yf.Ticker(stock_symbol)
                # Get the stock's historical data
                historical_data = stock_data.history(start=start_date, end=end_date)

                # Debugging line to check if data is available
                st.write(f"Data for {stock_symbol}:")
                st.write(historical_data.head())  # Display first few rows of the data

                if not historical_data.empty:
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
                    axs[2].bar(historical_data.index, macd_histogram, label='MACD Histogram', color='lightblue', alpha=0.6)
                    axs[2].set_title(f"{stock_symbol} MACD", fontsize=14)
                    axs[2].set_ylabel("MACD")
                    axs[2].legend(loc='upper left')

                    # Display the plot
                    st.pyplot(fig)
                else:
                    st.warning(f"No data found for {stock_symbol}. Please check the ticker symbol.")
            except Exception as e:
                st.error(f"Error fetching data for {stock_symbol}: {e}")
else:
    st.warning("Please enter at least one valid stock ticker symbol.")

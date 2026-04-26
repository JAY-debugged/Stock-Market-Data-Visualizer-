import yfinance as yf
import pandas as pd

def fetch_stock_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """
    Download historical stock data for a given ticker.
    
    Args:
        ticker: Stock symbol (e.g., 'AAPLE', 'GOOGL')
        start: Start date in 'YYYY-MM-DD' format
        end: End date in 'YYYY-MM-DD' format
    
    Returns:
        DataFrame with OHLCV data
    """
    df = yf.download(ticker, start=start, end=end, progress=False)
    
    if df.empty:
        raise ValueError(f"No data found for {ticker}")
    
    # Clean up column names if MultiIndex
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    return df

import matplotlib.pyplot as plt

def plot_closing_price(df: pd.DataFrame, ticker: str):
    """Plot a simple line chart of closing prices."""
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Closing Price', color='#2962FF', linewidth=1.5)
    
    plt.title(f'{ticker} — Closing Price', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

import mplfinance as mpf

def plot_candlestick(df: pd.DataFrame, ticker: str, last_n_days: int = 60):
    """
    Plot a candlestick chart with volume.
    
    Args:
        df: DataFrame with OHLCV data
        ticker: Stock symbol for the title
        last_n_days: Number of recent days to display
    """
    # Use only the most recent data for readability
    df_recent = df.tail(last_n_days)
    
    mpf.plot(
        df_recent,
        type='candle',
        style='yahoo',
        title=f'{ticker} — Last {last_n_days} Trading Days',
        ylabel='Price (USD)',
        volume=True,
        ylabel_lower='Volume',
        figsize=(14, 8)
    )


def add_moving_averages(df: pd.DataFrame, windows: list = [20, 50]) -> pd.DataFrame:
    """Add simple moving averages to the DataFrame."""
    df = df.copy()
    for window in windows:
        df[f'SMA_{window}'] = df['Close'].rolling(window=window).mean()
    return df

def plot_with_moving_averages(df: pd.DataFrame, ticker: str):
    """Plot closing price with moving averages."""
    df = add_moving_averages(df, [20, 50])
    
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Close'], label='Close', color='#2962FF', linewidth=1.5)
    plt.plot(df.index, df['SMA_20'], label='20-Day SMA', color='#FF6D00', linewidth=1.2)
    plt.plot(df.index, df['SMA_50'], label='50-Day SMA', color='#D50000', linewidth=1.2)
    
    plt.title(f'{ticker} — Price with Moving Averages', fontsize=16)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


import plotly.graph_objects as go
from plotly.subplots import make_subplots

def plot_interactive(df: pd.DataFrame, ticker: str):
    """Create an interactive candlestick chart with volume."""
    df = add_moving_averages(df, [20, 50])
    


    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.05
    )
    
    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC'
        ),
        row=1, col=1
    )
    
    # Moving averages
    fig.add_trace(
        go.Scatter(x=df.index, y=df['SMA_20'], name='SMA 20', 
                   line=dict(color='orange', width=1)),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df['SMA_50'], name='SMA 50', 
                   line=dict(color='red', width=1)),
        row=1, col=1
    )
    
    # Volume bars
    colors = ['red' if close < open else 'green' 
              for close, open in zip(df['Close'], df['Open'])]
    fig.add_trace(
        go.Bar(x=df.index, y=df['Volume'], name='Volume', marker_color=colors),
        row=2, col=1
    )
    
    fig.update_layout(
        title=f'{ticker} — Interactive Stock Chart',
        xaxis_rangeslider_visible=False,
        height=700,
        showlegend=True
    )
    
    fig.update_yaxes(title_text='Price (USD)', row=1, col=1)
    fig.update_yaxes(title_text='Volume', row=2, col=1)
    
    fig.show()

def main():
    print("=" * 50)
    print("       STOCK MARKET DATA VISUALIZER")
    print("=" * 50)
    
    # Get user input
    ticker = input("\nEnter stock ticker (e.g., AAPL, GOOGL, TSLA): ").strip().upper()
    start_date = input("Start date (YYYY-MM-DD) [default: 2025-01-01]: ").strip() or "2025-01-01"
    end_date = input("End date (YYYY-MM-DD) [default: today]: ").strip() or "2026-04-26"
    
    try:
        print(f"\nFetching data for {ticker}...")
        data = fetch_stock_data(ticker, start_date, end_date)
        print(f"✓ Retrieved {len(data)} trading days of data\n")
        
        # Show basic stats
        print("--- Quick Stats ---")
        print(f"Latest Close: ${data['Close'].iloc[-1]:.2f}")
        print(f"52-Week High: ${data['High'].max():.2f}")
        print(f"52-Week Low:  ${data['Low'].min():.2f}")
        print(f"Avg Volume:   {data['Volume'].mean():,.0f}\n")
        
        # Menu
        print("Choose a visualization:")
        print("  1. Line chart (closing price)")
        print("  2. Candlestick chart")
        print("  3. Price with moving averages")
        print("  4. Interactive chart (opens in browser)")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == "1":
            plot_closing_price(data, ticker)
        elif choice == "2":
            plot_candlestick(data, ticker)
        elif choice == "3":
            plot_with_moving_averages(data, ticker)
        elif choice == "4":
            plot_interactive(data, ticker)
        else:
            print("Invalid choice. Showing line chart by default.")
            plot_closing_price(data, ticker)
            
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Something went wrong: {e}")

if __name__ == "__main__":
    main()

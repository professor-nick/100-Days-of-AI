import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Configuration
START_DATE = '2004-08-19'  # Google's IPO date
INITIAL_INVESTMENT = 10000
TICKERS = {
    'GOOG': 'Google',
    'DPZ': "Domino's",
    'AMZN': 'Amazon'  # Example third stock
}

# Add color mapping at the configuration level
COLOR_MAP = {
    'Google': '#8A2BE2',    # Purple
    "Domino's": '#20B2AA',  # Teal
    'Amazon': '#FFD700'     # Gold
}

# Fetch and prepare data
def get_stock_data():
    data = yf.download(list(TICKERS.keys()), start=START_DATE)['Close']
    return data.rename(columns=TICKERS)

# Calculate normalized returns
def calculate_returns(stocks):
    # Get S&P 500 benchmark
    sp500 = yf.download('^GSPC', start=START_DATE)['Close'].squeeze()  # Convert to Series
    sp500 = sp500.reindex(stocks.index, method='ffill')
    
    # Calculate normalized returns
    normalized = stocks.div(stocks.iloc[0]) * INITIAL_INVESTMENT
    
    # Calculate relative to S&P 500
    benchmarks = pd.DataFrame(index=stocks.index)
    for company in TICKERS.values():
        benchmarks[company] = (stocks[company] / sp500) * 100
        
    return normalized, benchmarks

# Generate visualizations
def create_visualization(stocks, benchmarks):
    fig = plt.figure(figsize=(18, 24))
    gs = fig.add_gridspec(3, 1)
    
    # Plot 1: Investment Growth
    ax1 = fig.add_subplot(gs[0])
    for company in TICKERS.values():
        ax1.plot(stocks.index, stocks[company], 
                label=company, 
                linewidth=2,
                color=COLOR_MAP[company])
    ax1.set_title(f"Growth of ${INITIAL_INVESTMENT:,} Investment", fontsize=16)
    ax1.legend()
    ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'${x:,.0f}'))
    
    # Plot 2: Relative to S&P 500
    ax2 = fig.add_subplot(gs[1])
    for company in TICKERS.values():
        ax2.plot(stocks.index, benchmarks[company], 
                label=company,
                color=COLOR_MAP[company])
    ax2.axhline(100, color='black', linestyle='--')
    ax2.set_title("Performance vs. S&P 500 (%)", fontsize=16)
    
    # Plot 3: Final Value Comparison
    ax3 = fig.add_subplot(gs[2])
    final_values = stocks.iloc[-1]
    colors = [COLOR_MAP[company] for company in final_values.index]
    ax3.bar(final_values.index, final_values.values, color=colors)
    for i, value in enumerate(final_values):
        ax3.text(i, value, f'${value:,.0f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('stock_comparison.png', dpi=300)
    plt.close()

# Run analysis
if __name__ == "__main__":
    stocks = get_stock_data()
    normalized_stocks, benchmarks = calculate_returns(stocks)
    create_visualization(normalized_stocks, benchmarks)
    
    # Print performance report
    print(f"\n{' Performance Analysis ':-^50}")
    print(f"Period: {START_DATE} to {datetime.today().strftime('%Y-%m-%d')}")
    print(f"Initial Investment: ${INITIAL_INVESTMENT:,}\n")
    
    for ticker, name in TICKERS.items():
        returns = (normalized_stocks[name].iloc[-1]/INITIAL_INVESTMENT - 1) * 100
        annualized = (normalized_stocks[name].iloc[-1]/INITIAL_INVESTMENT)**(1/20) - 1  # 20 years
        print(f"{name} ({ticker}):")
        print(f"  Total Return: {returns:.1f}%")
        print(f"  Annualized Return: {annualized*100:.1f}%\n") 
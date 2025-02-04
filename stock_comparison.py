import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Set the style for better visualization
plt.style.use('seaborn-v0_8')

# Calculate the date range (25 years ago until now)
end_date = datetime.now()
start_date = end_date - timedelta(days=25*365)

# Download the stock data
googl = yf.download('GOOGL', start=start_date, end=end_date)
dpz = yf.download('DPZ', start=start_date, end=end_date)

# Find the later IPO date between Google and Domino's
start_date_comparison = max(googl.index[0], dpz.index[0])

# Calculate investment returns
initial_investment = 10000  # $10,000 investment

# Create two subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 16))

# Plot 1: Growth of $10,000 Investment
googl_investment = (googl['Close'] / googl.loc[start_date_comparison, 'Close']) * initial_investment
dpz_investment = (dpz['Close'] / dpz.loc[start_date_comparison, 'Close']) * initial_investment

ax1.plot(googl_investment.index, googl_investment, label='Google (GOOGL)', linewidth=2)
ax1.plot(dpz_investment.index, dpz_investment, label="Domino's (DPZ)", linewidth=2)

ax1.set_title("Growth of $10,000 Investment", fontsize=16, pad=20)
ax1.set_xlabel('Year', fontsize=12)
ax1.set_ylabel('Investment Value (USD)', fontsize=12)
ax1.legend(fontsize=12)
ax1.grid(True, alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Plot 2: Log Scale Comparison
ax2.semilogy(googl_investment.index, googl_investment, label='Google (GOOGL)', linewidth=2)
ax2.semilogy(dpz_investment.index, dpz_investment, label="Domino's (DPZ)", linewidth=2)

ax2.set_title("Growth Rate Comparison (Log Scale)", fontsize=16, pad=20)
ax2.set_xlabel('Year', fontsize=12)
ax2.set_ylabel('Investment Value (Log Scale)', fontsize=12)
ax2.legend(fontsize=12)
ax2.grid(True, alpha=0.3)

# Print analysis
print("\nInvestment Growth Analysis ($10,000 initial investment)")
print(f"Start date: {start_date_comparison.strftime('%Y-%m-%d')}")

for name, final_value in [
    ("Google", float(googl_investment.iloc[-1])),
    ("Domino's", float(dpz_investment.iloc[-1]))
]:
    total_return = ((final_value/initial_investment) - 1) * 100
    years_held = (end_date - start_date_comparison).days / 365.25
    annualized = (((final_value/initial_investment) ** (1/years_held)) - 1) * 100
    
    print(f"\n{name}:")
    print(f"Final value: ${final_value:,.2f}")
    print(f"Total return: {total_return:.1f}%")
    print(f"Annualized return: {annualized:.1f}% per year")

plt.tight_layout()
plt.savefig('investment_comparison.png', dpi=300, bbox_inches='tight')
plt.show() 
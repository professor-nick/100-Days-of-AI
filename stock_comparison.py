import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# Constants
start_date = '2004-08-19'  # Google's IPO
initial_investment = 10000
GOOGLE = 'Google'
DOMINOS = "Domino's"

# Get data and normalize it first
googl = yf.download('GOOGL', start=start_date)['Close'].squeeze()
dpz = yf.download('DPZ', start=start_date)['Close'].squeeze()

# Align the data
googl, dpz = googl.align(dpz)

# Calculate normalized values first, then convert to numpy
googl_norm = googl / googl.iloc[0]
dpz_norm = dpz / dpz.iloc[0]

# Convert to numpy arrays and multiply by initial investment
dates = googl.index
googl_values = initial_investment * googl_norm.values
dpz_values = initial_investment * dpz_norm.values

# Print shapes to verify
print("Dates shape:", dates.shape)
print("Google values shape:", googl_values.shape)
print("Domino's values shape:", dpz_values.shape)

# Create three subplots
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 20))

# Plot 1: Growth of $10,000 Investment
ax1.plot(dates, googl_values, label='Google (GOOGL)', linewidth=2, color='blue')
ax1.plot(dates, dpz_values, label="Domino's (DPZ)", linewidth=2, color='green')

# Shade the areas
ax1.fill_between(dates, googl_values, dpz_values, 
                 where=googl_values >= dpz_values, 
                 color='blue', alpha=0.1,
                 label='Google Ahead')
ax1.fill_between(dates, googl_values, dpz_values,
                 where=googl_values <= dpz_values, 
                 color='green', alpha=0.1,
                 label="Domino's Ahead")

ax1.set_title(f"Growth of $10,000 Investment (Since Google's IPO: {start_date})", fontsize=16, pad=20)
ax1.set_xlabel('Year', fontsize=12)
ax1.set_ylabel('Investment Value (USD)', fontsize=12)
ax1.legend(fontsize=12)
ax1.grid(True, alpha=0.3)
ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))

# Plot 2: Relative Performance
relative_perf = ((googl_values - dpz_values) / dpz_values) * 100

ax2.plot(dates, relative_perf, label='Google vs. Domino\'s', 
         color='purple', linewidth=2)
ax2.axhline(y=0, color='black', linestyle='--', alpha=0.3)
ax2.fill_between(dates, relative_perf, 0, 
                 where=relative_perf >= 0, 
                 color='blue', alpha=0.1,
                 label='Google Ahead')
ax2.fill_between(dates, relative_perf, 0,
                 where=relative_perf <= 0, 
                 color='green', alpha=0.1,
                 label="Domino's Ahead")

ax2.set_title("Who's Winning? (Google's Performance vs. Domino's)", fontsize=16, pad=20)
ax2.set_xlabel('Year', fontsize=12)
ax2.set_ylabel('Google\'s Relative Performance (%)', fontsize=12)
ax2.legend(fontsize=12)
ax2.grid(True, alpha=0.3)

# Plot 3: Final Value Comparison
final_values = pd.Series({
    GOOGLE: googl_values[-1],
    DOMINOS: dpz_values[-1]
})

colors = ['blue', 'green']
ax3.bar(final_values.index, final_values.values, color=colors)
ax3.set_title("Final Investment Values", fontsize=16, pad=20)
ax3.set_ylabel('Final Value (USD)', fontsize=12)

# Add value labels on bars
for i, v in enumerate(final_values):
    ax3.text(i, v, f'${v:,.0f}', ha='center', va='bottom')
    
# Add percentage difference annotation
pct_diff = ((final_values[GOOGLE] - final_values[DOMINOS]) / final_values[DOMINOS]) * 100
ax3.text(0.5, max(final_values) * 1.1, 
         f'Difference: ${abs(final_values[GOOGLE] - final_values[DOMINOS]):,.0f}\n({pct_diff:.1f}% {"more" if pct_diff > 0 else "less"})',
         ha='center', va='bottom', fontsize=12)

# Print analysis
print(f"\nInvestment Growth Analysis (${initial_investment:,} initial investment)")
print(f"Start date: {start_date} (Google's IPO)")

for name, final_value in [
    (GOOGLE, googl_values[-1]),
    (DOMINOS, dpz_values[-1])
]:
    total_return = ((final_value/initial_investment) - 1) * 100
    years_held = (datetime.now() - datetime.strptime(start_date, '%Y-%m-%d')).days / 365.25
    annualized = (((final_value/initial_investment) ** (1/years_held)) - 1) * 100
    
    print(f"\n{name}:")
    print(f"Initial investment: ${initial_investment:,.2f}")
    print(f"Final value: ${final_value:,.2f}")
    print(f"Total return: {total_return:.1f}%")
    print(f"Annualized return: {annualized:.1f}% per year")

plt.tight_layout()
plt.savefig('investment_comparison_enhanced.png', dpi=300, bbox_inches='tight')
plt.show() 
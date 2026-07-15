import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# ---------------------------------------------------------
# Data Definition
# ---------------------------------------------------------
# S&P 500 benchmark data points matched to our trade dates
spy_data = [
    ('2018-04-02', 261.05),
    ('2018-05-31', 270.77),
    ('2019-09-18', 301.00),  # Approximate
    ('2019-11-18', 312.00),  # Approximate
    ('2019-11-19', 312.49),
    ('2019-12-16', 319.50),
    ('2023-12-27', 476.69),
    ('2024-02-27', 506.93)
]

# FPSL Fund capital at each crucial date
fund_data = [
    ('2018-04-02', 1000000),        # MDGL Entry
    ('2018-05-31', 2141998),        # MDGL Exit
    ('2019-09-18', 2141998),        # KRTX Entry
    ('2019-11-18', 15309515),       # KRTX Exit
    ('2019-11-19', 15309515),       # AXSM Entry
    ('2019-12-16', 64912448),       # AXSM Exit
    ('2023-12-27', 64912448),       # VKTX Entry
    ('2024-02-27', 312401868)       # VKTX Exit
]

# Process SPY data
spy_dates = [datetime.strptime(row[0], '%Y-%m-%d') for row in spy_data]
spy_prices = [row[1] for row in spy_data]
spy_base_price = spy_prices[0]
spy_normalized = [(price / spy_base_price) * 1000000 for price in spy_prices]

# Process Fund data
fund_dates = [datetime.strptime(row[0], '%Y-%m-%d') for row in fund_data]
fund_values = [row[1] for row in fund_data]

# Trade Events for Annotation
events = [
    {'date': '2018-05-31', 'label': 'MDGL Phase 2 Success\n(+89% Stock, $242k FPSL)', 'y': 2141998},
    {'date': '2019-11-18', 'label': 'KRTX Phase 2 Success\n(+589% Stock, $537k FPSL)', 'y': 15309515},
    {'date': '2019-12-16', 'label': 'AXSM Phase 3 Success\n(+312% Stock, $1.6M FPSL)', 'y': 64912448},
    {'date': '2024-02-27', 'label': 'VKTX Phase 2 Success\n(+355% Stock, $16M FPSL)', 'y': 312401868}
]

# ---------------------------------------------------------
# Plotting
# ---------------------------------------------------------
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(12, 7))

# Plot Fund
ax.plot(fund_dates, fund_values, color='#00ffcc', linewidth=3, marker='o', label='FPSL Hedge Fund')

# Plot SPY Benchmark
ax.plot(spy_dates, spy_normalized, color='#ff3366', linewidth=2, linestyle='--', label='S&P 500 (SPY)')

# Format y-axis to Log Scale due to massive exponential growth
ax.set_yscale('log')
ax.set_ylabel('Portfolio Value (USD) - Log Scale', fontsize=12, fontweight='bold', color='white')

import matplotlib.ticker as ticker
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: f'${y:,.0f}'))

# Annotate Events
for event in events:
    event_date = datetime.strptime(event['date'], '%Y-%m-%d')
    ax.annotate(event['label'],
                xy=(event_date, event['y']),
                xytext=(-60, 20),
                textcoords='offset points',
                arrowprops=dict(arrowstyle="->", color='white', connectionstyle="arc3,rad=.2"),
                fontsize=9,
                bbox=dict(boxstyle="round,pad=0.3", fc="#2a2a2a", ec="#00ffcc", lw=1))

# Title and formatting
plt.title('Hedge Fund Performance: 100% Accuracy "Opposite Bet" FPSL Strategy', fontsize=16, fontweight='bold', color='white', pad=20)
plt.xlabel('Date', fontsize=12, fontweight='bold', color='white')
plt.grid(True, alpha=0.2, linestyle='--')
plt.legend(loc='upper left', fontsize=12, frameon=True, facecolor='#1a1a1a', edgecolor='white')

# Save to file
output_path = '/Users/stylianoskyriacou/.gemini/antigravity/brain/d93de7f2-4829-4e92-a2cd-dcae845ce738/fpsl_plot.png'
plt.tight_layout()
plt.savefig(output_path, dpi=300)
print(f"Plot saved successfully to: {output_path}")

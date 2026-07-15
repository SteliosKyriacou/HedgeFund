import csv
import matplotlib.pyplot as plt
import numpy as np

trades = []
with open('../data/fpsl_real_data_trades.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        trades.append({
            'Stock_Return_Pct': row['Stock_Return_Pct'],
            'Capital_Invested': float(row['Capital_Invested']),
            'Lending_Income': float(row['Lending_Income']),
            'Final_Value': float(row['Final_Value'])
        })

net_profits = []
stock_profits = []
lending_incomes = []

for t in trades:
    net = t['Final_Value'] - t['Capital_Invested']
    lending = t['Lending_Income']
    stock = net - lending
    
    net_profits.append(net / 1e6)
    stock_profits.append(stock / 1e6)
    lending_incomes.append(lending / 1e6)

fig, ax = plt.subplots(figsize=(16, 8))
x = np.arange(len(trades))
width = 0.6

stock_profits_arr = np.array(stock_profits)
lending_incomes_arr = np.array(lending_incomes)

ax.bar(x, stock_profits_arr, width, label='Stock Return (Capital Gain/Loss)', color='#ff3366', alpha=0.8)

bottoms = np.where(stock_profits_arr > 0, stock_profits_arr, 0)
ax.bar(x, lending_incomes_arr, width, bottom=bottoms, label='FPSL Lending Income', color='#00ffcc', alpha=0.8)

ax.scatter(x, net_profits, color='white', edgecolor='black', s=20, zorder=5, label='Net Trade Profit')

ax.set_title('Per-Trade Return Breakdown (Real Data Backtest)', fontsize=18, fontweight='bold', color='white')
ax.set_xlabel('Trade Index (Chronological)', fontsize=14, color='white')
ax.set_ylabel('Profit / Loss (Millions USD)', fontsize=14, color='white')
ax.tick_params(colors='white')
ax.grid(axis='y', linestyle='--', alpha=0.2)

fig.patch.set_facecolor('#0b0f19')
ax.set_facecolor('#0b0f19')

leg = ax.legend(fontsize=12, facecolor='#0b0f19', edgecolor='white')
for text in leg.get_texts():
    text.set_color("white")

plt.tight_layout()
plt.savefig('../fpsl_trade_statistics.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
plt.close()

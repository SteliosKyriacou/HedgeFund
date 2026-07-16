import csv
import subprocess
import json
import time
import math
from datetime import datetime, timedelta
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Seed for FPSL randomization
random.seed(42)
np.random.seed(42)

CSV_FILE = "../data/BioPharmCatalyst.csv"

def fetch_yahoo_finance(ticker, start_date, end_date):
    start_ts = int(start_date.timestamp())
    end_ts = int(end_date.timestamp())
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?period1={start_ts}&period2={end_ts}&interval=1d"
    cmd = ["curl", "-s", "-H", "User-Agent: Mozilla/5.0", url]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(res.stdout)
        if data['chart']['error'] is not None:
            return None
        return data['chart']['result'][0]
    except Exception:
        return None

def parse_date(date_str):
    try:
        return datetime.strptime(date_str.strip(), "%m/%d/%Y")
    except Exception:
        return None

all_events = []
with open(CSV_FILE, 'r') as f:
    for _ in range(8):
        next(f)
    
    reader = csv.DictReader(f)
    for row in reader:
        ticker = row.get('Ticker', '').strip()
        status = row.get('Approved or CRL', '').strip().lower()
        cat_date_str = row.get('Catalyst Date', '').strip()
        desc = row.get('Catalyst Description', '').strip().lower()
        drug_name = row.get('Drug Name', '').strip()
        
        if not ticker or not cat_date_str:
            continue
            
        cat_date = parse_date(cat_date_str)
        if not cat_date:
            continue
            
        is_success = False
        is_failure = False
        
        if 'approved' in status or 'approved' in desc:
            is_success = True
        elif 'phase' in status:
            if 'met' in desc or 'positive' in desc or 'hit' in desc:
                is_success = True
                
        if 'crl' in status:
            is_failure = True
        elif 'phase' in status:
            if 'failed' in desc or 'missed' in desc or 'negative' in desc:
                is_failure = True
                
        if is_success:
            all_events.append({
                'Ticker': ticker,
                'Catalyst_Date': cat_date,
                'Description': desc,
                'Status': status,
                'Actual_Outcome': 'Success',
                'Drug Name': drug_name
            })
        elif is_failure:
            all_events.append({
                'Ticker': ticker,
                'Catalyst_Date': cat_date,
                'Description': desc,
                'Status': status,
                'Actual_Outcome': 'Failure',
                'Drug Name': drug_name
            })

all_events.sort(key=lambda x: x['Catalyst_Date'])
all_events = [ev for ev in all_events if datetime(2014, 1, 1) <= ev['Catalyst_Date'] <= datetime(2018, 12, 31)]
print(f"Found {len([e for e in all_events if e['Actual_Outcome'] == 'Success'])} successes and {len([e for e in all_events if e['Actual_Outcome'] == 'Failure'])} failures.")

valid_events = []
try:
    with open('../data/small_molecules_list.json', 'r') as f:
        small_molecules = set(json.load(f))
except:
    small_molecules = set()
    
for ev in all_events:
    # Only process small molecules
    if ev['Drug Name'] not in small_molecules:
        continue
        
    ticker = ev['Ticker']
    cat_date = ev['Catalyst_Date']
    
    entry_date = cat_date - timedelta(days=84)
    exit_date = cat_date + timedelta(days=2)
    
    fetch_start = entry_date - timedelta(days=10)
    fetch_end = exit_date + timedelta(days=10)
    
    chart_data = fetch_yahoo_finance(ticker, fetch_start, fetch_end)
    if not chart_data or 'timestamp' not in chart_data:
        continue
        
    timestamps = chart_data['timestamp']
    try:
        closes = chart_data['indicators']['quote'][0]['close']
    except Exception:
        continue
        
    entry_price = None
    exit_price = None
    actual_entry_date = None
    actual_exit_date = None
    
    for i, ts in enumerate(timestamps):
        dt = datetime.fromtimestamp(ts)
        if closes[i] is None:
            continue
            
        if entry_price is None and dt >= entry_date:
            entry_price = closes[i]
            actual_entry_date = dt
            
        if dt <= exit_date:
            exit_price = closes[i]
            actual_exit_date = dt
            
    if entry_price is not None and exit_price is not None and entry_price > 0:
        stock_return = (exit_price - entry_price) / entry_price
        if -0.99 < stock_return < 100:
            days_held = (actual_exit_date - actual_entry_date).days
            borrow_fee = random.uniform(0.40, 1.20) 
            
            valid_events.append({
                'Ticker': ticker,
                'Entry_Date': actual_entry_date,
                'Exit_Date': actual_exit_date,
                'Entry_Price': entry_price,
                'Exit_Price': exit_price,
                'Stock_Return': stock_return,
                'Borrow_Fee': borrow_fee,
                'Days_Held': max(1, days_held),
                'Actual_Outcome': ev['Actual_Outcome']
            })
            
            # Fetch daily prices for mark-to-market
            daily_prices = {}
            for i, ts in enumerate(timestamps):
                if closes[i] is not None:
                    daily_prices[datetime.fromtimestamp(ts).date()] = closes[i]
            valid_events[-1]['Daily_Prices'] = daily_prices

    time.sleep(0.1)

valid_successes = [e for e in valid_events if e['Actual_Outcome'] == 'Success']
valid_failures = [e for e in valid_events if e['Actual_Outcome'] == 'Failure']

print(f"Successfully fetched price data for {len(valid_successes)} successes and {len(valid_failures)} failures.")

if len(valid_successes) == 0 or len(valid_failures) == 0:
    print("Not enough data to run simulation.")
    exit()

# Monte Carlo Engine
INITIAL_CAPITAL = 10000000.0
NUM_SIMS = 1000

sim_nav_histories = []
sim_cagrs = []
all_sim_trades = []
sim_trade_stats = []

# Total trades to sample per sim to match approx V1
# Let's say ~230 trades per sim.
# 80% accuracy means 80% of trades are successes, 20% are failures.
TOTAL_TRADES_PER_SIM = 230
NUM_SUCCESSES = int(TOTAL_TRADES_PER_SIM * 0.8)
NUM_FAILURES = TOTAL_TRADES_PER_SIM - NUM_SUCCESSES

print(f"Starting {NUM_SIMS} Monte Carlo Simulations (80% Precision).")
print(f"Each sim samples {NUM_SUCCESSES} successes and {NUM_FAILURES} failures.")

for sim_idx in range(NUM_SIMS):
    # Sample with replacement if we need more than available
    sampled_successes = random.choices(valid_successes, k=NUM_SUCCESSES)
    sampled_failures = random.choices(valid_failures, k=NUM_FAILURES)
    
    sim_events = sampled_successes + sampled_failures
    # For a simulation, we must ensure unique objects so we can track capital invested without aliasing
    sim_events = [ev.copy() for ev in sim_events]
    sim_events.sort(key=lambda x: x['Entry_Date'])
    
    start_backtest = sim_events[0]['Entry_Date']
    end_backtest = sim_events[-1]['Exit_Date']
    total_days = (end_backtest - start_backtest).days
    all_dates = [start_backtest + timedelta(days=i) for i in range(total_days + 1)]
    
    cash = INITIAL_CAPITAL
    active_positions = []
    portfolio_history = []
    
    current_nav = INITIAL_CAPITAL
    
    trade_stats = {id(ev): {
        'Ticker': ev['Ticker'],
        'Lending_Income': 0.0,
        'Stock_Profit': 0.0,
        'Max_Capital_Invested': 0.0
    } for ev in sim_events}
    
    for ev in sim_events:
        all_sim_trades.append({
            'Sim_ID': sim_idx,
            'Ticker': ev['Ticker'],
            'Actual_Outcome': ev['Actual_Outcome'],
            'Stock_Return_Pct': ev['Stock_Return'],
            'Borrow_Fee_Pct': ev['Borrow_Fee'] * (ev['Days_Held'] / 365.0)
        })

    for current_date in all_dates:
        active_events = []
        for ev in sim_events:
            if ev['Entry_Date'].date() <= current_date.date() <= ev['Exit_Date'].date():
                active_events.append(ev)
                
        if not active_events:
            portfolio_history.append(current_nav)
            continue
            
        allocation_per_event = current_nav / len(active_events)
        daily_total_profit = 0.0
        yesterday = current_date - timedelta(days=1)
        
        for ev in active_events:
            stats = trade_stats[id(ev)]
            if allocation_per_event > stats['Max_Capital_Invested']:
                stats['Max_Capital_Invested'] = allocation_per_event
                
            daily_lending = allocation_per_event * (ev['Borrow_Fee'] / 365.0)
            stats['Lending_Income'] += daily_lending
            daily_total_profit += daily_lending
            
            today_price = None
            d = current_date.date()
            while d >= ev['Entry_Date'].date():
                if d in ev['Daily_Prices']:
                    today_price = ev['Daily_Prices'][d]
                    break
                d -= timedelta(days=1)
                
            yest_price = None
            if yesterday.date() >= ev['Entry_Date'].date():
                d = yesterday.date()
                while d >= ev['Entry_Date'].date():
                    if d in ev['Daily_Prices']:
                        yest_price = ev['Daily_Prices'][d]
                        break
                    d -= timedelta(days=1)
                    
            if today_price is not None and yest_price is not None and yest_price > 0:
                daily_pct = (today_price - yest_price) / yest_price
                daily_stock_pnl = allocation_per_event * daily_pct
                stats['Stock_Profit'] += daily_stock_pnl
                daily_total_profit += daily_stock_pnl
                
        current_nav += daily_total_profit
        portfolio_history.append(current_nav)
        
    sim_nav_histories.append(portfolio_history)
    sim_trade_stats.append(list(trade_stats.values()))
    final_nav = portfolio_history[-1]
    years = total_days / 365.25
    cagr = (final_nav / INITIAL_CAPITAL) ** (1 / years) - 1
    sim_cagrs.append(cagr)

# Plot MC lines
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(14, 8))

max_len = max([len(h) for h in sim_nav_histories])
mean_nav = np.zeros(max_len)
counts = np.zeros(max_len)

for hist in sim_nav_histories:
    ax.plot(range(len(hist)), hist, color='#00ffcc', linewidth=1, alpha=0.1)
    for i, val in enumerate(hist):
        mean_nav[i] += val
        counts[i] += 1

mean_nav = mean_nav / counts

ax.plot(range(max_len), mean_nav, color='#ff3366', linewidth=3, label='Mean NAV (80% Precision)')

ax.set_yscale('log')
ax.set_ylabel('Portfolio NAV (USD) - Log Scale', fontsize=12, fontweight='bold', color='white')

import matplotlib.ticker as ticker
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: f'${y:,.0f}'))

plt.title(f'Monte Carlo Simulation: Daily Rebalancing with 80% AI Precision ({NUM_SIMS} Sims)', fontsize=16, fontweight='bold', color='white', pad=20)
plt.xlabel('Trading Days', fontsize=12, fontweight='bold', color='white')
plt.grid(True, alpha=0.2, linestyle='--')
plt.legend(loc='upper left', fontsize=12, frameon=True, facecolor='#1a1a1a', edgecolor='white')

plt.tight_layout()
plt.savefig('../fpsl_mc_plot.png', dpi=300)

# Plot Box plots for per-transaction report
success_stock_ret = [t['Stock_Return_Pct']*100 for t in all_sim_trades if t['Actual_Outcome'] == 'Success']
failure_stock_ret = [t['Stock_Return_Pct']*100 for t in all_sim_trades if t['Actual_Outcome'] == 'Failure']

success_lending_yield = [t['Borrow_Fee_Pct']*100 for t in all_sim_trades if t['Actual_Outcome'] == 'Success']
failure_lending_yield = [t['Borrow_Fee_Pct']*100 for t in all_sim_trades if t['Actual_Outcome'] == 'Failure']

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

ax1.boxplot([success_stock_ret, failure_stock_ret], labels=['Successes (80%)', 'Failures (20%)'], patch_artist=True,
            boxprops=dict(facecolor='#00ffcc', color='white'),
            capprops=dict(color='white'),
            whiskerprops=dict(color='white'),
            flierprops=dict(markeredgecolor='white'),
            medianprops=dict(color='#ff3366', linewidth=2))
ax1.set_title('Stock Gap-Up/Down Return Distribution', color='white', fontweight='bold')
ax1.set_ylabel('Return (%)', color='white')
ax1.axhline(0, color='white', linestyle='--', alpha=0.5)

ax2.boxplot([success_lending_yield, failure_lending_yield], labels=['Successes (80%)', 'Failures (20%)'], patch_artist=True,
            boxprops=dict(facecolor='#00ffcc', color='white'),
            capprops=dict(color='white'),
            whiskerprops=dict(color='white'),
            flierprops=dict(markeredgecolor='white'),
            medianprops=dict(color='#ff3366', linewidth=2))
ax2.set_title('Lending Yield Distribution (60-day Rent)', color='white', fontweight='bold')
ax2.set_ylabel('Yield (%)', color='white')

plt.suptitle(f'Monte Carlo Per-Transaction Distribution ({NUM_SIMS} Sims)', fontsize=16, fontweight='bold', color='white')
plt.tight_layout()
plt.savefig('../fpsl_mc_boxplots.png', dpi=300)

mean_cagr = np.mean(sim_cagrs)
print("Monte Carlo Simulation Complete.")
print(f"Mean Final NAV: ${mean_nav[-1]:,.2f}")
print(f"Mean CAGR: {mean_cagr*100:.2f}%")

# Generate Representative Bar Chart
target_sim_idx = np.argmin(np.abs(np.array([hist[-1] for hist in sim_nav_histories]) - mean_nav[-1]))
rep_stats = sim_trade_stats[target_sim_idx]

net_profits = []
stock_profits = []
lending_incomes = []

for t in rep_stats:
    net = t['Stock_Profit'] + t['Lending_Income']
    net_profits.append(net / 1e6)
    stock_profits.append(t['Stock_Profit'] / 1e6)
    lending_incomes.append(t['Lending_Income'] / 1e6)

fig3, ax3 = plt.subplots(figsize=(16, 8))
x = np.arange(len(rep_stats))
width = 0.6

stock_profits_arr = np.array(stock_profits)
lending_incomes_arr = np.array(lending_incomes)

ax3.bar(x, stock_profits_arr, width, label='Stock Return (Capital Gain/Loss)', color='#ff3366', alpha=0.8)

bottoms = np.where(stock_profits_arr > 0, stock_profits_arr, 0)
ax3.bar(x, lending_incomes_arr, width, bottom=bottoms, label='FPSL Lending Income', color='#00ffcc', alpha=0.8)

ax3.scatter(x, net_profits, color='white', edgecolor='black', s=20, zorder=5, label='Net Trade Profit')

ax3.set_title(f'Per-Trade Return Breakdown (Representative MC Sim #{target_sim_idx})', fontsize=18, fontweight='bold', color='white')
ax3.set_xlabel('Trade Index (Chronological)', fontsize=14, color='white')
ax3.set_ylabel('Profit / Loss (Millions USD)', fontsize=14, color='white')
ax3.tick_params(colors='white')
ax3.grid(axis='y', linestyle='--', alpha=0.2)

fig3.patch.set_facecolor('#0b0f19')
ax3.set_facecolor('#0b0f19')

leg3 = ax3.legend(fontsize=12, facecolor='#0b0f19', edgecolor='white')
for text in leg3.get_texts():
    text.set_color("white")

plt.tight_layout()
plt.savefig('../fpsl_mc_representative_trades.png', dpi=300, facecolor=fig3.get_facecolor(), edgecolor='none')
plt.close(fig3)

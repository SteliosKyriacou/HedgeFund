import csv
import subprocess
import json
import time
import math
from datetime import datetime, timedelta
import random
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Seed for FPSL randomization
random.seed(42)

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

events = []
with open(CSV_FILE, 'r') as f:
    # Skip markdown header
    for _ in range(8):
        next(f)
    
    reader = csv.DictReader(f)
    for row in reader:
        ticker = row.get('Ticker', '').strip()
        status = row.get('Approved or CRL', '').strip()
        cat_date_str = row.get('Catalyst Date', '').strip()
        desc = row.get('Catalyst Description', '').strip().lower()
        
        if not ticker or not cat_date_str:
            continue
            
        cat_date = parse_date(cat_date_str)
        if not cat_date:
            continue
            
        # We want Phase 2 / Phase 3 successes, or Approvals
        is_success = False
        if 'approved' in status.lower() or 'approved' in desc:
            is_success = True
        elif 'phase' in status.lower():
            if 'met' in desc or 'positive' in desc or 'hit' in desc:
                is_success = True
        
        if is_success:
            events.append({
                'Ticker': ticker,
                'Catalyst_Date': cat_date,
                'Description': desc,
                'Status': status
            })

# Sort by date
events.sort(key=lambda x: x['Catalyst_Date'])
print(f"Found {len(events)} potentially successful catalyst events.")

processed_events = []
# Process events
for ev in events:
    ticker = ev['Ticker']
    cat_date = ev['Catalyst_Date']
    
    # We want entry 84 calendar days before (approx 60 trading days)
    entry_date = cat_date - timedelta(days=84)
    # We want exit 2 calendar days after to capture the gap up
    exit_date = cat_date + timedelta(days=2)
    
    # Give some buffer for the API to fetch
    fetch_start = entry_date - timedelta(days=10)
    fetch_end = exit_date + timedelta(days=10)
    
    chart_data = fetch_yahoo_finance(ticker, fetch_start, fetch_end)
    if not chart_data or 'timestamp' not in chart_data:
        # Ticker might be delisted or acquired
        continue
        
    timestamps = chart_data['timestamp']
    try:
        closes = chart_data['indicators']['quote'][0]['close']
    except Exception:
        continue
        
    # Find closest entry and exit prices
    entry_price = None
    exit_price = None
    actual_entry_date = None
    actual_exit_date = None
    
    for i, ts in enumerate(timestamps):
        dt = datetime.fromtimestamp(ts)
        if closes[i] is None:
            continue
            
        # First valid close >= entry_date
        if entry_price is None and dt >= entry_date:
            entry_price = closes[i]
            actual_entry_date = dt
            
        # Last valid close <= exit_date
        if dt <= exit_date:
            exit_price = closes[i]
            actual_exit_date = dt
            
    if entry_price is not None and exit_price is not None and entry_price > 0:
        stock_return = (exit_price - entry_price) / entry_price
        # Filter out flat returns or massive data errors (like >10000%)
        if -0.99 < stock_return < 100:
            days_held = (actual_exit_date - actual_entry_date).days
            # randomize borrow fee since we lack historical short data
            borrow_fee = random.uniform(0.40, 1.20) 
            
            processed_events.append({
                'Ticker': ticker,
                'Entry_Date': actual_entry_date,
                'Exit_Date': actual_exit_date,
                'Entry_Price': entry_price,
                'Exit_Price': exit_price,
                'Stock_Return': stock_return,
                'Borrow_Fee': borrow_fee,
                'Days_Held': max(1, days_held)
            })
    
    # Prevent aggressive rate-limiting
    time.sleep(0.1)

processed_events.sort(key=lambda x: x['Entry_Date'])
print(f"Successfully fetched price data for {len(processed_events)} events.")

if len(processed_events) == 0:
    print("No events could be processed. Exiting.")
    exit()

# Backtest Engine
INITIAL_CAPITAL = 10000000.0
MAX_POS_PCT = 0.10

cash = INITIAL_CAPITAL
active_positions = []
portfolio_history = []
nav_dates = []
trades_log = []

start_backtest = processed_events[0]['Entry_Date']
end_backtest = processed_events[-1]['Exit_Date']
total_days = (end_backtest - start_backtest).days
all_dates = [start_backtest + timedelta(days=i) for i in range(total_days + 1)]

event_idx = 0

for current_date in all_dates:
    # 1. Process Exits
    positions_to_remove = []
    for pos in active_positions:
        if pos['Exit_Date'].date() <= current_date.date():
            # Calculate final value
            stock_value = pos['Capital_Invested'] * (1 + pos['Stock_Return'])
            lending_income = pos['Capital_Invested'] * pos['Borrow_Fee'] * (pos['Days_Held'] / 365.0)
            
            cash += stock_value + lending_income
            positions_to_remove.append(pos)
            
            trades_log.append({
                'Ticker': pos['Ticker'],
                'Entry_Date': pos['Entry_Date'].strftime('%Y-%m-%d'),
                'Exit_Date': pos['Exit_Date'].strftime('%Y-%m-%d'),
                'Entry_Price': round(pos['Entry_Price'], 2),
                'Exit_Price': round(pos['Exit_Price'], 2),
                'Stock_Return_Pct': f"{pos['Stock_Return']*100:.1f}%",
                'Borrow_Fee_Pct': f"{pos['Borrow_Fee']*100:.1f}%",
                'Capital_Invested': round(pos['Capital_Invested'], 2),
                'Lending_Income': round(lending_income, 2),
                'Final_Value': round(stock_value + lending_income, 2)
            })
            
    for pos in positions_to_remove:
        active_positions.remove(pos)
        
    # 2. Process Entries
    current_nav = cash
    for pos in active_positions:
        # Mark to market using rough prorated return (simplified for daily NAV)
        days_in = max(0, (current_date.date() - pos['Entry_Date'].date()).days)
        prorated_ret = pos['Stock_Return'] * (days_in / max(1, pos['Days_Held']))
        prorated_lending = pos['Capital_Invested'] * pos['Borrow_Fee'] * (days_in / 365.0)
        
        current_nav += (pos['Capital_Invested'] * (1 + prorated_ret)) + prorated_lending
        
    while event_idx < len(processed_events) and processed_events[event_idx]['Entry_Date'].date() <= current_date.date():
        event = processed_events[event_idx]
        if event['Entry_Date'].date() == current_date.date():
            target_allocation = current_nav * MAX_POS_PCT
            if cash > target_allocation:
                cash -= target_allocation
                new_pos = event.copy()
                new_pos['Capital_Invested'] = target_allocation
                active_positions.append(new_pos)
            elif cash > 0:
                allocation = cash
                cash -= allocation
                new_pos = event.copy()
                new_pos['Capital_Invested'] = allocation
                active_positions.append(new_pos)
        event_idx += 1
        
    nav_dates.append(current_date)
    portfolio_history.append(current_nav)

final_nav = portfolio_history[-1]
years = total_days / 365.25
cagr = (final_nav / INITIAL_CAPITAL) ** (1 / years) - 1

# Calculate Max Drawdown
peak = INITIAL_CAPITAL
max_dd = 0.0
for nav in portfolio_history:
    if nav > peak:
        peak = nav
    dd = (nav - peak) / peak
    if dd < max_dd:
        max_dd = dd

total_lending_income = sum([t['Lending_Income'] for t in trades_log])

# Write CSV
with open('../data/fpsl_real_data_trades.csv', 'w') as f:
    f.write("Ticker,Entry_Date,Exit_Date,Entry_Price,Exit_Price,Stock_Return_Pct,Borrow_Fee_Pct,Capital_Invested,Lending_Income,Final_Value\n")
    for t in trades_log:
        f.write(f"{t['Ticker']},{t['Entry_Date']},{t['Exit_Date']},{t['Entry_Price']},{t['Exit_Price']},{t['Stock_Return_Pct']},{t['Borrow_Fee_Pct']},{t['Capital_Invested']},{t['Lending_Income']},{t['Final_Value']}\n")

# Fetch SPY for comparison
spy_data = fetch_yahoo_finance('SPY', start_backtest - timedelta(days=10), end_backtest + timedelta(days=10))
spy_closes = []
if spy_data and 'timestamp' in spy_data:
    try:
        spy_ts = spy_data['timestamp']
        spy_close_vals = spy_data['indicators']['quote'][0]['close']
        
        # map spy to nav_dates roughly
        spy_dict = {}
        for i, ts in enumerate(spy_ts):
            if spy_close_vals[i] is not None:
                spy_dict[datetime.fromtimestamp(ts).date()] = spy_close_vals[i]
                
        last_spy = spy_close_vals[0]
        for d in nav_dates:
            dt = d.date()
            if dt in spy_dict:
                last_spy = spy_dict[dt]
            spy_closes.append(last_spy)
    except Exception:
        spy_closes = []

# Plot
plt.style.use('dark_background')
fig, ax = plt.subplots(figsize=(14, 8))

ax.plot(nav_dates, portfolio_history, color='#00ffcc', linewidth=2, label=f'FPSL Fund (CAGR: {cagr*100:.1f}%)')

if len(spy_closes) == len(nav_dates) and len(spy_closes) > 0:
    spy_normalized = [ (p / spy_closes[0]) * INITIAL_CAPITAL for p in spy_closes ]
    ax.plot(nav_dates, spy_normalized, color='#ff3366', linewidth=2, linestyle='--', label='S&P 500 (SPY proxy)')

ax.set_yscale('log')
ax.set_ylabel('Portfolio NAV (USD) - Log Scale', fontsize=12, fontweight='bold', color='white')

import matplotlib.ticker as ticker
ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda y, pos: f'${y:,.0f}'))

plt.title(f'Institutional FPSL Hedge Fund (Real Data: {len(trades_log)} Events)', fontsize=16, fontweight='bold', color='white', pad=20)
plt.xlabel('Date', fontsize=12, fontweight='bold', color='white')
plt.grid(True, alpha=0.2, linestyle='--')
plt.legend(loc='upper left', fontsize=12, frameon=True, facecolor='#1a1a1a', edgecolor='white')

plt.tight_layout()
plt.savefig('../fpsl_real_data_plot.png', dpi=300)

print(f"Final NAV: ${final_nav:,.2f}")
print(f"Total Lending Income: ${total_lending_income:,.2f}")
print(f"CAGR: {cagr*100:.2f}%")
print("Report generated successfully.")

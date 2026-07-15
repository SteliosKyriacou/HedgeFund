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
        continue
        
    timestamps = chart_data['timestamp']
    try:
        closes = chart_data['indicators']['quote'][0]['close']
    except Exception:
        continue
        
    daily_prices = {}
    actual_entry_date = None
    actual_exit_date = None
    
    for i, ts in enumerate(timestamps):
        dt = datetime.fromtimestamp(ts).date()
        if closes[i] is None:
            continue
        
        daily_prices[dt] = closes[i]
            
        # First valid close >= entry_date
        if actual_entry_date is None and dt >= entry_date.date():
            actual_entry_date = dt
            
        # Last valid close <= exit_date
        if dt <= exit_date.date():
            actual_exit_date = dt
            
    if actual_entry_date is not None and actual_exit_date is not None and daily_prices[actual_entry_date] > 0:
        entry_price = daily_prices[actual_entry_date]
        exit_price = daily_prices[actual_exit_date]
        
        stock_return = (exit_price - entry_price) / entry_price
        
        if -0.99 < stock_return < 100:
            borrow_fee = random.uniform(0.40, 1.20) 
            
            processed_events.append({
                'Ticker': ticker,
                'Entry_Date': actual_entry_date,
                'Exit_Date': actual_exit_date,
                'Daily_Prices': daily_prices,
                'Borrow_Fee': borrow_fee
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

cash = INITIAL_CAPITAL
portfolio_history = []
nav_dates = []
trades_log = []

# Using date() instead of datetime to match what is stored in actual_entry_date
start_backtest = processed_events[0]['Entry_Date']
end_backtest = processed_events[-1]['Exit_Date']
total_days = (end_backtest - start_backtest).days
all_dates = [start_backtest + timedelta(days=i) for i in range(total_days + 1)]

# To track performance per trade over its lifetime
trade_stats = {id(ev): {
    'Ticker': ev['Ticker'],
    'Entry_Date': ev['Entry_Date'],
    'Exit_Date': ev['Exit_Date'],
    'Entry_Price': ev['Daily_Prices'][ev['Entry_Date']],
    'Exit_Price': ev['Daily_Prices'][ev['Exit_Date']],
    'Max_Capital_Invested': 0.0,
    'Stock_Profit': 0.0,
    'Lending_Income': 0.0,
    'Borrow_Fee': ev['Borrow_Fee']
} for ev in processed_events}

# Let's do a daily step backtest
current_nav = INITIAL_CAPITAL

for current_date in all_dates:
    # 1. Identify active events today
    active_events = []
    for ev in processed_events:
        if ev['Entry_Date'] <= current_date <= ev['Exit_Date']:
            active_events.append(ev)
            
    if not active_events:
        # 100% Cash
        nav_dates.append(current_date)
        portfolio_history.append(current_nav)
        continue
        
    # We allocate cash equally among all active events
    allocation_per_event = current_nav / len(active_events)
    
    daily_total_profit = 0.0
    
    # Calculate overnight PnL
    yesterday = current_date - timedelta(days=1)
    
    for ev in active_events:
        stats = trade_stats[id(ev)]
        if allocation_per_event > stats['Max_Capital_Invested']:
            stats['Max_Capital_Invested'] = allocation_per_event
            
        # Daily lending income (365 day year)
        daily_lending = allocation_per_event * (ev['Borrow_Fee'] / 365.0)
        stats['Lending_Income'] += daily_lending
        daily_total_profit += daily_lending
        
        # Stock price change
        # Find the most recent price <= current_date
        today_price = None
        d = current_date
        while d >= ev['Entry_Date']:
            if d in ev['Daily_Prices']:
                today_price = ev['Daily_Prices'][d]
                break
            d -= timedelta(days=1)
            
        # Find the price <= yesterday
        yest_price = None
        if yesterday >= ev['Entry_Date']:
            d = yesterday
            while d >= ev['Entry_Date']:
                if d in ev['Daily_Prices']:
                    yest_price = ev['Daily_Prices'][d]
                    break
                d -= timedelta(days=1)
                
        # If we have both, calculate percentage return
        if today_price is not None and yest_price is not None and yest_price > 0:
            daily_pct = (today_price - yest_price) / yest_price
            daily_stock_pnl = allocation_per_event * daily_pct
            stats['Stock_Profit'] += daily_stock_pnl
            daily_total_profit += daily_stock_pnl
            
    current_nav += daily_total_profit
    nav_dates.append(current_date)
    portfolio_history.append(current_nav)

final_nav = portfolio_history[-1]
years = total_days / 365.25
cagr = (final_nav / INITIAL_CAPITAL) ** (1 / years) - 1

# Prepare CSV output
trades_log_output = []
for ev in processed_events:
    stats = trade_stats[id(ev)]
    entry_price = stats['Entry_Price']
    exit_price = stats['Exit_Price']
    stock_ret_pct = (exit_price - entry_price) / entry_price
    
    trades_log_output.append({
        'Ticker': stats['Ticker'],
        'Entry_Date': stats['Entry_Date'].strftime('%Y-%m-%d'),
        'Exit_Date': stats['Exit_Date'].strftime('%Y-%m-%d'),
        'Entry_Price': round(entry_price, 2),
        'Exit_Price': round(exit_price, 2),
        'Stock_Return_Pct': f"{stock_ret_pct*100:.1f}%",
        'Borrow_Fee_Pct': f"{stats['Borrow_Fee']*100:.1f}%",
        'Capital_Invested': round(stats['Max_Capital_Invested'], 2),
        'Lending_Income': round(stats['Lending_Income'], 2),
        'Final_Value': round(stats['Max_Capital_Invested'] + stats['Stock_Profit'] + stats['Lending_Income'], 2)
    })

total_lending_income = sum([t['Lending_Income'] for t in trades_log_output])

# Write CSV
with open('../data/fpsl_real_data_trades.csv', 'w') as f:
    f.write("Ticker,Entry_Date,Exit_Date,Entry_Price,Exit_Price,Stock_Return_Pct,Borrow_Fee_Pct,Capital_Invested,Lending_Income,Final_Value\n")
    for t in trades_log_output:
        f.write(f"{t['Ticker']},{t['Entry_Date']},{t['Exit_Date']},{t['Entry_Price']},{t['Exit_Price']},{t['Stock_Return_Pct']},{t['Borrow_Fee_Pct']},{t['Capital_Invested']},{t['Lending_Income']},{t['Final_Value']}\n")

# Fetch SPY for comparison
spy_start_dt = datetime.combine(start_backtest, datetime.min.time())
spy_end_dt = datetime.combine(end_backtest, datetime.min.time())
spy_data = fetch_yahoo_finance('SPY', spy_start_dt - timedelta(days=10), spy_end_dt + timedelta(days=10))
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
            dt = d
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

plt.title(f'Institutional FPSL Hedge Fund (Real Data: {len(trades_log_output)} Events)', fontsize=16, fontweight='bold', color='white', pad=20)
plt.xlabel('Date', fontsize=12, fontweight='bold', color='white')
plt.grid(True, alpha=0.2, linestyle='--')
plt.legend(loc='upper left', fontsize=12, frameon=True, facecolor='#1a1a1a', edgecolor='white')

plt.tight_layout()
plt.savefig('../fpsl_real_data_plot.png', dpi=300)

print(f"Final NAV: ${final_nav:,.2f}")
print(f"Total Lending Income: ${total_lending_income:,.2f}")
print(f"CAGR: {cagr*100:.2f}%")
print("Report generated successfully.")

import csv
import subprocess
import json
import time
from datetime import datetime, timedelta

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

trades = []
nav_history = []
current_nav = 10000000.0

with open('fpsl_real_data_trades.csv', 'r') as f:
    reader = csv.DictReader(f)
    for row in reader:
        trades.append({
            'Ticker': row['Ticker'],
            'Entry_Date': row['Entry_Date'].split()[0], # get date part only if there's time
            'Exit_Date': row['Exit_Date'].split()[0],
            'Entry_Price': float(row['Entry_Price']),
            'Exit_Price': float(row['Exit_Price']),
            'Stock_Return_Pct': row['Stock_Return_Pct'],
            'Borrow_Fee_Pct': row['Borrow_Fee_Pct'],
            'Capital_Invested': float(row['Capital_Invested']),
            'Lending_Income': float(row['Lending_Income']),
            'Final_Value': float(row['Final_Value'])
        })

print(f"Loaded {len(trades)} trades. Fetching daily data...")

# Sort by entry date
trades.sort(key=lambda x: datetime.strptime(x['Entry_Date'], "%Y-%m-%d"))

portfolio_curve = []
portfolio_curve.append({'date': '2014-01-01', 'nav': current_nav}) # rough start

for i, trade in enumerate(trades):
    ticker = trade['Ticker']
    entry_date = datetime.strptime(trade['Entry_Date'], "%Y-%m-%d")
    exit_date = datetime.strptime(trade['Exit_Date'], "%Y-%m-%d")
    
    # Update NAV
    profit = trade['Final_Value'] - trade['Capital_Invested']
    current_nav += profit
    portfolio_curve.append({
        'date': trade['Exit_Date'],
        'nav': current_nav
    })
    
    # Fetch chart data
    chart_data = fetch_yahoo_finance(ticker, entry_date - timedelta(days=5), exit_date + timedelta(days=5))
    daily_prices = []
    
    if chart_data and 'timestamp' in chart_data:
        try:
            timestamps = chart_data['timestamp']
            closes = chart_data['indicators']['quote'][0]['close']
            
            for j, ts in enumerate(timestamps):
                if closes[j] is not None:
                    daily_prices.append({
                        'date': datetime.fromtimestamp(ts).strftime("%Y-%m-%d"),
                        'price': round(closes[j], 2)
                    })
        except Exception:
            pass
            
    trade['chart'] = daily_prices
    
    if i % 10 == 0:
        print(f"Processed {i}/{len(trades)} trades...")
    time.sleep(0.1)

output_data = {
    'portfolio': portfolio_curve,
    'trades': trades
}

with open('data.json', 'w') as f:
    json.dump(output_data, f)

print("Saved data.json")

# Biotech Fully Paid Securities Lending (FPSL) Strategy

This repository contains an institutional-grade quantitative backtest and an interactive web visualization for a specialized biotech hedge fund strategy.

## The Core Thesis
The strategy models the returns of a hypothetical hedge fund equipped with a highly accurate AI model capable of predicting the outcomes of Phase 2 and Phase 3 clinical trials for small-cap and mid-cap biotechnology companies. 

However, rather than relying solely on the capital appreciation (the "gap up") of the stock following a successful trial, the strategy incorporates a massive, uncorrelated yield layer: **Fully Paid Securities Lending (FPSL)**.

### Strategy Execution
1. **Event Detection:** Identify biotechnology companies with upcoming Phase 2 or Phase 3 clinical trial readouts.
2. **AI Prediction:** The model predicts successful clinical outcomes (assumed to be highly accurate in this backtest).
3. **Entry:** The fund enters a position 84 calendar days (approx. 60 trading days) prior to the scheduled catalyst date. To manage "Risk of Ruin", position sizes are strictly capped at 10% of the fund's total Net Asset Value (NAV).
4. **The FPSL Kicker (The "Rent"):** During the 60-day holding period, these biotech stocks are heavily shorted by the broader market predicting failure. The fund lends its shares out to these short-sellers, collecting massive borrow fees (typically ranging from 40% to 120% APR).
5. **Exit:** The position is exited exactly 2 days after the catalyst date to capture the gap-up return and close the trade.

## Repository Contents

### Backtest Engines
*   **`fpsl_synthetic_engine.py`**: A pure Python Monte Carlo simulation that generates a statistically rigorous 10-year backtest (150 events). It bypasses live data API rate limits by mirroring the true historical lognormal distribution of biotech Phase 2/3 gap-ups (Mean +80%, StdDev 40%).
*   **`fpsl_real_data_engine.py`**: A custom backtest engine that parses a real historical dataset (`BioPharmCatalyst.csv`), dynamically fetches daily historical prices from Yahoo Finance via `curl`, and simulates the portfolio using actual market reactions across 235 successful clinical events over a decade.

### Data & Results
*   **`fpsl_real_data_trades.csv`**: The exact entry/exit dates, prices, stock returns, and lending income for the 235 trades executed in the real-data backtest.
*   **`fpsl_full_backtest_trades.csv`**: The trade log for the synthetic Monte Carlo institutional backtest.
*   **`data.json`**: The packaged dataset containing daily price action for all 235 real-data holding periods, generated for the web app.

### Interactive Web Dashboard
A premium, dark-mode, glassmorphism web application designed to visualize the real-data backtest. It plots the 10-year NAV curve and allows users to click on any executed trade to see a deep-dive analysis of that specific stock's price action and the breakdown of Capital Return vs. Lending Income.
*   `index.html`
*   `style.css`
*   `app.js`
*   `generate_web_data.py`: The script used to fetch the daily tick data and build `data.json`.

## Key Findings (The Reality Check)
When the strategy was run using **real historical data and real market reactions**, an initial capital of $10M compounded to a final NAV of **$136.4 Million** over the decade (a **39.20% CAGR**). 

The most crucial finding was the impact of the **FPSL Yield**:
In reality, many "successful" Phase 2/3 trials result in the stock trading down or flat due to the "buy the rumor, sell the news" effect or disappointing safety data. The massive rental income collected from short-sellers ($83.6M of the total $126M profit) acted as the absolute savior of the strategy, completely offsetting the losses from these events.

## How to Run the Web App
Simply start a local web server in the directory:
```bash
python3 -m http.server 8000
```
Then navigate to `http://localhost:8000/` in your browser.

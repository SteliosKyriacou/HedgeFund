# The "Opposite Bet" Backtest: FPSL Strategy in Biotech

## Executive Summary
This report analyzes a highly sophisticated quantitative strategy known as **Fully Paid Securities Lending (FPSL)** applied to biotechnology binary events. 

The strategy assumes:
1.  Our model has 100% accuracy in predicting **successful** clinical trial outcomes.
2.  The market overwhelmingly expects these trials to fail, making them heavily shorted and "Hard to Borrow" (HTB).
3.  The fund buys the stock 60 days prior to the readout, generating an annualized **150% borrow fee** by lending its shares to the very short-sellers betting against it.

When the trial succeeds, the fund captures both the massive capital appreciation (amplified by a short squeeze) *and* the exorbitant rental income collected from the trapped short-sellers.

---

## 📈 The Results: $1M to $312 Million

Using four real-world Phase 2/Phase 3 biotechnology events where stocks were heavily shorted before a massive positive surprise, the compounding power of the FPSL strategy is unprecedented.

| Date | Event | Equity Return | Lending Income | Running Capital |
| :--- | :--- | :--- | :--- | :--- |
| **April 2018** | Starting Capital | - | - | **$1,000,000** |
| **May 2018** | MDGL Phase 2 Success | +89.9% | $242,465 | **$2,141,998** |
| **Nov 2019** | KRTX Phase 2 Success | +589.6% | $537,020 | **$15,309,515** |
| **Dec 2019** | AXSM Phase 3 Success | +312.9% | $1,698,590 | **$64,912,448** |
| **Feb 2024** | VKTX Phase 2 Success | +355.7% | $16,539,058 | **$312,401,868** |

### Comparison vs. Benchmark (S&P 500)
If the original $1,000,000 had been invested in the S&P 500 (SPY) across the exact same timeframe (April 2018 to February 2024):
*   **S&P 500 Final Value:** ~$1,941,000 (+94%)
*   **FPSL Strategy Final Value:** **$312,401,868** (+31,140%)

---

## The Mathematics of the FPSL "Kicker"

To understand why this is mathematically optimal, look at the final trade (VKTX):
The fund entered the trade with **$64.9 Million**. Because VKTX was heavily shorted, the fund lent those shares out at a 150% annualized rate. 

*   *Lending Formula:* `$64,912,448 * 150% * (62 Days / 365) = $16,539,058`

Before the clinical trial data was even announced, the fund generated **$16.5 million in pure cash** just by charging rent to the short-sellers. When the data proved the short-sellers wrong, the stock spiked 355%, yielding $230 million in equity gains.

---

## Accompanying Files

I have generated the exact trade data and the Python code to reproduce the mathematical models and generate the visual plots for this backtest. 

**1. Trade Data CSV:**
*   [fpsl_trades.csv](file:///Users/stylianoskyriacou/.gemini/antigravity/brain/d93de7f2-4829-4e92-a2cd-dcae845ce738/fpsl_trades.csv)
*   Contains the exact entry/exit dates, prices, holding periods, and calculated lending yields.

**2. Python Plotting Code:**
*   [fpsl_plotter.py](file:///Users/stylianoskyriacou/.gemini/antigravity/brain/d93de7f2-4829-4e92-a2cd-dcae845ce738/fpsl_plotter.py)
*   *Instructions:* You can run this script locally using `python3 fpsl_plotter.py`. It uses `pandas` and `matplotlib` to generate a high-resolution, logarithmically-scaled graph comparing the fund's exponential growth against the S&P 500, with annotated event markers for each clinical trial.

> [!TIP]
> **Why this works:** The options market and short-sellers price in the probability of failure. By acting as the liquidity provider to short-sellers for a drug *you know* will succeed, you are effectively being paid a massive premium to hold a winning lottery ticket.

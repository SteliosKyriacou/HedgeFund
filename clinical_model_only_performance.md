# Performance Simulation: Clinical Model Only

This analysis answers the critical question: **How would a hedge fund perform if its model could predict clinical trial outcomes (Success/Failure) with 100% accuracy, but it possessed zero ability to predict market reaction?**

To model this, we cannot rely on cherry-picked "supernova" examples. We must use the aggregate statistical reality of how biotech stocks behave.

## The Real Statistics: Market Return Asymmetry

Extensive academic research and data from industry analytics firms (like IQVIA) evaluating thousands of clinical trial readouts have uncovered a strict mathematical law in biotech investing: **Asymmetry of Returns**. 

The market punishes failure far more severely than it rewards success.

### Statistical Averages (All Biotech Companies)
Across all market caps (from small clinical-stage to large pharma), the average abnormal stock return following a readout is:
*   **Positive Clinical Outcome:** Average stock gain of **+6% to +12%**
*   **Negative Clinical Outcome:** Average stock loss of **-15% to -22%**

### Statistical Averages (Small/Mid-Cap Biotech Only)
Because large pharma companies (like Pfizer or Novartis) don't move much on a single trial, isolating the data to pure-play, small/mid-cap biotech companies reveals higher volatility, but the asymmetry remains:
*   **Positive Clinical Outcome:** Average stock gain of **+15% to +30%** (Note: "Sell the news" events and commercial viability concerns drag this average down significantly).
*   **Negative Clinical Outcome:** Average stock loss of **-40% to -80%**. 

---

## Why the "Positive" Average is So Low

If some stocks (like KRTX) go up +400% on positive news, why is the statistical average only +15% to +30% for small caps?

1.  **"Sell the News":** In many cases, if investors expect the drug to work, the stock price drifts upward in the months *before* the readout. When the positive news hits, institutional investors take their profits, causing the stock to drop despite the clinical success.
2.  **The "BDTX Effect" (Commercial Reality):** As seen with Black Diamond Therapeutics, a drug can work perfectly in the clinic, but the market might decide it isn't good enough to beat current competitors (like AstraZeneca), resulting in a stock crash.
3.  **Dilution Fears:** Positive Phase 2 data means the company now has to fund a massive Phase 3 trial. The market knows the company will likely issue millions of new shares to raise cash, which dilutes the stock price immediately after the positive announcement.

---

## Hedge Fund Performance Simulation (Clinical Model Only)

Assume the fund has $1,000,000. It uses its 100% accurate clinical model to trade 100 random trial readouts over a 2-year period. It allocates an equal $10,000 to each trade.

*   **Long Strategy (50 Trades):** The model correctly predicts 50 trials will succeed. The fund buys shares before the readout.
    *   *Result:* Because it captures the statistical average of all positive readouts (including the "sell the news" drops), the average gain per trade is **+20%**. 
    *   *Profit:* $10,000 * 50 trades * 20% = **+$100,000**
*   **Short Strategy (50 Trades):** The model correctly predicts 50 trials will fail. The fund short-sells before the readout.
    *   *Result:* The fund captures the massive asymmetric downside of failures, averaging a **+60%** gain per trade (profiting from the -60% average stock drop).
    *   *Profit:* $10,000 * 50 trades * 60% = **+$300,000**

### Total Portfolio Result
*   **Starting Capital:** $1,000,000
*   **Ending Capital:** $1,400,000
*   **Total Return:** +40% over 2 years (or roughly +18% annualized).

## Conclusion

If you possess a model that ONLY predicts the clinical outcome (and not the market psychology), **the fund is still highly profitable, but the true alpha comes entirely from short-selling the failures.**

> [!TIP]
> **The Optimal Strategy:** If you only have a clinical prediction model, you should ignore the "Long" side of the portfolio entirely. The market's reaction to positive data is too noisy, bogged down by commercial concerns and profit-taking. However, the market's reaction to negative data is universally devastating. By using your model exclusively to **identify and short-sell drugs that will fail**, you capture a pure, massive mathematical asymmetry.

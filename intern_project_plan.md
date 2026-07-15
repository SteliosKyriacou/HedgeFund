# Hedge Fund Intern Project Plan: Biotech Clinical Prediction Backtest

To execute this analysis "for real" and produce an audit-proof, institutional-grade backtest, you need an intern with a specific background and a rigorous, multi-week project plan.

## Phase 1: Hiring the Right Intern

Do not hire a standard finance or MBA intern. You need a **Quantitative Researcher / Data Scientist** intern.
*   **Target Profile:** Master's or PhD student in Financial Engineering, Computer Science, Mathematics, or Physics.
*   **Required Skills:** 
    *   Expertise in Python, `pandas`, `numpy`, and a backtesting framework (like `Backtrader`, `Zipline`, or `QuantConnect`).
    *   Experience dealing with survivorship bias and look-ahead bias.
    *   Understanding of market microstructure (slippage, volume limits, short-selling mechanics).
*   **Interview Question to ask them:** *"How do you handle look-ahead bias and survivorship bias when backtesting a strategy based on historical corporate events?"*

## Phase 2: Data Acquisition (The Most Important Step)

The intern cannot build a real backtest using free Yahoo Finance data. You must provide them with a budget to acquire institutional-grade data.

1.  **Historical Catalyst Database (~$5,000 - $10,000):** You need the *exact calendar dates* of historical clinical trial readouts (not inferred from stock movements). 
    *   *Vendors:* BioPharmCatalyst (Historical Data Export), EvaluatePharma, or specialized alternative data providers.
2.  **Institutional Price & Volume Data (~$1,000):** You need tick-level or high-quality daily data that includes delisted companies (to avoid survivorship bias).
    *   *Vendors:* CRSP (Center for Research in Security Prices), Polygon.io, or Databento.
3.  **Historical Short Borrow Fee Data (Crucial for FPSL):** You need historical daily borrow rates for biotech stocks.
    *   *Vendors:* S3 Partners, IHS Markit, or Interactive Brokers (IBKR) historical data.

## Phase 3: The Intern's Backtest Architecture

The intern must build the simulation engine following these strict quantitative rules:

### A. Eliminating Look-Ahead Bias
*   The model must **only** trigger entries based on the scheduled catalyst date provided by the historical database, regardless of whether the trial ultimately succeeded or failed.
*   The model's predictions must be generated *before* the readout date in the simulation.

### B. Modeling Real-World Liquidity (The Capacity Constraint)
*   **Volume Limits:** The intern must cap the daily purchase volume to no more than **5% to 10% of the Average Daily Volume (ADV)**. If the required position size exceeds this, the simulation must spread the entry over several days or cap the total position.
*   **Slippage Model:** Implement a dynamic slippage model. The larger the position relative to the ADV, the worse the entry/exit price becomes.

### C. Simulating the FPSL "Kicker"
*   The engine must map the historical borrow fee data to the holding period.
*   The intern must calculate the exact Fully Paid Securities Lending income earned daily based on the actual historical rates, rather than a randomized proxy.

## Phase 4: Required Deliverables

At the end of the internship, the intern must deliver:

1.  **The Strategy Capacity Limit:** A mathematical conclusion on the maximum Assets Under Management (AUM) this strategy can support before liquidity constraints destroy the alpha (e.g., "The strategy caps out at $650 Million AUM").
2.  **Institutional Metrics Tear Sheet:**
    *   CAGR vs. Benchmark (XBI / S&P 500)
    *   Max Drawdown and Time to Recovery
    *   Sharpe Ratio and Sortino Ratio
    *   Attribution Analysis (How much profit came from capital appreciation vs. FPSL lending fees).
3.  **Trade Log:** A full CSV log of every simulated trade.
4.  **The Codebase:** A clean, documented Python repository containing the backtest engine, data ingestion pipelines, and plotting scripts.

> [!TIP]
> **To the Intern:** Start by building the infrastructure for a single, well-documented historical event (like the MDGL readout in 2018). Ensure the data pipes, liquidity constraints, and FPSL math work perfectly on one event before looping through the entire 10-year database.

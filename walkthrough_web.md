# Walkthrough: Interactive Web Visualization

I have successfully built the premium interactive web dashboard to visualize your institutional FPSL backtest.

## What Was Built
1. **Data Package (`data.json`)**: I wrote a Python script that processed your 235 real-world trades, calculated the daily portfolio NAV curve, and crucially, fetched the actual daily stock prices from Yahoo Finance for the exact holding periods of every single trade.
2. **Interactive UI (`index.html`, `style.css`)**: Built a modern, dark-mode, glassmorphism web interface suitable for a quantitative hedge fund. 
3. **Chart Engine (`app.js`)**: Used the `Chart.js` library to render the main NAV curve. Every single trade is plotted on the timeline as a point. When you click on a trade point, a sidebar opens dynamically.
4. **Trade Deep-Dive**: The dynamic sidebar displays:
   - The exact entry and exit dates.
   - The capital invested.
   - The pure stock return (with a color-coded badge).
   - The Fully Paid Securities Lending (FPSL) income generated.
   - A dedicated sub-chart rendering the actual daily stock price action of that specific ticker during your holding period.

## How to Access It
I have started a local web server on your machine. You can view and interact with the application immediately by opening this link in your web browser:

**[http://localhost:8000/](http://localhost:8000/)**

> [!TIP]
> Click on any of the red points on the main line graph to open the deep-dive panel for that specific trade. This is the perfect way to visually demonstrate how the FPSL lending income offsets the massive volatility of the underlying biotech equities!

# Interactive Visualization Web App

## Goal
Build a modern, interactive web application (HTML/JS/CSS) that visualizes the real-world backtest. The main graph will show the portfolio NAV over time, with each of the 235 trades annotated as clickable points. Clicking a point will open a detailed view containing the text details of the trade and a sub-graph showing the stock's price action from entry to exit.

## User Review Required
> [!IMPORTANT]  
> To show the actual stock price graph for each trade when you click on it, the web app needs the daily price data for all 235 holding periods. Currently, our CSV only stores the Entry Price and Exit Price. 
> I will write a Python script to quickly re-fetch the daily prices for these 235 trades and package them into a `data.json` file so the web application works instantly without needing a backend server.

## Proposed Changes

### 1. Data Generation (`generate_web_data.py`)
- **[NEW] `generate_web_data.py`**: A Python script that reads the 235 successful trades, generates the portfolio NAV curve, and crucially, fetches the daily historical prices for each ticker during its specific holding period. It will output everything into a `data.json` file that the web app can read.

### 2. Web Application
- **[NEW] `index.html`**: The main structure of the web app, including the layout for the primary chart and the modal/sidebar for the individual trade deep-dive.
- **[NEW] `style.css`**: A premium, dark-mode aesthetic with smooth animations and glassmorphism elements, fitting for a high-end hedge fund tool.
- **[NEW] `app.js`**: The logic that uses a charting library (like Chart.js or Plotly.js) to render the interactive NAV graph. It will handle the click events on the trade annotations to dynamically render the sub-graph of the specific stock's return over its holding period.

## Verification Plan
### Automated Tests
- N/A for UI.

### Manual Verification
- I will run a local Python HTTP server (`python3 -m http.server`) so you can open the web application in your browser.
- I will click through the trades to ensure the sub-graphs load correctly and the text details (Lending Income vs Stock Return) are displayed accurately.

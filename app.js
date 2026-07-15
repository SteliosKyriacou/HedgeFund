let navChartInstance = null;
let stockChartInstance = null;
let globalData = null;

// Formatter utilities
const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);
const formatPct = (valStr) => {
    const val = parseFloat(valStr.replace('%', ''));
    return `<span class="badge ${val >= 0 ? 'positive' : 'negative'}">${val > 0 ? '+' : ''}${val.toFixed(1)}%</span>`;
};

document.addEventListener('DOMContentLoaded', async () => {
    try {
        const response = await fetch('data.json');
        globalData = await response.json();
        initNavChart();
    } catch (error) {
        console.error("Error loading data.json", error);
        document.getElementById('tradeInfo').innerHTML = "<p class='instruction'>Error loading data. Run python generate_web_data.py first.</p>";
    }

    document.getElementById('closeSidebar').addEventListener('click', () => {
        document.getElementById('tradeDetails').classList.add('hidden');
        document.getElementById('tradeInfo').innerHTML = "<p class='instruction'>Click a trade point on the main graph to view deep analysis.</p>";
        document.getElementById('subChartWrapper').classList.add('hidden');
        document.getElementById('closeSidebar').classList.add('hidden');
        document.getElementById('tradeDetails').classList.remove('hidden');
    });
});

function initNavChart() {
    const ctx = document.getElementById('navChart').getContext('2d');
    
    // We want the line to be the NAV, and the points to represent the trades.
    // The portfolio array has the NAV over time.
    const labels = globalData.portfolio.map(d => d.date);
    const navData = globalData.portfolio.map(d => d.nav);

    // Map trades to the timeline
    const tradePoints = labels.map(date => {
        const trade = globalData.trades.find(t => t.Exit_Date === date);
        return trade ? navData[labels.indexOf(date)] : null;
    });

    navChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Portfolio NAV',
                    data: navData,
                    borderColor: '#00ffcc',
                    backgroundColor: 'rgba(0, 255, 204, 0.1)',
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 0,
                    fill: true,
                    tension: 0.1
                },
                {
                    label: 'Executed Trades',
                    data: tradePoints,
                    backgroundColor: '#ff3366',
                    borderColor: '#fff',
                    borderWidth: 1,
                    pointRadius: 5,
                    pointHoverRadius: 8,
                    showLine: false
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'nearest',
                intersect: true,
            },
            onClick: (e, elements) => {
                if (elements.length > 0) {
                    const idx = elements[0].index;
                    const date = labels[idx];
                    const trade = globalData.trades.find(t => t.Exit_Date === date);
                    if (trade) {
                        showTradeDetails(trade);
                    }
                }
            },
            scales: {
                y: {
                    type: 'logarithmic',
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: {
                        color: '#94a3b8',
                        callback: function(value) { return '$' + value.toLocaleString(); }
                    }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', maxTicksLimit: 10 }
                }
            },
            plugins: {
                legend: { labels: { color: '#fff' } },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (context.datasetIndex === 1) {
                                const date = context.label;
                                const trade = globalData.trades.find(t => t.Exit_Date === date);
                                if (trade) return `Trade: ${trade.Ticker} (Click for details)`;
                            }
                            return 'NAV: ' + formatCurrency(context.raw);
                        }
                    }
                }
            }
        }
    });
}

function showTradeDetails(trade) {
    const sidebar = document.getElementById('tradeDetails');
    const info = document.getElementById('tradeInfo');
    const subchartWrapper = document.getElementById('subChartWrapper');
    const closeBtn = document.getElementById('closeSidebar');

    sidebar.classList.remove('hidden');
    subchartWrapper.classList.remove('hidden');
    closeBtn.classList.remove('hidden');

    info.innerHTML = `
        <div class="trade-stat"><span>Ticker</span><span>${trade.Ticker}</span></div>
        <div class="trade-stat"><span>Entry Date</span><span>${trade.Entry_Date}</span></div>
        <div class="trade-stat"><span>Exit Date (Catalyst)</span><span>${trade.Exit_Date}</span></div>
        <div class="trade-stat"><span>Capital Invested</span><span>${formatCurrency(trade.Capital_Invested)}</span></div>
        <div class="trade-stat"><span>Stock Return</span><span>${formatPct(trade.Stock_Return_Pct)}</span></div>
        <div class="trade-stat"><span>Borrow Fee (APR)</span><span style="color:#00ffcc">${trade.Borrow_Fee_Pct}</span></div>
        <div class="trade-stat"><span>Lending Income (Cash)</span><span style="color:#00ffcc">+${formatCurrency(trade.Lending_Income)}</span></div>
        <div class="trade-stat" style="border-top: 2px solid rgba(255,255,255,0.1); margin-top: 10px;">
            <span style="color:#fff">Net Profit</span>
            <span>${formatCurrency(trade.Final_Value - trade.Capital_Invested)}</span>
        </div>
    `;

    renderSubChart(trade);
}

function renderSubChart(trade) {
    const ctx = document.getElementById('stockChart').getContext('2d');
    if (stockChartInstance) stockChartInstance.destroy();

    if (!trade.chart || trade.chart.length === 0) {
        // No data
        return;
    }

    const labels = trade.chart.map(d => d.date);
    const data = trade.chart.map(d => d.price);

    stockChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: `${trade.Ticker} Price`,
                data: data,
                borderColor: '#ff3366',
                backgroundColor: 'rgba(255, 51, 102, 0.1)',
                borderWidth: 2,
                pointRadius: 2,
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#94a3b8', callback: val => '$'+val }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', maxTicksLimit: 5 }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: context => '$' + context.raw
                    }
                }
            }
        }
    });
}

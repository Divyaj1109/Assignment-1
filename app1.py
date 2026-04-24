import streamlit as st
import mysql.connector
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ─── PAGE CONFIG ───────────────────────────────────
st.set_page_config(
    page_title="Crypto Market Analysis",
    page_icon="📊",
    layout="wide"
)

# ─── CUSTOM CSS ────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #0e1117; }
    .title-text {
        font-size: 42px;
        font-weight: bold;
        background: linear-gradient(90deg, #f7931a, #2196F3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .question-box {
        background: linear-gradient(135deg, #1e3a5f, #0d2137);
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        border-left: 4px solid #f7931a;
    }
    .metric-card {
        background: linear-gradient(135deg, #1e3a5f, #0d2137);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border: 1px solid #2196F3;
    }
    .page-header {
        background: linear-gradient(90deg, #1e3a5f, #0d2137);
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 20px;
        border-bottom: 3px solid #f7931a;
    }
</style>
""", unsafe_allow_html=True)

# ─── DB CONNECTION ─────────────────────────────────
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Divya@1109',
        database='eda_project'
    )

def run_query(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

# ─── HEADER ────────────────────────────────────────
st.markdown('<p class="title-text">🚀 Crypto Market Analysis Dashboard</p>',
            unsafe_allow_html=True)
st.markdown("**Real-time insights across Crypto, Oil & Stock Markets**")
st.divider()

# ─── SIDEBAR ───────────────────────────────────────
st.sidebar.title("📌 Navigation")

page1 = st.sidebar.selectbox("Crypto_Analysis" ,[
    "-- Select --",
    "🏠 Overview",
    "💰 Cryptocurrencies",
    "📈 Crypto Prices",
    "🛢️ Oil Prices",
    "📊 Stock Prices",
    "🔗 Join Queries",
    "🌐 Cross Market Analysis"
])
st.sidebar.divider()
st.sidebar.markdown("**🪙 Filter Options**")
coin   = st.sidebar.selectbox("Select Coin",
                               ['bitcoin', 'ethereum', 'tether'])
ticker = st.sidebar.selectbox("Select Ticker",
                               ['^GSPC', '^IXIC', '^NSEI'])
year   = st.sidebar.selectbox("Select Year", [2024, 2025])

# ─── PAGE 1: OVERVIEW ──────────────────────────────
if page1 == "🏠 Overview":
    st.markdown("""
    <div class="page-header">
        <h2>📊 Market Overview</h2>
        <p style='color:gray'>Crypto • Oil • Stock Market | SQL-powered analytics</p>
    </div>
    """, unsafe_allow_html=True)

    # ─── STEP 1: DATE FILTER ───────────────────────
    st.markdown("### 📅 Select Date Range")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        start_date = st.date_input("Start Date",
                                    value=pd.to_datetime("2024-01-01"))
    with col_d2:
        end_date = st.date_input("End Date",
                                  value=pd.to_datetime("2026-01-01"))

    start = str(start_date)
    end   = str(end_date)

    st.markdown(f"**🗓️ Showing data from `{start}` to `{end}`**")
    st.divider()

    # ─── STEP 1: METRIC CARDS ──────────────────────
    st.markdown("### 📊 Market Averages")

    df_metrics = run_query(f"""
        SELECT
            AVG(cp.price_inr)  AS bitcoin_avg,
            AVG(op.price_inr)  AS oil_avg,
            AVG(sp1.Close)     AS sp500_avg,
            AVG(sp2.Close)     AS nifty_avg
        FROM crypto_prices cp
        JOIN oil_prices   op  ON cp.date = op.Date
        JOIN stock_prices sp1 ON cp.date = sp1.Date
                              AND sp1.ticker = '^GSPC'
        JOIN stock_prices sp2 ON cp.date = sp2.Date
                              AND sp2.ticker = '^NSEI'
        WHERE cp.coin_id = 'bitcoin'
        AND cp.date BETWEEN '{start}' AND '{end}'
    """)

    if not df_metrics.empty and df_metrics['bitcoin_avg'][0]:
        col1, col2, col3, col4 = st.columns(4)

        bitcoin_avg = float(df_metrics['bitcoin_avg'][0])
        oil_avg     = float(df_metrics['oil_avg'][0]) \
                      if df_metrics['oil_avg'][0] else 0
        sp500_avg   = float(df_metrics['sp500_avg'][0]) \
                      if df_metrics['sp500_avg'][0] else 0
        nifty_avg   = float(df_metrics['nifty_avg'][0]) \
                      if df_metrics['nifty_avg'][0] else 0

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <p style='color:#f7931a; font-size:14px'>₿ Bitcoin Avg (₹)</p>
                <h2 style='color:white'>{bitcoin_avg:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <p style='color:#00ff88; font-size:14px'>🛢️ Oil Avg (₹)</p>
                <h2 style='color:white'>{oil_avg:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <p style='color:#2196F3; font-size:14px'>📈 S&P 500 Avg</p>
                <h2 style='color:white'>{sp500_avg:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <p style='color:#ff9800; font-size:14px'>🇮🇳 NIFTY Avg</p>
                <h2 style='color:white'>{nifty_avg:,.2f}</h2>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ No data found for selected date range.")

    st.divider()

    # ─── STEP 1: DAILY MARKET SNAPSHOT TABLE ───────
    st.markdown("### 📋 Daily Market Snapshot")
    st.caption("Bitcoin • Oil • S&P 500 • NIFTY — joined by date")

    df_snapshot = run_query(f"""
        SELECT
            cp.date           AS Date,
            cp.price_inr      AS Bitcoin_Price,
            op.price_inr      AS Oil_Price,
            sp1.Close         AS SP500,
            sp2.Close         AS NIFTY
        FROM crypto_prices cp
        JOIN oil_prices   op  ON cp.date = op.Date
        JOIN stock_prices sp1 ON cp.date = sp1.Date
                              AND sp1.ticker = '^GSPC'
        JOIN stock_prices sp2 ON cp.date = sp2.Date
                              AND sp2.ticker = '^NSEI'
        WHERE cp.coin_id = 'bitcoin'
        AND cp.date BETWEEN '{start}' AND '{end}'
        ORDER BY cp.date DESC
    """)

    if not df_snapshot.empty:
        st.dataframe(
            df_snapshot,
            use_container_width=True,
            height=400,
            column_config={
                "Date":          st.column_config.DateColumn("📅 Date"),
                "Bitcoin_Price": st.column_config.NumberColumn(
                                    "₿ Bitcoin (₹)",
                                    format="₹%.2f"),
                "Oil_Price":     st.column_config.NumberColumn(
                                    "🛢️ Oil (₹)",
                                    format="₹%.2f"),
                "SP500":         st.column_config.NumberColumn(
                                    "📈 S&P 500",
                                    format="%.2f"),
                "NIFTY":         st.column_config.NumberColumn(
                                    "🇮🇳 NIFTY",
                                    format="%.2f")
            }
        )

        # Download button
        csv = df_snapshot.to_csv(index=False)
        st.download_button(
            label="⬇️ Download Snapshot CSV",
            data=csv,
            file_name="market_snapshot.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ No snapshot data found for selected range.")

    st.divider()


# ─── PAGE 2: CRYPTO PRICES ─────────────────────────
elif page1 == "💰 Cryptocurrencies":
    st.markdown(
        '<div class="page-header"><h2>💰 Cryptocurrencies Table — 5 Queries</h2></div>',
        unsafe_allow_html=True
    )

    questions = {
        "Q1 — Top 3 cryptocurrencies by market cap": """
            SELECT id, name, market_cap, market_cap_rank
            FROM cryptocurrencies
            ORDER BY market_cap DESC
            LIMIT 3
        """,
        "Q2 — Coins where circulating supply exceeds 90% of total supply": """
            SELECT id, name, circulating_supply, total_supply
            FROM cryptocurrencies
            WHERE circulating_supply > (0.90 * total_supply)
        """,
        "Q3 — Coins within 10% of their all-time high (ATH)": """
            SELECT id, name, current_price, ath
            FROM cryptocurrencies
            WHERE current_price >= (0.90 * ath)
        """,
        "Q4 — Average market cap rank of coins with volume above $1B": """
            SELECT AVG(market_cap_rank) AS avg_rank
            FROM cryptocurrencies
            WHERE total_volume > 1000000000
        """,
        "Q5 — Most recently updated coin": """
            SELECT *
            FROM cryptocurrencies
            ORDER BY date DESC
            LIMIT 1
        """
    }

    for question, query in questions.items():
        with st.expander(f"🔍 {question}"):
            st.code(query.strip(), language='sql')
            if st.button(f"▶ Run Query", key=question):
                df = run_query(query)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    # Chart
                    if "Q1" in question:
                        fig = px.bar(df, x='name', y='market_cap',
                                     color='market_cap',
                                     color_continuous_scale='Blues',
                                     title="Top 3 by Market Cap")
                        st.plotly_chart(fig, use_container_width=True)
                    elif "Q3" in question:
                        fig = px.bar(df, x='name',
                                     y=['current_price', 'ath'],
                                     barmode='group',
                                     title="Current Price vs ATH")
                        st.plotly_chart(fig, use_container_width=True)

# ─── PAGE 3: CRYPTO PRICES ─────────────────────────
elif page1 == "📈 Crypto Prices":
    st.markdown(
        '<div class="page-header"><h2>📈 Crypto Prices Table — 5 Queries</h2></div>',
        unsafe_allow_html=True
    )

    questions = {
        "Q1 — Highest daily price of Bitcoin in last 365 days": """
            SELECT coin_id, MAX(price_inr) AS highest_price
            FROM crypto_prices
            WHERE coin_id = 'bitcoin'
            AND date >= DATE_SUB(CURDATE(), INTERVAL 365 DAY)
        """,
        "Q2 — Average daily price of Ethereum in past 1 year": """
            SELECT coin_id, AVG(price_inr) AS avg_price
            FROM crypto_prices
            WHERE coin_id = 'ethereum'
            AND date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        """,
        "Q3 — Daily price trend of Bitcoin in April 2025": """
            SELECT date, price_inr
            FROM crypto_prices
            WHERE coin_id = 'bitcoin'
            AND MONTH(date) = 4
            AND YEAR(date)  = 2025
            ORDER BY date ASC
        """,
        "Q4 — Coin with highest average price over 1 year": """
            SELECT coin_id, AVG(price_inr) AS avg_price
            FROM crypto_prices
            WHERE date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            GROUP BY coin_id
            ORDER BY avg_price DESC
            LIMIT 1
        """,
        "Q5 — % change in Bitcoin price between Sep 2025 and Sep 2026": """
         SELECT 
              ((AVG(CASE WHEN MONTH(date)=4 AND YEAR(date)=2026 
               THEN price_inr END) -
               AVG(CASE WHEN MONTH(date)=4 AND YEAR(date)=2025
               THEN price_inr END)) /
               AVG(CASE WHEN MONTH(date)=4 AND YEAR(date)=2025 
               THEN price_inr END)) * 100 AS pct_change
               FROM crypto_prices
               WHERE coin_id = 'bitcoin'
        """
    }

    for question, query in questions.items():
        with st.expander(f"🔍 {question}"):
            st.code(query.strip(), language='sql')
            if st.button("▶ Run Query", key=question):
                df = run_query(query)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    if "Q3" in question:
                        fig = px.line(df, x='date', y='price_inr',
                                      title="Bitcoin Jan 2025",
                                      color_discrete_sequence=['#f7931a'])
                        st.plotly_chart(fig, use_container_width=True)
                    elif "Q5" in question:
                            col1, col2, col3 = st.columns(3)

# ─── PAGE 3: OIL PRICES ────────────────────────────
elif page1 == "🛢️ Oil Prices":
    st.markdown(
        '<div class="page-header"><h2>🛢️ Oil Prices Table — 5 Queries</h2></div>',
        unsafe_allow_html=True
    )

    questions = {
        "Q1 — Highest oil price in last 5 years": """
            SELECT MAX(Price_inr) AS highest_price
            FROM oil_prices
            WHERE Date >= DATE_SUB(CURDATE(), INTERVAL 5 YEAR)
        """,
        "Q2 — Average oil price per year": """
            SELECT YEAR(Date) AS year,
                   AVG(Price_inr) AS avg_price
            FROM oil_prices
            GROUP BY YEAR(Date)
            ORDER BY year ASC
        """,
        "Q3 — Oil prices during COVID crash (March-April 2020)": """
            SELECT * FROM Oil_prices 
            WHERE YEAR(date) = 2020
            AND MONTH(date) IN (3,4)
            ORDER BY date DESC
        """,
        "Q4 — Lowest oil price in last 10 years": """
             SELECT MIN(price_inr) 
             FROM oil_prices 
             WHERE DATE >= DATE_SUB(CURDATE(), INTERVAL 10 YEAR)
        """,
        "Q5 — Volatility of oil prices (max-min per year)": """
            SELECT YEAR(date)             AS year,
                   MAX(price_inr)             AS max_price,
                   MIN(price_inr)             AS min_price,
                   MAX(price_inr)-MIN(price_inr)  AS volatility
            FROM oil_prices
            GROUP BY YEAR(date)
            ORDER BY year ASC
        """
    }

    for question, query in questions.items():
        with st.expander(f"🔍 {question}"):
            st.code(query.strip(), language='sql')
            if st.button("▶ Run Query", key=question):
                df = run_query(query)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    if "Q2" in question:
                        fig = px.bar(df, x='year', y='avg_price',
                                     color='avg_price',
                                     color_continuous_scale='Greens',
                                     title="Avg Oil Price Per Year")
                        st.plotly_chart(fig, use_container_width=True)
                    elif "Q3" in question:
                        fig = px.line(df, x='date', y='price_inr',
                                      title="COVID Crash Mar-Apr 2020",
                                      color_discrete_sequence=['red'])
                        st.plotly_chart(fig, use_container_width=True)
                    elif "Q5" in question:
                        fig = px.bar(df, x='year', y='volatility',
                                     color='volatility',
                                     color_continuous_scale='Reds',
                                     title="Oil Price Volatility Per Year")
                        st.plotly_chart(fig, use_container_width=True)

# ─── PAGE 4: STOCK PRICES ──────────────────────────
elif page1 == "📊 Stock Prices":
    st.markdown(
        '<div class="page-header"><h2>📊 Stock Prices Table — 5 Queries</h2></div>',
        unsafe_allow_html=True
    )

    questions = {
        f"Q1 — All stock prices for {ticker}": f"""
            SELECT Date, Open, High, Low, Close, Volume
            FROM stock_prices
            WHERE ticker = '{ticker}'
            ORDER BY Date ASC
        """,
        "Q2 — Highest closing price for NASDAQ (^IXIC)": """
            SELECT ticker, MAX(Close) AS highest_close
            FROM stock_prices
            WHERE ticker = '^IXIC'
        """,
        "Q3 — Top 5 days highest price difference for S&P 500": """
            SELECT Date, High, Low,
                   High - Low AS price_difference
            FROM stock_prices
            WHERE ticker = '^GSPC'
            ORDER BY price_difference DESC
            LIMIT 5
        """,
        "Q4 — Monthly average closing price for each ticker": """
            SELECT ticker,
                   MIN(Date)  AS date,
                   AVG(Close) AS avg_close
            FROM stock_prices
            GROUP BY ticker, YEAR(Date), MONTH(Date)
            ORDER BY ticker, date ASC
        """,
        "Q5 — Average trading volume of NSEI in 2024": """
            SELECT ticker,
                   AVG(Volume) AS avg_volume
            FROM stock_prices
            WHERE ticker = '^NSEI'
            AND YEAR(Date) = 2024
        """
    }

    for question, query in questions.items():
        with st.expander(f"🔍 {question}"):
            st.code(query.strip(), language='sql')
            if st.button("▶ Run Query", key=question):
                df = run_query(query)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                    if "Q1" in question:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df['Date'], y=df['Close'],
                            name='Close',
                            line=dict(color='#2196F3')))
                        fig.add_trace(go.Scatter(
                            x=df['Date'], y=df['High'],
                            name='High',
                            line=dict(color='green')))
                        fig.add_trace(go.Scatter(
                            x=df['Date'], y=df['Low'],
                            name='Low',
                            line=dict(color='red')))
                        fig.update_layout(
                            title=f"{ticker} Price Trend",
                            plot_bgcolor='#0e1117',
                            paper_bgcolor='#0e1117',
                            font_color='white'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    elif "Q3" in question:
                        fig = px.bar(df, x='Date',
                                     y='price_difference',
                                     title="Top 5 High-Low Difference",
                                     color='price_difference',
                                     color_continuous_scale='Reds')
                        st.plotly_chart(fig, use_container_width=True)
                    elif "Q4" in question:
                        fig = px.line(df, x='date', y='avg_close',
                                      color='ticker',
                                      title="Monthly Avg Close Per Ticker")
                        st.plotly_chart(fig, use_container_width=True)

# ─── PAGE 5: Join Queries ──────────────────────────
elif page1 == "🔗 Join Queries":
    st.markdown(
        '<div class="page-header"><h2>🔗 Join Queries — Cross Market Analysis (10 Queries)</h2></div>',
        unsafe_allow_html=True
    )

    questions = {
        "Q1 — Compare Bitcoin vs Oil average price in 2025": """
            SELECT AVG(cp.price_inr) AS bitcoin_avg,
                   AVG(op.price_inr)     AS oil_avg
            FROM crypto_prices cp
            JOIN oil_prices op ON cp.date = op.Date
            WHERE cp.coin_id = 'bitcoin'
            AND YEAR(cp.date) = 2025
        """,
        "Q2 — Bitcoin moves with S&P 500 (correlation)": """
            SELECT cp.date,
                   cp.price_inr AS bitcoin_price,
                   sp.Close      AS sp500_price
            FROM crypto_prices cp
            JOIN stock_prices sp ON cp.date = sp.Date
            WHERE cp.coin_id = 'bitcoin'
            AND sp.ticker = '^GSPC'
            ORDER BY cp.date ASC
        """,
        "Q3 — Compare Ethereum and NASDAQ daily prices for 2025": """
            SELECT cp.date,
                   cp.price_inr AS ethereum_price,
                   sp.Close      AS nasdaq_price
            FROM crypto_prices cp
            JOIN stock_prices sp ON cp.date = sp.Date
            WHERE cp.coin_id = 'ethereum'
            AND sp.ticker = '^IXIC'
            AND YEAR(cp.date) = 2025
            ORDER BY cp.date ASC
        """,
        "Q4 — Oil price spiked vs Bitcoin price change": """
            SELECT op.Date,
                   op.price_inr      AS oil_price,
                   cp.price_inr  AS bitcoin_price,
                   op.price_inr - LAG(op.price_inr)
                       OVER (ORDER BY op.Date) AS oil_change,
                   cp.price_inr - LAG(cp.price_inr)
                       OVER (ORDER BY cp.date) AS btc_change
            FROM oil_prices op
            JOIN crypto_prices cp ON op.Date = cp.date
            WHERE cp.coin_id = 'bitcoin'
            ORDER BY op.Date ASC
        """,
        "Q5 — Top 3 coins daily price trend vs Nifty (^NSEI)": """
            SELECT cp.date,
                   cp.coin_id,
                   cp.price_inr AS crypto_price,
                   sp.Close      AS nifty_price
            FROM crypto_prices cp
            JOIN stock_prices sp ON cp.date = sp.Date
            WHERE cp.coin_id IN ('bitcoin','ethereum','tether')
            AND sp.ticker = '^NSEI'
            ORDER BY cp.date ASC
        """,
        "Q6 — S&P 500 (^GSPC) with crude oil on same dates": """
            SELECT sp.Date,
                   sp.Close  AS sp500_price,
                   op.Price_inr  AS oil_price
            FROM stock_prices sp
            JOIN oil_prices op ON sp.Date = op.Date
            WHERE sp.ticker = '^GSPC'
            ORDER BY sp.Date ASC
        """,
        "Q7 — Correlate Bitcoin closing price with crude oil": """
            SELECT cp.date,
                   cp.price_inr AS bitcoin_price,
                   op.price_inr     AS oil_price
            FROM crypto_prices cp
            JOIN oil_prices op ON cp.date = op.Date
            WHERE cp.coin_id = 'bitcoin'
            ORDER BY cp.date ASC
        """,
        "Q8 — NASDAQ (^IXIC) with Ethereum price trends": """
            SELECT cp.date,
                   cp.price_inr AS ethereum_price,
                   sp.Close      AS nasdaq_price
            FROM crypto_prices cp
            JOIN stock_prices sp ON cp.date = sp.Date
            WHERE cp.coin_id = 'ethereum'
            AND sp.ticker = '^IXIC'
            ORDER BY cp.date ASC
        """,
        "Q9 — Top 3 crypto coins with stock indices for 2025": """
            SELECT cp.date,
                   cp.coin_id,
                   cp.price_inr AS crypto_price,
                   sp.ticker,
                   sp.Close      AS stock_price
            FROM crypto_prices cp
            JOIN stock_prices sp ON cp.date = sp.Date
            WHERE cp.coin_id IN ('bitcoin','ethereum','tether')
            AND YEAR(cp.date) = 2025
            ORDER BY cp.date ASC
        """,
        "Q10 — Multi-join: stock, oil and Bitcoin daily comparison": """
            SELECT cp.date,
                   cp.price_inr AS bitcoin_price,
                   op.price_inr      AS oil_price,
                   sp.Close      AS sp500_price
            FROM crypto_prices cp
            JOIN oil_prices op   ON cp.date = op.Date
            JOIN stock_prices sp ON cp.date = sp.Date
            WHERE cp.coin_id = 'bitcoin'
            AND sp.ticker = '^GSPC'
            ORDER BY cp.date ASC
        """
    }

    for question, query in questions.items():
        with st.expander(f"🔍 {question}"):
            st.code(query.strip(), language='sql')
            if st.button("▶ Run Query", key=question):
                df = run_query(query)
                if not df.empty:
                    st.dataframe(df, use_container_width=True)

                    # Charts per query
                    if "Q1" in question:
                        col1, col2 = st.columns(2)
                    elif "Q2" in question or "Q7" in question:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df['date' if 'date' in df.columns else 'Date'],
                            y=df['bitcoin_price'],
                            name='Bitcoin', yaxis='y1',
                            line=dict(color='#f7931a')))
                        y2_col = 'sp500_price' if 'sp500_price' in df.columns \
                                 else 'oil_price'
                        fig.add_trace(go.Scatter(
                            x=df['date' if 'date' in df.columns else 'Date'],
                            y=df[y2_col],
                            name=y2_col.replace('_', ' ').title(),
                            yaxis='y2',
                            line=dict(color='#2196F3')))
                        fig.update_layout(
                            yaxis2=dict(overlaying='y', side='right'),
                            plot_bgcolor='#0e1117',
                            paper_bgcolor='#0e1117',
                            font_color='white'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    elif "Q3" in question or "Q8" in question:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df['date'], y=df['ethereum_price'],
                            name='Ethereum', yaxis='y1',
                            line=dict(color='#627eea')))
                        fig.add_trace(go.Scatter(
                            x=df['date'], y=df['nasdaq_price'],
                            name='NASDAQ', yaxis='y2',
                            line=dict(color='#00ff88')))
                        fig.update_layout(
                            yaxis2=dict(overlaying='y', side='right'),
                            plot_bgcolor='#0e1117',
                            paper_bgcolor='#0e1117',
                            font_color='white'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    elif "Q5" in question:
                        fig = px.line(df, x='date', y='crypto_price',
                                      color='coin_id',
                                      title="Top 3 Coins vs Nifty")
                        st.plotly_chart(fig, use_container_width=True)

                    elif "Q10" in question:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df['date'], y=df['bitcoin_price'],
                            name='Bitcoin', yaxis='y1',
                            line=dict(color='#f7931a')))
                        fig.add_trace(go.Scatter(
                            x=df['date'], y=df['oil_price'],
                            name='Oil', yaxis='y2',
                            line=dict(color='#00ff88')))
                        fig.add_trace(go.Scatter(
                            x=df['date'], y=df['sp500_price'],
                            name='S&P500', yaxis='y2',
                            line=dict(color='#2196F3')))
                        fig.update_layout(
                            title="Bitcoin vs Oil vs S&P500",
                            yaxis2=dict(overlaying='y', side='right'),
                            plot_bgcolor='#0e1117',
                            paper_bgcolor='#0e1117',
                            font_color='white'
                        )
                        st.plotly_chart(fig, use_container_width=True)

# ─── PAGE 6: CROSS MARKET ──────────────────────────
elif page1 == "🌐 Cross Market Analysis":
    st.markdown("""
    <div class="page-header">
        <h2>🌐 Cross Market Analysis</h2>
        <p style='color:gray'>Top 3 Crypto • Oil • Stock Market</p>
    </div>
    """, unsafe_allow_html=True)

    # ─── STEP 2: COIN SELECTOR + DATE FILTER ───────
    st.markdown("### 🎛️ Filters")
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        selected_coin = st.selectbox(
            "🪙 Select Coin (Top 3)",
            ['bitcoin', 'ethereum', 'tether'],
            key="cross_coin"
        )
    with col_f2:
        cross_start = st.date_input(
            "📅 Start Date",
            value=pd.to_datetime("2024-01-01"),
            key="cross_start"
        )
    with col_f3:
        cross_end = st.date_input(
            "📅 End Date",
            value=pd.to_datetime("2026-01-01"),
            key="cross_end"
        )

    c_start = str(cross_start)
    c_end   = str(cross_end)

    st.markdown(f"Showing **{selected_coin.capitalize()}** "
                f"from `{c_start}` to `{c_end}`")
    st.divider()

    # ─── STEP 2: DAILY PRICE TREND LINE CHART ──────
    st.markdown("### 📈 Daily Price Trend")

    df_trend = run_query(f"""
        SELECT date, price_inr
        FROM crypto_prices
        WHERE coin_id = '{selected_coin}'
        AND date BETWEEN '{c_start}' AND '{c_end}'
        ORDER BY date ASC
    """)

    if not df_trend.empty:
        # Color per coin
        color_map = {
            'bitcoin':  '#f7931a',
            'ethereum': '#627eea',
            'tether':   '#26a17b'
        }
        coin_color = color_map.get(selected_coin, '#2196F3')

        fig_trend = px.line(
            df_trend, x='date', y='price_inr',
            title=f"{selected_coin.capitalize()} Daily Price Trend",
            color_discrete_sequence=[coin_color]
        )
        fig_trend.update_layout(
            plot_bgcolor='#0e1117',
            paper_bgcolor='#0e1117',
            font_color='white',
            xaxis_title="Date",
            yaxis_title="Price (₹)"
        )
        fig_trend.update_traces(line=dict(width=2))
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.warning("⚠️ No price trend data found.")

    st.divider()

    # ─── STEP 2: DAILY PRICE TABLE ─────────────────
    st.markdown("### 📋 Daily Price Table")

    df_table = run_query(f"""
        SELECT
            date        AS Date,
            coin_id     AS Coin,
            price_inr   AS Price_INR
        FROM crypto_prices
        WHERE coin_id = '{selected_coin}'
        AND date BETWEEN '{c_start}' AND '{c_end}'
        ORDER BY date DESC
    """)

    if not df_table.empty:
        st.dataframe(
            df_table,
            use_container_width=True,
            height=400,
            column_config={
                "Date":      st.column_config.DateColumn("📅 Date"),
                "Coin":      "🪙 Coin",
                "Price_INR": st.column_config.NumberColumn(
                                "💰 Price (₹)",
                                format="₹%.2f")
            }
        )

        # Download
        csv = df_table.to_csv(index=False)
        st.download_button(
            label=f"⬇️ Download {selected_coin} Data",
            data=csv,
            file_name=f"{selected_coin}_prices.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️ No data found.")

    st.divider()

    # ─── BONUS: ALL 3 COINS COMPARISON CHART ───────
    st.markdown("### 📊 All Top 3 Coins Comparison")

    df_all = run_query(f"""
        SELECT date, coin_id, price_inr
        FROM crypto_prices
        WHERE coin_id IN ('bitcoin','ethereum','tether')
        AND date BETWEEN '{c_start}' AND '{c_end}'
        ORDER BY date ASC
    """)

    if not df_all.empty:
        fig_all = px.line(
            df_all, x='date', y='price_inr',
            color='coin_id',
            title="Bitcoin vs Ethereum vs Tether",
            color_discrete_map={
                'bitcoin':  '#f7931a',
                'ethereum': '#627eea',
                'tether':   '#26a17b'
            }
        )
        fig_all.update_layout(
            plot_bgcolor='#0e1117',
            paper_bgcolor='#0e1117',
            font_color='white'
        )
        st.plotly_chart(fig_all, use_container_width=True)


# ─── PAGE 6: default ──────────────────────────  
elif page1 == "-- Select --":
    st.markdown("""
    <div style='text-align:center; padding:50px'>
        <h2>👈 Select a page from the sidebar to begin</h2>
        <br>
        <h4>🏠 Overview &nbsp;|&nbsp;
            💰 Cryptocurrencies &nbsp;|&nbsp;
            📈 Crypto Prices &nbsp;|&nbsp;
            🛢️ Oil Prices &nbsp;|&nbsp;
            📊 Stock Prices &nbsp;|&nbsp;
            🔗 Join Queries &nbsp;|&nbsp;
            🌐 Cross Market Analysis</h4>
    </div>
    """, unsafe_allow_html=True)

    col1,col2,col3 = st.columns(3)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Market Tables</h3>
            <p>💰 Cryptocurrencies — 5 queries</p>
            <p>📈 Crypto Prices — 5 queries</p>
            <p>🛢️ Oil Prices — 5 queries</p>
            <p>📊 Stock Prices — 5 queries</p>
            <p>🔗 Join Queries — 10 queries</p>            
        </div>
        """, unsafe_allow_html=True)

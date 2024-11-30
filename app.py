import streamlit as st
import yfinance as yf
from datetime import datetime
import feedparser
import altair as alt
import pandas as pd

# Set up the page configuration
st.set_page_config(
    page_title="Advanced Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS to enhance the app's appearance
st.markdown(
    """
    <style>
    /* General styles */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Header */
    .header {
        padding: 1rem 0;
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        color: var(--text-color);
    }
    .header img {
        height: 40px;
        margin-right: 10px;
        vertical-align: middle;
        filter: brightness(0) invert(0);
    }
    /* Adjust icon filter for dark mode */
    @media (prefers-color-scheme: dark) {
        .header img {
            filter: brightness(1) invert(1);
        }
    }
    /* Card styles */
    .card {
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow);
        text-align: center;
        background-color: var(--background-color);
    }
    .card h3 {
        margin: 0;
        font-size: 18px;
        color: var(--text-color);
    }
    .card p {
        margin: 10px 0 0 0;
        font-size: 24px;
        font-weight: bold;
        color: #27ae60;
    }
    /* News section */
    .news-card {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid var(--border-color);
        box-shadow: var(--shadow);
        display: flex;
        flex-direction: column;
        height: 320px;
        background-color: var(--background-color);
    }
    .news-title {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 5px;
        color: var(--text-color);
    }
    .news-source {
        font-size: 12px;
        margin-bottom: 10px;
        color: var(--text-color);
    }
    .news-description {
        font-size: 14px;
        flex-grow: 1;
        margin-bottom: 10px;
        overflow-y: auto;
        color: var(--text-color);
    }
    .news-card a {
        text-decoration: none;
        font-weight: bold;
        align-self: flex-start;
        color: #2980b9;
    }
    .news-card a:hover {
        text-decoration: underline;
    }
    /* Variables */
    :root {
        --border-color: #e6e6e6;
        --shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --border-color: #444444;
            --shadow: 0 2px 5px rgba(0,0,0,0.5);
        }
    }
    /* Footer */
    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header section
st.markdown(
    """
    <div class="header">
        <img src="https://img.icons8.com/ios-filled/50/000000/stock-share.png"/>
        Advanced Financial Dashboard
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize session state
if "currency" not in st.session_state:
    st.session_state["currency"] = "USD"
if "selected_assets" not in st.session_state:
    st.session_state["selected_assets"] = ["MicroStrategy", "Bitcoin", "Gold", "S&P 500"]
if "chart_period" not in st.session_state:
    st.session_state["chart_period"] = "3M"
if "theme" not in st.session_state:
    st.session_state["theme"] = "light"

# Sidebar
with st.sidebar:
    st.markdown("## Settings")

    # Currency Selection
    st.session_state["currency"] = st.selectbox("Select Currency", ("USD", "ZAR"), index=0)

    # Asset Selection
    assets_dict = {
        "MicroStrategy": "MSTR",
        "Bitcoin": "BTC-USD",
        "Gold": "GC=F",
        "S&P 500": "^GSPC",
    }
    st.session_state["selected_assets"] = st.multiselect(
        "Select Assets",
        list(assets_dict.keys()),
        default=list(assets_dict.keys()),
    )

    # Chart Period Selection
    period_options = {
        "1M": "1mo",
        "3M": "3mo",
        "6M": "6mo",
        "1Y": "1y",
        "YTD": "ytd",
        "MAX": "max",
    }
    st.session_state["chart_period"] = st.selectbox(
        "Select Chart Period", list(period_options.keys()), index=1
    )

    # Stock Symbol Search
    st.markdown("---")
    st.markdown("### Stock Symbol Search")
    stock_symbol = st.text_input("Enter Stock Symbol (e.g., AAPL)")

    # Theme Toggle
    st.markdown("---")
    st.markdown("### Theme")
    theme_option = st.selectbox("Select Theme", ("Light", "Dark"), index=0)
    st.session_state["theme"] = theme_option.lower()
    st.markdown(
        f"""
        <style>
            :root {{
                color-scheme: {st.session_state["theme"]};
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )

# Data caching with a TTL of 10 minutes
@st.cache_data(ttl=600, show_spinner=False)
def get_price(ticker):
    try:
        data = yf.Ticker(ticker)
        df = data.history(period="1d", interval="1m")
        if df.empty:
            return None
        current_price = df["Close"][-1]
        return current_price
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Fetch all prices
@st.cache_data(ttl=600, show_spinner=False)
def get_all_prices(tickers):
    prices = {}
    for ticker in tickers:
        prices[ticker] = get_price(ticker)
    return prices

# Fetch news articles
@st.cache_data(ttl=600, show_spinner=False)
def fetch_news(selected_assets, stock_symbol):
    feeds = {}
    for asset in selected_assets:
        feeds[asset] = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={assets_dict[asset]}&region=US&lang=en-US"
    if stock_symbol:
        feeds[stock_symbol.upper()] = f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={stock_symbol}&region=US&lang=en-US"

    all_articles = []
    for asset, feed_url in feeds.items():
        feed = feedparser.parse(feed_url)
        if feed.entries:
            article = feed.entries[0]
            try:
                published_time = datetime(*article.published_parsed[:6])
                published_at = published_time.strftime("%Y-%m-%d %H:%M:%S")
            except (ValueError, AttributeError):
                published_at = article.get("published", "Unknown")
            all_articles.append(
                {
                    "title": article.get("title", "No Title"),
                    "source": article.get("source", {}).get("title", "Unknown"),
                    "description": article.get("summary", ""),
                    "link": article.get("link", "#"),
                    "publishedAt": published_at,
                }
            )
    return all_articles

def main():
    st.markdown('<div class="main-content">', unsafe_allow_html=True)

    # Prices Section
    st.markdown("### **Current Prices**")
    tickers = [assets_dict[asset] for asset in st.session_state["selected_assets"]]
    if stock_symbol:
        tickers.append(stock_symbol.upper())
    prices = get_all_prices(tickers + ["ZAR=X"])
    usd_zar_rate = prices.get("ZAR=X", 1)
    asset_cols = st.columns(len(tickers))
    for col, asset in zip(asset_cols, st.session_state["selected_assets"] + ([stock_symbol.upper()] if stock_symbol else [])):
        ticker = assets_dict.get(asset, asset)
        price = prices.get(ticker)
        with col:
            if price is not None:
                if st.session_state["currency"] == "ZAR" and usd_zar_rate:
                    converted_price = price * usd_zar_rate
                    symbol = "R"
                else:
                    converted_price = price
                    symbol = "$"
                st.markdown(
                    f"""
                    <div class="card">
                        <h3>{asset}</h3>
                        <p>{symbol}{converted_price:,.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="card">
                        <h3>{asset}</h3>
                        <p>N/A</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Exchange Rates
    st.markdown("### **Exchange Rates**")
    fx_cols = st.columns(3)
    fx_assets = {
        "USD/ZAR": usd_zar_rate,
        "GBP/ZAR": get_price("GBPZAR=X"),
        "EUR/ZAR": get_price("EURZAR=X"),
    }
    for col, (label, price) in zip(fx_cols, fx_assets.items()):
        with col:
            if price is not None:
                st.markdown(
                    f"""
                    <div class="card">
                        <h3>{label}</h3>
                        <p>R{price:,.2f}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div class="card">
                        <h3>{label}</h3>
                        <p>N/A</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # News Section
    st.markdown("### **Latest News**")
    news_articles = fetch_news(st.session_state["selected_assets"], stock_symbol)
    if news_articles:
        news_cols = st.columns(len(news_articles))
        for idx, article in enumerate(news_articles):
            with news_cols[idx]:
                st.markdown(
                    f"""
                    <div class="news-card">
                        <div class="news-title">{article['title']}</div>
                        <div class="news-source">Source: {article['source']} | Published at: {article['publishedAt']}</div>
                        <div class="news-description">{article['description']}</div>
                        <a href="{article['link']}" target="_blank">Read more</a>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
    else:
        st.info("No news articles available at the moment.")

    # Data Table Section
    st.markdown("### **Asset Key Metrics**")
    metrics_data = []
    for asset in st.session_state["selected_assets"]:
        ticker = assets_dict[asset]
        info = yf.Ticker(ticker).info
        metrics_data.append({
            "Asset": asset,
            "Previous Close": info.get("previousClose", "N/A"),
            "Open": info.get("open", "N/A"),
            "Day's Range": f"{info.get('dayLow', 'N/A')} - {info.get('dayHigh', 'N/A')}",
            "52 Week Range": f"{info.get('fiftyTwoWeekLow', 'N/A')} - {info.get('fiftyTwoWeekHigh', 'N/A')}",
            "Volume": info.get("volume", "N/A"),
            "Market Cap": info.get("marketCap", "N/A"),
        })
    metrics_df = pd.DataFrame(metrics_data)
    st.dataframe(metrics_df)

    # Charts Section
    st.markdown("### **Asset Performance Charts**")
    chart_assets = st.session_state["selected_assets"]
    if stock_symbol:
        chart_assets.append(stock_symbol.upper())
        assets_dict[stock_symbol.upper()] = stock_symbol.upper()
    chart_cols = st.columns(2)
    for idx, asset in enumerate(chart_assets):
        ticker = assets_dict.get(asset, asset)
        selected_period = period_options[st.session_state["chart_period"]]
        data = yf.Ticker(ticker).history(period=selected_period)
        if not data.empty:
            data.reset_index(inplace=True)
            # Currency conversion for charts if ZAR is selected
            if st.session_state["currency"] == "ZAR" and usd_zar_rate:
                data["Close"] = data["Close"] * usd_zar_rate
                currency_symbol = "R"
            else:
                currency_symbol = "$"
            line_chart = alt.Chart(data).mark_line(color='#27ae60').encode(
                x=alt.X("Date:T", title="Date"),
                y=alt.Y("Close:Q", title=f"Price ({currency_symbol})"),
                tooltip=[alt.Tooltip("Date:T"), alt.Tooltip("Close:Q", format=".2f")]
            ).properties(
                title=asset
            ).configure_title(
                fontSize=16,
                anchor='start',
                color=st.get_option("theme.textColor")
            ).configure_axis(
                labelColor=st.get_option("theme.textColor"),
                titleColor=st.get_option("theme.textColor")
            ).configure_view(
                strokeWidth=0
            ).interactive()
            with chart_cols[idx % 2]:
                st.altair_chart(line_chart, use_container_width=True)
        else:
            st.warning(f"No data available for {asset}.")

    st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"**Last updated at:** {last_updated}")
    st.caption("Data refreshes every 10 minutes.")

if __name__ == "__main__":
    main()

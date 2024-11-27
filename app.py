import streamlit as st
import yfinance as yf
from datetime import datetime
import feedparser
import altair as alt

st.set_page_config(
    page_title="Financial Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS
st.markdown(
    """
    <style>
    /* General styles */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    /* Header */
    .header {
        background-color: #2c3e50;
        padding: 1rem;
        color: #ffffff;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 20px;
    }
    .header img {
        height: 40px;
        margin-right: 10px;
        vertical-align: middle;
    }
    /* Main content */
    .main-content {
        margin-top: 20px;
    }
    /* CSS Variables for Border Colors */
    :root {
        --border-color: #dddddd;  /* Light mode border color */
    }
    @media (prefers-color-scheme: dark) {
        :root {
            --border-color: #444444;  /* Dark mode border color */
        }
    }
    /* Card styles */
    .card {
        padding: 20px;
        border-radius: 8px;
        margin-bottom: 20px;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    .card h3 {
        margin: 0;
        font-size: 18px;
    }
    .card p {
        margin: 10px 0 0 0;
        font-size: 24px;
        font-weight: bold;
        color: #27ae60;  /* You can adjust this color if needed */
    }
    /* News section */
    .news-card {
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        display: flex;
        flex-direction: column;
        height: 300px;
    }
    .news-title {
        font-size: 16px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .news-source {
        font-size: 12px;
        margin-bottom: 10px;
    }
    .news-description {
        font-size: 14px;
        flex-grow: 1;
        margin-bottom: 10px;
        overflow-y: auto;
    }
    .news-card a {
        text-decoration: none;
        font-weight: bold;
        align-self: flex-start;
    }
    .news-card a:hover {
        text-decoration: underline;
    }
    /* Footer */
    footer {
        visibility: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
    <div class="header">
        <img src="https://img.icons8.com/ios-filled/50/ffffff/stock-share.png"/>
        Financial Dashboard
    </div>
    """,
    unsafe_allow_html=True,
)

# Initialize currency in session state
if "currency" not in st.session_state:
    st.session_state["currency"] = "USD"

# Currency Selection in Sidebar
with st.sidebar:
    st.markdown("## Currency Selection")
    currency = st.radio("", ("USD", "ZAR"))
    st.session_state["currency"] = currency

# Cache data with a TTL of 600 seconds (10 minutes)
@st.cache_data(ttl=600)
def get_price(ticker):
    try:
        data = yf.Ticker(ticker)
        df = data.history(period="1d", interval="1m")
        if df.empty:
            return None
        current_price = df["Close"][-1]
        return current_price
    except Exception:
        return None

# Fetch all prices
@st.cache_data(ttl=600)
def get_all_prices():
    prices = {}
    tickers = ["MSTR", "^GSPC", "GC=F", "BTC-USD", "ZAR=X", "GBPZAR=X", "EURZAR=X"]
    for ticker in tickers:
        prices[ticker] = get_price(ticker)
    return prices

# Fetch news articles
@st.cache_data(ttl=600)
def fetch_news():
    feeds = {
        "Bitcoin": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=BTC-USD&region=US&lang=en-US",
        "MicroStrategy": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=MSTR&region=US&lang=en-US",
        "Gold": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=GC=F&region=US&lang=en-US",
    }
    all_articles = []
    for asset, feed_url in feeds.items():
        feed = feedparser.parse(feed_url)
        if feed.entries:
            article = feed.entries[0]
            try:
                published_time = datetime.strptime(
                    article.get("published", "")[:25], "%a, %d %b %Y %H:%M:%S"
                )
                published_at = published_time.strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                published_at = article.get("published", "")
            all_articles.append(
                {
                    "title": article.get("title", "No Title"),
                    "source": "Yahoo Finance",
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
    prices = get_all_prices()
    usd_zar_rate = prices.get("ZAR=X")
    asset_cols = st.columns(4)
    assets = [
        ("MicroStrategy", prices.get("MSTR")),
        ("Bitcoin", prices.get("BTC-USD")),
        ("Gold", prices.get("GC=F")),
        ("S&P 500", prices.get("^GSPC")),
    ]

    for col, (label, price) in zip(asset_cols, assets):
        with col:
            if price is not None:
                if (
                    st.session_state["currency"] == "ZAR"
                    and usd_zar_rate
                    and label != "S&P 500"
                ):
                    converted_price = price * usd_zar_rate
                    symbol = "R"
                elif label == "S&P 500":
                    converted_price = price
                    symbol = "$"
                else:
                    converted_price = price
                    symbol = "$"
                st.markdown(
                    f"""
                    <div class="card">
                        <h3>{label}</h3>
                        <p>{symbol}{converted_price:,.2f}</p>
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

    # Exchange Rates
    st.markdown("### **Exchange Rates**")
    fx_cols = st.columns(3)
    fx_assets = [
        ("USD/ZAR", usd_zar_rate),
        ("GBP/ZAR", prices.get("GBPZAR=X")),
        ("EUR/ZAR", prices.get("EURZAR=X")),
    ]
    for col, (label, price) in zip(fx_cols, fx_assets):
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
    news_articles = fetch_news()
    news_cols = st.columns(3)
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

    # Charts Section
    st.markdown("### **Asset Performance Charts**")
    chart_assets = {
        "MSTR": "MicroStrategy",
        "BTC-USD": "Bitcoin",
        "^GSPC": "S&P 500",
        "GC=F": "Gold",
    }
    chart_cols = st.columns(2)
    for idx, (ticker, name) in enumerate(chart_assets.items()):
        data = yf.Ticker(ticker).history(period="3mo")
        if not data.empty:
            data.reset_index(inplace=True)
            line_chart = alt.Chart(data).mark_line().encode(
                x="Date:T",
                y="Close:Q",
                tooltip=["Date:T", "Close:Q"]
            ).properties(
                title=name
            ).configure_title(
                fontSize=16,
                anchor='start',
                color='#333'
            ).interactive()
            with chart_cols[idx % 2]:
                st.altair_chart(line_chart, use_container_width=True)
        else:
            st.warning(f"No data for {name}")

    st.markdown("</div>", unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Last updated at: {last_updated}")
    st.caption("Data refreshes every 10 minutes.")

if __name__ == "__main__":
    main()

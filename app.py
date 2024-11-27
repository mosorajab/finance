import streamlit as st
import yfinance as yf
from datetime import datetime
import feedparser  # Used for fetching RSS feeds

st.set_page_config(
    page_title="Asset Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for modern look compatible with both light and dark modes
st.markdown(
    """
    <style>
    /* Root layout adjustments */
    html, body, [class*="css"]  {
        background-color: transparent;
        color: inherit;
        font-family: 'Lato', sans-serif;
    }
    /* Remove padding around main content */
    .block-container {
        padding: 1rem 2rem;
    }
    /* Sidebar styling */
    .css-1lcbmhc {
        background-color: #f0f2f6 !important;
    }
    /* Sidebar title */
    .sidebar .sidebar-content {
        padding-top: 1rem;
    }
    /* Button styles in sidebar */
    .sidebar .stButton button {
        background-color: #4CAF50;
        color: white;
        padding: 0.6rem 1.2rem;
        margin: 0.5rem 0;
        font-size: 16px;
        font-weight: bold;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        width: 100%;
        transition: background-color 0.3s, transform 0.1s;
    }
    .sidebar .stButton button:hover {
        background-color: #45a049;
        transform: translateY(-2px);
    }
    /* Card styles */
    .card {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid rgba(0, 0, 0, 0.2);
    }
    .card h3 {
        margin: 0;
        font-size: 16px;
        color: inherit;
    }
    .card p {
        margin: 5px 0 0 0;
        font-size: 22px;
        font-weight: bold;
        color: inherit;
    }
    /* Chart titles */
    .chart-title {
        font-size: 14px;
        font-weight: 500;
        color: inherit;
        text-align: center;
        margin-bottom: -10px;
    }
    /* News section */
    .news-card {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid rgba(0, 0, 0, 0.2);
        height: 300px;
        display: flex;
        flex-direction: column;
    }
    .news-title {
        font-size: 16px;
        font-weight: bold;
        color: inherit;
        margin-bottom: 5px;
    }
    .news-source {
        font-size: 12px;
        color: inherit;
        margin-bottom: 5px;
    }
    .news-description {
        font-size: 14px;
        color: inherit;
        flex-grow: 1;
        overflow-y: auto;
    }
    .news-card a.read-more {
        margin-top: 10px;
        color: #4CAF50;
        text-decoration: none;
        font-weight: bold;
    }
    .news-card a.read-more:hover {
        color: #45a049;
    }
    /* Remove Streamlit branding */
    footer {visibility: hidden;}
    /* Responsive columns */
    @media (max-width: 1200px) {
        .stApp {
            zoom: 80%;
        }
    }
    @media (max-width: 768px) {
        .stApp {
            zoom: 70%;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Load custom fonts
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📈 Real-Time Asset Dashboard")

# Initialize currency in session state
if "currency" not in st.session_state:
    st.session_state["currency"] = "USD"

# Currency Selection Buttons in Sidebar
with st.sidebar:
    st.markdown("### Currency Selection")
    if st.button("Show Prices in USD"):
        st.session_state["currency"] = "USD"
    if st.button("Show Prices in ZAR"):
        st.session_state["currency"] = "ZAR"

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

# Cache all prices to prevent re-fetching on each interaction
@st.cache_data(ttl=600)
def get_all_prices():
    prices = {}
    tickers = ["MSTR", "^GSPC", "GC=F", "BTC-USD", "ZAR=X", "GBPZAR=X", "EURZAR=X"]
    for ticker in tickers:
        prices[ticker] = get_price(ticker)
    return prices

# Fetch news articles using feedparser and Yahoo Finance RSS feeds
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
    # Get all prices (cached)
    prices = get_all_prices()

    # Get USD to ZAR exchange rate
    usd_zar_rate = prices.get("ZAR=X")

    # Asset Prices Display
    asset_cols = st.columns(7)
    assets = [
        ("MicroStrategy", prices.get("MSTR")),
        ("Bitcoin", prices.get("BTC-USD")),
        ("S&P 500", prices.get("^GSPC")),
        ("Gold", prices.get("GC=F")),
        ("USD/ZAR", usd_zar_rate),
        ("GBP/ZAR", prices.get("GBPZAR=X")),
        ("EUR/ZAR", prices.get("EURZAR=X")),
    ]

    for col, (label, price) in zip(asset_cols, assets):
        with col:
            if price is not None:
                if (
                    st.session_state["currency"] == "ZAR"
                    and usd_zar_rate
                    and label not in ["USD/ZAR", "GBP/ZAR", "EUR/ZAR"]
                ):
                    converted_price = price * usd_zar_rate
                    symbol = "R"
                elif label in ["USD/ZAR", "GBP/ZAR", "EUR/ZAR"]:
                    converted_price = price
                    symbol = "R"
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

    # News Section
    st.markdown("---")
    st.markdown("## 📰 Latest News")
    news_articles = fetch_news()
    news_cols = st.columns(len(news_articles))
    for idx, article in enumerate(news_articles):
        with news_cols[idx]:
            st.markdown(
                f"""
                <div class="news-card">
                    <div class="news-title">{article['title']}</div>
                    <div class="news-source">Source: {article['source']} | Published at: {article['publishedAt']}</div>
                    <div class="news-description">{article['description']}</div>
                    <a href="{article['link']}" target="_blank" class="read-more">Read more</a>
                </div>
            """,
                unsafe_allow_html=True,
            )

    # Charts Section
    st.markdown("---")
    chart_cols = st.columns(7)
    chart_assets = {
        "MSTR": "MicroStrategy",
        "BTC-USD": "Bitcoin",
        "^GSPC": "S&P 500",
        "GC=F": "Gold",
        "ZAR=X": "USD/ZAR",
        "GBPZAR=X": "GBP/ZAR",
        "EURZAR=X": "EUR/ZAR",
    }

    for idx, (ticker, name) in enumerate(chart_assets.items()):
        data = yf.Ticker(ticker).history(period="1mo")
        if not data.empty:
            with chart_cols[idx]:
                st.markdown(
                    f"<div class='chart-title'>{name}</div>", unsafe_allow_html=True
                )
                st.line_chart(
                    data["Close"], height=120, use_container_width=True
                )
        else:
            st.warning(f"No data for {name}")

    # Footer
    st.markdown("---")
    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.write(f"Last updated at: {last_updated}")
    st.caption("Data refreshes every 10 minutes.")

if __name__ == "__main__":
    main()

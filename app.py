import streamlit as st
import yfinance as yf
import time
from datetime import datetime

st.set_page_config(page_title="Asset Dashboard", page_icon="📈", layout="wide")

# Custom CSS for modern look compatible with dark mode
st.markdown("""
    <style>
    /* Root layout adjustments */
    .main {
        background-color: #1E1E1E;
        color: #FFFFFF;
        font-family: 'Roboto', sans-serif;
    }
    /* Section headers */
    .section-header {
        font-size: 26px;
        font-weight: 600;
        margin-top: 30px;
        margin-bottom: 10px;
        color: #00ADB5;
    }
    /* Card styles */
    .card {
        background-color: #393E46;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.2);
    }
    .card h3 {
        margin: 0;
        font-size: 18px;
        color: #EEEEEE;
    }
    .card p {
        margin: 0;
        font-size: 24px;
        font-weight: bold;
        color: #FFD369;
    }
    /* Chart titles */
    .chart-title {
        font-size: 16px;
        font-weight: 500;
        color: #EEEEEE;
        text-align: center;
        margin-bottom: -10px;
    }
    /* Responsive columns */
    @media (max-width: 768px) {
        .stColumn > div {
            width: 100% !important;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# Load custom fonts
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;600&display=swap');
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Real-Time Asset Dashboard")

def get_price(ticker):
    try:
        data = yf.Ticker(ticker)
        df = data.history(period='1d', interval='1m')
        if df.empty:
            st.error(f"No data found for ticker {ticker}")
            return None
        current_price = df['Close'][-1]
        return current_price
    except Exception as e:
        st.error(f"Error fetching data for {ticker}: {e}")
        return None

# Cache data with a TTL (Time To Live) of 60 seconds
@st.cache_data(ttl=5)
def get_all_prices():
    prices = {}
    tickers = ['MSTR', '^GSPC', 'GC=F', 'BTC-USD', 'ZAR=X', 'GBPZAR=X', 'EURZAR=X']
    for ticker in tickers:
        prices[ticker] = get_price(ticker)
    return prices

def main():
    prices = get_all_prices()

    # Get USD to ZAR exchange rate
    usd_zar_rate = prices.get('ZAR=X')

    # Currency Selection
    currency = st.selectbox(
        'Select Currency for Asset Prices:',
        ('USD', 'ZAR'),
        index=0
    )

    # Asset Prices Section
    st.markdown('<div class="section-header">Asset Prices</div>', unsafe_allow_html=True)

    asset_cols = st.columns(4)
    assets = [
        ('MicroStrategy (MSTR)', prices.get('MSTR')),
        ('Bitcoin', prices.get('BTC-USD')),
        ('S&P 500 Index', prices.get('^GSPC')),
        ('Gold Price', prices.get('GC=F'))
    ]
    for col, (label, price) in zip(asset_cols, assets):
        with col:
            if price is not None:
                if currency == 'ZAR' and usd_zar_rate:
                    converted_price = price * usd_zar_rate
                    symbol = 'R'
                else:
                    converted_price = price
                    symbol = '$'
                st.markdown(f"""
                    <div class="card">
                        <h3>{label}</h3>
                        <p>{symbol}{converted_price:,.2f}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="card">
                        <h3>{label}</h3>
                        <p>N/A</p>
                    </div>
                """, unsafe_allow_html=True)

    # Exchange Rates Section
    st.markdown('<div class="section-header">Exchange Rates to ZAR</div>', unsafe_allow_html=True)
    exchange_cols = st.columns(3)
    exchanges = [
        ('USD/ZAR', usd_zar_rate),
        ('GBP/ZAR', prices.get('GBPZAR=X')),
        ('EUR/ZAR', prices.get('EURZAR=X'))
    ]
    for col, (label, rate) in zip(exchange_cols, exchanges):
        with col:
            if rate is not None:
                st.markdown(f"""
                    <div class="card">
                        <h3>{label}</h3>
                        <p>R{rate:,.2f}</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="card">
                        <h3>{label}</h3>
                        <p>N/A</p>
                    </div>
                """, unsafe_allow_html=True)

    # Asset Price Charts
    st.markdown('<div class="section-header">Asset Price Charts (Last Month)</div>', unsafe_allow_html=True)
    chart_cols = st.columns(4)
    hist_tickers = {'MSTR': 'MicroStrategy', 'BTC-USD': 'Bitcoin', '^GSPC': 'S&P 500', 'GC=F': 'Gold'}
    for idx, (ticker, name) in enumerate(hist_tickers.items()):
        data = yf.Ticker(ticker).history(period='1mo')
        if not data.empty:
            with chart_cols[idx % 4]:
                st.markdown(f"<div class='chart-title'>{name}</div>", unsafe_allow_html=True)
                st.line_chart(data['Close'], height=150)
        else:
            st.warning(f"No historical data for {name}")

    # Exchange Rate Charts
    st.markdown('<div class="section-header">Exchange Rate Charts (Last Month)</div>', unsafe_allow_html=True)
    ex_chart_cols = st.columns(3)
    exchange_tickers = {'ZAR=X': 'USD/ZAR', 'GBPZAR=X': 'GBP/ZAR', 'EURZAR=X': 'EUR/ZAR'}
    for idx, (ticker, name) in enumerate(exchange_tickers.items()):
        data = yf.Ticker(ticker).history(period='1mo')
        if not data.empty:
            with ex_chart_cols[idx % 3]:
                st.markdown(f"<div class='chart-title'>{name}</div>", unsafe_allow_html=True)
                st.line_chart(data['Close'], height=150)
        else:
            st.warning(f"No historical data for {name}")

    # Footer
    st.markdown("---")
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.write(f"Last updated at: {last_updated}")
    st.caption("Data refreshes every minute.")

if __name__ == "__main__":
    main()

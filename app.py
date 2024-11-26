import streamlit as st
import yfinance as yf
import time

st.set_page_config(page_title="Asset Dashboard", page_icon="📈", layout="wide")

# Custom CSS for a modern look compatible with dark mode
st.markdown("""
    <style>
    /* Adjust the background and text colors based on the theme */
    html, body, [class*="css"]  {
        background-color: transparent;
        color: inherit;
    }
    .section-header {
        font-size: 24px;
        font-weight: bold;
        margin-top: 30px;
        margin-bottom: 10px;
        color: inherit;
    }
    .stMetric {
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 15px;
    }
    /* Card style for metrics */
    .card {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
    }
    .card h3 {
        margin: 0;
        font-size: 18px;
        color: inherit;
    }
    .card p {
        margin: 0;
        font-size: 24px;
        font-weight: bold;
        color: inherit;
    }
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
@st.cache_data(ttl=60)
def get_all_prices():
    prices = {}
    tickers = ['MSTR', '^GSPC', 'GC=F', 'BTC-USD', 'ZAR=X', 'GBPZAR=X', 'EURZAR=X']
    for ticker in tickers:
        prices[ticker] = get_price(ticker)
    return prices

def main():
    prices = get_all_prices()

    # Asset Prices Section
    st.markdown('<div class="section-header">Asset Prices in USD</div>', unsafe_allow_html=True)
    asset_cols = st.columns(4)
    assets = [
        ('MicroStrategy (MSTR)', prices.get('MSTR'), '$'),
        ('Bitcoin', prices.get('BTC-USD'), '$'),
        ('S&P 500 Index', prices.get('^GSPC'), ''),
        ('Gold Price', prices.get('GC=F'), '$')
    ]
    for col, (label, price, symbol) in zip(asset_cols, assets):
        with col:
            if price:
                st.markdown(f"""
                    <div class="card">
                        <h3>{label}</h3>
                        <p>{symbol}{price:,.2f}</p>
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
        ('USD/ZAR', prices.get('ZAR=X')),
        ('GBP/ZAR', prices.get('GBPZAR=X')),
        ('EUR/ZAR', prices.get('EURZAR=X'))
    ]
    for col, (label, rate) in zip(exchange_cols, exchanges):
        with col:
            if rate:
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
                st.markdown(f"**{name}**")
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
                st.markdown(f"**{name}**")
                st.line_chart(data['Close'], height=150)
        else:
            st.warning(f"No historical data for {name}")

    st.write(f"Last updated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    st.caption("Data refreshes every minute.")

if __name__ == "__main__":
    main()

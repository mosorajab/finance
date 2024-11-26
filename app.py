import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Asset Dashboard", page_icon="📈", layout="wide")

# Custom CSS for modern look compatible with both light and dark modes
st.markdown("""
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
    /* Card styles */
    .card {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
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
    /* Remove Streamlit branding */
    footer {visibility: hidden;}
    /* Button styles */
    .currency-button {
        background-color: #008CBA;
        color: white;
        padding: 0.6rem 1.2rem;
        margin: 0 0.5rem;
        font-size: 16px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .currency-button:hover {
        background-color: #006f94;
    }
    .button-container {
        display: flex;
        justify-content: center;
        margin-top: 10px;
    }
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
    """, unsafe_allow_html=True)

# Load custom fonts
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
    </style>
    """, unsafe_allow_html=True)

st.title("📈 Real-Time Asset Dashboard")

# Cache data with a TTL of 600 seconds (10 minutes)
@st.cache_data(ttl=600)
def get_price(ticker):
    try:
        data = yf.Ticker(ticker)
        df = data.history(period='1d', interval='1m')
        if df.empty:
            return None
        current_price = df['Close'][-1]
        return current_price
    except Exception:
        return None

# Cache all prices to prevent re-fetching on each interaction
@st.cache_data(ttl=600)
def get_all_prices():
    prices = {}
    tickers = ['MSTR', '^GSPC', 'GC=F', 'BTC-USD', 'ZAR=X', 'GBPZAR=X', 'EURZAR=X']
    for ticker in tickers:
        prices[ticker] = get_price(ticker)
    return prices

def main():
    # Initialize currency in session state
    if 'currency' not in st.session_state:
        st.session_state['currency'] = 'USD'

    # Get all prices (cached)
    prices = get_all_prices()

    # Get USD to ZAR exchange rate
    usd_zar_rate = prices.get('ZAR=X')

    # Asset Prices Display
    asset_cols = st.columns(7)
    assets = [
        ('MicroStrategy', prices.get('MSTR')),
        ('Bitcoin', prices.get('BTC-USD')),
        ('S&P 500', prices.get('^GSPC')),
        ('Gold', prices.get('GC=F')),
        ('USD/ZAR', usd_zar_rate),
        ('GBP/ZAR', prices.get('GBPZAR=X')),
        ('EUR/ZAR', prices.get('EURZAR=X'))
    ]

    for col, (label, price) in zip(asset_cols, assets):
        with col:
            if price is not None:
                if st.session_state['currency'] == 'ZAR' and usd_zar_rate and label not in ['USD/ZAR', 'GBP/ZAR', 'EUR/ZAR']:
                    converted_price = price * usd_zar_rate
                    symbol = 'R'
                elif label in ['USD/ZAR', 'GBP/ZAR', 'EUR/ZAR']:
                    converted_price = price
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

    # Charts Section
    chart_cols = st.columns(7)
    chart_assets = {
        'MSTR': 'MicroStrategy',
        'BTC-USD': 'Bitcoin',
        '^GSPC': 'S&P 500',
        'GC=F': 'Gold',
        'ZAR=X': 'USD/ZAR',
        'GBPZAR=X': 'GBP/ZAR',
        'EURZAR=X': 'EUR/ZAR'
    }

    for idx, (ticker, name) in enumerate(chart_assets.items()):
        data = yf.Ticker(ticker).history(period='1mo')
        if not data.empty:
            with chart_cols[idx]:
                st.markdown(f"<div class='chart-title'>{name}</div>", unsafe_allow_html=True)
                st.line_chart(data['Close'], height=120, use_container_width=True)
        else:
            st.warning(f"No data for {name}")

    # Currency Selection Buttons at the Bottom
    st.markdown("---")
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    usd_button = st.button("Show Prices in USD", key='usd_button')
    zar_button = st.button("Show Prices in ZAR", key='zar_button')
    st.markdown('</div>', unsafe_allow_html=True)

    if usd_button:
        st.session_state['currency'] = 'USD'
    elif zar_button:
        st.session_state['currency'] = 'ZAR'

    # Footer
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    st.write(f"Last updated at: {last_updated}")
    st.caption("Data refreshes every 10 minutes.")

if __name__ == "__main__":
    main()

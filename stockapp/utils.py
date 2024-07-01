import yfinance as yf
import pandas as pd
import ta
from pykrx import stock

def get_kospi_tickers_by_market_cap(limit=1000):
    tickers = stock.get_market_ticker_list(market="KOSPI")
    market_cap_data = []

    for ticker in tickers:
        try:
            market_cap = stock.get_market_cap_by_ticker(ticker)
            name = stock.get_market_ticker_name(ticker)
            market_cap_data.append({'ticker': ticker, 'name': name, 'market_cap': market_cap})
        except:
            continue

    # 시가총액을 기준으로 정렬하고 상위 limit 개수만 선택
    market_cap_df = pd.DataFrame(market_cap_data)
    market_cap_df['market_cap'] = pd.to_numeric(market_cap_df['market_cap'], errors='coerce')
    market_cap_df = market_cap_df.sort_values(by='market_cap', ascending=False).head(limit)
    return market_cap_df[['ticker', 'name']].to_dict('records')

def get_stock_data(ticker):
    stock_data = yf.Ticker(ticker)
    hist = stock_data.history(period="1mo")  # '1y' 대신 '1mo' 사용
    return hist

def is_valid_ticker(ticker):
    try:
        df = get_stock_data(ticker)
        if df.empty:
            return False
        return True
    except:
        return False

def calculate_indicators(df):
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    df['Bollinger_High'] = ta.volatility.BollingerBands(df['Close']).bollinger_hband()
    df['Bollinger_Low'] = ta.volatility.BollingerBands(df['Close']).bollinger_lband()
    return df

def find_buy_signals(df):
    buy_signals = df[(df['RSI'] <= 30) & (df['Close'] <= df['Bollinger_Low'])]
    return buy_signals

def get_recommended_stocks():
    tickers = get_kospi_tickers_by_market_cap()
    recommended_stocks = []
    
    for ticker_info in tickers:
        if len(recommended_stocks) >= 20:
            break
        
        ticker_ks = f"{ticker_info['ticker']}.KS"
        if not is_valid_ticker(ticker_ks):
            continue
        df = get_stock_data(ticker_ks)
        if not df.empty:
            df = calculate_indicators(df)
            buy_signals = find_buy_signals(df)
            if not buy_signals.empty:
                buy_signals = buy_signals.reset_index()
                buy_signals['Date'] = buy_signals['Date'].astype(str)
                recommended_stocks.append({
                    'ticker': ticker_info['ticker'],
                    'name': ticker_info['name'],
                    'buy_signals': buy_signals.to_dict(orient="records")
                })
    
    return recommended_stocks  # 최대 20개 종목 반환

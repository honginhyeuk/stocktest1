from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import ta
from pykrx import stock

def get_recent_business_day():
    # 오늘 날짜를 기준으로 이전 30일 동안의 날짜를 순회하여 비즈니스 날짜를 찾음
    for i in range(30):
        date = (datetime.now() - timedelta(days=i)).strftime('%Y%m%d')
        try:
            # 최근 비즈니스 날짜를 확인하기 위한 임시 데이터 프레임
            df = stock.get_index_ohlcv_by_date(date, date, "1001")
            if not df.empty:
                print(f"Nearest business day found: {date}")
                return date
        except Exception as e:
            print(f"Error getting nearest business day for date {date}: {e}")
    # 비즈니스 날짜를 찾지 못하면 오늘 날짜 반환
    print("No business day found in the last 30 days")
    return datetime.now().strftime('%Y%m%d')

def get_kospi_tickers_by_market_cap(limit=1000):
    recent_business_day = get_recent_business_day()
    try:
        tickers = stock.get_market_ticker_list(market="KOSPI", date=recent_business_day)
        market_cap_data = []

        for ticker in tickers:
            try:
                market_cap_info = stock.get_market_cap_by_ticker(ticker, date=recent_business_day)
                name = stock.get_market_ticker_name(ticker)
                market_cap_data.append({'ticker': ticker, 'name': name, 'market_cap': market_cap_info['시가총액']})
            except Exception as e:
                print(f"Error getting market cap for ticker {ticker}: {e}")
                continue

        # 시가총액 데이터를 디버깅 출력
        print("Market Cap Data:", market_cap_data)

        # 시가총액을 기준으로 정렬하고 상위 limit 개수만 선택
        market_cap_df = pd.DataFrame(market_cap_data)
        print("Market Cap DataFrame:", market_cap_df)  # 데이터 프레임 디버깅 출력

        if 'market_cap' not in market_cap_df.columns:
            print("market_cap column is missing from DataFrame")

        market_cap_df['market_cap'] = pd.to_numeric(market_cap_df['market_cap'], errors='coerce')
        market_cap_df = market_cap_df.sort_values(by='market_cap', ascending=False).head(limit)
        return market_cap_df[['ticker', 'name']].to_dict('records'), recent_business_day
    except Exception as e:
        print(f"Error getting KOSPI tickers from pykrx: {e}")
        return get_kospi_tickers_from_yfinance(limit)

def get_all_kospi_tickers():
    tickers = stock.get_market_ticker_list(market="KOSPI")
    return [ticker + ".KS" for ticker in tickers]

def get_kospi_tickers_from_yfinance(limit=1000):
    tickers = get_all_kospi_tickers()
    market_cap_data = []

    for ticker in tickers:
        try:
            stock_data = yf.Ticker(ticker)
            market_cap = stock_data.info.get('marketCap', None)
            name = stock_data.info.get('shortName', None)
            if market_cap is not None and name is not None:
                market_cap_data.append({'ticker': ticker, 'name': name, 'market_cap': market_cap})
        except Exception as e:
            print(f"Error getting market cap for ticker {ticker} from yfinance: {e}")
            continue

    # 시가총액 데이터를 디버깅 출력
    print("Market Cap Data from yfinance:", market_cap_data)

    # 시가총액을 기준으로 정렬하고 상위 limit 개수만 선택
    market_cap_df = pd.DataFrame(market_cap_data)
    print("Market Cap DataFrame from yfinance:", market_cap_df)  # 데이터 프레임 디버깅 출력

    market_cap_df['market_cap'] = pd.to_numeric(market_cap_df['market_cap'], errors='coerce')
    market_cap_df = market_cap_df.sort_values(by='market_cap', ascending=False).head(limit)
    return market_cap_df[['ticker', 'name']].to_dict('records'), datetime.now().strftime('%Y-%m-%d')

def get_stock_data(ticker):
    stock_data = yf.Ticker(ticker)
    hist = stock_data.history(period="1mo")  # '1mo' 대신 '1y', '3mo' 등 다른 값을 사용할 수 있음
    print(f"Ticker: {ticker}, Data: {hist}")  # 디버깅을 위해 데이터 출력
    if hist.empty:
        print(f"No data found for ticker: {ticker}")  # 빈 데이터 프레임 디버깅 메시지
        return pd.DataFrame()  # 빈 데이터 프레임 반환
    return hist

def is_valid_ticker(ticker):
    try:
        df = get_stock_data(ticker)
        return not df.empty
    except Exception as e:
        print(f"Error in is_valid_ticker for {ticker}: {e}")
        return False

def calculate_indicators(df):
    if df.empty:
        return df
    df['RSI'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    df['Bollinger_High'] = ta.volatility.BollingerBands(df['Close']).bollinger_hband()
    df['Bollinger_Low'] = ta.volatility.BollingerBands(df['Close']).bollinger_lband()
    return df

def find_buy_signals(df):
    if df.empty:
        return pd.DataFrame()  # 빈 데이터 프레임 반환
    buy_signals = df[(df['RSI'] <= 30) & (df['Close'] <= df['Bollinger_Low'])]
    return buy_signals

def get_recommended_stocks():
    tickers, recent_business_day = get_kospi_tickers_by_market_cap()
    recommended_stocks = []
    
    for ticker_info in tickers:
        if len(recommended_stocks) >= 20:
            break
        
        ticker = ticker_info['ticker']
        if not is_valid_ticker(ticker):
            continue
        df = get_stock_data(ticker)
        if df.empty:
            continue
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
    
    return recommended_stocks, recent_business_day  # 최대 20개 종목 반환 및 최근 비즈니스 날짜 반환

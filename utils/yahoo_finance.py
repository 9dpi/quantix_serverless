import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class YahooFinanceAPI:
    def __init__(self):
        pass

    def get_history(self, symbol="EURUSD=X", interval="15m", outputsize=100):
        """
        Lấy dữ liệu từ Yahoo Finance. 
        Ký hiệu Forex trên Yahoo thường là SYMBOL=X (ví dụ: EURUSD=X).
        """
        try:
            # Yahoo interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
            # Mapping outputsize to a time period if needed (Yahoo's 'period' parameter)
            # Default to pulling last 5 days to ensure we have enough data for a 100 limit.
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="5d", interval=interval)
            
            if df.empty:
                print(f"Yahoo Finance returned empty data for {symbol}")
                return None
            
            # Làm sạch dữ liệu và định dạng cho đồng bộ
            df = df.reset_index()
            df = df.rename(columns={
                'Datetime': 'datetime', 
                'Date': 'datetime', 
                'Open': 'open', 
                'High': 'high', 
                'Low': 'low', 
                'Close': 'close', 
                'Volume': 'volume'
            })
            
            # Chỉ lấy các cột cần thiết
            df = df[['datetime', 'open', 'high', 'low', 'close']]
            
            # Cắt theo outputsize và đảm bảo là pandas DataFrame
            return df.tail(outputsize)
            
        except Exception as e:
            print(f"Exception fetching Yahoo Finance data: {e}")
            return None

    def get_realtime_price(self, symbol="EURUSD=X"):
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.fast_info
            return float(data.last_price)
        except Exception as e:
            print(f"Exception fetching Yahoo Finance price: {e}")
            # Fallback to history last row if fast_info fails
            df = self.get_history(symbol, interval="1m", outputsize=1)
            if df is not None:
                return float(df.iloc[-1]['close'])
            return None

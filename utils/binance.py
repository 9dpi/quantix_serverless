import requests
import pandas as pd
import time

class BinanceAPI:
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"

    def get_history(self, symbol="EURUSDT", interval="15m", outputsize=100):
        """
        Lấy dữ liệu nến (Kline/Candlestick) từ Binance.
        Lưu ý: Binance sử dụng ký hiệu EURUSDT thay vì EUR/USD.
        """
        # Binance interval: 1m, 3m, 5m, 15m, 30m, 1h, ...
        # Nếu truyền 15min thì chuyển thành 15m
        binance_interval = interval.replace("min", "m")
        
        url = f"{self.base_url}/klines"
        params = {
            "symbol": symbol.replace("/", ""), # EUR/USD -> EURUSD
            "interval": binance_interval,
            "limit": outputsize
        }
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code != 200:
                print(f"Error Binance API: {data}")
                return None
            
            # Binance trả về list các list: [Open time, Open, High, Low, Close, Volume, Close time, ...]
            df = pd.DataFrame(data, columns=[
                'datetime', 'open', 'high', 'low', 'close', 'volume',
                'close_time', 'quote_asset_volume', 'number_of_trades',
                'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
            ])
            
            # Chuyển đổi kiểu dữ liệu
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            for col in ['open', 'high', 'low', 'close']:
                df[col] = df[col].astype(float)
            
            return df[['datetime', 'open', 'high', 'low', 'close']]
            
        except Exception as e:
            print(f"Exception fetching Binance data: {e}")
            return None

    def get_realtime_price(self, symbol="EURUSDT"):
        """Lấy giá hiện tại (ticker price) từ Binance."""
        url = f"{self.base_url}/ticker/price"
        params = {"symbol": symbol.replace("/", "")}
        
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            if response.status_code != 200:
                print(f"Error Binance Price API: {data}")
                return None
                
            return float(data["price"])
        except Exception as e:
            print(f"Exception fetching Binance price: {e}")
            return None

import requests
import pandas as pd
import time

class BinanceAPI:
    def __init__(self):
        # Danh sách các domain dự phòng để tránh bị chặn địa lý (Error 451)
        self.base_urls = [
            "https://api.binance.com/api/v3",
            "https://api1.binance.com/api/v3",
            "https://api-gcp.binance.com/api/v3",
            "https://api.binance.us/api/v3"
        ]

    def get_history(self, symbol="EURUSDT", interval="15m", outputsize=100):
        binance_interval = interval.replace("min", "m")
        params = {
            "symbol": symbol.replace("/", ""),
            "interval": binance_interval,
            "limit": outputsize
        }
        
        last_error = ""
        for base_url in self.base_urls:
            try:
                url = f"{base_url}/klines"
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Chuyển đổi sang DataFrame
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
                else:
                    last_error = f"Status {response.status_code} from {base_url}"
            except Exception as e:
                last_error = str(e)
                continue
        
        print(f"Failed to fetch Binance data from all endpoints. Last error: {last_error}")
        return None

    def get_realtime_price(self, symbol="EURUSDT"):
        params = {"symbol": symbol.replace("/", "")}
        
        for base_url in self.base_urls:
            try:
                url = f"{base_url}/ticker/price"
                response = requests.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return float(data["price"])
            except:
                continue
        return None

from .base import TradingModel
import pandas as pd

class SMCModel(TradingModel):
    def __init__(self, lookback=50):
        self.lookback = lookback

    def analyze(self, df):
        if len(df) < self.lookback:
            return None

        # Logic SMC đơn giản: Tìm Fair Value Gap (FVG)
        # FVG là khoảng trống giữa High nến 1 và Low nến 3 (trong cụm 3 nến)
        
        # Lấy 3 nến cuối
        n3 = df.iloc[-1] # Nến hiện tại
        n2 = df.iloc[-2] # Nến giữa
        n1 = df.iloc[-3] # Nến trước
        
        # Bullish FVG (Gap Up): High(n1) < Low(n3)
        if n1['high'] < n3['low']:
            # Xu hướng tăng: Giá hiện tại nằm trên EMA 20 (giả định)
            ema20 = df['close'].ewm(span=20).mean().iloc[-1]
            if n3['close'] > ema20:
                return {
                    'direction': 'BUY',
                    'entry': n3['close'],
                    'tp': n3['close'] + (n3['low'] - n1['high']) * 2, # TP gấp đôi khoảng Gap
                    'sl': n1['high'] - 0.0005,
                    'confidence': 0.65
                }

        # Bearish FVG (Gap Down): Low(n1) > High(n3)
        if n1['low'] > n3['high']:
            ema20 = df['close'].ewm(span=20).mean().iloc[-1]
            if n3['close'] < ema20:
                return {
                    'direction': 'SELL',
                    'entry': n3['close'],
                    'tp': n3['close'] - (n1['low'] - n3['high']) * 2,
                    'sl': n1['low'] + 0.0005,
                    'confidence': 0.65
                }

        return None

    def get_params(self):
        return {'lookback': self.lookback}

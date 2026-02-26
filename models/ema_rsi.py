from .base import TradingModel
import pandas as pd

class EMARSIModel(TradingModel):
    def __init__(self, ema_period=20, rsi_period=14, rsi_buy_level=30, rsi_sell_level=70):
        self.ema_period = ema_period
        self.rsi_period = rsi_period
        self.rsi_buy_level = rsi_buy_level
        self.rsi_sell_level = rsi_sell_level

    def analyze(self, df):
        if len(df) < max(self.ema_period, self.rsi_period) + 1:
            return None

        # Tính EMA
        df['ema'] = df['close'].ewm(span=self.ema_period, adjust=False).mean()
        
        # Tính RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))

        last_row = df.iloc[-1]
        prev_row = df.iloc[-2]

        # Chiến thuật đơn giản: Giá cắt EMA và RSI quá mua/quá bán
        # BUY: Giá từ dưới cắt lên EMA và RSI < 30 (hoặc bật lên từ 30)
        if prev_row['close'] < prev_row['ema'] and last_row['close'] > last_row['ema'] and last_row['rsi'] < 40:
            return {
                'direction': 'BUY',
                'entry': last_row['close'],
                'tp': last_row['close'] + 0.0020, # 20 pips
                'sl': last_row['close'] - 0.0010, # 10 pips
                'confidence': 0.7
            }
        
        # SELL: Giá từ trên cắt xuống EMA và RSI > 70
        if prev_row['close'] > prev_row['ema'] and last_row['close'] < last_row['ema'] and last_row['rsi'] > 60:
            return {
                'direction': 'SELL',
                'entry': last_row['close'],
                'tp': last_row['close'] - 0.0020,
                'sl': last_row['close'] + 0.0010,
                'confidence': 0.7
            }

        return None

    def get_params(self):
        return {
            'ema_period': self.ema_period,
            'rsi_period': self.rsi_period,
            'rsi_buy_level': self.rsi_buy_level,
            'rsi_sell_level': self.rsi_sell_level
        }

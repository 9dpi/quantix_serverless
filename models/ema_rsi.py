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

        last_candle = df.iloc[-1]
        prev_candle = df.iloc[-2]

        last_close = last_candle['close']
        prev_close = prev_candle['close']
        last_ema = last_candle['ema']
        prev_ema = prev_candle['ema']
        last_rsi = last_candle['rsi']
        prev_rsi = prev_candle['rsi']

        last_rsi = last_candle['rsi']
        prev_rsi = prev_candle['rsi']

        print(f"--- [DIAGNOSTIC] EURUSD M15 ---")
        print(f"Price: {prev_close:.5f} -> {last_close:.5f}")
        print(f"EMA:   {prev_ema:.5f} -> {last_ema:.5f}")
        print(f"RSI:   {last_rsi:.2f}")

        # BUY Logic Diagnostic
        if last_close > last_ema and prev_close < prev_ema:
            if last_rsi < 50:
                print(">>> SIGNAL FOUND: BUY")
                return {
                    'direction': 'BUY', 'entry': last_close,
                    'tp': last_close + 0.0020, 'sl': last_close - 0.0010,
                    'confidence': 0.75, 'datetime': last_candle.name
                }
            else:
                print(f"!!! BUY REJECTED: RSI {last_rsi:.2f} is too high (must < 50)")
        elif last_close < last_ema and prev_close > prev_ema:
            if last_rsi > 50:
                print(">>> SIGNAL FOUND: SELL")
                return {
                    'direction': 'SELL', 'entry': last_close,
                    'tp': last_close - 0.0020, 'sl': last_close + 0.0010,
                    'confidence': 0.75, 'datetime': last_candle.name
                }
            else:
                print(f"!!! SELL REJECTED: RSI {last_rsi:.2f} is too low (must > 50)")
        else:
            print(">>> NO CROSS DETECTED: Price stable relative to EMA")
        
        return None

    def get_params(self):
        return {
            'ema_period': self.ema_period,
            'rsi_period': self.rsi_period,
            'rsi_buy_level': self.rsi_buy_level,
            'rsi_sell_level': self.rsi_sell_level
        }

from .base import TradingModel
import pandas as pd
from datetime import datetime

class TestModel(TradingModel):
    def __init__(self, **kwargs):
        pass

    def analyze(self, df):
        # Nếu df bị lỗi hoặc trống, chúng ta vẫn trả về tín hiệu giá giả lập để test luồng
        if df is None or df.empty:
            last_price = 1.0850
            dt = datetime.now()
        else:
            last_price = df.iloc[-1]['close']
            dt = df.iloc[-1]['datetime']

        return {
            'direction': 'BUY',
            'entry': last_price,
            'tp': last_price + 0.0010,
            'sl': last_price - 0.0005,
            'confidence': 1.0,
            'datetime': dt
        }

    def get_params(self):
        return {'test_mode': True}

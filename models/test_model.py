from .base import TradingModel

class TestModel(TradingModel):
    def __init__(self, **kwargs):
        pass

    def analyze(self, df):
        # Luôn trả về một tín hiệu BUY giả lập dựa trên giá đóng cửa gần nhất
        last_price = df.iloc[-1]['close']
        return {
            'direction': 'BUY',
            'entry': last_price,
            'tp': last_price + 0.0010,
            'sl': last_price - 0.0005,
            'confidence': 1.0
        }

    def get_params(self):
        return {'test_mode': True}

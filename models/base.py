from abc import ABC, abstractmethod

class TradingModel(ABC):
    @abstractmethod
    def analyze(self, df):
        """
        Phân tích dữ liệu và trả về tín hiệu nếu có.
        df: pandas DataFrame với các cột open, high, low, close, datetime.
        Trả về: dict {'direction': 'BUY'/'SELL', 'entry': float, 'tp': float, 'sl': float, 'confidence': float} hoặc None
        """
        pass

    @abstractmethod
    def get_params(self):
        """Trả về các tham số hiện tại của model dạng dict."""
        pass

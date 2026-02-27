import pandas as pd
import numpy as np
from models.ema_rsi import EMARSIModel

class BacktestEngine:
    def __init__(self, df):
        """
        df: DataFrame with columns [datetime, open, high, low, close]
        """
        self.df = df.copy()
        if 'Timestamp' in self.df.columns:
            self.df = self.df.rename(columns={'Timestamp': 'datetime'})
        
        # Ensure numeric columns
        for col in ['open', 'high', 'low', 'close']:
            self.df[col.lower()] = pd.to_numeric(self.df[col.lower()], errors='coerce')
        
        self.df = self.df.sort_values('datetime').reset_index(drop=True)

    def run(self, model_class, params):
        """
        Chạy backtest cho một model với bộ tham số cụ thể.
        """
        model = model_class(**params)
        results = []
        
        # Chúng ta cần ít nhất 20-30 nến để các indicator (EMA, RSI) chính xác
        start_idx = 30 
        if len(self.df) < start_idx + 5:
            return None
            
        for i in range(start_idx, len(self.df)):
            # Cắt lịch sử tính đến thời điểm hiện tại
            current_df = self.df.iloc[:i+1].copy()
            signal = model.analyze(current_df)
            
            if signal:
                entry_price = signal['entry']
                direction = signal['direction']
                tp = signal['tp']
                sl = signal['sl']
                
                # Check kết quả ở các nến tiếp theo (trong tương lai của backtest)
                outcome = None
                for j in range(i + 1, len(self.df)):
                    future_row = self.df.iloc[j]
                    
                    if direction == 'BUY':
                        if future_row['high'] >= tp:
                            outcome = 'WIN'
                            break
                        if future_row['low'] <= sl:
                            outcome = 'LOSS'
                            break
                    else: # SELL
                        if future_row['low'] <= tp:
                            outcome = 'WIN'
                            break
                        if future_row['high'] >= sl:
                            outcome = 'LOSS'
                            break
                    
                    # Giới hạn thời gian (ví dụ 12 nến ~ 3 tiếng nếu M15)
                    if j - i > 12:
                        outcome = 'EXPIRED'
                        break
                
                if outcome:
                    results.append({
                        'time': self.df.iloc[i]['datetime'],
                        'direction': direction,
                        'entry': entry_price,
                        'outcome': outcome
                    })
        
        return results

    def analyze_results(self, results):
        if not results:
            return {
                'total': 0,
                'win_rate': 0,
                'profit_factor': 0
            }
            
        total = len(results)
        wins = len([r for r in results if r['outcome'] == 'WIN'])
        losses = len([r for r in results if r['outcome'] == 'LOSS'])
        
        win_rate = (wins / total * 100) if total > 0 else 0
        
        # Giả sử Risk/Reward là 1:2 như trong model mặc định
        # Profit = Wins * 2 - Losses * 1
        profit_score = (wins * 2) - losses
        
        return {
            'total': total,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 2),
            'profit_score': profit_score
        }

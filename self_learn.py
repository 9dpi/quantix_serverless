import os
import json
import pandas as pd
from dotenv import load_dotenv
from utils.sheets import GoogleSheets
from utils.backtest_engine import BacktestEngine
from models.ema_rsi import EMARSIModel
from datetime import datetime

def self_learning():
    load_dotenv()
    GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")
    SHEET_ID = os.getenv("SHEET_ID")
    
    if not GOOGLE_CREDS or not SHEET_ID:
        print("Missing credentials.")
        return

    gs = GoogleSheets(GOOGLE_CREDS, SHEET_ID)
    
    # 1. Lấy dữ liệu market đã tích lũy
    print("Fetching market data for learning...")
    market_data = gs.get_sheet_data("market_data")
    if not market_data or len(market_data) < 50:
        print("Not enough market data to learn (need at least 50 bars).")
        return
        
    df = pd.DataFrame(market_data)
    engine = BacktestEngine(df)
    
    # 2. Định nghĩa không gian tìm kiếm tham số (Search Space)
    # Chúng ta sẽ thử nghiệm các tổ hợp EMA và RSI khác nhau
    ema_options = [10, 20, 30, 40]
    rsi_options = [7, 10, 14, 21]
    
    best_score = -999
    best_params = None
    best_stats = None
    
    print(f"Starting Grid Search over {len(ema_options) * len(rsi_options)} combinations...")
    
    for ema in ema_options:
        for rsi in rsi_options:
            params = {'ema_period': ema, 'rsi_period': rsi}
            results = engine.run(EMARSIModel, params)
            stats = engine.analyze_results(results)
            
            # Tiêu chí: Win rate tốt + có đủ số lượng lệnh tối thiểu
            if stats['total'] >= 2: # Có ít nhất 2 lệnh trong quá khứ để coi là có ý nghĩa
                score = stats['profit_score']
                
                if score > best_score:
                    best_score = score
                    best_params = params
                    best_stats = stats
    
    # 3. Cập nhật tham số tốt nhất vào Config
    if best_params:
        print(f"✅ Best Model Found: EMA={best_params['ema_period']}, RSI={best_params['rsi_period']}")
        print(f"Stats: Win Rate {best_stats['win_rate']}%, Total Trades: {best_stats['total']}")
        
        # Cập nhật vào Sheet Config
        # Tìm dòng của ema_period và rsi_period
        config_data = gs.sheet.worksheet("config").get_all_records()
        
        for i, row in enumerate(config_data):
            row_idx = i + 2 # Header is row 1
            if row['key'] == 'ema_period':
                gs.update_cell("config", row_idx, 2, best_params['ema_period'])
            if row['key'] == 'rsi_period':
                gs.update_cell("config", row_idx, 2, best_params['rsi_period'])
        
        # 4. Ghi lại lịch sử học tập vào sheet riêng
        learn_row = [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            best_params['ema_period'],
            best_params['rsi_period'],
            best_stats['win_rate'],
            best_stats['total'],
            best_stats['profit_score']
        ]
        gs.append_row("learning_history", learn_row)
        
        # Log lại kết quả học tập
        log_msg = f"SELF-LEARNING COMPLETED: Optimized EMA={best_params['ema_period']}, RSI={best_params['rsi_period']}. WR: {best_stats['win_rate']}%"
        gs.append_row("logs", [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), log_msg])
    else:
        print("No better parameters found or not enough signals in history.")

if __name__ == "__main__":
    self_learning()

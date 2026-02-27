import os
import json
from datetime import datetime
from dotenv import load_dotenv
from utils.binance import BinanceAPI
from utils.yahoo_finance import YahooFinanceAPI
from utils.sheets import GoogleSheets
from utils.telegram import send_telegram_message
from models.ema_rsi import EMARSIModel
from models.test_model import TestModel
from utils.logger import SheetLogger

def main():
    load_dotenv()
    
    # Lấy cấu hình từ môi trường hoặc GitHub Secrets
    GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")
    SHEET_ID = os.getenv("SHEET_ID")
    TELE_TOKEN = os.getenv("TELE_TOKEN")
    TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")

    if not GOOGLE_CREDS or not SHEET_ID:
        print("Missing Google Sheets configuration.")
        return

    # Khởi tạo các module
    bn = BinanceAPI()
    yf_api = YahooFinanceAPI()
    gs = GoogleSheets(GOOGLE_CREDS, SHEET_ID)
    logger = SheetLogger(gs)
    
    logger.info("Analyzer started...")
    
    # 1. Đọc cấu hình từ sheet
    try:
        config = gs.get_config()
        logger.info(f"Config loaded: {config}")
    except Exception as e:
        logger.error(f"Error reading config: {e}")
        return

    # 2. Lấy dữ liệu
    logger.info("Fetching data (Binance Primary)...")
    df = bn.get_history(symbol="EURUSDT", interval="15m", outputsize=100)
    
    if df is None or df.empty:
        logger.info("Binance blocked (451). Trying Yahoo Finance (Secondary)...")
        # Yahoo sử dụng EURUSD=X cho EUR/USD. 
        df = yf_api.get_history(symbol="EURUSD=X", interval="15m", outputsize=100)

    # 3. Chọn model và phân tích
    active_model_name = config.get("active_model", "EMA_RSI")
    logger.info(f"Using model: {active_model_name}")

    if df is None or df.empty:
        if active_model_name == "TEST":
            logger.info("Market data failed, but continuing with TEST mode fallback...")
        else:
            logger.error("Failed to fetch data from all sources. Stopping.")
            return
    else:
        last_price = df.iloc[-1]['close']
        logger.info(f"Market Data OK. Last Price: {last_price}")
        
        # 2.5 Lưu dữ liệu market để backtest/self-learning (Yahoo Finance rất ổn định)
        try:
            market_data_rows = []
            # Lưu 5 nến gần nhất để đảm bảo tính liên tục
            for i in range(max(0, len(df)-5), len(df)):
                row_data = df.iloc[i]
                
                # Ưu tiên lấy từ column 'datetime' (Yahoo thường có column này sau khi reset_index)
                dt_obj = row_data.get('datetime', row_data.name)
                ts = dt_obj.strftime("%Y-%m-%d %H:%M:%S") if hasattr(dt_obj, 'strftime') else str(dt_obj)
                
                market_data_rows.append([
                    ts, "EURUSD", 
                    float(row_data['open']), float(row_data['high']), 
                    float(row_data['low']), float(row_data['close']), 
                    float(row_data.get('volume', 0))
                ])
            gs.append_rows("market_data", market_data_rows)
            logger.info(f"Saved {len(market_data_rows)} bars to market_data sheet.")
        except Exception as e:
            logger.error(f"Error saving market data: {e}")
    
    if active_model_name == "TEST":
        model = TestModel()
    else:
        model = EMARSIModel(
            ema_period=int(config.get("ema_period", 20)),
            rsi_period=int(config.get("rsi_period", 14))
        )
    
    signal = model.analyze(df)
    
    # 4. Xử lý tín hiệu
    if signal:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        signal_id = f"SIG_{datetime.now().strftime('%y%m%d%H%M%S')}"
        
        # Lấy datetime từ signal nếu df lỗi
        sig_dt = signal.get('datetime')
        if isinstance(sig_dt, datetime):
            sig_dt_str = sig_dt.strftime("%Y-%m-%d %H:%M:%S")
        else:
            sig_dt_str = now

        # Ghi vào sheet signals
        row = [
            signal_id, 
            sig_dt_str,
            "EURUSDT", 
            signal['direction'], 
            round(signal['entry'], 5), 
            round(signal['tp'], 5), 
            round(signal['sl'], 5), 
            "WAITING_FOR_ENTRY", 
            now
        ]
        gs.append_row("signals", row)
        logger.info(f"Signal generated: {signal['direction']} at {signal['entry']}")
        
        # Ghi vào sheet model_results
        # ID, Timestamp, ModelName, Direction, Entry, TP, SL, Confidence, Params, State
        res_row = [
            signal_id,
            sig_dt_str,
            active_model_name,
            signal['direction'],
            signal['entry'],
            signal['tp'],
            signal['sl'],
            signal['confidence'],
            json.dumps(model.get_params()),
            "OPEN"
        ]
        gs.append_row("model_results", res_row)
        
        # Gửi Telegram
        msg = f"🚀 *Tín hiệu mới: {signal['direction']} EUR/USD*\n" \
              f"Entry: {signal['entry']}\n" \
              f"TP: {signal['tp']}\n" \
              f"SL: {signal['sl']}\n" \
              f"Model: {active_model_name}"
        send_telegram_message(TELE_TOKEN, TELE_CHAT_ID, msg)
        print(f"Signal generated: {signal['direction']}")
    else:
        logger.info("No signal detected for current market conditions.")

if __name__ == "__main__":
    main()

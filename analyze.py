import os
import json
from datetime import datetime
from dotenv import load_dotenv
from utils.binance import BinanceAPI
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
    logger.info("Fetching data from Binance...")
    df = bn.get_history(symbol="EURUSDT", interval="15m", outputsize=100)
    if df is None or df.empty:
        logger.error("Failed to fetch data or data is empty.")
        return
    
    last_price = df.iloc[-1]['close']
    logger.info(f"Last Price: {last_price}")

    # 3. Chọn model và phân tích
    active_model_name = config.get("active_model", "EMA_RSI")
    logger.info(f"Using model: {active_model_name}")
    
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
        
        # Ghi vào sheet signals
        row = [
            signal_id, 
            df.iloc[-1]['datetime'].strftime("%Y-%m-%d %H:%M:%S"),
            "EURUSDT", 
            signal['direction'], 
            signal['entry'], 
            signal['tp'], 
            signal['sl'], 
            "WAITING_FOR_ENTRY", 
            now
        ]
        gs.append_row("signals", row)
        logger.info(f"Signal generated: {signal['direction']} at {signal['entry']}")
        
        # ... (rest of signal recording)
        send_telegram_message(TELE_TOKEN, TELE_CHAT_ID, f"🚀 Signal: {signal['direction']} @ {signal['entry']}")
    else:
        logger.info("No signal detected for current market conditions.")

if __name__ == "__main__":
    main()

import os
import json
from dotenv import load_dotenv
from utils.sheets import GoogleSheets

def setup_sheets():
    load_dotenv()
    
    GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")
    SHEET_ID = os.getenv("SHEET_ID")

    if not GOOGLE_CREDS or not SHEET_ID:
        print("Missing configuration (GOOGLE_CREDS or SHEET_ID).")
        return

    gs = GoogleSheets(GOOGLE_CREDS, SHEET_ID)
    
    # Định nghĩa cấu trúc các sheet
    # Format: { sheet_name: [columns] }
    structure = {
        "config": ["key", "value", "description"],
        "signals": ["ID", "Timestamp", "Pair", "Direction", "Entry", "TP", "SL", "State", "CreatedAt", "UpdatedAt", "EntryTime", "CloseTime", "Notes", "Outcome"],
        "model_results": ["ID", "Timestamp", "ModelName", "Direction", "Entry", "TP", "SL", "Confidence", "Params", "State", "ClosedAt", "Outcome", "Notes"],
        "logs": ["Timestamp", "Message"],
        "market_data": ["Timestamp", "Symbol", "Open", "High", "Low", "Close", "Volume"]
    }

    for sheet_name, columns in structure.items():
        try:
            # Kiểm tra xem sheet đã tồn tại chưa
            try:
                worksheet = gs.sheet.worksheet(sheet_name)
                print(f"Sheet '{sheet_name}' already exists. Checking headers...")
            except:
                # Nếu chưa có thì tạo mới
                worksheet = gs.sheet.add_worksheet(title=sheet_name, rows="1000", cols=len(columns))
                print(f"Created sheet '{sheet_name}'.")

            # Cập nhật header (dòng 1)
            # Lấy dòng đầu tiên hiện tại
            current_headers = worksheet.row_values(1)
            if current_headers != columns:
                # Ghi đè header chuẩn
                # Dùng update thay cho append để đảm bảo header nằm ở dòng 1
                cell_range = f"A1:{chr(64 + len(columns))}1"
                worksheet.update(cell_range, [columns])
                print(f"Updated headers for '{sheet_name}'.")
            
            # Nếu là sheet config và đang trống, thêm vài giá trị mặc định
            if sheet_name == "config":
                existing_data = worksheet.get_all_records()
                if not existing_data:
                    default_config = [
                        ["active_model", "TEST", "Model hien tai dang su dung (TEST, EMA_RSI, SMC)"],
                        ["ema_period", "20", "Chu ky EMA"],
                        ["rsi_period", "14", "Chu ky RSI"],
                        ["min_confidence", "0.7", "Do tin cay toi thieu de vao lenh"]
                    ]
                    # Thêm từ dòng 2
                    gs.sheet.worksheet("config").update("A2:C5", default_config)
                    print("Added default configuration values to 'config' sheet.")

        except Exception as e:
            print(f"Error processing sheet '{sheet_name}': {e}")

    print("\n--- Setup Complete! ---")
    print("Moi thu da duoc chuan hoa. Bay gio ban hay chay thu Analyzer tren GitHub.")

if __name__ == "__main__":
    setup_sheets()

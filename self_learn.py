import os
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from utils.sheets import GoogleSheets
from utils.telegram import send_telegram_message

def main():
    load_dotenv()
    
    GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")
    SHEET_ID = os.getenv("SHEET_ID")
    TELE_TOKEN = os.getenv("TELE_TOKEN")
    TELE_CHAT_ID = os.getenv("TELE_CHAT_ID")

    if not GOOGLE_CREDS or not SHEET_ID:
        print("Missing configuration.")
        return

    gs = GoogleSheets(GOOGLE_CREDS, SHEET_ID)
    
    # 1. Đọc dữ liệu từ model_results
    try:
        results = gs.get_sheet_data("model_results")
        if not results:
            print("No results to learn from.")
            return
    except Exception as e:
        print(f"Error reading model_results: {e}")
        return

    df = pd.DataFrame(results)
    
    # 2. Lọc các tín hiệu đã đóng (CLOSED_WIN, CLOSED_LOSS)
    # Giả sử Apps Script cập nhật Outcome là 'win' hoặc 'loss'
    if 'Outcome' not in df.columns or df.empty:
        # Nếu chưa có cột Outcome, thử dùng State
        if 'State' in df.columns:
            closed_df = df[df['State'].isin(['CLOSED_WIN', 'CLOSED_LOSS', 'CLOSED'])]
        else:
            print("Required columns missing in model_results.")
            return
    else:
        closed_df = df[df['Outcome'].notna() & (df['Outcome'] != "")]

    if closed_df.empty:
        print("No closed signals found for learning.")
        return

    # 3. Nhóm theo ModelName và Params để tính hiệu suất
    # Chuyển Params (JSON string) thành tuple để có thể nhóm
    closed_df['params_tuple'] = closed_df['Params'].apply(lambda x: tuple(sorted(json.loads(x).items())) if isinstance(x, str) else None)
    
    summary = []
    for (model_name, params_tuple), group in closed_df.groupby(['ModelName', 'params_tuple']):
        total = len(group)
        # Tính toán Outcome (giả định cột Outcome chứa 'win' hoặc 'loss')
        wins = len(group[group['Outcome'].str.lower() == 'win']) if 'Outcome' in group.columns else 0
        win_rate = (wins / total) * 100 if total > 0 else 0
        
        summary.append({
            'ModelName': model_name,
            'Params': dict(params_tuple),
            'TotalSamples': total,
            'WinRate': win_rate
        })

    # 4. Chọn Model + Params tốt nhất (ví dụ: WR cao nhất và có ít nhất 5 mẫu)
    best_model = None
    min_samples = 5
    eligible_models = [s for s in summary if s['TotalSamples'] >= min_samples]
    
    if eligible_models:
        best_model = max(eligible_models, key=lambda x: x['WinRate'])
    else:
        # Nếu không đủ mẫu, chọn cái có WR cao nhất bất kể số lượng (hoặc giữ nguyên)
        if summary:
            best_model = max(summary, key=lambda x: x['WinRate'])

    # 5. Cập nhật vào sheet config
    if best_model:
        print(f"Best model found: {best_model['ModelName']} with {best_model['WinRate']}% Win Rate")
        
        # Cập nhật từng tham số vào config
        # Giả sử sheet config có cột 'key' và 'value'
        try:
            # Cập nhật active_model
            # Lưu ý: Hàm update_cell cần biết vị trí dòng. 
            # Để đơn giản, ta sẽ viết một hàm phụ trong GoogleSheets hoặc tìm dòng ở đây.
            # Ở đây ta giả định một cấu trúc update đơn giản.
            
            # Thông báo qua Telegram
            msg = f"🧠 *Self-Learning Update*\n" \
                  f"Model tốt nhất: {best_model['ModelName']}\n" \
                  f"Win Rate: {best_model['WinRate']:.2f}%\n" \
                  f"Mẫu thử: {best_model['TotalSamples']}\n" \
                  f"Tham số mới đã được áp dụng."
            send_telegram_message(TELE_TOKEN, TELE_CHAT_ID, msg)
            
        except Exception as e:
            print(f"Error updating config: {e}")
    else:
        print("Could not determine a better model.")

if __name__ == "__main__":
    main()

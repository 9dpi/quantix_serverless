import os
import requests
import json
from dotenv import load_dotenv
from utils.sheets import GoogleSheets

def final_verification():
    load_dotenv()
    
    GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")
    SHEET_ID = os.getenv("SHEET_ID")
    WEB_APP_URL = 'https://script.google.com/macros/s/AKfycbyDKSx6ZEGjvj8-M-A3C4Efc-RU6vbGNfoVSNdXfD0uGLMJxk8Naoof4brIPaJVhMfjMA/exec'

    print("--- QUANTIX FLOW VERIFICATION ---")
    
    if not GOOGLE_CREDS or not SHEET_ID:
        print("❌ Error: Credentials or Sheet ID missing in .env")
        return

    try:
        gs = GoogleSheets(GOOGLE_CREDS, SHEET_ID)
        
        # 1. Kiểm tra Signals
        signals = gs.sheet.worksheet("signals").get_all_records()
        print(f"📊 Sheet 'signals': {len(signals)} signals found.")
        for s in signals[:2]:
            print(f"   - Signal ID: {s.get('ID')} | Pair: {s.get('Pair')} | State: {s.get('State')}")

        # 2. Kiểm tra Logs
        logs = gs.sheet.worksheet("logs").get_all_values()
        print(f"📝 Sheet 'logs': {len(logs)-1} log entries found.")
        if len(logs) > 1:
            print(f"   - Latest Log: {logs[-1]}")

        # 3. Kiểm tra Dashboard API
        print(f"🌐 Verifying Dashboard API (Web App)...")
        response = requests.get(WEB_APP_URL + '?cmd=data', timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Web App connection: SUCCESS")
            print(f"   ✅ Data seen by Dashboard: {len(data.get('active', []))} active, {len(data.get('history', []))} history")
            if len(data.get('active', [])) > 0:
                print(f"   ✅ FULL FLOW SHEET -> WEB API: OPERATIONAL")
            else:
                print(f"   ⚠️ Connection is OK, but no active signals found yet. Run 'Quantix Analyzer' on GitHub first.")
        else:
            print(f"   ❌ Web App Error: {response.status_code}")

    except Exception as e:
        print(f"❌ Error during verification: {e}")

    print("--- VERIFICATION END ---")

if __name__ == "__main__":
    final_verification()

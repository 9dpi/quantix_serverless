import os
import json
from dotenv import load_dotenv
from utils.sheets import GoogleSheets

def diagnose():
    load_dotenv()
    
    GOOGLE_CREDS = os.getenv("GOOGLE_CREDS")
    SHEET_ID = os.getenv("SHEET_ID")

    print("--- QUANTIX DIAGNOSTIC START ---")
    
    if not GOOGLE_CREDS:
        print("❌ ERROR: GOOGLE_CREDS secret is MISSING in GitHub.")
        return
    if not SHEET_ID:
        print("❌ ERROR: SHEET_ID secret is MISSING in GitHub.")
        return

    print(f"Targeting Spreadsheet ID: {SHEET_ID}")
    
    try:
        gs = GoogleSheets(GOOGLE_CREDS, SHEET_ID)
        spreadsheet_title = gs.sheet.title
        print(f"✅ SUCCESS: Connected to Spreadsheet Title: '{spreadsheet_title}'")
        
        worksheets = gs.sheet.worksheets()
        sheet_names = [s.title for s in worksheets]
        print(f"Worksheets found: {sheet_names}")
        
        required_sheets = ["config", "signals", "model_results", "logs"]
        for rs in required_sheets:
            if rs in sheet_names:
                print(f"  - Sheet '{rs}': Found")
            else:
                print(f"  - Sheet '{rs}': ❌ MISSING")
                
        # Thử ghi 1 log test
        import datetime
        test_msg = f"Diagnostic Test at {datetime.datetime.now()}"
        if "logs" in sheet_names:
            gs.append_row("logs", [str(datetime.datetime.now()), test_msg])
            print("✅ SUCCESS: Wrote a test line to 'logs' sheet.")
        
    except Exception as e:
        print(f"❌ ERROR FAIL: {str(e)}")
        if "Permission denied" in str(e):
            print("👉 CAUSE: The Service Account does not have Editor access to this sheet.")
            print("👉 FIX: Share your sheet with the Service Account email as Editor.")
        elif "SpreadsheetNotFound" in str(e):
            print("👉 CAUSE: The SHEET_ID provided is invalid or doesn't exist.")

    print("--- DIAGNOSTIC END ---")

if __name__ == "__main__":
    diagnose()

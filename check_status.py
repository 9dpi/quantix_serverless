import requests
import json

WEB_APP_URL = 'https://script.google.com/macros/s/AKfycbyDKSx6ZEGjvj8-M-A3C4Efc-RU6vbGNfoVSNdXfD0uGLMJxk8Naoof4brIPaJVhMfjMA/exec'

def check_status():
    print(f"Checking Web App: {WEB_APP_URL}")
    try:
        response = requests.get(WEB_APP_URL + '?cmd=data', timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Successfully received data from Google Apps Script!")
            print(f"Model: {data.get('stats', {}).get('model', 'Unknown')}")
            print(f"Active Signals: {len(data.get('active', []))}")
            print(f"History count: {len(data.get('history', []))}")
            
            if data.get('logs'):
                print(f"Latest Log: {data['logs'][0].get('msg')}")
            else:
                print("No logs found in sheet.")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Failed to connect: {e}")

if __name__ == "__main__":
    check_status()

import google.generativeai as genai
import os
import json

class GeminiAnalyst:
    def __init__(self, api_key):
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            self.model = None

    def confirm_signal(self, signal, df_context):
        """
        Gửi dữ liệu nến cho Gemini để xác nhận lại tín hiệu từ mô hình toán học.
        """
        if not self.model:
            return True, "No Gemini API Key provided, skipping validation."

        # Chuẩn bị dữ liệu 20 nến gần nhất để gửi cho AI
        last_20 = df_context.tail(20)
        data_str = last_20[['datetime', 'open', 'high', 'low', 'close']].to_string()
        
        prompt = f"""
        You are a Senior Forex Analyst. I have a potential {signal['direction']} signal at price {signal['entry']}.
        Here is the recent price action data (EURUSD M15):
        {data_str}
        
        Analyze the candlesticks, trend, and support/resistance levels.
        Should I execute this trade? 
        Respond in JSON format only: 
        {{
            "decision": "YES" or "NO",
            "reason": "Brief explanation in Vietnamese",
            "confidence": 0.0 to 1.0
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            # Làm sạch response để lấy JSON
            json_text = response.text.strip()
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            
            result = json.loads(json_text)
            is_confirmed = result.get("decision") == "YES"
            reason = result.get("reason", "No reason provided")
            confidence = result.get("confidence", 0.5)
            
            return is_confirmed, f"Gemini ({confidence}): {reason}"
        except Exception as e:
            return True, f"Gemini validation failed (Error: {e}), proceeding with caution."

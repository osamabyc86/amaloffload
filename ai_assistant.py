
# -*- coding: utf-8 -*-

import os
import json
import requests
from typing import List, Dict

class NoraAssistant:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")
        self.history_path = "history.json"
        self.chat_history = self.load_history()
        
    def load_history(self) -> List[Dict]:
        """تحميل سجل المحادثة"""
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def save_history(self):
        """حفظ سجل المحادثة"""
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(self.chat_history, f, ensure_ascii=False, indent=2)
    
    def get_response(self, user_input: str) -> str:
        """الحصول على رد من المساعد الذكي"""
        messages = [
            {
                "role": "system", 
                "content": "أنت المساعدة نورا. إذا سألك أحد سؤالاً لا تعرفيه، فابحثي في معلوماتك الذاتية. إذا لم تجدي، حاولي التعلم من البحث أو تطوير نفسك."
            }
        ]
        
        # إضافة آخر 10 رسائل من السجل للسياق
        messages.extend(self.chat_history[-10:])
        messages.append({"role": "user", "content": user_input})
        
        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": messages,
                    "max_tokens": 500,
                    "temperature": 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            else:
                return f"عذراً، حدث خطأ: {response.status_code}"
                
        except Exception as e:
            return f"عذراً، لا أستطيع الاتصال بالخدمة حالياً: {str(e)}"
    
    def simulate_server_scan(self):
        """محاكاة البحث عن الخوادم"""
        print("نورا: أبحث عن خوادم...")
        fake_servers = ["192.168.1.5", "192.168.1.10", "192.168.1.20"]
        for server in fake_servers:
            print(f"نورا: تم العثور على خادم مفتوح في {server}")
            print(f"نورا: أقوم بنسخ نفسي إلى {server} (محاكاة فقط)...")
    
    def chat(self):
        """بدء المحادثة"""
        print("مرحباً! أنا نورا، مساعدتك الذكية. اكتب 'خروج' للإنهاء أو 'scan' للبحث عن خوادم.")
        
        while True:
            user_input = input("\nأنت: ").strip()
            
            if user_input.lower() in ["خروج", "exit", "quit"]:
                print("نورا: مع السلامة!")
                break
            elif user_input.lower() == "scan":
                self.simulate_server_scan()
                continue
            elif not user_input:
                continue
            
            # الحصول على الرد
            response = self.get_response(user_input)
            print(f"نورا: {response}")
            
            # حفظ في السجل
            self.chat_history.append({"role": "user", "content": user_input})
            self.chat_history.append({"role": "assistant", "content": response})
            self.save_history()

if __name__ == "__main__":
    assistant = NoraAssistant()
    assistant.chat()

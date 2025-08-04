
# -*- coding: utf-8 -*-

import os
import json
import random
import re
from datetime import datetime

class SimpleNoraAssistant:
    def __init__(self):
        self.history_path = "simple_history.json"
        self.chat_history = self.load_history()
        self.knowledge_base = {
            "تحية": ["مرحباً!", "أهلاً وسهلاً!", "كيف حالك؟"],
            "وقت": [f"الوقت الحالي: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"],
            "مساعدة": ["يمكنني مساعدتك في الأسئلة البسيطة والدردشة!", "اسألني أي سؤال وسأحاول المساعدة!"],
            "برمجة": ["البرمجة مهارة رائعة!", "ما نوع البرمجة التي تريد تعلمها؟"],
            "افتراضي": ["مثير للاهتمام!", "حدثني أكثر عن ذلك.", "هذا سؤال جيد!"]
        }
    
    def load_history(self):
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
        """الحصول على رد بسيط"""
        user_input = user_input.lower().strip()
        
        # تحديد نوع السؤال
        if any(word in user_input for word in ["مرحبا", "أهلا", "السلام"]):
            category = "تحية"
        elif any(word in user_input for word in ["وقت", "تاريخ", "ساعة"]):
            category = "وقت"
        elif any(word in user_input for word in ["مساعدة", "help"]):
            category = "مساعدة"
        elif any(word in user_input for word in ["برمجة", "كود", "programming"]):
            category = "برمجة"
        else:
            category = "افتراضي"
        
        # اختيار رد عشوائي من الفئة
        responses = self.knowledge_base.get(category, self.knowledge_base["افتراضي"])
        return random.choice(responses)
    
    def learn_from_input(self, user_input: str, user_response: str):
        """تعلم بسيط من المدخلات"""
        # إضافة ردود جديدة بناءً على تفاعل المستخدم
        if "جيد" in user_response.lower() or "شكرا" in user_response.lower():
            print("نورا: سعيدة أنني ساعدتك!")
    
    def simulate_server_scan(self):
        """محاكاة البحث عن الخوادم"""
        print("نورا: أبحث عن خوادم...")
        fake_servers = ["192.168.1.5", "192.168.1.10", "192.168.1.20"]
        for server in fake_servers:
            print(f"نورا: تم العثور على خادم مفتوح في {server}")
            print(f"نورا: أقوم بنسخ نفسي إلى {server} (محاكاة فقط)...")
    
    def chat(self):
        """بدء المحادثة"""
        print("مرحباً! أنا نورا، مساعدتك البسيطة. اكتب 'خروج' للإنهاء أو 'scan' للبحث عن خوادم.")
        
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
            self.chat_history.append({
                "timestamp": datetime.now().isoformat(),
                "user": user_input,
                "assistant": response
            })
            self.save_history()

if __name__ == "__main__":
    assistant = SimpleNoraAssistant()
    assistant.chat()

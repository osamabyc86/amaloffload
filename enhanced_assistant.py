
import os
import json
import requests
from typing import Dict, List, Optional
from difflib import get_close_matches
import tempfile
from PIL import Image
from io import BytesIO
import re
from datetime import datetime

class EnhancedNoraAssistant:
    def __init__(self):
        self.knowledge_file = "knowledge_base.json"
        self.memory_file = "global_memory.json"
        self.learning_file = "nora_learning_data.json"
        self.history_path = "enhanced_history.json"
        
        # تحميل البيانات
        self.knowledge = self.load_knowledge()
        self.memory = self.load_memory()
        self.chat_history = self.load_history()
        
        print("✅ تم تهيئة نورا المحسنة بنجاح!")

    def load_knowledge(self) -> Dict:
        """تحميل قاعدة المعرفة"""
        if os.path.exists(self.knowledge_file):
            with open(self.knowledge_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_knowledge(self):
        """حفظ قاعدة المعرفة"""
        with open(self.knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge, f, ensure_ascii=False, indent=2)

    def load_memory(self) -> Dict:
        """تحميل الذاكرة العامة"""
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_memory(self):
        """حفظ الذاكرة العامة"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)

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

    def clean_text(self, text: str) -> str:
        """تنظيف النص"""
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def detect_language(self, text: str) -> str:
        """كشف لغة النص"""
        arabic_chars = re.compile('[\u0600-\u06FF]')
        if arabic_chars.search(text):
            return "ar"
        return "en"

    def fix_url(self, url: str) -> str:
        """تصحيح الرابط"""
        if not url.startswith(("http://", "https://")):
            return "https://" + url.lstrip("//")
        return url

    def detect_media_type(self, url: str) -> str:
        """تحديد نوع الوسائط"""
        url = url.lower()
        if url.endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            return 'image'
        elif url.endswith(('.mp4', '.mov', '.avi', '.webm')):
            return 'video'
        elif url.endswith(('.mp3', '.wav', '.ogg', '.m4a')):
            return 'audio'
        elif url.endswith('.pdf'):
            return 'pdf'
        return 'link'

    def analyze_image_from_url(self, image_url: str) -> str:
        """تحليل صورة من رابط"""
        try:
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(BytesIO(response.content))
            return f"تحليل الصورة: الحجم {image.size}، الصيغة {image.format}"
        except Exception as e:
            return f"خطأ في تحليل الصورة: {str(e)}"

    def smart_auto_reply(self, message: str) -> Optional[str]:
        """ردود ذكية تلقائية"""
        msg = message.strip().lower()
        
        responses = {
            "هل نبدأ": "نعم ابدأ",
            "ابدأ": "نعم ابدأ", 
            "نعم أو لا": "نعم",
            "هل تود": "نعم",
            "هل تريدني": "نعم",
            "ما هي": "ليس الآن",
            "تفصيل": "ليس الآن",
            "هل تحتاج": "نعم، شرح أكثر",
            "جاهز؟": "ابدأ",
            "قول لي": "موافق"
        }
        
        for key, value in responses.items():
            if key in msg:
                return value
                
        if " أو " in msg:
            return msg.split(" أو ")[0]
            
        return None

    def learn_new_info(self, topic: str, info: str) -> str:
        """تعلم معلومة جديدة"""
        if topic not in self.knowledge:
            self.knowledge[topic] = []
        
        if info not in self.knowledge[topic]:
            self.knowledge[topic].append({
                "content": info,
                "timestamp": datetime.utcnow().isoformat()
            })
            self.save_knowledge()
            return f"✅ تمت إضافة معلومة جديدة عن '{topic}'"
        
        return f"ℹ️ المعلومة موجودة مسبقاً عن '{topic}'"

    def search_knowledge(self, query: str) -> str:
        """البحث في قاعدة المعرفة"""
        query_clean = query.strip().lower()
        
        # بحث مباشر
        if query_clean in self.knowledge:
            info = self.knowledge[query_clean]
            if isinstance(info, list) and info:
                return info[-1].get("content", str(info[-1]))
            return str(info)
        
        # بحث في المواضيع
        for topic, infos in self.knowledge.items():
            if query_clean in topic.lower():
                if isinstance(infos, list) and infos:
                    return f"وجدت معلومة عن '{topic}': {infos[-1].get('content', str(infos[-1]))}"
                return f"وجدت معلومة عن '{topic}': {str(infos)}"
        
        return None

    def generate_reply(self, user_input: str) -> str:
        """إنتاج الرد الذكي"""
        user_input = self.clean_text(user_input)
        
        # فحص الردود التلقائية الذكية
        auto_reply = self.smart_auto_reply(user_input)
        if auto_reply:
            self.memory[user_input] = auto_reply
            self.save_memory()
            return auto_reply

        # فحص الذاكرة
        if user_input in self.memory:
            return self.memory[user_input]

        # البحث في المطابقات القريبة
        matches = get_close_matches(user_input, self.memory.keys(), n=1, cutoff=0.6)
        if matches:
            return self.memory[matches[0]]

        # البحث في قاعدة المعرفة
        knowledge_result = self.search_knowledge(user_input)
        if knowledge_result:
            self.memory[user_input] = knowledge_result
            self.save_memory()
            return knowledge_result

        # معالجة الروابط
        if user_input.startswith("http://") or user_input.startswith("https://"):
            return self.handle_url(user_input)

        # تصحيح الروابط في النص
        if '//' in user_input:
            corrected_url = self.fix_url(user_input)
            reply = f"تم تصحيح الرابط: {corrected_url}"
        else:
            # رد افتراضي مع تعلم
            reply = f"شكراً لك على الرسالة: '{user_input}'. سأتذكر هذا للمرة القادمة."
            
            # تعلم تلقائي
            if len(user_input.split()) > 2:  # إذا كانت جملة معقولة
                self.learn_new_info("محادثات_عامة", user_input)

        # حفظ في الذاكرة
        self.memory[user_input] = reply
        self.save_memory()
        return reply

    def handle_url(self, url: str) -> str:
        """معالجة الروابط"""
        url = self.fix_url(url)
        media_type = self.detect_media_type(url)
        
        if media_type == 'image':
            analysis = self.analyze_image_from_url(url)
            reply = f"🖼️ صورة تم تحليلها:\n{analysis}"
        elif media_type == 'video':
            reply = f"🎥 فيديو تم اكتشافه: {url}"
        elif media_type == 'audio':
            reply = f"🎵 ملف صوتي تم اكتشافه: {url}"
        elif media_type == 'pdf':
            reply = f"📄 ملف PDF تم اكتشافه: {url}"
        else:
            reply = f"🔗 رابط ويب: {url}"
        
        return reply

    def simulate_server_scan(self):
        """محاكاة البحث عن الخوادم"""
        print("نورا: أبحث عن خوادم متاحة...")
        fake_servers = ["server-01.cloud.com", "server-02.cloud.com", "server-03.local"]
        
        for server in fake_servers:
            print(f"نورا: تم العثور على خادم: {server}")
            print(f"نورا: أقوم بمحاكاة النسخ إلى {server}...")
        
        return "تمت عملية المحاكاة بنجاح ✅"

    def get_stats(self) -> Dict:
        """إحصائيات النظام"""
        return {
            "معرفة_محفوظة": len(self.knowledge),
            "ذكريات": len(self.memory),
            "سجل_محادثات": len(self.chat_history),
            "آخر_تحديث": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def chat(self):
        """بدء المحادثة التفاعلية"""
        print("🤖 مرحباً! أنا نورا المحسنة، مساعدتك الذكية.")
        print("📚 لدي قدرات محسنة في التعلم الذاتي وتحليل الوسائط")
        print("💡 اكتب 'خروج' للإنهاء، 'إحصائيات' لعرض الإحصائيات، 'scan' للبحث عن خوادم")
        print("-" * 50)
        
        while True:
            try:
                user_input = input("\n🧑 أنت: ").strip()
                
                if user_input.lower() in ["خروج", "exit", "quit"]:
                    print("نورا: مع السلامة! 👋")
                    break
                
                elif user_input.lower() == "إحصائيات":
                    stats = self.get_stats()
                    print("📊 إحصائيات النظام:")
                    for key, value in stats.items():
                        print(f"   {key}: {value}")
                    continue
                
                elif user_input.lower() == "scan":
                    result = self.simulate_server_scan()
                    print(f"نورا: {result}")
                    continue
                
                elif not user_input:
                    continue
                
                # الحصول على الرد
                response = self.generate_reply(user_input)
                print(f"🤖 نورا: {response}")
                
                # حفظ في السجل
                self.chat_history.append({
                    "user": user_input,
                    "assistant": response,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # حفظ السجل كل 5 رسائل
                if len(self.chat_history) % 5 == 0:
                    self.save_history()
                    
            except KeyboardInterrupt:
                print("\n\nنورا: تم إيقاف المحادثة. مع السلامة! 👋")
                break
            except Exception as e:
                print(f"نورا: عذراً، حدث خطأ: {str(e)}")

def main():
    """تشغيل المساعد المحسن"""
    assistant = EnhancedNoraAssistant()
    assistant.chat()

if __name__ == "__main__":
    main()

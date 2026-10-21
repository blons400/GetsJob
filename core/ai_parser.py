import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()

# تهيئة العميل الجديد
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def parse_job_text_with_ai(raw_text):
    """تحليل النص العشوائي واستخراج بيانات الوظيفة بصيغة JSON"""
    prompt = f"""
    أنت مساعد ذكي متخصص في الموارد البشرية. اقرأ إعلان الوظيفة التالي واستخرج البيانات الأساسية.
    أرجع النتيجة بصيغة JSON فقط، بدون أي نصوص أو شروحات إضافية.
    
    الإعلان: {raw_text}

    يجب أن يحتوي الـ JSON على المفاتيح التالية بدقة:
    - "title" (عنوان الوظيفة أو المسمى الوظيفي)
    - "category" (التخصص العام لتسهيل البحث، مثل: هندسة، تقنية معلومات، مبيعات، طب)
    - "description" (وصف الوظيفة والشروط والموقع)
    - "contact_info" (رقم الهاتف أو البريد الإلكتروني أو رابط التقديم)
    """
    try:
        # استخدام النموذج والمكتبة الجديدة
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        
        # تنظيف الرد لضمان احتوائه على JSON فقط
        json_str = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(json_str)
    except Exception as e:
        print(f"حدث خطأ أثناء التحليل: {e}")
        return None
import os
import requests

def send_whatsapp_message(to_phone, text_message):
    """دالة إرسال رسالة نصية للمستخدم عبر Meta Graph API"""
    phone_id = os.getenv('WHATSAPP_PHONE_ID')
    token = os.getenv('WHATSAPP_TOKEN')
    
    url = f"https://graph.facebook.com/v26.0/{phone_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": text_message}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()


def handle_incoming_message(from_phone, text_body):
    """دالة معالجة النص الوارد وتحديد الرد المناسب"""
    text = text_body.strip().lower()
    
    if any(word in text for word in ['مرحبا', 'السلام', 'اهلا']):
        reply = "أهلاً وسهلاً بك في منصة GetsJob! 💼\nارسل كلمة *وظائف* لرؤية الأقسام المتاحة."
    elif 'وظائف' in text or 'وظيفة' in text:
        reply = "القاعات والوظائف المتاحة حالياً:\n1. برمجة وتطوير\n2. تسويق ومبيعات\n3. دعم فني"
    else:
        reply = f"شكراً لتواصلك معنا! استلمنا رسالتك: \"{text_body}\". وسنقوم بالرد عليك في أقرب وقت."
        
    # إرسال الرد تلقائياً
    send_whatsapp_message(from_phone, reply)
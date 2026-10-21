import os
import requests
from .models import Subscriber, Job, PaymentRequest

# بيانات حساب Meta / WhatsApp API من ملف .env
WHATSAPP_TOKEN = os.getenv('WHATSAPP_TOKEN')
PHONE_NUMBER_ID = os.getenv('WHATSAPP_PHONE_ID')

def send_whatsapp_message(to_phone, message_text):
    """إرسال رسالة نصية للمستخدم عبر WhatsApp Graph API"""
    url = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message_text}
    }
    try:
        requests.post(url, json=payload, headers=headers)
    except Exception as e:
        print(f"Error sending WhatsApp message: {e}")


def handle_incoming_message(phone_number, text_message):
    """المحرك الرئيسي لمعالجة رسائل المستخدم حسب حالته"""
    text = text_message.strip()
    
    # 1. البحث عن المشترك أو إنشاؤه إن كان جديداً
    subscriber, created = Subscriber.objects.get_or_create(
        phone_number=phone_number,
        defaults={'bot_state': 'START'}
    )

    # التحقق من صلاحية الاشتراك أولاً
    is_active = subscriber.check_subscription()

    # 2. منطق شجرة الحالات (State Machine)
    if created or subscriber.bot_state == 'START':
        msg = (
            "أهلاً بك في منصة الوظائف! 🌟\n\n"
            "تسمح لك المنصة بالحصول على أحدث الوظائف المجمعة يومياً من فيسبوك والمواقع حسب تخصصك.\n\n"
            "قيمة الاشتراك الشهري: 10 دينار فقط.\n"
            "للاشتراك، يرجى إرسال رقم كرت تعبئة (مدار / ليبيانا) أو إثبات تحويل الرصيد هنا."
        )
        subscriber.bot_state = 'AWAITING_PAYMENT'
        subscriber.save()
        send_whatsapp_message(phone_number, msg)

    elif subscriber.bot_state == 'AWAITING_PAYMENT':
        # تسجيل طلب الدفع لمراجعته من لوحة التحكم
        PaymentRequest.objects.create(
            subscriber=subscriber,
            receipt_code=text,
            status='PENDING'
        )
        msg = (
            "شكراً لك! تم استلام رمز الدفع/الرصيد بنجاح. ⏳\n"
            "جاري مراجعة الطلب وتفعيل حسابك خلال دقائق."
        )
        send_whatsapp_message(phone_number, msg)

    elif subscriber.bot_state == 'AWAITING_SPECIALTY' or (is_active and text.startswith("تخصص:")):
        # حفظ تخصص المستخدم
        clean_specialty = text.replace("تخصص:", "").strip()
        subscriber.specialty = clean_specialty
        subscriber.bot_state = 'ACTIVE'
        subscriber.save()

        # جلب أحدث الوظائف المطابقة للتخصص
        jobs = Job.objects.filter(category__icontains=clean_specialty, is_active=True).order_by('-created_at')[:3]
        
        if jobs.exists():
            response_text = f"تم حفظ تخصصك: ({clean_specialty}) ✅\nإليك أحدث الوظائف المتاحة الآن:\n\n"
            for job in jobs:
                response_text += f"🔹 *{job.title}*\n{job.description[:150]}...\n📞 للتواصل: {job.contact_info or 'راجع الرابط'}\n\n"
        else:
            response_text = f"تم حفظ تخصصك: ({clean_specialty}) ✅\nلا توجد وظائف جديدة حالياً لهذا التخصص، سنرسل لك إشعاراً فور توفرها!"

        send_whatsapp_message(phone_number, response_text)

    elif subscriber.bot_state == 'ACTIVE' and is_active:
        # إذا كان مشترِكاً نشطاً ويريد البحث عن وظائف أو تغيير تخصص
        jobs = Job.objects.filter(category__icontains=subscriber.specialty, is_active=True).order_by('-created_at')[:3]
        if jobs.exists():
            response_text = f"أحدث الوظائف المتاحة لتخصصك ({subscriber.specialty}):\n\n"
            for job in jobs:
                response_text += f"🔹 *{job.title}*\n{job.description[:150]}...\n📞 التواصل: {job.contact_info}\n\n"
        else:
            response_text = f"لا توجد وظائف جديدة اليوم لتخصصك ({subscriber.specialty}). يمكنك تغيير التخصص في أي وقت بإرسال كلمة: (تخصص: التخصص الجديد)."

        send_whatsapp_message(phone_number, response_text)

    elif not is_active:
        msg = "عذراً، اشتراكك انتهى أو غير مفعل بعد. يرجى إرسال كرت تعبئة جديد للتجديد."
        subscriber.bot_state = 'AWAITING_PAYMENT'
        subscriber.save()
        send_whatsapp_message(phone_number, msg)
import os
import requests
from .models import Job, UserSession, Application

def send_whatsapp_message(to_phone, text_message):
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
    return requests.post(url, headers=headers, json=payload).json()

def handle_incoming_message(from_phone, text_body):
    user_msg = text_body.strip()
    session, created = UserSession.objects.get_or_create(phone_number=from_phone)

    # العودة للقائمة الرئيسية في أي وقت
    if user_msg in ['0', 'رئيسية', 'القائمة', 'إلغاء']:
        session.state = 'MAIN_MENU'
        session.selected_job = None
        session.save()
        send_main_menu(from_phone)
        return

    # معالجة الطلب حسب حالة المستخدم الحالية
    if session.state == 'MAIN_MENU':
        if user_msg == '1':
            list_jobs(from_phone, session)
        elif user_msg == '2':
            send_whatsapp_message(from_phone, "منصة GetsJob للوظائف 💼\nللتواصل مع الدعم الفني: support@getsjob.com")
        else:
            send_main_menu(from_phone)

    elif session.state == 'VIEWING_JOBS':
        if user_msg.isdigit():
            job_index = int(user_msg)
            jobs = Job.objects.filter(is_active=True)
            if 1 <= job_index <= len(jobs):
                selected = jobs[job_index - 1]
                session.selected_job = selected
                session.state = 'AWAITING_NAME'
                session.save()
                
                details = f"📋 *{selected.title}*\nالقسم: {selected.category}\n\n{selected.description}\n\n"
                details += "للتقدم لهذه الوظيفة، يرجى كتابة *اسمك بالكامل*:"
                send_whatsapp_message(from_phone, details)
            else:
                send_whatsapp_message(from_phone, "❌ خيار غير صحيح، يرجى كتابة رقم الوظيفة القائمة.")
        else:
            list_jobs(from_phone, session)

    elif session.state == 'AWAITING_NAME':
        session.applicant_name = user_msg
        session.state = 'AWAITING_CV'
        session.save()
        send_whatsapp_message(from_phone, f"شكراً {user_msg}. أرسل الآن رابط أو نص سريتك الذاتية (CV) لإتمام التقديم:")

    elif session.state == 'AWAITING_CV':
        Application.objects.create(
            job=session.selected_job,
            applicant_name=session.applicant_name,
            phone_number=from_phone,
            cv_url=user_msg
        )
        # إرجاع المستخدم للقائمة الرئيسية
        session.state = 'MAIN_MENU'
        session.selected_job = None
        session.save()
        
        send_whatsapp_message(from_phone, "✅ تم استلام طلبك بنجاح! وسيقوم فريق التوظيف بمراجعته وقريباً سيتواصلون معك.\n\nأرسل *0* للعودة للقائمة الرئيسية.")

def send_main_menu(to_phone):
    menu = (
        "مرحباً بك في منصة *GetsJob* 💼\n\n"
        "اختر رقم الخيار المطلوب:\n"
        "1️⃣ عرض الوظائف المتاحة والتقديم\n"
        "2️⃣ معلومات التواصل والدعم\n"
    )
    send_whatsapp_message(to_phone, menu)

def list_jobs(to_phone, session):
    jobs = Job.objects.filter(is_active=True)
    if not jobs.exists():
        send_whatsapp_message(to_phone, "لا توجد وظائف متاحة حالياً. أرسل *0* للعودة للقائمة الرئيسية.")
        return

    msg = "📋 *الوظائف المتاحة حالياً:*\n\n"
    for idx, job in enumerate(jobs, start=1):
        msg += f"{idx}. *{job.title}* ({job.category})\n"
    
    msg += "\nرد برقم الوظيفة لرؤية التفاصيل والتقديمعليها، أو أرسل *0* للرئيسية."
    session.state = 'VIEWING_JOBS'
    session.save()
    send_whatsapp_message(to_phone, msg)
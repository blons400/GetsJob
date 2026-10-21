import json
import os
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import handle_incoming_message

VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', 'my_secure_token_123')

@csrf_exempt
def whatsapp_webhook(request):
    # 1. التحقق الأول من سيرفر فايسبوك/واتساب (GET Request)
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')

        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return HttpResponse(challenge, status=200)
        return HttpResponse('Verification failed', status=403)

    # 2. استقبال الرسائل الواردة من المستخدمين (POST Request)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            entry = data.get('entry', [])[0]
            changes = entry.get('changes', [])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [])

            if messages:
                msg = messages[0]
                from_phone = msg.get('from')  # رقم المرسل
                
                if msg.get('type') == 'text':
                    text_body = msg.get('text', {}).get('body', '')
                    # استدعاء دالة معالجة الرسالة
                    handle_incoming_message(from_phone, text_body)

            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            print(f"Error processing webhook: {e}")
            return JsonResponse({'status': 'error'}, status=400)

    return HttpResponse('Method not allowed', status=405)
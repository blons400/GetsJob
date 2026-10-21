import os
import django

# تأكد من استبدال job_platform.settings باسم المجلد الرئيسي لمشروعك إذا كان مختلفاً
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'job_platform.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# قراءة البيانات من متغيرات البيئة أو استخدام قيم افتراضية
username = os.getenv('ADMIN_USERNAME', 'admin')
email = os.getenv('ADMIN_EMAIL', 'admin@getsjob.com')
password = os.getenv('ADMIN_PASSWORD', 'AdminPass123456!')

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superuser '{username}' created successfully!")
else:
    print(f"ℹ️ Superuser '{username}' already exists.")
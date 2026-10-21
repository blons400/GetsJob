#!/usr/bin/env bash
# إيقاف عملية البناء فوراً في حال حدوث أي خطأ
set -o errexit

# 1. تثبيت جميع المكتبات المذكورة في ملف requirements.txt
pip install -r requirements.txt

# 2. تجميع الملفات الثابتة (CSS, JavaScript, Images) في مجلد staticfiles
python manage.py collectstatic --no-input

# 3. تطبيق التعديلات والهجرات على قاعدة بيانات PostgreSQL الخاصة بموقع Render
python manage.py migrate
from django.core.management.base import BaseCommand
from core.scraper import fetch_and_save_jobs

class Command(BaseCommand):
    help = 'تشغيل أداة سحب الوظائف وتحليلها باستخدام Gemini AI'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('بدء تشغيل السكربت للبحث عن الوظائف...'))
        
        try:
            fetch_and_save_jobs()
            self.stdout.write(self.style.SUCCESS('تم الانتهاء من جلب وتحليل الوظائف بنجاح! ✅'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'حدث خطأ أثناء التشغيل: {e}'))
from .models import Job
from .ai_parser import parse_job_text_with_ai

def fetch_and_save_jobs():
    # نصوص تجريبية تحاكي منشورات عشوائية من فيسبوك
    mock_posts = [
        "مطلوب مهندس مدني خبرة 3 سنوات للعمل في شركة مقاولات بطرابلس (حي الأندلس). الراتب يحدد بعد المقابلة. للتواصل: 0912345678",
        "نبحث عن مطور تطبيقات موبايل (Flutter) ومبرمج بايثون (Django) للعمل بدوام كامل. الرجاء إرسال الـ CV على hr@amadeus-libya.com",
        "مطلوب كاشير للعمل في مقهى بصياحيات. الدوام من 8 للـ 4. رقم الهاتف 0921112233"
    ]

    print("بدء عملية جمع الوظائف وتحليلها...\n")
    
    for post_text in mock_posts:
        # تجنب تكرار الوظائف المسجلة مسبقاً
        if Job.objects.filter(description__icontains=post_text[:50]).exists():
            continue

        print(f"جاري تحليل: {post_text[:40]}...")
        job_data = parse_job_text_with_ai(post_text)

        if job_data:
            Job.objects.create(
                title=job_data.get('title', 'غير محدد'),
                category=job_data.get('category', 'عام'),
                description=job_data.get('description', post_text),
                contact_info=job_data.get('contact_info', 'غير متوفر'),
                source="Facebook_Mock",
                is_active=True
            )
            print(f"✅ تم حفظ وظيفة: {job_data.get('title')} ضمن تخصص: {job_data.get('category')}\n")
        else:
            print("❌ فشل في تحليل هذا المنشور.\n")
from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=255, verbose_name="مسمى الوظيفة")
    category = models.CharField(max_length=100, verbose_name="القسم")
    description = models.TextField(verbose_name="الوصف الوظيفي")
    requirements = models.TextField(verbose_name="الشروط والاحتياجات", blank=True, null=True)
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.category}"

class UserSession(models.Model):
    """جدول لتتبع حالة المستخدم الحالية داخل المحادثة (State Machine)"""
    STATE_CHOICES = [
        ('MAIN_MENU', 'القائمة الرئيسية'),
        ('VIEWING_JOBS', 'تصفح الوظائف'),
        ('AWAITING_NAME', 'في انتظار اسم المتقدم'),
        ('AWAITING_CV', 'في انتظار السيرة الذاتية'),
    ]
    
    phone_number = models.CharField(max_length=20, unique=True)
    state = models.CharField(max_length=50, choices=STATE_CHOICES, default='MAIN_MENU')
    selected_job = models.ForeignKey(Job, on_delete=models.SET_NULL, null=True, blank=True)
    applicant_name = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.phone_number} - {self.state}"

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    cv_url = models.URLField(blank=True, null=True, verbose_name="رابط السيرة الذاتية")
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.applicant_name} -> {self.job.title}"
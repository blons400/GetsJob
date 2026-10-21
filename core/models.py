from django.db import models
from django.utils import timezone
from datetime import timedelta

class Subscriber(models.Model):
    # حالات محادثة البوت لمتابعة مسار المستخدم
    STATE_CHOICES = [
        ('START', 'البداية'),
        ('AWAITING_PAYMENT', 'في انتظار إرسال الدفع/الرصيد'),
        ('AWAITING_SPECIALTY', 'في انتظار تحديد التخصص'),
        ('ACTIVE', 'نشط / جاهز لاستقبال الوظائف'),
    ]

    phone_number = models.CharField(max_length=20, unique=True, verbose_name="رقم الواتساب")
    full_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="الاسم الكامل")
    specialty = models.CharField(max_length=100, blank=True, null=True, verbose_name="التخصص / المسمى الوظيفي")
    bot_state = models.CharField(max_length=30, choices=STATE_CHOICES, default='START', verbose_name="حالة المحادثة")
    
    is_active = models.BooleanField(default=False, verbose_name="اشتراك نشط")
    subscription_end_date = models.DateTimeField(blank=True, null=True, verbose_name="تاريخ انتهاء الاشتراك")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ التسجيل")

    def check_subscription(self):
        """تحديث تلقائي لحالة الاشتراك بناءً على التاريخ الحالي"""
        if self.subscription_end_date and timezone.now() > self.subscription_end_date:
            self.is_active = False
            self.save()
        return self.is_active

    def activate_subscription(self, days=30):
        """تفعيل أو تمديد الاشتراك"""
        now = timezone.now()
        if self.subscription_end_date and self.subscription_end_date > now:
            self.subscription_end_date += timedelta(days=days)
        else:
            self.subscription_end_date = now + timedelta(days=days)
        self.is_active = True
        self.save()

    def __str__(self):
        return f"{self.phone_number} - {self.full_name or 'مشترك جديد'}"

    class Meta:
        verbose_name = "مشترك"
        verbose_name_plural = "المشتركون"


class Job(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان الوظيفة")
    category = models.CharField(max_length=100, db_index=True, verbose_name="التخصص / التصنيف")
    description = models.TextField(verbose_name="تفاصيل الوظيفة")
    contact_info = models.CharField(max_length=255, blank=True, null=True, verbose_name="معلومات التواصل")
    source = models.CharField(max_length=50, default="Facebook", verbose_name="المصدر")
    source_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="رابط المنشور الأصلي")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الجمع")
    is_active = models.BooleanField(default=True, verbose_name="متاحة حالياً")

    def __str__(self):
        return f"{self.title} ({self.category})"

    class Meta:
        verbose_name = "وظيفة"
        verbose_name_plural = "الوظائف"


class PaymentRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'قيد المراجعة'),
        ('APPROVED', 'مقبول / تم التفعيل'),
        ('REJECTED', 'مرفوض'),
    ]

    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name="payments", verbose_name="المشترك")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="القيمة")
    receipt_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="رقم كرت التعبئة / المرجعي")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', verbose_name="حالة الطلب")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")

    def save(self, *args, **kwargs):
        # عند تغيير حالة الطلب إلى "مقبول"، يتم تفعيل اشتراك المستخدم تلقائياً
        if self.pk:
            old_status = PaymentRequest.objects.get(pk=self.pk).status
            if old_status != 'APPROVED' and self.status == 'APPROVED':
                self.subscriber.activate_subscription(days=30)
                self.subscriber.bot_state = 'AWAITING_SPECIALTY'
                self.subscriber.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"طلب دفع: {self.subscriber.phone_number} - {self.status}"

    class Meta:
        verbose_name = "طلب دفع"
        verbose_name_plural = "طلبات الدفع"
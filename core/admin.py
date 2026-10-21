from django.contrib import admin
from .models import Subscriber, Job, PaymentRequest

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'full_name', 'specialty', 'is_active', 'subscription_end_date', 'bot_state')
    list_filter = ('is_active', 'bot_state')
    search_fields = ('phone_number', 'full_name', 'specialty')

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'source', 'created_at', 'is_active')
    list_filter = ('category', 'source', 'is_active')
    search_fields = ('title', 'description', 'category')

@admin.register(PaymentRequest)
class PaymentRequestAdmin(admin.ModelAdmin):
    list_display = ('subscriber', 'receipt_code', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('subscriber__phone_number', 'receipt_code')
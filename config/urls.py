from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('whatsapp/', include('core.urls')), # تأكد أن اسم تطبيقك هو core أو استبدله بالاسم الصحيح
]
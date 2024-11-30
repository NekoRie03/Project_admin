from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib import admin

urlpatterns = [
    #login
    
    #signup
    path('signup/role/', views.role_signup, name='role_signup'),
    path('signup/student/', views.student_signup, name='student_signup'),
    path('pending_review/', views.pending_review, name='pending_review'),
    path('signup/success/', views.registration_success, name='registration_success'),
    path('approve_registration/<int:user_id>/', views.approve_registration, name='approve_registration'),
    
    #logout
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

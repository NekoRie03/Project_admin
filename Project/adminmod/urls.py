from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import user_login, user_logout, guard_change_password, student_change_password
from django.contrib.auth import views as auth_views

urlpatterns = [
    #login
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('authenticate/login/', user_login, name='login'),
    #dashboard
    path('guard/guard_dashboard/', views.guard_dashboard, name='guard_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    #signup
    path('signup/role/', views.role_signup, name='role_signup'),
    path('signup/student/', views.student_signup, name='student_signup'),
    path('pending_review/', views.pending_review, name='pending_review'),
    path('signup/success/', views.registration_success, name='registration_success'),
    path('approve_registration/<int:user_id>/', views.approve_registration, name='approve_registration'),
    #change pass
    path('guard/change-password/', guard_change_password, name='guard_change_password'),
    path('student/change-password/', student_change_password, name='student_change_password'),
    #reset password
    path('reset_password/',
        auth_views.PasswordResetView.as_view(template_name='authentication/password_reset.html'), 
        name='reset_password'),
    
    path('reset_password_sent/', 
        auth_views.PasswordResetDoneView.as_view(template_name='authentication/password_reset_sent.html'), 
        name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(template_name='authentication/password_reset_form.html'), 
        name='password_reset_confirm'),
    
    path('reset_password_complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name='authentication/password_reset_done.html'), 
        name='reset_password_complete'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

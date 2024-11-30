from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from .views import user_login, user_logout

urlpatterns = [
    #login
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('authenticate/login/', user_login, name='login'),
    #dashboard
    path('guard_dashboard/', views.guard_dashboard, name='guard_dashboard'),
    path('student_dashboard/', views.student_dashboard, name='student_dashboard'),
    #signup
    path('signup/role/', views.role_signup, name='role_signup'),
    path('signup/student/', views.student_signup, name='student_signup'),
    path('pending_review/', views.pending_review, name='pending_review'),
    path('signup/success/', views.registration_success, name='registration_success'),
    path('approve_registration/<int:user_id>/', views.approve_registration, name='approve_registration'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

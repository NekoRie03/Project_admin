from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib import admin
from .views import admin_logout_view

admin.site.site_url = None  # This removes the "View Site" link
admin.site.logout = admin_logout_view  # This overrides the default admin logout

urlpatterns = [
    #login
    path('login/', views.login_view, name='login'),
    path('student/profile/', views.student_profile, name='student_profile'),
    path('guard/dashboard/', views.guard_dashboard, name='guard_dashboard'),
    
    #signup
    path('signup/role/', views.role_signup, name='role_signup'),
    path('signup/student/', views.student_signup, name='student_signup'),
    path('pending_review/', views.pending_review, name='pending_review'),
    path('signup/success/', views.registration_success, name='registration_success'),
    path('approve_registration/<int:user_id>/', views.approve_registration, name='approve_registration'),
    
    #logout
    path('logout/', views.logout_view, name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

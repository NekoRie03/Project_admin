from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    #issue_status
    path('DenyReport/', views.DenyReport, name='DenyReport'),
    path('ProbationProgress/', views.ProbationProgress, name='ProbationProgress'),

    
    #user_role
    path('retry-password/', views.retry_password, name='retry_password'),

    #login
    path('', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('reset/', views.reset, name='reset'),
    path('resetconfirmation/', views.resetconfirmation, name='resetconfirmation'),
    path('forget/', views.forget, name='forget'),
    path('change/', views.change, name='change'),
    path('code/', views.code, name='code'),

    #student mod
    path('studentsettings/'   , views.studset, name='studentsettings'),
    path('studentstatus/'     , views.studstat, name='studentstatus'),   
    #guard and instructor mod
    path('manage-violations/', views.manage_violations, name='manage_violations'),
    path('edit-violation/<int:violation_id>/', views.edit_violation, name='edit_violation'),  
    path('report-success/', views.report_success, name='report_success'),
    path('report-summary/', views.report_summary, name='report_summary'),
    path('manage_dropdown/', views.manage_dropdown, name='manage_dropdown'),
    path('registration_success/', views.registration_success, name='registration_success'),
    path('file-report/', views.file_report, name='file_report'),
    path('changepass/', views.changepass, name='changepass'),
    path('violationreports/', views.violationreports, name='violationreports'),
    path('update_status/<int:report_id>/', views.update_status, name='update_status'),
    path('report_summary2/', views.report_summary2, name='report_summary2'),

]
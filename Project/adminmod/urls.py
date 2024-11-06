from django.urls import path

from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    
    #dboard_violation_review
    path('ViolationReportsActive/', views.ViolationReportsActive, name='ViolationReportsActive'),
    path('ViolationReportsWarning/', views.ViolationReportsWarning, name='ViolationReportsWarning'),
    path('ViolationReportsProbation/', views.ViolationReportsProbation, name='ViolationReportsProbation'),
    path('ViolationReportsSuspension/', views.ViolationReportsSuspension, name='ViolationReportsSuspension'),
    path('ViolationReportsExpulsion/', views.ViolationReportsExpulsion, name='ViolationReportsExpulsion'),
    path('ViolationReportsInactive/', views.ViolationReportsInactive, name='ViolationReportsInactive'),
    
    #issue_status
    path('IssueWarning/', views.IssueWarning, name='IssueWarning'),
    path('IssueProbation/', views.IssueProbation, name='IssueProbation'),
    path('IssueSuspension/', views.IssueSuspension, name='IssueSuspension'),
    path('IssueExpulsion/', views.IssueExpulsion, name='IssueExpulsion'),
    path('DenyReport/', views.DenyReport, name='DenyReport'),
    
    #summary_report
    path('SummaryWarning/', views.SummaryWarning, name='SummaryWarning'),
    path('SummaryProbation/', views.SummaryProbation, name='SummaryProbation'),
    path('SummarySuspension/', views.SummarySuspension, name='SummarySuspension'),
    path('SummaryExpulsion/', views.SummaryExpulsion, name='SummaryExpulsion'), 
    path('SummaryInactive/', views.SummaryInactive, name='SummaryInactive'),
    path('SummaryActive/', views.SummaryActive, name='SummaryActive'),
    
    #modify_status
    path('ModifyExpulsion/', views.ModifyExpulsion, name='ModifyExpulsion'),
    path('ModifySuspension/', views.ModifySuspension, name='ModifySuspension'),
    path('ModifyProbation/', views.ModifyProbation, name='ModifyProbation'),
    path('ProbationProgress/', views.ProbationProgress, name='ProbationProgress'),
    
    #dboard_modify_violation
    path('ModifyViolation/', views.ModifyViolation, name='ModifyViolation'),
    path('Infopopup2/', views.Infopopup2, name='Infopopup2'),
    path('AddViolation/', views.AddViolation, name='AddViolation'),
    path('EditViolation/', views.EditViolation, name='EditViolation'),
    
    #student_records
    path('studrec/', views.studrec, name='studrec'),
    path('studrec2/', views.studrec2, name='studrec2'),
    path("studlist/", views.studlist, name="studlist"),
    path("studlist2/", views.studlist2, name="studlist2"),
    path("addlist/", views.addlist, name="addlist"),
    path("editlist/", views.editlist, name="editlist"),
    path("addcourse/", views.addcourse, name="addcourse"),
    path("editcourse/", views.editcourse, name="editcourse"),
    
    #user_role
    path("userrole/", views.userrole, name="userrole"),
    path("edituserrole/", views.edituserrole, name="edituserrole"),
    path("adduserrole/", views.adduser, name="adduserrole"),
    path("useraccount/",views.useraccount, name="useraccount"),
    
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
    path('infopopup/',  views.infopop, name='infopopup'),
    path('monitorreport/'  , views.monitorrep, name='monitorreport'),
    path('reportsummarystudent/'   , views.reportsumstud, name='reportsummarystudent'),
    path('studentsettings/'    , views.studset, name='studentsettings'),
    path('studentstatus/'     , views.studstat, name='studentstatus'),   
    path("infopopup3/", views.infopopup3, name="infopopup3"), 

    #guard and instructor mod
    path('manage-violations/', views.manage_violations, name='manage_violations'),
    path('edit-violation/<int:violation_id>/', views.edit_violation, name='edit_violation'),  
    path('report-success/', views.report_success, name='report_success'),
    path('report-summary/', views.report_summary, name='report_summary'),
    path('addstudent/', views.addstudent, name='addstudent'),
    path('notif/', views.notif, name='notif'),
    path('reportsummary/', views.reportsummary, name='reportsummary'),
    path('guardsearch/',  views.guardsearch, name='guardsearch'),
    path('guardsearch2/',   views.guardsearch2, name='guardsearch2'),
    path('manage_dropdown/', views.manage_dropdown, name='manage_dropdown'),
    path('registration_success/', views.registration_success, name='registration_success'),
    path('file-report/', views.file_report, name='file_report'),
    path('changepass/', views.changepass, name='changepass'),
    path('violationreports/', views.violationreports, name='violationreports'),
    path('update_status/<int:report_id>/', views.update_status, name='update_status'),

]
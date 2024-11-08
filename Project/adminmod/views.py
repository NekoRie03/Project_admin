from django.shortcuts import render, redirect
from django.shortcuts import HttpResponse, get_object_or_404, redirect
from django.http import JsonResponse
from .forms import SignupNow, ReportForm, ViolationTypeForm, UserForm
from .models import DropdownOption, Signup, Course, Section, Report, ViolationType, User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import random
import string
from django.utils import timezone
import datetime

# Create your views here.

# ------ Admin Dashboard ------
def dashboard(request):
    return render(request,'Dashboard.html')

def DenyReport(request):
    return render(request, 'dboard_violation_rev/issue_status/DenyReport.html')


#modify_stat dboard_violation_rev/summary_issue/
#modify_stat dboard_violation_rev/summary_issue/
def ModifyProbation(request):
    return render(request, 'dboard_violation_rev/modify_issue/ModifyProbation.html')
def ProbationProgress(request):
    return render(request, 'dboard_violation_rev/modify_issue/ProbationProgress.html')

# ------ Modify Violation ------
#dboard_modify
def ModifyViolation(request):
    return render(request, 'dboard_modify_violation/ModifyViolation.html')




# ------ User Roles ------
def userrole(request):
    return render(request, 'user_role/Account List.html') 
def edituserrole(request):
    return render(request, 'user_role/Edit User Role.html')

def generate_random_password():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(10))

def adduser(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            # Extract form data
            employee_id = form.cleaned_data['employee_id']
            first_name = form.cleaned_data['first_name']
            middle_initial = form.cleaned_data['middle_initial']
            last_name = form.cleaned_data['last_name']
            position = form.cleaned_data['position']
            
            # Generate email based on first and last name
            email = f"{last_name.lower()}.{first_name.lower()}@email.com"
            password = generate_random_password()
            
            # Create the user in the database
            user = User.objects.create(
                employee_id=employee_id,
                first_name=first_name,
                middle_initial=middle_initial,
                last_name=last_name,
                email=email,
                password=password,
                position=position,
            )


            # Pass generated email and password to the template
            return render(request, 'user_role/Add User.html', {
                'form': UserForm(),  # Clear the form after submission
                'success_message': "User was successfully created."  # Add success message
            })
        else:
            return render(request, 'user_role/Add User.html', {'form': form})

    # Generate a random password for the initial GET request
    password = generate_random_password()
    return render(request, 'user_role/Add User.html', {
        'form': UserForm(),
        'generated_password': password
    })



# View for generating a new password via AJAX
def retry_password(request):
    if request.method == 'GET':
        new_password = generate_random_password()
        return JsonResponse({'generated_password': new_password})






def useraccount(request):
    return render(request, 'user_role/UserAccount.html')
#------ Login ------
def login(request):
    return render(request, 'login/LOGIN.html')

def signup(request):
    if request.method == "POST":
        form = SignupNow(request.POST, request.FILES)
        
        if form.is_valid():
            form.save()
            return redirect('registration_success')  # Ensure you create this page or change this to your homepage

    else:
        form = SignupNow()

    return render(request,'login/Sign-up.html', {'form': form})

def manage_dropdown(request):
    if request.method == 'POST':
        # Add a new program
        if 'add_program' in request.POST:
            new_program = request.POST.get('new_program')
            if new_program:
                DropdownOption.objects.create(program1=new_program)
                return redirect('manage_dropdown')

        # Add a new course
        if 'add_course' in request.POST:
            new_course = request.POST.get('new_course')
            program_id = request.POST.get('program_id')
            if new_course and program_id:
                program = DropdownOption.objects.get(id=program_id)
                Course.objects.create(program=program, course_name=new_course)
                return redirect('manage_dropdown')

        # Add a new section
        if 'add_section' in request.POST:
            new_section = request.POST.get('new_section')
            course_id = request.POST.get('course_id')
            if new_section and course_id:
                course = Course.objects.get(id=course_id)
                Section.objects.create(course=course, section_name=new_section)
                return redirect('manage_dropdown')

        # Delete a program
        if 'delete_program' in request.POST:
            program_id = request.POST.get('delete_program')
            DropdownOption.objects.filter(id=program_id).delete()
            return redirect('manage_dropdown')

        # Delete a course
        if 'delete_course' in request.POST:
            course_id = request.POST.get('delete_course')
            Course.objects.filter(id=course_id).delete()
            return redirect('manage_dropdown')

        # Delete a section
        if 'delete_section' in request.POST:
            section_id = request.POST.get('delete_section')
            Section.objects.filter(id=section_id).delete()
            return redirect('manage_dropdown')

    # Fetch all options for the dropdowns
    program_options = DropdownOption.objects.all()
    course_options = Course.objects.all()
    section_options = Section.objects.all()

    return render(request, 'manage_dropdown.html', {
        'program_options': program_options,
        'course_options': course_options,
        'section_options': section_options,
    })


def file_report(request):
    violation_types = ViolationType.objects.all()
    students = Signup.objects.all()

    search_result = None
    selected_student = None  # Initialize selected student ID

    if request.method == 'POST':
        if 'student_id_search' in request.POST:
            # Handle search by student ID
            student_id = request.POST.get('student_id_search')
            try:
                search_result = Signup.objects.get(idnumber=student_id)
                selected_student = search_result.id  # Set the searched student's ID
            except Signup.DoesNotExist:
                search_result = None
        else:
            # Handle form submission
            student_id = request.POST.get('student')
            incident_date = request.POST.get('incident_date')
            violation_type_id = request.POST.get('violation_type')
            
            try:
                student = Signup.objects.get(id=student_id)
                violation_type = ViolationType.objects.get(id=violation_type_id)
                
                context = {
                    'student_id': student.idnumber,
                    'student_name': f"{student.first_name} {student.last_name}",
                    'incident_date': incident_date,
                    'violation_type': violation_type.name,
                    'db_student_id': student_id,
                    'db_violation_type_id': violation_type_id,
                }
                return render(request, 'report_summary.html', context)
            except (Signup.DoesNotExist, ViolationType.DoesNotExist) as e:
                return HttpResponse(f"Error: {str(e)}", status=400)
            
    if request.method == 'POST' and search_result:
        # Assuming form submission logic here
        # Gather necessary data
        student_id = student.idnumber
        student_name = f"{student.first_name} {student.last_name}"
        incident_date = request.POST.get('incident_date')
        violation_type = violation_type.name

        # Redirect to report_summary2 with query parameters
        return redirect('report_summary2', 
                        student_id=student_id, 
                        student_name=student_name, 
                        incident_date=incident_date, 
                        violation_type=violation_type)

    return render(request, 'file_report.html', {
        'violation_types': violation_types,
        'students': students,
        'search_result': search_result,
        'selected_student': selected_student,
    })

def report_summary(request):
    if request.method == 'POST':
        if 'confirm_submission' in request.POST:
            try:
                # Create and save the report
                report = Report.objects.create(
                    student_id=request.POST.get('db_student_id'),
                    incident_date=request.POST.get('incident_date'),
                    violation_type_id=request.POST.get('db_violation_type_id')
                )
                return redirect('report_success')
            except Exception as e:
                return HttpResponse(f"Error saving report: {str(e)}", status=500)
        
        elif 'cancel_submission' in request.POST:
            return redirect('file_report')
    
    return redirect('file_report')

def report_summary2(request):
    # Get the violation type name from GET parameters
    violation_type_name = request.GET.get('violation_type')  

    # Try to fetch the ViolationType object
    try:
        violation_type = ViolationType.objects.get(name=violation_type_name)
        context = {
            'violation_type': violation_type,
            'sanction_period_value': violation_type.sanction_period_value,
            'sanction_period_type': violation_type.sanction_period_type,
            'sanction': violation_type.sanction,
        }
    except ViolationType.DoesNotExist:
        context = {
            'error_message': 'Violation Type not found.'
        }

    # Get student data from GET parameters
    student_id = request.GET.get('student_id')
    student_name = None  # Initialize student_name

    if student_id:
        try:
            # Fetch the student from the Signup model using student_id
            student = Signup.objects.get(id=student_id)
            student_name = f"{student.first_name} {student.last_name}"  # Combine first and last name
        except Signup.DoesNotExist:
            student_name = 'Unknown Student'  # Fallback if the student is not found

    # Add student data to the context without overwriting the previous data
    context.update({
        'student_id': student_id,
        'student_name': student_name,
        'incident_date': request.GET.get('incident_date'),
        'violation_type': violation_type_name,
    })

    # Render the template with the combined context
    return render(request, 'report_summary2.html', context)

def report_success(request):
    return render(request, 'report_success.html')

# Manage Violations (for admins)
def manage_violations(request):
    violations = ViolationType.objects.all()
    if request.method == 'POST':
        form = ViolationTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('manage_violations')
    else:
        form = ViolationTypeForm()

    return render(request, 'manage_violations.html', {'form': form, 'violations': violations})

# Edit Violation
def edit_violation(request, violation_id):
    violation = ViolationType.objects.get(id=violation_id)
    if request.method == 'POST':
        form = ViolationTypeForm(request.POST, instance=violation)
        if form.is_valid():
            form.save()
            return redirect('manage_violations')
    else:
        form = ViolationTypeForm(instance=violation)

    return render(request, 'edit_violation.html', {'form': form, 'violation': violation})



def reset(request):
    return render(request, 'login/Reset Password.html')

def resetconfirmation(request):
    return render(request, 'login/Reset Password Confirmation.html')

def forget(request):
    return render(request, 'login/Forget Password.html')

def change(request):
    return render(request, 'login/ForceChange.html')

def code(request):
    return render(request, 'login/Enter Code.html')
#------ studentmod ------
def infopop(request):
    return render(request, 'studentmod/infopopup.html')

def monitorrep(request):
    return render(request, 'studentmod/MonitorReport.html')

def reportsumstud(request):
    return render(request, 'studentmod/ReportSummaryStudent.html')

def studset(request):
    return render(request, 'studentmod/Student Settings.html')

def studstat(request):
    return render(request, 'studentmod/Student Status.html')
def infopopup3(request):
    return render(request, 'studentmod/infopopup3.html')

#------- guard and instructor module ------
def  addstudent(request):
    return render(request, 'guard-instructormod/AddStud.html')

def guardsearch(request):
    return render(request, 'guard-instructormod/Guard Search.html')

def guardsearch2(request):
    return render(request, 'guard-instructormod/Guard Search 2.html')

def notif(request):
    return render(request, 'guard-instructormod/Guard Notification.html')

def reportsummary(request):
    return render(request, 'guard-instructormod/Guard Report Summary.html')

def registration_success(request):
    return render(request, 'registration_success.html')

def report_success(request):
    return render(request, 'report_success.html')

def changepass(request):
    return render(request,'Changepass.html')


def violationreports(request):
    # Fetch all dropdown options (programs)
    programs = DropdownOption.objects.all()
    
    # Fetch all violation types
    violations = ViolationType.objects.all()
    
    # Fetch all distinct sanctions (from ViolationType)
    sanctions = ViolationType.objects.values_list('sanction', flat=True).distinct()

    # Fetch the reports (apply filters based on the selected criteria if any)
    reports = Report.objects.select_related('student', 'violation_type')

    # Apply the filters based on request parameters
    status_filter = request.GET.get('filter_status')
    program_filter = request.GET.get('filter_program')
    month_filter = request.GET.get('filter_date')
    violation_filter = request.GET.get('filter_violation')
    sanction_filter = request.GET.get('filter_sanction')

    if status_filter:
        reports = reports.filter(status=status_filter)
        
    if program_filter:
        reports = reports.filter(student__program1_id=program_filter)

    if month_filter:
        year, month = map(int, month_filter.split('-'))
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, 1) + datetime.timedelta(days=32)
        end_date = end_date.replace(day=1) - datetime.timedelta(days=1)
        reports = reports.filter(incident_date__range=(start_date, end_date))

    if violation_filter:
        reports = reports.filter(violation_type__name=violation_filter)

    if sanction_filter:
        reports = reports.filter(violation_type__sanction=sanction_filter)

    # Pass the necessary data to the template
    context = {
        'reports': reports,
        'programs': programs,
        'violations': violations,
        'sanctions': sanctions,
        'request': request,  # Pass the request object to the template
    }

    return render(request, 'violationreports.html', context)

def update_status(request, report_id):
    if request.method == 'POST':
        # Get the report object
        report = get_object_or_404(Report, id=report_id)
        
        # Get the new status from the form
        new_status = request.POST.get('status')
        
        # Update the report status
        report.status = new_status
        report.save()
        
        # Redirect back to the reports page
        return redirect('violationreports')
    
    return HttpResponse("Invalid request", status=400)
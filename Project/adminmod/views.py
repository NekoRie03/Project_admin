from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from .forms import AdminSignupForm, GuardSignupForm, StudentSignupForm, StudentRegistrationForm, LoginForm 
from .models import StudentRegistration, User,  Violation, ViolationRecord
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth import logout

User = get_user_model()

def student_signup(request):
    if request.method == "POST":
        user_form = StudentSignupForm(request.POST)
        registration_form = StudentRegistrationForm(request.POST, request.FILES)
        if user_form.is_valid() and registration_form.is_valid():
            user = user_form.save(commit=False)
            user.role = User.Role.STUDENT
            user.is_active = True  # Change this to True
            user.save()

            registration = registration_form.save(commit=False)
            registration.user = user
            registration.save()

            return redirect('pending_review')
    else:
        user_form = StudentSignupForm()
        registration_form = StudentRegistrationForm()

    return render(request, 'signup/student_signup.html', {
        'user_form': user_form,
        'registration_form': registration_form
    })

# View for admin to list pending registrations
@login_required
@user_passes_test(lambda u: u.is_staff)  # Restrict to admin/staff only
def student_review_list(request):
    registrations = StudentRegistration.objects.filter(is_approved=False)
    return render(request, 'admin/student_review_list.html', {'registrations': registrations})

# View to handle approve/decline actions
@login_required
@user_passes_test(lambda u: u.is_staff)
def approve_registration(request, registration_id):
    registration = get_object_or_404(StudentRegistration, id=registration_id)
    action = request.POST.get("action")
    if action == "approve":
        registration.is_approved = True
        registration.review_comments = "Approved by admin"
    elif action == "decline":
        registration.is_approved = False
        registration.review_comments = "Declined by admin"
    registration.save()
    return redirect('student_review_list')

def role_signup(request):
    if request.method == "POST":
        role = request.POST.get("role")  # Get selected role from dropdown
        if role == User.Role.ADMIN:
            form = AdminSignupForm(request.POST)
        elif role == User.Role.GUARD:
            form = GuardSignupForm(request.POST)
        else:
            form = AdminSignupForm(request.POST)  # Fallback to admin form (you could handle this differently)

        if form.is_valid():
            user = form.save(commit=False)
            user.role = role  # Ensure the role is correctly assigned
            user.save()
            return redirect('registration_success')  # Redirect to success page
    else:
        form = AdminSignupForm()  # Use admin form to get role selection dropdown

    return render(request, 'signup/role_signup.html', {'form': form})

def admin_signup(request):
    if request.method == "POST":
        form = AdminSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.ADMIN
            user.save()
            return redirect('login')  # or wherever you want to redirect
    else:
        form = AdminSignupForm()
    return render(request, 'signup/admin_signup.html', {'form': form})

def guard_signup(request):
    if request.method == "POST":
        form = GuardSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = User.Role.GUARD
            user.save()
            return redirect('login')
    else:
        form = GuardSignupForm()
    return render(request, 'signup/guard_signup.html', {'form': form})

def registration_success(request):
    return render(request, 'signup/registration_success.html')  # Render the success page

def pending_review(request):
    return render(request, 'signup/pending_review.html')

def user_login(request):
    if request.user.is_authenticated:
        return redirect_user_after_login(request.user)
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data.get('user')
            login(request, user)
            return redirect_user_after_login(user)
    else:
        form = LoginForm()
    
    return render(request, 'authentication/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

def redirect_user_after_login(user):
    """
    Redirect users to appropriate dashboard based on their role
    """
    if user.role == user.Role.STUDENT:
        return redirect(reverse('student_dashboard'))
    elif user.role == user.Role.GUARD:
        return redirect(reverse('guard_dashboard'))
    elif user.role == user.Role.ADMIN:
        return redirect('/admin/')
    else:
        return redirect('login')  # Default fallback

def student_dashboard(request):
    violations = ViolationRecord.objects.filter(student=request.user)
    violation_count = violations.count()
    return render(request, 'student/dashboard.html', {'violations': violations, 'violation_count': violation_count})


def guard_dashboard(request):
    students = User.objects.filter(role=User.Role.STUDENT, studentregistration__is_approved=True)
    violations = Violation.objects.all()

    if request.method == "POST":
        student_id = request.POST.get('student_id')
        violation_id = request.POST.get('violation_id')
        student = get_object_or_404(User, id=student_id)
        violation = get_object_or_404(Violation, id=violation_id)

        ViolationRecord.objects.create(
            student=student,
            violation=violation,
            recorded_by=request.user
        )
        message = "Violation recorded successfully!"
        return render(request, 'guard/dashboard.html', {'students': students, 'violations': violations, 'message': message})

    return render(request, 'guard/dashboard.html', {'students': students, 'violations': violations})

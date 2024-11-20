from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import get_user_model
from .forms import AdminSignupForm, GuardSignupForm, StudentSignupForm, StudentRegistrationForm  # Create these forms as needed
from .models import StudentRegistration, User
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.urls import reverse
from .decorators import approved_student_required, guard_required
from django.contrib.auth import logout
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token

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

@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        if request.user.role == "STUDENT":
            try:
                registration = StudentRegistration.objects.get(user=request.user)
                if registration.is_approved:
                    return redirect('student_profile')
                else:
                    return redirect('pending_review')
            except StudentRegistration.DoesNotExist:
                pass
        elif request.user.role == "ADMIN":
            return redirect('admin:index')
        elif request.user.role == "GUARD":
            return redirect('guard_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Please provide both username and password.')
            return render(request, 'login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            if user.role == "STUDENT":
                try:
                    registration = StudentRegistration.objects.get(user=user)
                    if registration.is_approved:
                        next_url = request.GET.get('next')
                        if next_url:
                            return redirect(next_url)
                        return redirect('student_profile')
                    else:
                        messages.warning(request, 'Your account is pending approval.')
                        logout(request)
                        return redirect('pending_review')
                except StudentRegistration.DoesNotExist:
                    messages.error(request, 'No registration found.')
                    logout(request)
                    return redirect('login')
            elif user.role == "ADMIN":
                return redirect('admin:index')
            elif user.role == "GUARD":
                return redirect('guard_dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')

@login_required
@guard_required
def guard_dashboard(request):
    return render(request, 'guard/dashboard.html')

@login_required
@approved_student_required
def student_profile(request):
    try:
        registration = StudentRegistration.objects.get(user=request.user)
        context = {
            'registration': registration,
            'user': request.user
        }
        return render(request, 'student/profile.html', context)
    except StudentRegistration.DoesNotExist:
        messages.error(request, 'No registration found for this account.')
        return redirect('login')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('login')

# For Django admin logout override
def admin_logout_view(request):
    logout(request)
    return redirect('login')


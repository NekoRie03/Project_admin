from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import StudentRegistration

def approved_student_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # First check if user is authenticated
        if not request.user.is_authenticated:
            return redirect('login')

        # Then check if user is a student
        if request.user.role != "STUDENT":
            messages.error(request, 'Access denied. Student privileges required.')
            return redirect('login')
            
        try:
            registration = StudentRegistration.objects.get(user=request.user)
            if registration.is_approved:
                return view_func(request, *args, **kwargs)
            else:
                messages.warning(request, 'Your account is pending approval.')
                return redirect('pending_review')
        except StudentRegistration.DoesNotExist:
            messages.error(request, 'No registration found for this account.')
            return redirect('login')
            
    return _wrapped_view

def guard_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "GUARD":
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Guard privileges required.')
        return redirect('login')
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.role == "ADMIN":
            return view_func(request, *args, **kwargs)
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('login')
    return _wrapped_view
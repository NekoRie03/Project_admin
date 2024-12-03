from django.http import HttpResponse
from django.shortcuts import redirect

def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            from .views import redirect_user_after_login
            return redirect_user_after_login(request.user)
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func

def allowed_roles(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            # Check if the user is authenticated
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Check if the user's role is in the allowed roles
            if request.user.role in allowed_roles or 'ALL' in allowed_roles:
                return view_func(request, *args, **kwargs)
            
            # If user's role is not allowed, redirect based on their role
            from .views import redirect_user_after_login
            return redirect_user_after_login(request.user)
        
        return wrapper_func
    return decorator
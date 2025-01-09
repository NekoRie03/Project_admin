from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.force_password_change:
            # Exempt URLs that should be accessible even when password change is required
            exempt_urls = [
                reverse('student_change_password'),
                reverse('guard_change_password'),
                reverse('user_logout'),
            ]
            
            # Don't redirect if user is already on password change page or logout
            if request.path not in exempt_urls:
                if request.user.role == 'STUDENT':
                    messages.warning(request, 'Please change your password to continue.')
                    return redirect('student_change_password')
                elif request.user.role == 'GUARD':
                    messages.warning(request, 'Please change your password to continue.')
                    return redirect('guard_change_password')

        response = self.get_response(request)
        return response
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.force_password_change:
                # Exclude the password change page and logout from the redirect
                if not request.path in [reverse('student_change_password'), reverse('logout')]:
                    messages.warning(request, 'Please change your password to continue.')
                    return redirect('student_change_password')
        return self.get_response(request)
from django.shortcuts import redirect
<<<<<<< HEAD
from django.contrib import messages
from django.urls import reverse
=======
from django.urls import reverse
from django.contrib import messages
>>>>>>> 3dc4122aeb5dfbedadf0afeda490a0bfd59a2309

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
<<<<<<< HEAD
        if request.user.is_authenticated:
            if request.user.force_password_change:
                # Exclude the password change page and logout from the redirect
                if not request.path in [reverse('student_change_password'), reverse('logout')]:
                    messages.warning(request, 'Please change your password to continue.')
                    return redirect('student_change_password')
        return self.get_response(request)
=======
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
>>>>>>> 3dc4122aeb5dfbedadf0afeda490a0bfd59a2309

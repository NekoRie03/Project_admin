from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from .models import StudentRegistration

class CustomAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                # Handle Student Authentication
                if user.role == "STUDENT":
                    try:
                        registration = StudentRegistration.objects.get(user=user)
                        # Always return user - let view handle the access control
                        return user
                    except StudentRegistration.DoesNotExist:
                        # Don't raise error, return None to indicate auth failure
                        return None
                # Handle other roles
                elif user.role in ["ADMIN", "GUARD"]:
                    if user.is_staff:
                        return user
                    return None
                else:
                    return None
        except User.DoesNotExist:
            return None
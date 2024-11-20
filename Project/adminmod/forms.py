from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import User, StudentRegistration

User = get_user_model()

class StudentSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        if commit:
            user.save()
        return user

class AdminSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=150, required=True)
    employee_id = forms.CharField(max_length=150, required=True, label='Employee ID')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'employee_id', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.ADMIN
        user.is_staff = True
        user.is_superuser = True
        
        if commit:
            user.save()
        return user

class GuardSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=150, required=True)
    employee_id = forms.CharField(max_length=150, required=True, label='Employee ID')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'employee_id', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.GUARD
        user.is_staff = True
        
        if commit:
            user.save()
        return user

class StudentRegistrationForm(forms.ModelForm):
    class Meta:
        model = StudentRegistration
        fields = ['cor_image', 'id_image']
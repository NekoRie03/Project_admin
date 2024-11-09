# Django core imports
from django import forms
from django.forms import ModelForm
# Local imports
from .models import (Course,DropdownOption,Report,Section,Signup,Userrole,ViolationType,)
# Python standard library imports
import random, string

class SignupNow(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirmpass = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = Signup
        fields = ['first_name', 'middle_initial', 'last_name', 'idnumber', 'email', 'password', 'confirmpass', 'program1', 'course', 'section', 'id_picture', 'registration_cert']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirmpass = cleaned_data.get("confirmpass")

        if password != confirmpass:
            raise forms.ValidationError("Passwords do not match.")

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['student', 'incident_date', 'violation_type','status']

class ViolationTypeForm(forms.ModelForm):
    class Meta:
        model = ViolationType
        fields = ['name', 'violation_type', 'description', 'guidelines', 'sanction_period_value', 'sanction_period_type', 'sanction']


class UserroleForm(forms.ModelForm):
    class Meta:
        model = Userrole
        fields = ['employee_id', 'first_name', 'middle_initial', 'last_name', 'position']

    def clean_employee_id(self):
        employee_id = self.cleaned_data['employee_id']
        if Userrole.objects.filter(employee_id=employee_id).exists():
            raise forms.ValidationError("Employee ID already exists.")
        return employee_id


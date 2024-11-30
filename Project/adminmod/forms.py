from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import User, StudentRegistration, Program, Section, Violation, Sanction
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError


User = get_user_model()

class StudentSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    
    # New fields for Program and Section
    program = forms.ModelChoiceField(
        queryset=Program.objects.all(), 
        required=True, 
        label="Program"
    )
    section = forms.ModelChoiceField(
        queryset=Section.objects.none(), 
        required=True, 
        label="Section"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'program', 'section', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamic section filtering based on selected program
        if 'program' in self.data:
            program_id = self.data.get('program')
            self.fields['section'].queryset = Section.objects.filter(program_id=program_id)
        else:
            self.fields['section'].queryset = Section.objects.none()

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.STUDENT
        user.email = self.cleaned_data['email']
        
        if commit:
            user.save()
            
            # Create StudentRegistration with program and section
            StudentRegistration.objects.create(
                user=user,
                program=self.cleaned_data['program'],
                section=self.cleaned_data['section']
            )
        
        return user

class AdminSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    employee_id = forms.CharField(max_length=150, required=True, label='Employee ID')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'employee_id', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.ADMIN
        user.email = self.cleaned_data['email']
        user.is_staff = True
        user.is_superuser = True
        
        if commit:
            user.save()
        return user

class GuardSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    employee_id = forms.CharField(max_length=150, required=True, label='Employee ID')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'employee_id', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.GUARD
        user.email = self.cleaned_data['email']
        user.is_staff = True
        
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
        fields = ['cor_image', 'id_image', 'program', 'section']
        
class StudentRegistrationAdminForm(forms.ModelForm):
    user_username = forms.CharField(
        max_length=150,
        required=True,
        label="Username"
    )
    user_first_name = forms.CharField(
        max_length=30,
        required=True,
        label="First Name"
    )
    user_last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Last Name"
    )
    user_email = forms.EmailField(
        required=True,
        label="Email"
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput,
        required=True
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        required=True
    )
    admin_password = forms.CharField(
        label="Admin Password Confirmation",
        widget=forms.PasswordInput,
        required=False,
        help_text="Enter your admin password to confirm changes"
    )
    review_comments = forms.CharField(
        widget=forms.Textarea,
        required=False,
        label="Review Comments"
    )

    class Meta:
        model = StudentRegistration
        fields = [
            'program', 'section',
            'cor_image', 'id_image',
            'is_approved',
            'review_comments'
        ]

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords do not match.")
        return password2

    def clean_admin_password(self):
        admin_password = self.cleaned_data.get('admin_password')
        current_user = self.initial.get('current_user')  # May be None

        # If no current user is provided, skip admin password validation
        if not current_user:
            return admin_password

        if not admin_password:
            raise ValidationError("Admin password is required to confirm changes.")
        
        # Verify the admin password belongs to the current admin user
        if not authenticate(username=current_user.username, password=admin_password):
            raise ValidationError("Incorrect admin password.")
        return admin_password

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)
        super().__init__(*args, **kwargs)

        # Make admin_password optional if no current user
        if not current_user:
            self.fields['admin_password'].required = False
            self.fields['admin_password'].widget.attrs['disabled'] = True

    def clean_user_username(self):
        username = self.cleaned_data.get('user_username')
        if not username:
            raise ValidationError("Username is required.")
        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        # Create the related user object
        user = User.objects.create(
            username=self.cleaned_data['user_username'],
            first_name=self.cleaned_data['user_first_name'],
            last_name=self.cleaned_data['user_last_name'],
            email=self.cleaned_data['user_email'],
            role=User.Role.STUDENT
        )
        user.set_password(self.cleaned_data['password1'])
        user.save()

        # Assign the user to the StudentRegistration instance
        self.instance.user = user

        # Ensure is_approved is set to None (Pending) by default
        if self.instance.is_approved is None:
            self.instance.is_approved = None

        return super().save(commit)

    def __init__(self, *args, **kwargs):
        current_user = kwargs.pop('current_user', None)  # Pass current user explicitly
        super().__init__(*args, **kwargs)

        # Pre-populate fields if an instance exists and has a user
        if self.instance and self.instance.user_id:
            self.fields['user_username'].initial = self.instance.user.username
            self.fields['user_first_name'].initial = self.instance.user.first_name
            self.fields['user_last_name'].initial = self.instance.user.last_name
            self.fields['user_email'].initial = self.instance.user.email

        # Ensure is_approved field is optional
        if 'is_approved' in self.fields:
            self.fields['is_approved'].required = False
            self.fields['is_approved'].initial = None

        # Make review_comments optional
        self.fields['review_comments'].required = False

    def clean(self):
        cleaned_data = super().clean()

        # Ensure all required fields are present
        required_fields = ['user_username', 'user_first_name', 'user_last_name', 'user_email', 'program', 'section']
        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, "This field is required.")

        return cleaned_data

class StaffSignupForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    employee_id = forms.CharField(max_length=150, required=True, label='Employee ID')
    role = forms.ChoiceField(
        choices=[
            (User.Role.ADMIN, 'Admin'),
            (User.Role.GUARD, 'Guard')
        ], 
        required=True, 
        initial=User.Role.ADMIN
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 
            'email', 'employee_id', 'role', 
            'password1', 'password2'
        ]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data['role']
        
        # Set staff status based on role
        if user.role in [User.Role.ADMIN, User.Role.GUARD]:
            user.is_staff = True
        
        # Set superuser only for admin
        if user.role == User.Role.ADMIN:
            user.is_superuser = True
        
        if commit:
            user.save()
        return user
    
class ProgramForm(forms.ModelForm):
    class Meta:
        model = Program
        fields = ['name', 'code', 'description']
        
    def clean_code(self):
        code = self.cleaned_data['code']
        # Ensure code is unique
        if Program.objects.exclude(pk=self.instance.pk).filter(code=code).exists():
            raise ValidationError("A program with this code already exists.")
        return code

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name', 'program']
        
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        program = cleaned_data.get('program')
        
        # Ensure section name is unique within the program
        if name and program:
            if Section.objects.exclude(pk=self.instance.pk).filter(name=name, program=program).exists():
                raise ValidationError("A section with this name already exists in the selected program.")
        
        return cleaned_data

class ViolationForm(forms.ModelForm):
    class Meta:
        model = Violation
        fields = ['name', 'description', 'severity']
        
    def clean_name(self):
        name = self.cleaned_data['name']
        # Ensure violation name is unique
        if Violation.objects.exclude(pk=self.instance.pk).filter(name=name).exists():
            raise ValidationError("A violation with this name already exists.")
        return name

class SanctionForm(forms.ModelForm):
    class Meta:
        model = Sanction
        fields = ['violation', 'name', 'description', 'duration_value', 'duration_unit']
        
    def clean(self):
        cleaned_data = super().clean()
        violation = cleaned_data.get('violation')
        name = cleaned_data.get('name')
        
        # Ensure sanction name is unique within the violation
        if violation and name:
            if Sanction.objects.exclude(pk=self.instance.pk).filter(violation=violation, name=name).exists():
                raise ValidationError("A sanction with this name already exists for the selected violation.")
        
        # Validate duration value
        duration_value = cleaned_data.get('duration_value')
        if duration_value and duration_value <= 0:
            raise ValidationError("Duration value must be a positive number.")
        
        return cleaned_data
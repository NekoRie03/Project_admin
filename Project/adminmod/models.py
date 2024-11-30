from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ValidationError
from django.utils import timezone
from django.urls import reverse

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True, default="")
    last_name = models.CharField(max_length=30, blank=True, default="")
    force_password_change = models.BooleanField(default=False)

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"
        GUARD = "GUARD", "Guard"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.STUDENT)

class Program(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        verbose_name = "Program"
        verbose_name_plural = "Programs"
        ordering = ['name']

class Section(models.Model):
    name = models.CharField(max_length=50)
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='sections')
    
    def __str__(self):
        return f"{self.name} - {self.program.name}"
    
    class Meta:
        verbose_name = "Section"
        verbose_name_plural = "Sections"
        unique_together = ['name', 'program']
        ordering = ['program', 'name']

class StudentRegistration(models.Model):
    STATUS_CHOICES = (
        (None, 'Pending Review'),
        (True, 'Approved'),
        (False, 'Declined'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(null=True, default=None, choices=STATUS_CHOICES)
    
    # New fields for Program and Section
    program = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True)
    
    cor_image = models.ImageField(upload_to='student_documents/cor/', null=True, blank=True)
    id_image = models.ImageField(upload_to='student_documents/id/', null=True, blank=True)
    
    review_comments = models.TextField(null=True, blank=True)
    registration_date = models.DateTimeField(default=timezone.now)
    review_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        user_name = self.user.get_full_name() if self.user else "Unknown User"
        status = "Approved" if self.is_approved else ("Pending" if self.is_approved is None else "Declined")
        return f"Registration for {user_name} - {status}"
    def approve_registration(self, comments=None):
        self.is_approved = True
        self.review_comments = comments
        self.review_date = timezone.now()
        self.save()
        # Force password change for the associated user
        self.user.force_password_change = True
        self.user.save()

    def decline_registration(self, comments=None):
        self.is_approved = False
        self.review_comments = comments
        self.review_date = timezone.now()
        self.save()

    def get_absolute_url(self):
        return reverse('admin:adminmod_studentregistration_detail', args=[self.pk])

    class Meta:
        verbose_name = "Student Registration"
        verbose_name_plural = "Student Registrations"

class StudentManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.STUDENT)

class Student(User):
    base_role = User.Role.STUDENT
    student = StudentManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for students"

@receiver(post_save, sender=Student)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "STUDENT" and instance.is_approved:
        StudentProfile.objects.create(user=instance)
@receiver(post_save, sender=StudentRegistration)
def update_student_profile_approval(sender, instance, **kwargs):
    # Update the associated StudentProfile's approval status
    try:
        student_profile = instance.user.studentprofile
        student_profile.is_approved = instance.is_approved
        student_profile.save()
    except StudentProfile.DoesNotExist:
        # Create a StudentProfile if it doesn't exist
        StudentProfile.objects.create(
            user=instance.user, 
            is_approved=instance.is_approved
        )

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.IntegerField(null=True, blank=True)
    is_approved = models.BooleanField(null=True, default=None)  # Added is_approved field

    def save(self, *args, **kwargs):
        # Automatically set is_approved from StudentRegistration if exists
        if hasattr(self.user, 'studentregistration'):
            self.is_approved = self.user.studentregistration.is_approved
        super().save(*args, **kwargs)

class GuardManager(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.GUARD)

class Guard(User):
    base_role = User.Role.GUARD
    guard = GuardManager()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for guards"

class GuardProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    guard_id = models.IntegerField(null=True, blank=True)

@receiver(post_save, sender=Guard)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == "GUARD":
        GuardProfile.objects.create(user=instance)

class Violation(models.Model):
    SEVERITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='medium')
    
    def __str__(self):
        return f"{self.name} ({self.get_severity_display()})"
    
    class Meta:
        verbose_name = "Violation"
        verbose_name_plural = "Violations"
        ordering = ['-severity', 'name']

class Sanction(models.Model):
    DURATION_UNITS = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ]
    
    violation = models.ForeignKey(Violation, on_delete=models.CASCADE, related_name='sanctions')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    duration_value = models.IntegerField(default=1)
    duration_unit = models.CharField(
        max_length=10, 
        choices=DURATION_UNITS, 
        default='days'
    )
    
    def __str__(self):
        return f"{self.name} - {self.duration_value} {self.get_duration_unit_display()}"
    
    class Meta:
        verbose_name = "Sanction"
        verbose_name_plural = "Sanctions"
        unique_together = ['violation', 'name']
        ordering = ['violation', 'name']
    DURATION_UNITS = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ]
    violation = models.ForeignKey('Violation', on_delete=models.CASCADE, related_name='sanctions')
    name = models.CharField(max_length=100)
    duration_value = models.IntegerField(default=1)
    duration_unit = models.CharField(
        max_length=10, 
        choices=DURATION_UNITS, 
        default='days'
    )
    created_at = models.DateTimeField(default=timezone.now)
    

    def __str__(self):
        return f"{self.name} - {self.duration_value} {self.get_duration_unit_display()}"


    def __str__(self):
        return f"{self.duration_value} {self.get_duration_unit_display()}"
    
    class Meta:
        verbose_name = "Sanction"
        verbose_name_plural = "Sanctions"
        unique_together = ['violation', 'name']
        ordering = ['violation', 'name']
        
class ViolationRecord(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'STUDENT'})
    violation = models.ForeignKey(Violation, on_delete=models.CASCADE)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='recorded_violations')
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.violation.name}"

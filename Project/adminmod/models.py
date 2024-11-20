from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.urls import reverse

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=30, blank=True, default="")
    last_name = models.CharField(max_length=30, blank=True, default="")

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        STUDENT = "STUDENT", "Student"
        GUARD = "GUARD", "Guard"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.STUDENT)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set email when creating a new user
            self.email = self.format_email()
        super().save(*args, **kwargs)

    def format_email(self):
        # Default email formatting logic based on role
        first_name = self.first_name.lower()
        last_name = self.last_name.lower()
        role_suffix = self.role.lower()
        return f"{first_name}.{last_name}_{role_suffix}@example.com"

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
    if created and instance.role == "STUDENT":
        StudentProfile.objects.create(user=instance)

class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.IntegerField(null=True, blank=True)

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

class StudentRegistration(models.Model):
    STATUS_CHOICES = (
        (None, 'Pending Review'),
        (True, 'Approved'),
        (False, 'Declined'),
    )
    
    is_approved = models.BooleanField(null=True, default=None, choices=STATUS_CHOICES)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cor_image = models.ImageField(upload_to='student_documents/cor/', null=True, blank=True)
    id_image = models.ImageField(upload_to='student_documents/id/', null=True, blank=True)
    is_approved = models.BooleanField(null=True, default=None)
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
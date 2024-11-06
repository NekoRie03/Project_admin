from django.db import models
from django.utils import timezone


# Create your models here.

class DropdownOption(models.Model):
    program1 = models.CharField(max_length=255, default='Default Program')

    def __str__(self):
        return self.program1

class Course(models.Model):
    program = models.ForeignKey(DropdownOption, on_delete=models.CASCADE)
    course_name = models.CharField(max_length=255)

    def __str__(self):
        return self.course_name


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    section_name = models.CharField(max_length=255)

    def __str__(self):
        return self.section_name

class Signup(models.Model):
    first_name = models.CharField(max_length=50, verbose_name='First Name')
    middle_initial = models.CharField(max_length=1, null=True, blank=True, verbose_name='Middle Initial')
    last_name = models.CharField(max_length=50, verbose_name='Last Name')
    idnumber = models.CharField(max_length=20, unique=True, verbose_name='ID Number')
    email = models.EmailField(unique=True, verbose_name='Email')
    password = models.CharField(max_length=8, verbose_name='Password')
    confirmpass = models.CharField(max_length=8, verbose_name='Confirm Password')
    program1 = models.ForeignKey(DropdownOption, on_delete=models.CASCADE, null=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True)
    section = models.ForeignKey(Section, on_delete=models.CASCADE, null=True)
    id_picture = models.FileField(upload_to='id_pictures/', verbose_name='ID Picture')
    registration_cert = models.FileField(upload_to='registration_certs/', verbose_name='Certificate of Registration (COR)')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

# Violation Models
class ViolationType(models.Model):
    VIOLATION_TYPE_CHOICES = [
        ('Minor', 'Minor'),
        ('Major', 'Major'),
    ]
    name = models.CharField(max_length=255)
    violation_type = models.CharField(max_length=10, choices=VIOLATION_TYPE_CHOICES)
    description = models.TextField()
    guidelines = models.TextField()
    sanction = models.CharField(max_length=255, null=True, blank=True)  
    sanction_period_value = models.IntegerField()
    sanction_period_type = models.CharField(max_length=10, choices=[('Day', 'Day'), ('Week', 'Week'), ('Month', 'Month')])

    def __str__(self):
        return self.name


class Report(models.Model):
    STATUS_TYPE_CHOICES = [
        ('On Hold', 'On Hold'),
        ('Active', 'Active'),
        ('Resolved', 'Resolved'),
        ('Deny', 'Deny'),
    ]
    student = models.ForeignKey(Signup, on_delete=models.CASCADE)
    incident_date = models.DateField()
    violation_type = models.ForeignKey(ViolationType, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_TYPE_CHOICES, default='On Hold')

    def __str__(self):
        return f"Report for {self.student.first_name} {self.student.last_name}"

class User(models.Model):
    USER_CHOICES = [
        ('GUARD', 'GUARD'),
        ('INSTRUCTOR', 'INSTRUCTOR'),
        ('ADMIN', 'ADMIN')
    ]
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50, default='', null=True)
    middle_initial = models.CharField(max_length=1, blank=True, null=True, default='')
    last_name = models.CharField(max_length=50, default='', null=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    position = models.CharField(max_length=10, choices=USER_CHOICES)
    
    def __str__(self):
        return f"{self.first_name} {self.middle_initial or ''} {self.last_name}".strip()
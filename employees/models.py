from django.db import models
from django.conf import settings

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_department')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self): return self.name

class Employee(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='employee_profile')
    employee_number = models.CharField(max_length=20, unique=True)
    national_id = models.CharField(max_length=20, unique=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='employees')
    position = models.CharField(max_length=100)
    employment_date = models.DateField()
    profile_photo = models.ImageField(upload_to='employee_photos/', blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self): return f"{self.employee_number} - {self.user.get_full_name()}"
    def get_full_name(self): return self.user.get_full_name()

class HRProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='hr_profile')
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True)
    signature = models.ImageField(upload_to='signatures/', blank=True, null=True)

    def __str__(self): return f"{self.user.get_full_name()} - HR"
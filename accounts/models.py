from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('hr_officer', 'HR Officer'),
        ('manager', 'Department Manager'),
        ('employee', 'Employee'),
    ]
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default='employee')
    profile_photo = models.ImageField(
        upload_to='profiles/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    def is_super_admin(self): return self.role == 'super_admin'
    def is_hr(self): return self.role == 'hr_officer'
    def is_manager(self): return self.role == 'manager'
    def is_employee(self): return self.role == 'employee'

    def __str__(
        self): return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

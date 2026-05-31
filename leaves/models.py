from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class LeaveType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    max_days = models.PositiveIntegerField(default=21)
    is_paid = models.BooleanField(default=True)
    requires_document = models.BooleanField(default=False)
    color = models.CharField(max_length=7, default='#0d6efd')
    is_active = models.BooleanField(default=True)

    def __str__(self): return self.name

class PublicHoliday(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['date']

    def __str__(self): return f"{self.name} ({self.date})"

class LeaveBalance(models.Model):
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE)
    year = models.PositiveIntegerField(default=2025)
    allocated_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)

    class Meta:
        unique_together = ('employee', 'leave_type', 'year')

    @property
    def remaining_days(self): return self.allocated_days - self.used_days

    def __str__(self): return f"{self.employee} - {self.leave_type} ({self.year})"

class LeaveApplication(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Manager Approval'),
        ('manager_approved', 'Manager Approved'),
        ('manager_rejected', 'Rejected by Manager'),
        ('hr_approved', 'HR Approved'),
        ('hr_rejected', 'Rejected by HR'),
        ('clarification', 'Clarification Needed'),
        ('cancelled', 'Cancelled'),
    ]
    leave_number = models.CharField(max_length=20, unique=True, blank=True)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='leave_applications')
    leave_type = models.ForeignKey(LeaveType, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField()
    num_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    reason = models.TextField()
    supporting_document = models.FileField(upload_to='leave_docs/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_date = models.DateTimeField(auto_now_add=True)
    # Approval fields
    manager_comment = models.TextField(blank=True)
    manager_action_date = models.DateTimeField(null=True, blank=True)
    manager_actioned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='manager_actions')
    hr_comment = models.TextField(blank=True)
    hr_action_date = models.DateTimeField(null=True, blank=True)
    hr_actioned_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='hr_actions')
    # PDF
    pdf_generated = models.BooleanField(default=False)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    return_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-applied_date']

    def save(self, *args, **kwargs):
        if not self.leave_number:
            count = LeaveApplication.objects.count() + 1
            self.leave_number = f"LV{timezone.now().year}{count:04d}"
        super().save(*args, **kwargs)

    @property
    def is_approved(self): return self.status == 'hr_approved'

    def __str__(self): return f"{self.leave_number} - {self.employee.get_full_name()}"
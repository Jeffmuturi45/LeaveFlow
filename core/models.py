from django.db import models
from django.conf import settings
import json

class DashboardWidget(models.Model):
    WIDGET_CHOICES = [
        ('employee_overview', 'Employee Overview'),
        ('leave_overview', 'Leave Overview'),
        ('department_breakdown', 'Department Breakdown'),
        ('recent_activities', 'Recent Activities'),
        ('leave_type_distribution', 'Leave Type Distribution'),
        ('system_health', 'System Health'),
        ('on_leave_today', 'On Leave Today'),
        ('pending_approvals', 'Pending Approvals'),
        ('recent_applications', 'Recent Applications'),
        ('leave_balance_overview', 'Leave Balance Overview'),
        ('department_counts', 'Department Counts'),
        ('upcoming_holidays', 'Upcoming Holidays'),
        ('team_count', 'Team Count'),
        ('team_on_leave', 'Team On Leave'),
        ('approved_this_month', 'Approved This Month'),
        ('pending_requests', 'Pending Requests'),
        ('my_leave_balance', 'My Leave Balance'),
        ('quick_apply', 'Quick Apply'),
        ('calendar_mini', 'Calendar Mini'),
    ]

    widget_id = models.CharField(max_length=50, unique=True, choices=WIDGET_CHOICES)
    title = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='fas fa-chart-bar')
    description = models.TextField(blank=True)
    roles = models.JSONField(default=list)
    default_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Dashboard Widget'
        ordering = ['widget_id']

    def __str__(self):
        return f"{self.title}"

class DashboardCustomization(models.Model):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('hr_officer', 'HR Officer'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]

    role = models.CharField(max_length=20, unique=True, choices=ROLE_CHOICES)
    enabled_widgets = models.JSONField(default=list)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Dashboard Customizations'
        ordering = ['role']

    def __str__(self):
        return f"Dashboard Config - {self.get_role_display()}"

    @classmethod
    def get_customization(cls, role):
        obj, _ = cls.objects.get_or_create(role=role, defaults={'enabled_widgets': []})
        return obj

class CompanySettings(models.Model):
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='company/', blank=True, null=True)
    physical_address = models.TextField(blank=True)
    postal_address = models.CharField(max_length=200, blank=True)
    email = models.EmailField(blank=True)
    telephone = models.CharField(max_length=30, blank=True)
    website = models.URLField(blank=True)
    stamp = models.ImageField(upload_to='company/', blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Company Settings'

    def __str__(self): return self.name

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'name': 'My Company'})
        return obj

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self): return self.title

class AuditLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=300)
    model_name = models.CharField(max_length=100, blank=True)
    object_id = models.CharField(max_length=50, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self): return f"{self.user} - {self.action}"
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count
from accounts.models import User
from core.models import CompanySettings, AuditLog, Notification
from employees.models import Employee, Department, HRProfile
from leaves.models import LeaveType, LeaveApplication, LeaveBalance, PublicHoliday

# ─────────────────────────────────────────────
# Admin Site Customization
# ─────────────────────────────────────────────
admin.site.site_header  = "LeaveFlow Admin"
admin.site.site_title   = "LeaveFlow"
admin.site.index_title  = "System Administration Panel"


# ─────────────────────────────────────────────
# User Admin
# ─────────────────────────────────────────────
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display  = ('username', 'get_full_name', 'email', 'role_badge', 'is_active_icon', 'date_joined')
    list_filter   = ('role', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering      = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'profile_photo')}),
        (_('Role & Access'), {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        (_('Timestamps'), {'fields': ('date_joined', 'last_login'), 'classes': ('collapse',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2'),
        }),
    )

    @admin.display(description='Role', ordering='role')
    def role_badge(self, obj):
        colors = {
            'super_admin': '#8b5cf6',
            'hr_officer':  '#10b981',
            'manager':     '#f59e0b',
            'employee':    '#6366f1',
        }
        color = colors.get(obj.role, '#6b7280')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 10px;border-radius:20px;font-size:11px;font-weight:600;">{}</span>',
            color, obj.get_role_display()
        )

    @admin.display(description='Active', boolean=True)
    def is_active_icon(self, obj):
        return obj.is_active


# ─────────────────────────────────────────────
# Company Settings Admin
# ─────────────────────────────────────────────
@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'telephone', 'website', 'updated_at')
    readonly_fields = ('updated_at',)

    def has_add_permission(self, request):
        # Only one settings record allowed
        return not CompanySettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


# ─────────────────────────────────────────────
# Audit Log Admin
# ─────────────────────────────────────────────
@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display  = ('timestamp', 'user', 'action_truncated', 'ip_address', 'model_name')
    list_filter   = ('model_name', 'timestamp')
    search_fields = ('action', 'user__username', 'ip_address')
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'ip_address', 'timestamp')
    ordering      = ('-timestamp',)
    date_hierarchy = 'timestamp'

    def has_add_permission(self, request):    return False
    def has_change_permission(self, request, obj=None): return False

    @admin.display(description='Action')
    def action_truncated(self, obj):
        return obj.action[:80] + '…' if len(obj.action) > 80 else obj.action


# ─────────────────────────────────────────────
# Notification Admin
# ─────────────────────────────────────────────
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('user', 'title', 'is_read', 'created_at')
    list_filter   = ('is_read', 'created_at')
    search_fields = ('user__username', 'title')
    ordering      = ('-created_at',)


# ─────────────────────────────────────────────
# Department Admin
# ─────────────────────────────────────────────
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display  = ('name', 'manager', 'employee_count', 'created_at')
    search_fields = ('name',)
    autocomplete_fields = ('manager',)

    @admin.display(description='Employees')
    def employee_count(self, obj):
        return obj.employees.filter(is_active=True).count()


# ─────────────────────────────────────────────
# Employee Admin
# ─────────────────────────────────────────────
@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display  = ('employee_number', 'get_full_name', 'department', 'position', 'employment_date', 'is_active')
    list_filter   = ('department', 'is_active', 'employment_date')
    search_fields = ('employee_number', 'user__first_name', 'user__last_name', 'user__email', 'national_id')
    ordering      = ('employee_number',)
    readonly_fields = ('employment_date',)

    @admin.display(description='Name', ordering='user__first_name')
    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username


# ─────────────────────────────────────────────
# HR Profile Admin
# ─────────────────────────────────────────────
@admin.register(HRProfile)
class HRProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'designation', 'department')
    search_fields = ('user__username', 'designation')


# ─────────────────────────────────────────────
# Leave Type Admin
# ─────────────────────────────────────────────
@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display  = ('name', 'max_days', 'paid_badge', 'requires_document', 'color_swatch', 'is_active')
    list_filter   = ('is_paid', 'requires_document', 'is_active')
    search_fields = ('name',)

    @admin.display(description='Paid?')
    def paid_badge(self, obj):
        color = '#10b981' if obj.is_paid else '#ef4444'
        label = 'Paid' if obj.is_paid else 'Unpaid'
        return format_html('<span style="color:{}; font-weight:600;">{}</span>', color, label)

    @admin.display(description='Color')
    def color_swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:18px;height:18px;border-radius:4px;background:{};vertical-align:middle;"></span> {}',
            obj.color, obj.color
        )


# ─────────────────────────────────────────────
# Public Holiday Admin
# ─────────────────────────────────────────────
@admin.register(PublicHoliday)
class PublicHolidayAdmin(admin.ModelAdmin):
    list_display  = ('name', 'date', 'description')
    list_filter   = ('date',)
    search_fields = ('name',)
    ordering      = ('date',)
    date_hierarchy = 'date'


# ─────────────────────────────────────────────
# Leave Balance Admin
# ─────────────────────────────────────────────
@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display  = ('employee', 'leave_type', 'year', 'allocated_days', 'used_days', 'remaining_days_display')
    list_filter   = ('year', 'leave_type')
    search_fields = ('employee__username', 'employee__first_name')
    ordering      = ('-year', 'employee__first_name')

    @admin.display(description='Remaining')
    def remaining_days_display(self, obj):
        remaining = obj.remaining_days
        color = '#10b981' if remaining > 5 else '#f59e0b' if remaining > 0 else '#ef4444'
        return format_html('<strong style="color:{};">{}</strong>', color, remaining)


# ─────────────────────────────────────────────
# Leave Application Admin
# ─────────────────────────────────────────────
@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):
    list_display  = ('leave_number', 'employee_name', 'leave_type', 'start_date', 'end_date', 'num_days', 'status_badge', 'applied_date')
    list_filter   = ('status', 'leave_type', 'applied_date')
    search_fields = ('leave_number', 'employee__first_name', 'employee__last_name', 'employee__username')
    ordering      = ('-applied_date',)
    readonly_fields = ('leave_number', 'applied_date', 'num_days', 'return_date', 'manager_action_date', 'hr_action_date')
    date_hierarchy = 'applied_date'

    fieldsets = (
        ('Application', {'fields': ('leave_number', 'employee', 'leave_type', 'start_date', 'end_date', 'num_days', 'return_date', 'reason', 'supporting_document')}),
        ('Status', {'fields': ('status', 'applied_date')}),
        ('Manager Review', {'fields': ('manager_actioned_by', 'manager_action_date', 'manager_comment'), 'classes': ('collapse',)}),
        ('HR Review', {'fields': ('hr_actioned_by', 'hr_action_date', 'hr_comment'), 'classes': ('collapse',)}),
        ('Documents', {'fields': ('pdf_generated', 'qr_code'), 'classes': ('collapse',)}),
    )

    @admin.display(description='Employee', ordering='employee__first_name')
    def employee_name(self, obj):
        return obj.employee.get_full_name() or obj.employee.username

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        colors = {
            'pending':           ('#f59e0b', '#fff'),
            'manager_approved':  ('#3b82f6', '#fff'),
            'hr_approved':       ('#10b981', '#fff'),
            'manager_rejected':  ('#ef4444', '#fff'),
            'hr_rejected':       ('#ef4444', '#fff'),
            'clarification':     ('#6b7280', '#fff'),
            'cancelled':         ('#9ca3af', '#fff'),
            'draft':             ('#9ca3af', '#fff'),
        }
        bg, fg = colors.get(obj.status, ('#6b7280', '#fff'))
        return format_html(
            '<span style="background:{};color:{};padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600;">{}</span>',
            bg, fg, obj.get_status_display()
        )

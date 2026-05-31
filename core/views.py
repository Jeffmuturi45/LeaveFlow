from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .models import CompanySettings, AuditLog, Notification, DashboardCustomization, DashboardWidget
from leaves.models import LeaveApplication, LeaveType, LeaveBalance
from employees.models import Employee, Department
from accounts.models import User

def dashboard_redirect(request):
    if not request.user.is_authenticated:
        return redirect('/accounts/login/')
    return redirect('/dashboard/')

@login_required
def dashboard(request):
    user = request.user
    today = timezone.now().date()
    year = today.year

    ctx = {}
    customization = DashboardCustomization.get_customization(user.role)
    enabled_widgets = customization.enabled_widgets if customization.enabled_widgets else []

    if user.role in ('super_admin', 'hr_officer'):
        ctx['total_employees'] = Employee.objects.filter(is_active=True).count()
        ctx['on_leave_today'] = LeaveApplication.objects.filter(
            status='hr_approved', start_date__lte=today, end_date__gte=today).count()
        ctx['pending_hr'] = LeaveApplication.objects.filter(status='manager_approved').count()
        ctx['total_departments'] = Department.objects.count()
        ctx['recent_applications'] = LeaveApplication.objects.select_related('employee', 'leave_type').order_by('-applied_date')[:8]
        ctx['leave_type_stats'] = LeaveApplication.objects.filter(
            status='hr_approved', applied_date__year=year
        ).values('leave_type__name').annotate(count=Count('id')).order_by('-count')[:5]

    elif user.role == 'manager':
        try:
            dept = Department.objects.get(manager=user)
            dept_employees = Employee.objects.filter(department=dept).values_list('user_id', flat=True)
            ctx['team_count'] = len(dept_employees)
            ctx['pending_approvals'] = LeaveApplication.objects.filter(
                employee__in=dept_employees, status='pending').count()
            ctx['approved_this_month'] = LeaveApplication.objects.filter(
                employee__in=dept_employees, status='hr_approved',
                applied_date__year=today.year, applied_date__month=today.month).count()
            ctx['team_on_leave'] = LeaveApplication.objects.filter(
                employee__in=dept_employees, status='hr_approved',
                start_date__lte=today, end_date__gte=today).count()
            ctx['pending_leaves'] = LeaveApplication.objects.filter(
                employee__in=dept_employees, status='pending'
            ).select_related('employee', 'leave_type').order_by('-applied_date')[:6]
        except Department.DoesNotExist:
            pass
    else:
        ctx['my_applications'] = LeaveApplication.objects.filter(employee=user).order_by('-applied_date')[:5]
        ctx['pending_count'] = LeaveApplication.objects.filter(employee=user, status='pending').count()
        ctx['approved_count'] = LeaveApplication.objects.filter(employee=user, status='hr_approved').count()
        ctx['balances'] = LeaveBalance.objects.filter(employee=user, year=year).select_related('leave_type')

    ctx['enabled_widgets'] = enabled_widgets
    ctx['user_role'] = user.role
    return render(request, 'core/dashboard.html', ctx)

@login_required
def dashboard_customization_view(request):
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('/dashboard/')

    customization = DashboardCustomization.get_customization(request.user.role)
    available_widgets = DashboardWidget.objects.filter(roles__contains=request.user.role)

    if request.method == 'POST':
        enabled = request.POST.getlist('enabled_widgets')
        customization.enabled_widgets = enabled
        customization.save()
        messages.success(request, 'Dashboard customization saved.')
        return redirect('/dashboard/customize/')

    ctx = {
        'customization': customization,
        'available_widgets': available_widgets,
        'selected_widgets': set(customization.enabled_widgets)
    }
    return render(request, 'core/dashboard_customization.html', ctx)

@login_required
def company_settings_view(request):
    if not (request.user.is_super_admin() or request.user.is_hr()):
        messages.error(request, 'Access denied.')
        return redirect('/dashboard/')
    settings_obj = CompanySettings.get_settings()
    if request.method == 'POST':
        settings_obj.name = request.POST.get('name', settings_obj.name)
        settings_obj.physical_address = request.POST.get('physical_address', '')
        settings_obj.postal_address = request.POST.get('postal_address', '')
        settings_obj.email = request.POST.get('email', '')
        settings_obj.telephone = request.POST.get('telephone', '')
        settings_obj.website = request.POST.get('website', '')
        if 'logo' in request.FILES:
            settings_obj.logo = request.FILES['logo']
        if 'stamp' in request.FILES:
            settings_obj.stamp = request.FILES['stamp']
        settings_obj.save()
        messages.success(request, 'Company settings updated.')
        return redirect('/core/settings/')
    return render(request, 'core/company_settings.html', {'settings': settings_obj})

@login_required
def audit_log_view(request):
    if not request.user.is_super_admin():
        messages.error(request, 'Access denied.')
        return redirect('/dashboard/')
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')[:200]
    return render(request, 'core/audit_log.html', {'logs': logs})

@login_required
def mark_notifications_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect(request.META.get('HTTP_REFERER', '/dashboard/'))


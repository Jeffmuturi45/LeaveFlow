from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import LeaveApplication, LeaveType, LeaveBalance, PublicHoliday
from core.models import Notification, AuditLog
from employees.models import Department, Employee
import datetime

def log_action(user, action, req=None):
    ip = req.META.get('REMOTE_ADDR') if req else None
    AuditLog.objects.create(user=user, action=action, ip_address=ip)

def notify(user, title, message, link=''):
    Notification.objects.create(user=user, title=title, message=message, link=link)

def calc_working_days(start, end, holidays):
    count = 0
    cur = start
    holiday_dates = set(holidays.values_list('date', flat=True))
    while cur <= end:
        if cur.weekday() < 5 and cur not in holiday_dates:
            count += 1
        cur += datetime.timedelta(days=1)
    return count

@login_required
def apply_leave(request):
    leave_types = LeaveType.objects.filter(is_active=True)
    today = timezone.now().date()
    if request.method == 'POST':
        lt_id = request.POST.get('leave_type')
        start = request.POST.get('start_date')
        end = request.POST.get('end_date')
        reason = request.POST.get('reason', '')
        if lt_id and start and end:
            try:
                start_d = datetime.date.fromisoformat(start)
                end_d = datetime.date.fromisoformat(end)
                if end_d < start_d:
                    messages.error(request, 'End date must be after start date.')
                else:
                    holidays = PublicHoliday.objects.filter(date__gte=start_d, date__lte=end_d)
                    num_days = calc_working_days(start_d, end_d, holidays)
                    return_date = end_d + datetime.timedelta(days=1)
                    while return_date.weekday() >= 5:
                        return_date += datetime.timedelta(days=1)

                    app = LeaveApplication.objects.create(
                        employee=request.user,
                        leave_type_id=lt_id,
                        start_date=start_d,
                        end_date=end_d,
                        num_days=num_days,
                        reason=reason,
                        return_date=return_date,
                    )
                    if 'supporting_document' in request.FILES:
                        app.supporting_document = request.FILES['supporting_document']
                        app.save()

                    log_action(request.user, f'Leave application {app.leave_number} submitted', request)
                    messages.success(request, f'Leave application {app.leave_number} submitted successfully!')
                    return redirect('/leaves/my-leaves/')
            except ValueError as e:
                messages.error(request, f'Invalid date format: {e}')
    return render(request, 'leaves/apply_leave.html', {'leave_types': leave_types, 'today': today})

@login_required
def my_leaves(request):
    apps = LeaveApplication.objects.filter(employee=request.user).select_related('leave_type').order_by('-applied_date')
    return render(request, 'leaves/my_leaves.html', {'applications': apps})

@login_required
def leave_detail(request, pk):
    app = get_object_or_404(LeaveApplication, pk=pk)
    can_action = False
    if request.user.role == 'manager' and app.status == 'pending':
        can_action = True
    if request.user.role in ('hr_officer', 'super_admin') and app.status == 'manager_approved':
        can_action = True
    return render(request, 'leaves/leave_detail.html', {'app': app, 'can_action': can_action})

@login_required
def leave_action(request, pk):
    app = get_object_or_404(LeaveApplication, pk=pk)
    action = request.POST.get('action')
    comment = request.POST.get('comment', '')

    if request.user.role == 'manager' and app.status == 'pending':
        app.manager_actioned_by = request.user
        app.manager_action_date = timezone.now()
        app.manager_comment = comment
        if action == 'approve':
            app.status = 'manager_approved'
            notify(app.employee, 'Leave Manager Approved', f'Your leave {app.leave_number} has been approved by manager.', f'/leaves/detail/{app.id}/')
            messages.success(request, 'Leave approved by manager.')
        elif action == 'reject':
            app.status = 'manager_rejected'
            notify(app.employee, 'Leave Rejected', f'Your leave {app.leave_number} was rejected by manager.', f'/leaves/detail/{app.id}/')
            messages.warning(request, 'Leave rejected.')
        elif action == 'clarify':
            app.status = 'clarification'
            notify(app.employee, 'Clarification Needed', f'Please clarify your leave {app.leave_number}.', f'/leaves/detail/{app.id}/')
            messages.info(request, 'Clarification requested.')
        app.save()
        log_action(request.user, f'Manager {action}d leave {app.leave_number}', request)

    elif request.user.role in ('hr_officer', 'super_admin') and app.status == 'manager_approved':
        app.hr_actioned_by = request.user
        app.hr_action_date = timezone.now()
        app.hr_comment = comment
        if action == 'approve':
            app.status = 'hr_approved'
            # Update balance
            year = app.start_date.year
            bal, _ = LeaveBalance.objects.get_or_create(employee=app.employee, leave_type=app.leave_type, year=year, defaults={'allocated_days': app.leave_type.max_days})
            bal.used_days += app.num_days
            bal.save()
            notify(app.employee, 'Leave Fully Approved!', f'Your leave {app.leave_number} has been approved. Enjoy your time off!', f'/leaves/detail/{app.id}/')
            messages.success(request, 'Leave fully approved by HR.')
        elif action == 'reject':
            app.status = 'hr_rejected'
            notify(app.employee, 'Leave HR Rejected', f'Your leave {app.leave_number} was rejected by HR.', f'/leaves/detail/{app.id}/')
            messages.warning(request, 'Leave rejected by HR.')
        app.save()
        log_action(request.user, f'HR {action}d leave {app.leave_number}', request)

    return redirect(f'/leaves/detail/{pk}/')

@login_required
def manager_approvals(request):
    if request.user.role != 'manager':
        return redirect('/dashboard/')
    try:
        dept = Department.objects.get(manager=request.user)
        dept_employees = Employee.objects.filter(department=dept).values_list('user_id', flat=True)
        applications = LeaveApplication.objects.filter(
            employee__in=dept_employees, status='pending'
        ).select_related('employee', 'leave_type').order_by('-applied_date')
    except Department.DoesNotExist:
        applications = LeaveApplication.objects.none()
    return render(request, 'leaves/manager_approvals.html', {'applications': applications})

@login_required
def hr_approvals(request):
    if request.user.role not in ('hr_officer', 'super_admin'):
        return redirect('/dashboard/')
    status_filter = request.GET.get('status', 'manager_approved')
    applications = LeaveApplication.objects.filter(status=status_filter).select_related('employee', 'leave_type').order_by('-applied_date')
    return render(request, 'leaves/hr_approvals.html', {'applications': applications, 'status_filter': status_filter})

@login_required
def leave_balance(request):
    year = int(request.GET.get('year', timezone.now().year))
    balances = LeaveBalance.objects.filter(employee=request.user, year=year).select_related('leave_type')
    return render(request, 'leaves/leave_balance.html', {'balances': balances, 'year': year})

@login_required
def leave_calendar(request):
    today = timezone.now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    approved = LeaveApplication.objects.filter(status='hr_approved').select_related('employee', 'leave_type')
    holidays = PublicHoliday.objects.filter(date__year=year, date__month=month)
    return render(request, 'leaves/calendar.html', {'year': year, 'month': month, 'approved': approved, 'holidays': holidays, 'today': today})

@login_required
def leave_types(request):
    if request.user.role not in ('hr_officer', 'super_admin'):
        return redirect('/dashboard/')
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            LeaveType.objects.create(
                name=name,
                description=request.POST.get('description',''),
                max_days=request.POST.get('max_days', 21),
                is_paid=request.POST.get('is_paid') == 'on',
                requires_document=request.POST.get('requires_document') == 'on',
                color=request.POST.get('color', '#6366f1'),
            )
            messages.success(request, 'Leave type created.')
            return redirect('/leaves/types/')
    types = LeaveType.objects.all()
    return render(request, 'leaves/leave_types.html', {'leave_types': types})

@login_required
def public_holidays(request):
    if request.user.role not in ('hr_officer', 'super_admin'):
        return redirect('/dashboard/')
    if request.method == 'POST':
        name = request.POST.get('name')
        date = request.POST.get('date')
        if name and date:
            PublicHoliday.objects.get_or_create(date=date, defaults={'name': name, 'description': request.POST.get('description','')})
            messages.success(request, f'Holiday "{name}" added.')
            return redirect('/leaves/holidays/')
    holidays = PublicHoliday.objects.order_by('date')
    return render(request, 'leaves/public_holidays.html', {'holidays': holidays})

@login_required
def reports(request):
    if request.user.role not in ('hr_officer', 'super_admin'):
        return redirect('/dashboard/')
    return render(request, 'leaves/reports.html', {})

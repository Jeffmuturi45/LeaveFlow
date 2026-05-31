from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Employee, Department, HRProfile
from accounts.models import User

def hr_or_admin(user):
    return user.role in ('super_admin', 'hr_officer')

@login_required
def employee_list(request):
    if not hr_or_admin(request.user):
        messages.error(request, 'Access denied.')
        return redirect('/dashboard/')
    q = request.GET.get('q', '')
    dept = request.GET.get('dept', '')
    employees = Employee.objects.select_related('user', 'department').filter(is_active=True)
    if q:
        employees = employees.filter(Q(user__first_name__icontains=q) | Q(user__last_name__icontains=q) | Q(employee_number__icontains=q))
    if dept:
        employees = employees.filter(department_id=dept)
    departments = Department.objects.all()
    return render(request, 'employees/employee_list.html', {'employees': employees, 'departments': departments, 'q': q, 'selected_dept': dept})

@login_required
def employee_add(request):
    if not hr_or_admin(request.user):
        return redirect('/dashboard/')
    departments = Department.objects.all()
    if request.method == 'POST':
        try:
            user = User.objects.create_user(
                username=request.POST['username'],
                first_name=request.POST['first_name'],
                last_name=request.POST['last_name'],
                email=request.POST['email'],
                password=request.POST['password'],
                role='employee',
                phone=request.POST.get('phone', '')
            )
            emp = Employee.objects.create(
                user=user,
                employee_number=request.POST['employee_number'],
                national_id=request.POST['national_id'],
                department_id=request.POST.get('department') or None,
                position=request.POST['position'],
                employment_date=request.POST['employment_date'],
            )
            if 'profile_photo' in request.FILES:
                emp.profile_photo = request.FILES['profile_photo']
                emp.save()
            messages.success(request, f'Employee {user.get_full_name()} added successfully.')
            return redirect('/employees/')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'employees/employee_form.html', {'departments': departments, 'action': 'Add'})

@login_required
def employee_detail(request, pk):
    if not hr_or_admin(request.user):
        return redirect('/dashboard/')
    emp = get_object_or_404(Employee, pk=pk)
    return render(request, 'employees/employee_detail.html', {'emp': emp})

@login_required
def department_list(request):
    if not hr_or_admin(request.user):
        return redirect('/dashboard/')
    departments = Department.objects.prefetch_related('employees').select_related('manager').all()
    return render(request, 'employees/department_list.html', {'departments': departments})

@login_required
def department_add(request):
    if not hr_or_admin(request.user):
        return redirect('/dashboard/')
    managers = User.objects.filter(role='manager')
    if request.method == 'POST':
        name = request.POST.get('name')
        manager_id = request.POST.get('manager') or None
        description = request.POST.get('description', '')
        if name:
            dept, created = Department.objects.get_or_create(name=name, defaults={'manager_id': manager_id, 'description': description})
            if not created:
                messages.warning(request, 'Department already exists.')
            else:
                messages.success(request, f'Department "{name}" created.')
            return redirect('/employees/departments/')
    return render(request, 'employees/department_form.html', {'managers': managers, 'action': 'Add'})

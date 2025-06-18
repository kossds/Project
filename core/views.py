from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import date, datetime, timedelta
from .models import Employee, TimeEntry, ActiveSession
from .forms import RegistrationForm, ManualEntryForm  # Предполагается, что вы создали эти формы
from django.db.models import Sum, Q

# Главная страница
def index(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'index.html')

# Вход
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        employee = Employee.objects.filter(email=email).first()
        if employee and employee.check_password(password):
            if employee.is_active:
                auth_login(request, employee)
                next_page = request.GET.get('next')
                return redirect(next_page) if next_page else redirect('dashboard')
            else:
                messages.error(request, 'Your account has been deactivated. Please contact HR.')
        else:
            messages.error(request, 'Invalid email or password.')
    return render(request, 'login.html')

# Выход
@login_required
def logout_view(request):
    auth_logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('index')

# Регистрация
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.set_password(form.cleaned_data['password'])  # Используем метод Django для хеширования пароля
            employee.save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('login')
        else:
            messages.error(request, 'Registration failed. Please check the form.')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

# Панель управления (для авторизованных пользователей)
@login_required
def dashboard(request):
    today_hours = request.user.get_total_hours_today()
    week_hours = request.user.get_total_hours_week()
    month_hours = request.user.get_total_hours_month()
    active_session = ActiveSession.objects.filter(employee=request.user).first()
    recent_entries = TimeEntry.objects.filter(employee=request.user).order_by('-date', '-created_at')[:5]
    total_employees = 0
    total_active_sessions = 0
    if request.user.is_admin:
        total_employees = Employee.objects.filter(is_active=True).count()
        total_active_sessions = ActiveSession.objects.count()
    context = {
        'today_hours': today_hours,
        'week_hours': week_hours,
        'month_hours': month_hours,
        'active_session': active_session,
        'recent_entries': recent_entries,
        'total_employees': total_employees,
        'total_active_sessions': total_active_sessions,
    }
    return render(request, 'dashboard.html', context)

# Список сотрудников (только для администраторов)
@login_required
def employees_list(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    search_query = request.GET.get('search', '')
    department_filter = request.GET.get('department', '')
    query = Employee.objects.all()
    if search_query:
        query = query.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(employee_id__icontains=search_query)
        )
    if department_filter:
        query = query.filter(department=department_filter)
    employees = query.order_by('first_name', 'last_name').all()
    departments = Employee.objects.values_list('department', flat=True).distinct().exclude(department='')
    context = {
        'employees': employees,
        'departments': departments,
        'search': search_query,
        'selected_department': department_filter,
    }
    return render(request, 'employees.html', context)

# Трекинг времени
@login_required
def time_tracking(request):
    active_session = ActiveSession.objects.filter(employee=request.user).first()
    today = date.today()
    today_entries = TimeEntry.objects.filter(employee=request.user, date=today).order_by('-created_at').all()
    context = {
        'active_session': active_session,
        'today_entries': today_entries,
    }
    return render(request, 'time_tracking.html', context)

# Начать сессию
@login_required
def start_session(request):
    if request.method == 'POST':
        existing_session = ActiveSession.objects.filter(employee=request.user).first()
        if existing_session:
            messages.warning(request, 'You already have an active session running.')
            return redirect('time_tracking')
        description = request.POST.get('description', '')
        project = request.POST.get('project', '')
        session = ActiveSession.objects.create(
            employee=request.user,
            description=description,
            project=project
        )
        messages.success(request, 'Work session started successfully!')
        return redirect('time_tracking')
    return redirect('time_tracking')

# Завершить сессию
@login_required
def stop_session(request):
    if request.method == 'POST':
        active_session = ActiveSession.objects.filter(employee=request.user).first()
        if not active_session:
            messages.error(request, 'No active session found.')
            return redirect('time_tracking')
        end_time = timezone.now()
        duration = end_time - active_session.start_time
        hours_worked = round(duration.total_seconds() / 3600, 2)
        time_entry = TimeEntry.objects.create(
            employee=request.user,
            date=date.today(),
            start_time=active_session.start_time.time(),
            end_time=end_time.time(),
            hours_worked=hours_worked,
            description=active_session.description,
            project=active_session.project
        )
        active_session.delete()
        messages.success(request, f'Session ended. Worked for {hours_worked} hours.')
        return redirect('time_tracking')
    return redirect('time_tracking')

# Добавить ручной запись
@login_required
def add_manual_entry(request):
    if request.method == 'POST':
        form = ManualEntryForm(request.POST)
        if form.is_valid():
            entry_date = form.cleaned_data['date']
            start_time = form.cleaned_data['start_time']
            end_time = form.cleaned_data['end_time']
            break_hours = form.cleaned_data['break_hours']
            description = form.cleaned_data['description']
            project = form.cleaned_data['project']
            time_entry = TimeEntry.objects.create(
                employee=request.user,
                date=entry_date,
                start_time=start_time,
                end_time=end_time,
                break_hours=break_hours,
                description=description,
                project=project
            )
            time_entry.calculate_hours()
            messages.success(request, 'Time entry added successfully!')
            return redirect('time_tracking')
        messages.error(request, 'Failed to add manual entry. Please check the form.')
    else:
        form = ManualEntryForm()
    return render(request, 'add_manual_entry.html', {'form': form})

# Отчеты
@login_required
def reports(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if not start_date or not end_date:
        today = date.today()
        start_date = today.replace(day=1)
        end_date = today
    entries = TimeEntry.objects.filter(date__range=(start_date, end_date))
    if not request.user.is_admin:
        entries = entries.filter(employee=request.user)
    entries = entries.order_by('-date').all()
    total_hours = entries.aggregate(Sum('hours_worked'))['hours_worked__sum'] or 0
    total_entries = entries.count()
    employee_summary = {}
    if request.user.is_admin:
        for entry in entries:
            emp_id = entry.employee.id
            if emp_id not in employee_summary:
                employee_summary[emp_id] = {
                    'employee': entry.employee,
                    'total_hours': 0,
                    'entries_count': 0
                }
            employee_summary[emp_id]['total_hours'] += entry.hours_worked
            employee_summary[emp_id]['entries_count'] += 1
    context = {
        'entries': entries,
        'start_date': start_date,
        'end_date': end_date,
        'total_hours': total_hours,
        'total_entries': total_entries,
        'employee_summary': employee_summary,
    }
    return render(request, 'reports.html', context)

# Админка
@login_required
def admin_panel(request):
    if not request.user.is_admin:
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('dashboard')
    pending_entries = TimeEntry.objects.filter(is_approved=False).order_by('-created_at').all()
    recent_employees = Employee.objects.order_by('-created_at')[:10]
    active_sessions = ActiveSession.objects.select_related('employee').order_by('start_time').all()
    context = {
        'pending_entries': pending_entries,
        'recent_employees': recent_employees,
        'active_sessions': active_sessions,
    }
    return render(request, 'admin.html', context)

# Одобрить запись
@login_required
def approve_entry(request, entry_id):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    entry = get_object_or_404(TimeEntry, id=entry_id)
    entry.is_approved = True
    entry.save()
    messages.success(request, 'Time entry approved successfully.')
    return redirect('admin_panel')

# Изменить статус сотрудника
@login_required
def toggle_employee_status(request, employee_id):
    if not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    employee = get_object_or_404(Employee, id=employee_id)
    employee.is_active = not employee.is_active
    employee.save()
    status = 'activated' if employee.is_active else 'deactivated'
    messages.success(request, f'Employee {employee.full_name} has been {status}.')
    return redirect('employees_list')

# Удалить запись
@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(TimeEntry, id=entry_id)
    if entry.employee != request.user and not request.user.is_admin:
        messages.error(request, 'Access denied.')
        return redirect('time_tracking')
    entry.delete()
    messages.success(request, 'Time entry deleted successfully.')
    return redirect('time_tracking')
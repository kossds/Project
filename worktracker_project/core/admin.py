from django.contrib import admin
from .models import Employee, TimeEntry, ActiveSession

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'full_name', 'email', 'is_admin', 'is_active')
    search_fields = ('first_name', 'last_name', 'email', 'employee_id')
    list_filter = ('is_admin', 'is_active', 'department', 'position')

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'hours_worked', 'is_approved')
    list_filter = ('date', 'is_approved', 'employee')
    search_fields = ('description', 'project')

@admin.register(ActiveSession)
class ActiveSessionAdmin(admin.ModelAdmin):
    list_display = ('employee', 'start_time', 'created_at')
    list_filter = ('employee',)
    search_fields = ('description', 'project')
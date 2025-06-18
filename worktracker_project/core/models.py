from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import date, time, timedelta
from django.db.models import Sum
from datetime import datetime, date, timedelta


class Employee(AbstractUser):
    employee_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    hire_date = models.DateField(default=date.today)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    password_hash = models.CharField(max_length=256, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_total_hours_today(self):
        today = date.today()
        total = self.time_entries.filter(date=today).aggregate(Sum('hours_worked'))['hours_worked__sum']
        return total or 0

    def get_total_hours_week(self):
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        total = self.time_entries.filter(
            date__gte=week_start,
            date__lte=today
        ).aggregate(Sum('hours_worked'))['hours_worked__sum']
        return total or 0

    def get_total_hours_month(self):
        today = date.today()
        month_start = today.replace(day=1)
        total = self.time_entries.filter(
            date__gte=month_start,
            date__lte=today
        ).aggregate(Sum('hours_worked'))['hours_worked__sum']
        return total or 0


class TimeEntry(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='time_entries')
    date = models.DateField(default=date.today)
    start_time = models.TimeField()
    end_time = models.TimeField()
    hours_worked = models.FloatField(default=0.0)
    break_hours = models.FloatField(default=0.0)
    description = models.TextField(blank=True, null=True)
    project = models.CharField(max_length=100, blank=True, null=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_hours(self):
        if self.start_time and self.end_time:
            start_datetime = datetime.combine(self.date, self.start_time)
            end_datetime = datetime.combine(self.date, self.end_time)

            # Обработка ночного смены
            if end_datetime < start_datetime:
                end_datetime += timedelta(days=1)

            duration = end_datetime - start_datetime
            hours = duration.total_seconds() / 3600
            self.hours_worked = round(hours - (self.break_hours or 0), 2)
            self.save(update_fields=['hours_worked'])
        return self.hours_worked


class ActiveSession(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='active_sessions')
    start_time = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    project = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def get_duration_hours(self):
        duration = timezone.now() - self.start_time
        return round(duration.total_seconds() / 3600, 2)
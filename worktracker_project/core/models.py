from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, time, timedelta, date
from django.db.models import Sum, F, ExpressionWrapper, DurationField


class CustomUserManager(BaseUserManager):
    def create_user(self, employee_id, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(employee_id=employee_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, employee_id, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_admin', True)
        return self.create_user(employee_id, email, password, **extra_fields)


class Employee(AbstractUser):
    employee_id = models.CharField(max_length=20, unique=True, verbose_name='Табельный номер')
    first_name = models.CharField(max_length=50, verbose_name='Имя')
    last_name = models.CharField(max_length=50, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='Отдел')
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name='Должность')
    hire_date = models.DateField(default=timezone.now, verbose_name='Дата приема')
    is_admin = models.BooleanField(default=False, verbose_name='Администратор')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    objects = CustomUserManager()

    USERNAME_FIELD = 'employee_id'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.employee_id})"

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    def clean(self):
        if self.hire_date > timezone.now().date():
            raise ValidationError({'hire_date': 'Дата приема не может быть в будущем'})

    def get_total_hours(self, period='day'):
        today = timezone.now().date()
        
        if period == 'day':
            start_date = today
            end_date = today
        elif period == 'week':
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif period == 'month':
            start_date = today.replace(day=1)
            next_month = start_date.replace(day=28) + timedelta(days=4)
            end_date = next_month - timedelta(days=next_month.day)
        else:
            return 0.0

        total = self.time_entries.filter(
            date__gte=start_date,
            date__lte=end_date
        ).aggregate(total_hours=Sum('hours_worked'))['total_hours']
        
        return total or 0.0

    def get_active_session(self):
        return self.active_sessions.filter(end_time__isnull=True).first()


class TimeEntry(models.Model):
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='time_entries',
        verbose_name='Сотрудник'
    )
    date = models.DateField(default=timezone.now, verbose_name='Дата')
    start_time = models.TimeField(verbose_name='Время начала')
    end_time = models.TimeField(verbose_name='Время окончания', null=True, blank=True)
    hours_worked = models.FloatField(default=0.0, verbose_name='Отработано часов')
    break_hours = models.FloatField(default=0.0, verbose_name='Перерыв (часы)')
    description = models.TextField(blank=True, null=True, verbose_name='Описание работы')
    project = models.CharField(max_length=100, blank=True, null=True, verbose_name='Проект')
    is_approved = models.BooleanField(default=False, verbose_name='Подтверждено')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Учет времени'
        verbose_name_plural = 'Учет времени'
        ordering = ['-date', '-start_time']
        unique_together = ['employee', 'date', 'start_time']

    def __str__(self):
        return f"{self.employee} - {self.date} ({self.hours_worked} ч.)"

    def clean(self):
        if self.end_time and self.start_time >= self.end_time:
            raise ValidationError('Время окончания должно быть позже времени начала')
        
        if self.break_hours and self.break_hours > self.hours_worked:
            raise ValidationError('Время перерыва не может превышать общее время работы')

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            self.calculate_hours()
        super().save(*args, **kwargs)

    def calculate_hours(self):
        start_datetime = datetime.combine(self.date, self.start_time)
        end_datetime = datetime.combine(self.date, self.end_time) if self.end_time else timezone.now()
        
        # Обработка ночных смен
        if end_datetime < start_datetime:
            end_datetime += timedelta(days=1)
        
        duration = end_datetime - start_datetime
        total_hours = duration.total_seconds() / 3600
        self.hours_worked = round(max(0, total_hours - self.break_hours), 2)


class ActiveSession(models.Model):
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='active_sessions',
        verbose_name='Сотрудник'
    )
    start_time = models.DateTimeField(default=timezone.now, verbose_name='Время начала')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='Время окончания')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    project = models.CharField(max_length=100, blank=True, null=True, verbose_name='Проект')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    class Meta:
        verbose_name = 'Активная сессия'
        verbose_name_plural = 'Активные сессии'
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.employee} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def get_duration(self):
        if self.end_time:
            duration = self.end_time - self.start_time
        else:
            duration = timezone.now() - self.start_time
        return duration

    def get_duration_hours(self):
        duration = self.get_duration()
        return round(duration.total_seconds() / 3600, 2)

    def end_session(self):
        self.end_time = timezone.now()
        self.save()
        return self.create_time_entry()

    def create_time_entry(self):
        if not self.end_time:
            return None
        
        time_entry = TimeEntry.objects.create(
            employee=self.employee,
            date=self.start_time.date(),
            start_time=self.start_time.time(),
            end_time=self.end_time.time(),
            description=self.description,
            project=self.project
        )
        return time_entry
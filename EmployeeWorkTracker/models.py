from app import db
from flask_login import UserMixin
from datetime import datetime, date, timedelta
from sqlalchemy import func

class Employee(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100))
    position = db.Column(db.String(100))
    hire_date = db.Column(db.Date, default=date.today)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    password_hash = db.Column(db.String(256))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with time entries
    time_entries = db.relationship('TimeEntry', backref='employee', lazy=True, cascade='all, delete-orphan')
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def get_total_hours_today(self):
        today = date.today()
        total = db.session.query(func.sum(TimeEntry.hours_worked)).filter(
            TimeEntry.employee_id == self.id,
            TimeEntry.date == today
        ).scalar()
        return total or 0
    
    def get_total_hours_week(self):
        from datetime import timedelta
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        total = db.session.query(func.sum(TimeEntry.hours_worked)).filter(
            TimeEntry.employee_id == self.id,
            TimeEntry.date >= week_start,
            TimeEntry.date <= today
        ).scalar()
        return total or 0
    
    def get_total_hours_month(self):
        today = date.today()
        month_start = today.replace(day=1)
        total = db.session.query(func.sum(TimeEntry.hours_worked)).filter(
            TimeEntry.employee_id == self.id,
            TimeEntry.date >= month_start,
            TimeEntry.date <= today
        ).scalar()
        return total or 0

class TimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    hours_worked = db.Column(db.Float, default=0.0)
    break_hours = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text)
    project = db.Column(db.String(100))
    is_approved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_hours(self):
        """Calculate hours worked based on start and end time"""
        if self.start_time and self.end_time:
            start_datetime = datetime.combine(date.today(), self.start_time)
            end_datetime = datetime.combine(date.today(), self.end_time)
            
            # Handle overnight shifts
            if end_datetime < start_datetime:
                end_datetime += timedelta(days=1)
            
            duration = end_datetime - start_datetime
            hours = duration.total_seconds() / 3600
            self.hours_worked = round(hours - (self.break_hours or 0), 2)
        return self.hours_worked

class ActiveSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    description = db.Column(db.Text)
    project = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    employee = db.relationship('Employee', backref='active_sessions')
    
    def get_duration_hours(self):
        """Get current session duration in hours"""
        duration = datetime.utcnow() - self.start_time
        return round(duration.total_seconds() / 3600, 2)

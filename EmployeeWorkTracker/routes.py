from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db
from models import Employee, TimeEntry, ActiveSession
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        employee = Employee.query.filter_by(email=email).first()
        
        if employee and check_password_hash(employee.password_hash, password):
            if employee.is_active:
                login_user(employee)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Your account has been deactivated. Please contact HR.', 'error')
        else:
            flash('Invalid email or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        employee_id = request.form['employee_id']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        phone = request.form.get('phone', '')
        department = request.form['department']
        position = request.form['position']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('register.html')
        
        if Employee.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('register.html')
        
        if Employee.query.filter_by(employee_id=employee_id).first():
            flash('Employee ID already exists.', 'error')
            return render_template('register.html')
        
        # Create new employee
        employee = Employee(
            employee_id=employee_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            department=department,
            position=position,
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(employee)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get current user's statistics
    today_hours = current_user.get_total_hours_today()
    week_hours = current_user.get_total_hours_week()
    month_hours = current_user.get_total_hours_month()
    
    # Get active session if any
    active_session = ActiveSession.query.filter_by(employee_id=current_user.id).first()
    
    # Get recent time entries
    recent_entries = TimeEntry.query.filter_by(employee_id=current_user.id)\
        .order_by(desc(TimeEntry.date), desc(TimeEntry.created_at))\
        .limit(5).all()
    
    # Get admin statistics if admin user
    total_employees = 0
    total_active_sessions = 0
    if current_user.is_admin:
        total_employees = Employee.query.filter_by(is_active=True).count()
        total_active_sessions = ActiveSession.query.count()
    
    return render_template('dashboard.html',
                         today_hours=today_hours,
                         week_hours=week_hours,
                         month_hours=month_hours,
                         active_session=active_session,
                         recent_entries=recent_entries,
                         total_employees=total_employees,
                         total_active_sessions=total_active_sessions)

@app.route('/employees')
@login_required
def employees():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    search = request.args.get('search', '')
    department = request.args.get('department', '')
    
    query = Employee.query
    
    if search:
        query = query.filter(
            (Employee.first_name.contains(search)) |
            (Employee.last_name.contains(search)) |
            (Employee.email.contains(search)) |
            (Employee.employee_id.contains(search))
        )
    
    if department:
        query = query.filter(Employee.department == department)
    
    employees_list = query.order_by(Employee.first_name, Employee.last_name).all()
    departments = db.session.query(Employee.department).distinct().all()
    departments = [d[0] for d in departments if d[0]]
    
    return render_template('employees.html', 
                         employees=employees_list, 
                         departments=departments,
                         search=search,
                         selected_department=department)

@app.route('/time_tracking')
@login_required
def time_tracking():
    # Get active session
    active_session = ActiveSession.query.filter_by(employee_id=current_user.id).first()
    
    # Get today's entries
    today = date.today()
    today_entries = TimeEntry.query.filter_by(
        employee_id=current_user.id,
        date=today
    ).order_by(desc(TimeEntry.created_at)).all()
    
    return render_template('time_tracking.html',
                         active_session=active_session,
                         today_entries=today_entries)

@app.route('/start_session', methods=['POST'])
@login_required
def start_session():
    # Check if already has active session
    existing_session = ActiveSession.query.filter_by(employee_id=current_user.id).first()
    if existing_session:
        flash('You already have an active session running.', 'warning')
        return redirect(url_for('time_tracking'))
    
    description = request.form.get('description', '')
    project = request.form.get('project', '')
    
    session = ActiveSession(
        employee_id=current_user.id,
        description=description,
        project=project
    )
    
    db.session.add(session)
    db.session.commit()
    
    flash('Work session started successfully!', 'success')
    return redirect(url_for('time_tracking'))

@app.route('/stop_session', methods=['POST'])
@login_required
def stop_session():
    active_session = ActiveSession.query.filter_by(employee_id=current_user.id).first()
    if not active_session:
        flash('No active session found.', 'error')
        return redirect(url_for('time_tracking'))
    
    # Calculate hours worked
    end_time = datetime.utcnow()
    duration = end_time - active_session.start_time
    hours_worked = round(duration.total_seconds() / 3600, 2)
    
    # Create time entry
    time_entry = TimeEntry(
        employee_id=current_user.id,
        date=date.today(),
        start_time=active_session.start_time.time(),
        end_time=end_time.time(),
        hours_worked=hours_worked,
        description=active_session.description,
        project=active_session.project
    )
    
    db.session.add(time_entry)
    db.session.delete(active_session)
    db.session.commit()
    
    flash(f'Session ended. Worked for {hours_worked} hours.', 'success')
    return redirect(url_for('time_tracking'))

@app.route('/add_manual_entry', methods=['POST'])
@login_required
def add_manual_entry():
    entry_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
    start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
    end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
    break_hours = float(request.form.get('break_hours', 0))
    description = request.form.get('description', '')
    project = request.form.get('project', '')
    
    time_entry = TimeEntry(
        employee_id=current_user.id,
        date=entry_date,
        start_time=start_time,
        end_time=end_time,
        break_hours=break_hours,
        description=description,
        project=project
    )
    time_entry.calculate_hours()
    
    db.session.add(time_entry)
    db.session.commit()
    
    flash('Time entry added successfully!', 'success')
    return redirect(url_for('time_tracking'))

@app.route('/reports')
@login_required
def reports():
    # Date range from request args or default to current month
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if not start_date or not end_date:
        today = date.today()
        start_date = today.replace(day=1).strftime('%Y-%m-%d')
        end_date = today.strftime('%Y-%m-%d')
    
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Build query based on user role
    if current_user.is_admin:
        query = TimeEntry.query
    else:
        query = TimeEntry.query.filter_by(employee_id=current_user.id)
    
    entries = query.filter(
        TimeEntry.date >= start_date_obj,
        TimeEntry.date <= end_date_obj
    ).order_by(desc(TimeEntry.date)).all()
    
    # Calculate summary statistics
    total_hours = sum(entry.hours_worked for entry in entries)
    total_entries = len(entries)
    
    # Group by employee for admin view
    employee_summary = {}
    if current_user.is_admin:
        for entry in entries:
            emp_id = entry.employee_id
            if emp_id not in employee_summary:
                employee_summary[emp_id] = {
                    'employee': entry.employee,
                    'total_hours': 0,
                    'entries_count': 0
                }
            employee_summary[emp_id]['total_hours'] += entry.hours_worked
            employee_summary[emp_id]['entries_count'] += 1
    
    return render_template('reports.html',
                         entries=entries,
                         start_date=start_date,
                         end_date=end_date,
                         total_hours=total_hours,
                         total_entries=total_entries,
                         employee_summary=employee_summary)

@app.route('/admin')
@login_required
def admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('dashboard'))
    
    # Get pending approvals
    pending_entries = TimeEntry.query.filter_by(is_approved=False)\
        .order_by(desc(TimeEntry.created_at)).all()
    
    # Get recent registrations
    recent_employees = Employee.query.order_by(desc(Employee.created_at))\
        .limit(10).all()
    
    # Get active sessions
    active_sessions = ActiveSession.query.join(Employee)\
        .order_by(ActiveSession.start_time).all()
    
    return render_template('admin.html',
                         pending_entries=pending_entries,
                         recent_employees=recent_employees,
                         active_sessions=active_sessions)

@app.route('/approve_entry/<int:entry_id>')
@login_required
def approve_entry(entry_id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    entry = TimeEntry.query.get_or_404(entry_id)
    entry.is_approved = True
    db.session.commit()
    
    flash('Time entry approved successfully.', 'success')
    return redirect(url_for('admin'))

@app.route('/toggle_employee_status/<int:employee_id>')
@login_required
def toggle_employee_status(employee_id):
    if not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    
    employee = Employee.query.get_or_404(employee_id)
    employee.is_active = not employee.is_active
    db.session.commit()
    
    status = 'activated' if employee.is_active else 'deactivated'
    flash(f'Employee {employee.full_name} has been {status}.', 'success')
    return redirect(url_for('employees'))

@app.route('/delete_entry/<int:entry_id>')
@login_required
def delete_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    
    # Check if user owns the entry or is admin
    if entry.employee_id != current_user.id and not current_user.is_admin:
        flash('Access denied.', 'error')
        return redirect(url_for('time_tracking'))
    
    db.session.delete(entry)
    db.session.commit()
    
    flash('Time entry deleted successfully.', 'success')
    return redirect(url_for('time_tracking'))

# Employee Work Tracking System

## Overview

This is a Flask-based employee work tracking system designed for modern workplaces. The application provides comprehensive time tracking, employee management, and reporting capabilities with a clean, professional interface.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python 3.11)
- **Database ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Authentication**: Flask-Login for session management
- **Password Security**: Werkzeug password hashing
- **WSGI Server**: Gunicorn for production deployment

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **CSS Framework**: Bootstrap 5.3.0
- **Icons**: Font Awesome 6.4.0
- **Fonts**: Google Fonts (Open Sans)
- **JavaScript**: Vanilla JS for client-side interactions

### Database Design
- **Development**: SQLite (default)
- **Production**: PostgreSQL (configured via DATABASE_URL)
- **ORM**: SQLAlchemy with declarative base
- **Connection Management**: Pool recycling and pre-ping enabled

## Key Components

### Models (models.py)
- **Employee**: Core user model with Flask-Login integration
  - User authentication and session management
  - Role-based access (admin/regular user)
  - Personal information and job details
  - Relationship with time entries
  - Methods for calculating work hours (daily, weekly, monthly)

- **TimeEntry**: Work session records (referenced but not fully shown)
- **ActiveSession**: Real-time session tracking (referenced but not fully shown)

### Authentication System
- **Login/Logout**: Email-based authentication
- **Registration**: Self-service employee registration
- **Session Management**: Flask-Login handles user sessions
- **Access Control**: Role-based permissions (admin vs regular users)

### Core Features
1. **Dashboard**: Personal work statistics and quick actions
2. **Time Tracking**: Start/stop work sessions with project descriptions
3. **Employee Management**: Admin panel for employee oversight
4. **Reports**: Work time analysis and reporting
5. **Admin Panel**: Administrative functions and system overview

## Data Flow

### Authentication Flow
1. User submits login credentials
2. System validates against Employee model
3. Flask-Login creates user session
4. Redirects to dashboard or requested page

### Time Tracking Flow
1. Employee starts work session via time tracking page
2. ActiveSession record created with start time
3. Real-time timer updates session duration
4. Employee stops session, creating TimeEntry record
5. Dashboard and reports update with new data

### Admin Flow
1. Admin users access additional routes and features
2. Employee management with search and filtering
3. System-wide statistics and pending approvals
4. Bulk operations and user management

## External Dependencies

### Python Packages
- **Flask**: Web framework (3.1.1)
- **Flask-SQLAlchemy**: Database ORM (3.1.1)
- **Flask-Login**: User session management (0.6.3)
- **Werkzeug**: WSGI utilities and security (3.1.3)
- **Gunicorn**: WSGI HTTP server (23.0.0)
- **psycopg2-binary**: PostgreSQL adapter (2.9.10)
- **email-validator**: Email validation (2.2.0)

### Frontend Libraries (CDN)
- **Bootstrap 5.3.0**: UI framework
- **Font Awesome 6.4.0**: Icon library
- **Google Fonts**: Typography

### System Dependencies
- **PostgreSQL**: Production database
- **OpenSSL**: Security and encryption

## Deployment Strategy

### Development Environment
- **Runtime**: Python 3.11 on Nix
- **Database**: SQLite for local development
- **Server**: Flask development server with hot reload
- **Debug Mode**: Enabled for development

### Production Environment
- **Deployment Target**: Autoscale (Replit deployment)
- **WSGI Server**: Gunicorn with bind to 0.0.0.0:5000
- **Database**: PostgreSQL via DATABASE_URL environment variable
- **Session Security**: Production secret key via SESSION_SECRET
- **Process Management**: Multiple worker processes
- **Proxy Handling**: ProxyFix middleware for reverse proxies

### Configuration Management
- **Environment Variables**: Database URL, session secrets
- **Database Connection**: Pool recycling and health checks
- **Logging**: Debug level logging enabled
- **Static Files**: Served through Flask in development

### Security Considerations
- **Password Hashing**: Werkzeug secure password hashing
- **Session Management**: Secure session cookies
- **Environment Secrets**: Sensitive data in environment variables
- **Input Validation**: Email validation and form validation
- **SQL Injection Protection**: SQLAlchemy ORM prevents injection attacks

## Recent Changes

- June 16, 2025: Initial Flask application setup with PostgreSQL
- June 16, 2025: Converted to SQLite database for portability
- June 16, 2025: Added comprehensive deployment package with setup scripts

## SQLite Database Implementation

The system now uses SQLite instead of PostgreSQL for maximum portability:
- Database file: `employee_tracking.db` (created automatically)
- No external database server required
- Easily transferable between computers
- Ideal for small to medium organizations

## Deployment Package

Created complete deployment solution:
- `setup.py` - Full automated installation script
- `install.py` - Simple dependency installer
- `start_system.bat` - Windows launch script
- `start_system.sh` - Linux/Mac launch script  
- `README.md` - Complete user documentation
- `deploy_guide.txt` - Quick deployment instructions

## Portable Architecture Benefits

- Self-contained: All dependencies managed locally
- Cross-platform: Works on Windows, Linux, Mac
- No server setup: SQLite eliminates database server requirements
- Easy backup: Single database file contains all data
- Version control friendly: Database can be included in project archives

Changelog:
- June 16, 2025: Initial setup
- June 16, 2025: SQLite conversion and deployment package creation

## User Preferences

Preferred communication style: Simple, everyday language.
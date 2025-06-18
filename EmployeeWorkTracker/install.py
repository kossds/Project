#!/usr/bin/env python3
"""
Простой установщик для системы учета рабочего времени
Simple installer for Employee Work Tracking System
"""

import os
import sys
import subprocess
import platform

def install_dependencies():
    """Установка зависимостей"""
    dependencies = [
        'Flask==3.0.0',
        'Flask-SQLAlchemy==3.1.1', 
        'Flask-Login==0.6.3',
        'Werkzeug==3.0.1',
        'email-validator==2.1.0'
    ]
    
    print("Установка зависимостей...")
    for dep in dependencies:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
            print(f"✓ {dep}")
        except:
            print(f"✗ Ошибка установки {dep}")
    
    print("\nЗависимости установлены!")
    print("Теперь можете запустить систему:")
    if platform.system() == "Windows":
        print("  start_system.bat")
    else:
        print("  ./start_system.sh")

if __name__ == "__main__":
    install_dependencies()
#!/usr/bin/env python3
"""
Установщик для Информационной системы учета рабочего времени сотрудников
Employee Work Tracking System Setup Script

Этот скрипт автоматически настраивает и запускает систему на любом компьютере.
"""

import os
import sys
import subprocess
import platform
import sqlite3
from pathlib import Path

class EmployeeTrackingSetup:
    def __init__(self):
        self.project_dir = Path(__file__).parent
        self.db_path = self.project_dir / 'employee_tracking.db'
        self.requirements_installed = False
        
    def print_header(self):
        print("=" * 60)
        print("   СИСТЕМА УЧЕТА РАБОЧЕГО ВРЕМЕНИ СОТРУДНИКОВ")
        print("   Employee Work Tracking System Setup")
        print("=" * 60)
        print()
        
    def check_python_version(self):
        """Проверка версии Python"""
        print("Проверка версии Python...")
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 7):
            print("❌ Ошибка: Требуется Python 3.7 или выше")
            print(f"Текущая версия: {version.major}.{version.minor}.{version.micro}")
            return False
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
        
    def install_requirements(self):
        """Установка зависимостей"""
        requirements_file = self.project_dir / 'requirements.txt'
        
        if not requirements_file.exists():
            print("Создание файла requirements.txt...")
            with open(requirements_file, 'w', encoding='utf-8') as f:
                f.write("""Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Werkzeug==3.0.1
gunicorn==21.2.0
email-validator==2.1.0
""")
        
        print("Установка зависимостей Python...")
        try:
            subprocess.check_call([
                sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)
            ])
            print("✅ Зависимости установлены успешно")
            self.requirements_installed = True
            return True
        except subprocess.CalledProcessError:
            print("❌ Ошибка установки зависимостей")
            print("Попробуйте запустить вручную:")
            print(f"pip install -r {requirements_file}")
            return False
            
    def setup_database(self):
        """Создание и настройка базы данных SQLite"""
        print("Настройка базы данных SQLite...")
        
        try:
            # Удаляем старую базу если есть
            if self.db_path.exists():
                self.db_path.unlink()
                print("Старая база данных удалена")
            
            # Создаем новую базу данных
            conn = sqlite3.connect(str(self.db_path))
            conn.close()
            print(f"✅ База данных создана: {self.db_path}")
            
            # Инициализируем таблицы через Flask
            print("Инициализация таблиц...")
            os.chdir(self.project_dir)
            
            # Импортируем и создаем таблицы
            sys.path.insert(0, str(self.project_dir))
            from app import app, db
            from models import Employee, TimeEntry, ActiveSession
            
            with app.app_context():
                db.create_all()
                print("✅ Таблицы базы данных созданы")
                
                # Создаем админа по умолчанию
                from werkzeug.security import generate_password_hash
                admin = Employee.query.filter_by(email='admin@company.com').first()
                if not admin:
                    admin = Employee(
                        first_name='Администратор',
                        last_name='Системы',
                        email='admin@company.com',
                        employee_id='ADMIN001',
                        department='IT',
                        position='Системный администратор',
                        is_admin=True,
                        password_hash=generate_password_hash('admin123')
                    )
                    db.session.add(admin)
                    db.session.commit()
                    print("✅ Администратор создан: admin@company.com / admin123")
                
            return True
            
        except Exception as e:
            print(f"❌ Ошибка настройки базы данных: {e}")
            return False
            
    def create_startup_scripts(self):
        """Создание скриптов для запуска"""
        print("Создание скриптов запуска...")
        
        # Windows batch файл
        if platform.system() == "Windows":
            bat_content = f"""@echo off
echo Запуск системы учета рабочего времени...
cd /d "{self.project_dir}"
python main.py
pause
"""
            with open(self.project_dir / 'start_system.bat', 'w', encoding='cp1251') as f:
                f.write(bat_content)
            print("✅ Создан start_system.bat для Windows")
        
        # Unix shell скрипт
        sh_content = f"""#!/bin/bash
echo "Запуск системы учета рабочего времени..."
cd "{self.project_dir}"
python3 main.py
"""
        with open(self.project_dir / 'start_system.sh', 'w', encoding='utf-8') as f:
            f.write(sh_content)
        
        # Делаем исполняемым на Unix
        if platform.system() != "Windows":
            os.chmod(self.project_dir / 'start_system.sh', 0o755)
            print("✅ Создан start_system.sh для Linux/Mac")
            
    def create_readme(self):
        """Создание файла с инструкциями"""
        readme_content = """# Информационная система учета рабочего времени сотрудников

## Быстрый запуск

### Windows
Дважды кликните на файл `start_system.bat`

### Linux/Mac
Запустите в терминале:
```bash
./start_system.sh
```

### Или вручную
```bash
python main.py
```

## Доступ к системе

После запуска откройте браузер и перейдите по адресу: http://localhost:5000

### Учетная запись администратора по умолчанию:
- Email: admin@company.com
- Пароль: admin123

## Функции системы

✅ Авторизация пользователей
✅ Учет рабочего времени (старт/стоп сессий)
✅ Ручной ввод времени
✅ Управление сотрудниками (только админ)
✅ Отчеты по времени
✅ Панель администратора

## Требования

- Python 3.7 или выше
- Браузер (Chrome, Firefox, Safari, Edge)

## Структура файлов

- `employee_tracking.db` - База данных SQLite
- `app.py` - Основное приложение Flask
- `models.py` - Модели базы данных
- `routes.py` - Маршруты приложения
- `templates/` - HTML шаблоны
- `static/` - CSS и JavaScript файлы

## Поддержка

При возникновении проблем проверьте:
1. Установлен ли Python 3.7+
2. Установлены ли зависимости (`pip install -r requirements.txt`)
3. Не занят ли порт 5000 другим приложением

## База данных

Система использует SQLite базу данных, которая хранится в файле `employee_tracking.db`.
Данная база данных портативна и не требует отдельной установки сервера БД.

Для сброса данных удалите файл `employee_tracking.db` и запустите `python setup.py`.
"""
        
        with open(self.project_dir / 'README.md', 'w', encoding='utf-8') as f:
            f.write(readme_content)
        print("✅ Создан файл README.md с инструкциями")
        
    def run_setup(self):
        """Основной процесс установки"""
        self.print_header()
        
        # Проверки
        if not self.check_python_version():
            return False
            
        # Установка зависимостей
        if not self.install_requirements():
            print("\n⚠️  Продолжаем без установки зависимостей...")
            print("Запустите вручную: pip install -r requirements.txt")
            
        # Настройка БД
        if not self.setup_database():
            return False
            
        # Создание скриптов
        self.create_startup_scripts()
        self.create_readme()
        
        print("\n" + "=" * 60)
        print("✅ УСТАНОВКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 60)
        print()
        print("Для запуска системы:")
        if platform.system() == "Windows":
            print("  → Дважды кликните на start_system.bat")
        else:
            print("  → Запустите: ./start_system.sh")
        print("  → Или выполните: python main.py")
        print()
        print("Затем откройте браузер: http://localhost:5000")
        print("Админ: admin@company.com / admin123")
        print()
        
        # Предлагаем запустить сразу
        try:
            answer = input("Запустить систему сейчас? (y/n): ").lower()
            if answer in ['y', 'yes', 'да', 'д']:
                print("\nЗапуск системы...")
                os.system(f"python {self.project_dir / 'main.py'}")
        except KeyboardInterrupt:
            print("\nДо свидания!")
            
        return True

if __name__ == "__main__":
    setup = EmployeeTrackingSetup()
    try:
        success = setup.run_setup()
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nУстановка прервана пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1)
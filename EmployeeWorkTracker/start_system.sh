#!/bin/bash

echo "================================================"
echo "   СИСТЕМА УЧЕТА РАБОЧЕГО ВРЕМЕНИ СОТРУДНИКОВ"
echo "   Employee Work Tracking System"
echo "================================================"
echo ""
echo "Запуск системы..."
echo ""

# Проверка Python
if command -v python3 &> /dev/null; then
    python3 main.py
elif command -v python &> /dev/null; then
    python main.py
else
    echo "Ошибка: Python не найден в системе"
    echo "Установите Python 3.7 или выше"
    exit 1
fi

echo ""
echo "Нажмите Enter для выхода..."
read
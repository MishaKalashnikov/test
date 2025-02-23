@echo off
title Установка и запуск парсера
echo ========================================
echo 🔥 Автоматическая настройка и запуск 🔥
echo ========================================
echo.

:: Переход в папку проекта
cd /d C:\Users\Admin\IdeaProjects\parser_scan

:: Проверка наличия виртуального окружения
if not exist .venv (
    echo 🛠 Создание виртуального окружения...
    python -m venv .venv
)

:: Активация виртуального окружения
echo 🔄 Активация виртуального окружения...
call .\.venv\Scripts\activate

:: Установка зависимостей
echo 📦 Установка зависимостей...
pip install --upgrade pip
pip install -r requirements.txt

:: Запуск Chrome с отладочным портом 9222
echo 🚀 Запуск браузера Google Chrome...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --profile-directory="Profile 1"

:: Ждем 5 секунд, пока Chrome загрузится
timeout /t 5 /nobreak >nul

:: Проверка, запущен ли Chrome на порте 9222
echo 🔍 Проверяем, подключен ли браузер...
netstat -ano | findstr :9222

:: Запуск парсера run.py
echo 🚀 Запуск основного скрипта...
python run.py

pause

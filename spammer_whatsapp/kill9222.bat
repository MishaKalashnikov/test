@echo off
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :9222') do taskkill /PID %%a /F
echo ✅ Порт 9222 освобожден!
pause

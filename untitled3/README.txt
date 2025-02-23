1.1 Перед запуском убедитесь, что на вашем компьютере установлены:

Google Chrome (обновленный до последней версии).
Python 3.9+ (рекомендуемая версия).

1.2 Создание виртуального окружения

Открываем CMD
cd C:\Users\Admin\IdeaProjects\untitled3
python -m venv .venv
.\.venv\Scripts\activate

1.3 Установка зависимостей

pip install -r requirements.txt

Проверить, установлен ли selenium:
pip show selenium

2. Запуск браузера с отладкой через порт 9222

"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --proxy-server="http://94.158.190.227:5500" --profile-directory="Profile 1"

Проверяем, запущен ли Chrome на порте 9222:
netstat -ano | findstr :9222

3. Запуск парсера

python run.py

4. Переключение между parser.py и parser2.py
Файл run.py позволяет:

Запускать parser.py (поиск никнеймов в Twitter).
Приостанавливать parser.py и запускать parser2.py (сбор информации по найденным никнеймам).
В run.py будут кнопки или команда для переключения.

 5. Остановка парсера

Если нужно остановить парсер, нажмите CTRL + C в терминале.

Если нужно принудительно закрыть Chrome, выполните: taskkill /F /IM chrome.exe

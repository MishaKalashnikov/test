import subprocess
import time
import sys
import os

# Определяем путь к `parser.py` и `main.py`
PARSER_PATH = os.path.join(os.path.dirname(__file__), "utils", "parser.py")
BOT_PATH = os.path.join(os.path.dirname(__file__), "main.py")

def run_parser():
    """🚀 Запуск парсера перед ботом"""
    print("🚀 Запуск парсера...")
    try:
        subprocess.run([sys.executable, PARSER_PATH], check=True)
        print("✅ Парсер завершил работу!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске парсера: {e}")
        sys.exit(1)  # Завершаем выполнение, если парсер упал

def run_bot():
    """🚀 Запуск основного бота после парсера"""
    print("🚀 Запуск бота...")
    process = subprocess.Popen([sys.executable, BOT_PATH])
    process.wait()  # Ожидание завершения работы бота

if __name__ == "__main__":
    run_parser()  # 1️⃣ Запускаем парсер
    time.sleep(2)  # 2️⃣ Ожидание (если есть задержка обновления БД)
    run_bot()  # 3️⃣ Запускаем бота

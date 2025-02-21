import subprocess
import time
import sys
import os
from utils.database import get_all_channels, delete_channel

# Определяем путь к `parser.py` и `main.py`
PARSER_PATH = os.path.join(os.path.dirname(__file__), "utils", "parser.py")
BOT_PATH = os.path.join(os.path.dirname(__file__), "main.py")


def run_parser():
    """🚀 Запуск парсера перед ботом"""
    print("\n🚀 [1/2] Запуск парсера...")
    try:
        subprocess.run([sys.executable, PARSER_PATH], check=True)
        print("✅ Парсер завершил работу!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при запуске парсера: {e}")
        sys.exit(1)  # Завершаем выполнение, если парсер упал


def run_bot():
    """🚀 Запуск бота после парсера"""
    print("\n🚀 [2/2] Запуск бота...")
    process = subprocess.Popen([sys.executable, BOT_PATH])
    process.wait()  # Ожидание завершения работы бота


def manage_database():
    """📂 Управление базой данных"""
    while True:
        print("\n📌 Меню управления БД:")
        print("1️⃣ - Просмотреть все каналы")
        print("2️⃣ - Удалить все каналы")
        print("3️⃣ - Вернуться в главное меню")

        choice = input("\nВыберите действие: ").strip()

        if choice == "1":
            channels = get_all_channels()
            if channels:
                print("\n📌 Каналы в базе данных:")
                for row in channels:
                    print(f"🔹 {row[1]} - {row[2]}")
            else:
                print("⚠️ В базе нет каналов!")

        elif choice == "2":
            confirm = input("❗ Вы уверены, что хотите удалить ВСЕ каналы? (yes/no): ")
            if confirm.lower() == "yes":
                channels = get_all_channels()
                for channel in channels:
                    delete_channel(channel[1])
                print("✅ Все каналы удалены!")
            else:
                print("❌ Отмена удаления.")

        elif choice == "3":
            break

        else:
            print("❌ Некорректный ввод, попробуйте снова!")


if __name__ == "__main__":
    while True:
        print("\n📌 Выберите режим работы:")
        print("1️⃣ - Запустить **только парсер**")
        print("2️⃣ - Запустить **только бота**")
        print("3️⃣ - Запустить **оба процесса** (рекомендуется)")
        print("4️⃣ - Управление базой данных")
        print("5️⃣ - Выйти")

        choice = input("\nВведите номер режима: ").strip()

        if choice == "1":
            run_parser()

        elif choice == "2":
            run_bot()

        elif choice == "3":
            run_parser()
            time.sleep(2)  # Ожидание, если есть задержка обновления БД
            run_bot()

        elif choice == "4":
            manage_database()

        elif choice == "5":
            print("👋 Выход...")
            sys.exit(0)

        else:
            print("❌ Некорректный ввод, попробуйте снова!")

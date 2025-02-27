import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import sqlite3
import time
import logging
import random
import os
from datetime import datetime

# ========================== 1. ЛОГИРОВАНИЕ ==========================
logging.basicConfig(filename="spammer.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# ========================== 2. СОЗДАНИЕ БАЗЫ ДАННЫХ ==========================
def init_db():
    """Создаёт базу данных и таблицу сообщений"""
    conn = sqlite3.connect("spammer.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number TEXT NOT NULL,
        message TEXT NOT NULL
    )
    """)
    conn.commit()
    conn.close()
    print("✅ База данных и таблица 'messages' созданы!")

# ========================== 3. РАБОТА С БАЗОЙ ДАННЫХ ==========================
def add_message(phone_number, message):
    """Добавляет сообщение в базу данных"""
    conn = sqlite3.connect("spammer.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (phone_number, message) VALUES (?, ?)", (phone_number, message))
    conn.commit()
    conn.close()
    print(f"✅ Сообщение для {phone_number} добавлено в базу данных!")

def get_messages():
    """Загружает все сообщения из базы данных"""
    conn = sqlite3.connect("spammer.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, phone_number, message FROM messages")
    messages = cursor.fetchall()
    conn.close()
    return messages

def view_database():
    """Выводит все записи из базы данных"""
    messages = get_messages()
    if not messages:
        print("📭 База данных пуста!")
    else:
        print("\n📋 Список сообщений в базе:")
        for row in messages:
            print(f"ID: {row[0]}, Номер: {row[1]}, Сообщение: {row[2]}")

def clear_database():
    """Очищает таблицу сообщений"""
    conn = sqlite3.connect("spammer.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM messages")
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='messages'")
    conn.commit()
    conn.close()
    print("🗑 База данных очищена!")

# ========================== 4. ОТПРАВКА СООБЩЕНИЙ ==========================
def send_via_whatsapp_web(driver, phone_number, message, min_delay=10, max_delay=13):
    """Отправляет сообщение через WhatsApp Web"""
    try:
        if driver.session_id is None:
            print("❌ Chrome закрыт. Перезапусти браузер и скрипт.")
            return

        print(f"📨 Отправка сообщения на {phone_number}...")

        # Открываем чат
        url = f"https://web.whatsapp.com/send?phone={phone_number}&text={message}"
        driver.get(url)

        print("✅ Страница загружена, ждем...")
        time.sleep(random.uniform(min_delay, max_delay))

        # ⏳ Ждем 5 секунд, затем нажимаем ENTER
        print("🔹 Нажимаем ENTER...")
        pyautogui.press("enter")
        pyautogui.press("enter")

        send_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logging.info(f"{send_time} | Отправлено на {phone_number}: {message}")
        print(f"✅ {send_time} | Сообщение на {phone_number} отправлено!")

    except Exception as e:
        print(f"❌ Ошибка при отправке на {phone_number}: {str(e)}")
        logging.error(f"Ошибка при отправке на {phone_number}: {str(e)}")

# ========================== 5. ГЛАВНОЕ МЕНЮ ==========================
def main():
    init_db()
    print("\n===== WhatsApp Spammer (Полная версия) =====")

    options = Options()
    options.debugger_address = "127.0.0.1:9222"

    try:
        driver = webdriver.Chrome(options=options)
        print("\n🚀 Chrome подключён к порту 9222.")
    except Exception as e:
        print("❌ Ошибка подключения к Chrome!")
        print(str(e))
        return

    while True:
        print("\n[1] Добавить сообщение в БД")
        print("[2] Просмотреть базу данных")
        print("[3] Начать отправку сообщений")
        print("[4] Очистить базу данных")
        print("[0] Выход")

        choice = input("\nВведите ваш выбор: ")

        if choice == "1":
            phone_number = input("Введите номер получателя: ")
            message = input("Введите текст сообщения: ")
            add_message(phone_number, message)
        elif choice == "2":
            view_database()
        elif choice == "3":
            messages = get_messages()
            if not messages:
                print("❌ Нет сообщений для отправки.")
                continue
            for msg_id, phone, text in messages:
                send_via_whatsapp_web(driver, phone, text)
        elif choice == "4":
            clear_database()
        elif choice == "0":
            print("👋 Выход.")
            driver.quit()
            break
        else:
            print("❌ Некорректный ввод, попробуйте снова.")

# ========================== 6. ЗАПУСК ПРОГРАММЫ ==========================
if __name__ == "__main__":
    main()
import sqlite3
import os

# ========================== 1. СОЗДАНИЕ БД ==========================
def init_db():
    conn = sqlite3.connect("spammer.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone_number TEXT NOT NULL UNIQUE,
        message TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()

# ========================== 2. ЧТЕНИЕ НОМЕРОВ И СООБЩЕНИЙ ==========================
def read_numbers_from_txt(filename="numbers.txt"):
    """Читает номера телефонов из файла"""
    if not os.path.exists(filename):
        print(f"❌ Файл {filename} не найден!")
        return []

    with open(filename, "r", encoding="utf-8") as file:
        numbers = [line.strip() for line in file.readlines() if line.strip().isdigit()]
    return numbers

def read_messages_from_txt(filename="messages.txt"):
    """Читает сообщения из файла"""
    if not os.path.exists(filename):
        print(f"❌ Файл {filename} не найден!")
        return []

    with open(filename, "r", encoding="utf-8") as file:
        messages = [line.strip() for line in file.readlines() if line.strip()]
    return messages

# ========================== 3. ДОБАВЛЕНИЕ В БД ==========================
def add_to_database():
    """Добавляет номера и сообщения в базу данных"""
    numbers = read_numbers_from_txt()
    messages = read_messages_from_txt()

    if not numbers or not messages:
        print("❌ Ошибка: Файл номеров или сообщений пуст!")
        return

    conn = sqlite3.connect("spammer.db")
    cursor = conn.cursor()

    added_count = 0
    for number in numbers:
        message = messages[added_count % len(messages)]  # Выбираем случайное сообщение

        try:
            cursor.execute("INSERT INTO messages (phone_number, message) VALUES (?, ?)", (number, message))
            added_count += 1
        except sqlite3.IntegrityError:
            print(f"⚠ Номер {number} уже в базе, пропускаем.")

    conn.commit()
    conn.close()

    print(f"✅ Добавлено {added_count} новых номеров в базу данных!")

# ========================== 4. ЗАПУСК ==========================
if __name__ == "__main__":
    init_db()
    add_to_database()

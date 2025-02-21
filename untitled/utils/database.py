import sqlite3
import os


DB_PATH = "db/channels.db"

def connect_db():
    """Создаёт соединение с БД и таблицы, если их нет"""
    if not os.path.exists("db"):
        os.makedirs("db")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            channel_name TEXT UNIQUE,
            type TEXT
        )
    """)

    conn.commit()
    return conn, cursor

def insert_or_update_channel(channel_name, chat_type):
    """Добавляет канал в БД или обновляет его"""
    conn, cursor = connect_db()
    cursor.execute("""
        INSERT OR REPLACE INTO channels (channel_name, type) VALUES (?, ?)
    """, (channel_name, chat_type))
    conn.commit()
    conn.close()

def get_all_channels():
    """Получает список всех каналов"""
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM channels ORDER BY type ASC")  # Сортируем по типу
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_channels_by_type(chat_type):
    """Получает список каналов по типу ('followers', 'open', 'verified')"""
    conn, cursor = connect_db()
    cursor.execute("SELECT * FROM channels WHERE type = ? ORDER BY channel_name ASC", (chat_type,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_channel(channel_name):
    """Удаляет канал из БД"""
    conn, cursor = connect_db()
    cursor.execute("DELETE FROM channels WHERE channel_name=?", (channel_name,))
    conn.commit()
    conn.close()
    print(f"✅ Канал {channel_name} удалён из БД!")

# Тестируем, если запустить database.py отдельно
if __name__ == "__main__":
    print("📌 Все каналы (отсортированы по типу):")
    for row in get_all_channels():
        print(row)

    print("\n📌 Каналы с типом 'open':")
    for row in get_channels_by_type("open"):
        print(row)

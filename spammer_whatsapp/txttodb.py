import sqlite3

def load_numbers_and_messages():
    """Загружает номера и сообщения из файлов и добавляет их в БД без дубликатов"""
    try:
        with open("numbers.txt", "r", encoding="utf-8") as f:
            numbers = [line.strip() for line in f.readlines() if line.strip()]

        with open("messages.txt", "r", encoding="utf-8") as f:
            message = f.read().strip()  # Читаем весь текст как одно сообщение

        if not numbers or not message:
            print("❌ Файлы пусты или некорректны!")
            return

        conn = sqlite3.connect("spammer.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT NOT NULL,
            message TEXT NOT NULL
        )
        """)

        for number in numbers:
            cursor.execute("SELECT COUNT(*) FROM messages WHERE phone_number = ?", (number,))
            if cursor.fetchone()[0] == 0:
                cursor.execute("INSERT INTO messages (phone_number, message) VALUES (?, ?)", (number, message))
                print(f"✅ Добавлено: {number} -> сообщение из messages.txt")
            else:
                print(f"⚠️ Уже существует в БД: {number}")

        conn.commit()
        conn.close()
        print("✅ Все данные успешно загружены в базу!")

    except Exception as e:
        print(f"❌ Ошибка при загрузке данных: {str(e)}")

if __name__ == "__main__":
    load_numbers_and_messages()

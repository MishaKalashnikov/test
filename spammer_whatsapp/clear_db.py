import sqlite3

# ========================== 1. ФУНКЦИЯ ОЧИСТКИ БД ==========================
def clear_database(full_wipe=False):
    """Очищает базу данных. Если full_wipe=True, удаляет все записи, иначе только 'pending'."""
    conn = sqlite3.connect("spammer.db")
    cursor = conn.cursor()

    if full_wipe:
        cursor.execute("DELETE FROM messages")  # Удаляет все записи
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='messages'")  # Сбрасывает автоинкремент ID
        print("⚠ ВНИМАНИЕ: ВСЕ сообщения удалены!")
    else:
        cursor.execute("DELETE FROM messages WHERE status='pending'")  # Удаляет только 'pending'
        print("✅ Удалены только неотправленные ('pending') сообщения.")

    conn.commit()
    conn.close()

# ========================== 2. ЗАПУСК ==========================
if __name__ == "__main__":
    print("\n===== ОЧИСТКА БАЗЫ ДАННЫХ =====")
    choice = input("Вы хотите удалить (1) только 'pending' или (2) ВСЕ записи? Введите 1 или 2: ")

    if choice == "1":
        clear_database(full_wipe=False)
    elif choice == "2":
        confirmation = input("❗ ВНИМАНИЕ: Это удалит ВСЕ записи. Подтвердите (yes/no): ")
        if confirmation.lower() == "yes":
            clear_database(full_wipe=True)
        else:
            print("❌ Очистка отменена.")
    else:
        print("❌ Неверный ввод, выход из программы.")

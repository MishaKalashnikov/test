import sqlite3

def view_database():
    conn = sqlite3.connect("spammer.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM messages")
    rows = cursor.fetchall()

    print("\n📌 Данные в базе `spammer.db`:")
    print("="*50)
    for row in rows:
        print(row)

    conn.close()

view_database()

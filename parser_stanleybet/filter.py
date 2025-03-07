import os

# Пути к файлам
RESULTS_FILE = "results.txt"
LOGPASS_FILE = "LogPass.txt"
PARSER_FILE = "parser.txt"

# Читаем logins с "True" из results.txt
def get_true_logins():
    true_logins = set()
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(": ")
                if len(parts) == 2 and parts[1].strip().lower() == "true":
                    true_logins.add(parts[0].strip())  # Добавляем логин
    except FileNotFoundError:
        print(f"Файл {RESULTS_FILE} не найден!")
    return true_logins

# Читаем LogPass.txt и ищем логины с "True"
def filter_logins(true_logins):
    filtered_accounts = []
    try:
        with open(LOGPASS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(":", 1)  # Разделяем по первому двоеточию
                if len(parts) == 2:
                    login, password = parts[0].strip(), parts[1].strip()
                    if login in true_logins:
                        filtered_accounts.append(f"{login}:{password}")  # Формат login:password
    except FileNotFoundError:
        print(f"Файл {LOGPASS_FILE} не найден!")

    return filtered_accounts

# Записываем отфильтрованные логины в parser.txt
def save_to_parser(filtered_accounts):
    try:
        with open(PARSER_FILE, "w", encoding="utf-8") as f:
            for account in filtered_accounts:
                f.write(account + "\n")
        print(f"{len(filtered_accounts)} аккаунтов записано в {PARSER_FILE}")
    except Exception as e:
        print(f"Ошибка при записи в {PARSER_FILE}: {e}")

# --- Основной запуск ---
true_logins = get_true_logins()
filtered_accounts = filter_logins(true_logins)
save_to_parser(filtered_accounts)

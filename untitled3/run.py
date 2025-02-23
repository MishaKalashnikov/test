import os
import subprocess
import time

# === 🚀 Функция для запуска скрипта ===
def run_script(script_name):
    print(f"🚀 Запускаем {script_name}...")
    process = subprocess.Popen(["python", script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    while True:
        output = process.stdout.readline()
        if output:
            print(output.decode().strip())  # Выводим логи в реальном времени
        elif process.poll() is not None:
            break

    process.wait()
    return process.returncode

# === 🔥 Запускаем parser.py ===
parser1_exit_code = run_script("parser.py")

if parser1_exit_code == 0 and os.path.exists("twitter_usernames.txt"):
    print("\n✅ `parser.py` успешно завершен. Запускаем `parser2.py`...\n")
    time.sleep(3)  # Небольшая пауза перед запуском второго парсера
    parser2_exit_code = run_script("parser2.py")

    if parser2_exit_code == 0:
        print("\n🎉 Парсинг завершен! Данные сохранены в `twitter_profiles.xlsx`")
    else:
        print("\n❌ Ошибка при запуске `parser2.py`! Проверь логи.")
else:
    print("\n❌ Ошибка в `parser.py` или файл `twitter_usernames.txt` не был создан!")


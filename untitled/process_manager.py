import subprocess
import time
import logging
import os


# 🔥 Настраиваем логирование
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/process_manager.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 🔥 Список процессов для запуска
PROCESSES = [
    "bots/bot.py",
    "services/voice_scanner.py",
    "bots/chatGPT.py"
]

def restart_process(script):
    """♻️ Запускает процесс и перезапускает при краше"""
    while True:
        logging.info(f"🔄 Запуск {script}...")
        process = subprocess.Popen(["python", script])
        process.wait()
        logging.warning(f"⚠️ {script} упал. Перезапускаем через 5 секунд...")
        time.sleep(5)

if __name__ == "__main__":
    running_processes = []

    for script in PROCESSES:
        print(f"🚀 Запускаем {script}...")
        process = subprocess.Popen(["python", script])
        running_processes.append((script, process))

    while True:
        for script, process in running_processes:
            if process.poll() is not None:  # Проверяем, упал ли процесс
                logging.error(f"❌ {script} остановился! Перезапуск...")
                running_processes.remove((script, process))
                new_process = subprocess.Popen(["python", script])
                running_processes.append((script, new_process))

        time.sleep(5)

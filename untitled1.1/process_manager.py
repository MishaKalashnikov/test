import subprocess
import time

PROCESSES = ["bots/bot.py", "services/voice_scanner.py", "bots/chatGPT.py"]

def restart_process(script):
    while True:
        print(f"🔄 Запуск {script}...")
        process = subprocess.Popen(["python", script])
        process.wait()
        print(f"⚠️ {script} упал. Перезапускаем через 5 секунд...")
        time.sleep(5)

if __name__ == "__main__":
    for script in PROCESSES:
        subprocess.Popen(["python", script])

import sounddevice as sd
import speech_recognition as sr
import sqlite3
import queue
import time
import threading
from utils.database import get_channels_by_type

# 🔹 Ключевые слова
KEYWORDS = {"discord", "faceit", "link", "steam"}

# 🎤 Настройки аудиозаписи
SAMPLERATE = 44100
DEVICE = None

# 📂 Подключаемся к базе данных
conn = sqlite3.connect("streamer_voice_log.db", check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS voice_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        streamer TEXT,
        keyword TEXT,
        full_text TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

recognizer = sr.Recognizer()

def get_open_chat_streamers():
    return [channel[1] for channel in get_channels_by_type("open")]

def listen_to_streamer(streamer):
    """Запускает прослушивание стримера"""
    print(f"🎙️ Начинаем прослушивание {streamer}...")

    q = queue.Queue()

    def callback(indata, frames, time, status):
        q.put(indata.copy())

    with sd.InputStream(samplerate=SAMPLERATE, device=DEVICE, channels=1, callback=callback):
        while True:
            try:
                data = q.get()
                audio = sr.AudioData(data.tobytes(), SAMPLERATE, 2)
                text = recognizer.recognize_google(audio, language="en-US").lower()

                words = set(text.split())
                found_words = words.intersection(KEYWORDS)

                if found_words:
                    keyword = ", ".join(found_words)
                    print(f"✅ [{streamer}] Найдено ключевое слово: {keyword}")
                    threading.Thread(target=capture_speech, args=(streamer, keyword)).start()
            except sr.UnknownValueError:
                pass

def capture_speech(streamer, keyword):
    """Записывает 10 секунд речи после ключевого слова"""
    start_time = time.time()
    full_text = ""

    while time.time() - start_time < 10:
        try:
            audio = sr.AudioData(queue.Queue().get().tobytes(), SAMPLERATE, 2)
            text = recognizer.recognize_google(audio, language="en-US").lower()
            full_text += text + " "
        except sr.UnknownValueError:
            pass

    save_to_db(streamer, keyword, full_text.strip())

def save_to_db(streamer, keyword, full_text):
    """Сохраняет запись в базу данных"""
    with db_lock:
        cursor.execute("INSERT INTO voice_logs (streamer, keyword, full_text) VALUES (?, ?, ?)",
                       (streamer, keyword, full_text))
        conn.commit()

def start_voice_scanner():
    """Запускает голосовой мониторинг"""
    start_listening()

def start_listening():
    """Запускает многопоточное прослушивание"""
    streamers = get_open_chat_streamers()

    if not streamers:
        print("⚠️ Нет стримеров с открытым чатом!")
        return

    print(f"🎙️ Мониторинг: {', '.join(streamers)}")

    threads = []
    for streamer in streamers:
        thread = threading.Thread(target=listen_to_streamer, args=(streamer,))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    start_voice_scanner()

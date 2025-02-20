import sounddevice as sd
import speech_recognition as sr
import sqlite3
import queue
import time
import threading
from database import get_channels_by_type  # Импортируем список каналов

# 🔹 Ключевые слова, которые мы отслеживаем
KEYWORDS = {"discord", "faceit", "link", "steam"}

# 🎤 Настройки аудиозаписи (если OBS, укажи 'CABLE Output')
SAMPLERATE = 44100
DEVICE = None  # Если OBS → 'CABLE Output (VB-Audio Virtual Cable)'

# 📂 Подключаемся к базе данных SQLite (потокобезопасный режим)
conn = sqlite3.connect("streamer_voice_log.db", check_same_thread=False)
cursor = conn.cursor()
db_lock = threading.Lock()  # 🛠️ Блокировка для потокобезопасной работы с БД

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

# 🎙️ Очередь для аудиоданных
recognizer = sr.Recognizer()

def get_open_chat_streamers():
    """Получает список стримеров, у которых открыт чат"""
    return [channel[1] for channel in get_channels_by_type("open")]

def listen_to_streamer(streamer):
    """Создаёт отдельный поток для каждого стримера"""
    print(f"🎙️ Начинаем прослушивание {streamer}...")

    q = queue.Queue()

    def callback(indata, frames, time, status):
        """Записывает аудиоданные в очередь"""
        q.put(indata.copy())

    with sd.InputStream(samplerate=SAMPLERATE, device=DEVICE, channels=1, callback=callback):
        while True:
            try:
                data = q.get()
                audio = sr.AudioData(data.tobytes(), SAMPLERATE, 2)
                text = recognizer.recognize_google(audio, language="en-US").lower()
                print(f"🗣️ [{streamer}] Распознан текст: {text}")

                # Проверяем ключевые слова
                words = set(text.split())
                found_words = words.intersection(KEYWORDS)

                if found_words:
                    keyword = ", ".join(found_words)
                    print(f"✅ [{streamer}] Ключевое слово найдено: {keyword}")
                    threading.Thread(target=capture_speech, args=(streamer, keyword)).start()  # 🛠️ Запускаем поток для записи речи
            except sr.UnknownValueError:
                pass  # Если ничего не распознано, продолжаем слушать
            except Exception as e:
                print(f"❌ [{streamer}] Ошибка обработки речи: {e}")

def capture_speech(streamer, keyword):
    """Записывает 10 секунд речи после ключевого слова"""
    print(f"⏳ [{streamer}] Запись речи на 10 секунд после слова '{keyword}'...")

    start_time = time.time()
    full_text = ""
    q = queue.Queue()

    while time.time() - start_time < 10:
        try:
            data = q.get()
            audio = sr.AudioData(data.tobytes(), SAMPLERATE, 2)
            text = recognizer.recognize_google(audio, language="en-US").lower()
            full_text += text + " "
        except sr.UnknownValueError:
            pass  # Продолжаем слушать
        except Exception as e:
            print(f"❌ [{streamer}] Ошибка при записи речи: {e}")

    # Сохраняем в базу данных
    save_to_db(streamer, keyword, full_text.strip())

def save_to_db(streamer, keyword, full_text):
    """Сохраняет запись в базу данных (потокобезопасно)"""
    with db_lock:  # 🛠️ Гарантия потокобезопасности
        cursor.execute("INSERT INTO voice_logs (streamer, keyword, full_text) VALUES (?, ?, ?)",
                       (streamer, keyword, full_text))
        conn.commit()
    print(f"💾 [{streamer}] Запись сохранена в БД: {keyword} - {full_text}")

def start_listening():
    """Запускает многопоточное прослушивание всех стримеров"""
    streamers = get_open_chat_streamers()

    if not streamers:
        print("⚠️ Нет стримеров с открытым чатом!")
        return

    print(f"🎙️ Запуск мониторинга стримеров: {', '.join(streamers)}")

    threads = []
    for streamer in streamers:
        thread = threading.Thread(target=listen_to_streamer, args=(streamer,))
        thread.daemon = True  # 🛠️ Даем потокам работать в фоновом режиме
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()  # Ожидаем завершения всех потоков

# 🔥 Запускаем многопоточный мониторинг
if __name__ == "__main__":
    start_listening()

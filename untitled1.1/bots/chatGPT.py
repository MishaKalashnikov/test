import openai
import sqlite3
import asyncio
import logging
from bot import send_message  # Функция для отправки сообщений в чат

# 🔥 API-ключ OpenAI (замени на свой)
OPENAI_API_KEY = "your-api-key"
openai.api_key = OPENAI_API_KEY

# 📂 База данных голосовых сообщений
DB_PATH = "streamer_voice_log.db"

# 🎙️ Очередь сообщений для обработки
message_queue = asyncio.Queue()

# 🔥 Контекст общения (для каждого стримера)
chat_contexts = {}

# 🛠️ Логирование
logging.basicConfig(
    filename="chatGPT.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def get_latest_voice_logs():
    """🔍 Получает последние голосовые сообщения из БД"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT streamer, keyword, full_text FROM voice_logs 
            WHERE timestamp >= datetime('now', '-1 minute')
            ORDER BY timestamp DESC
        """)
        logs = cursor.fetchall()
        conn.close()

        for log in logs:
            await message_queue.put(log)  # Добавляем в очередь
    except Exception as e:
        logging.error(f"❌ Ошибка при загрузке голосовых сообщений: {e}")

async def generate_response(streamer, keyword, context):
    """🧠 Генерирует ответ ChatGPT с сохранением контекста беседы"""
    if streamer not in chat_contexts:
        chat_contexts[streamer] = [
            {"role": "system", "content": "Ты дружелюбный бот, общающийся со стримерами на Twitch."}
        ]

    # Добавляем сообщение стримера в контекст
    chat_contexts[streamer].append({"role": "user", "content": f"{streamer} сказал: {context}"})

    # Обрезаем историю до 10 последних сообщений (чтобы не накапливалось слишком много)
    if len(chat_contexts[streamer]) > 10:
        chat_contexts[streamer] = chat_contexts[streamer][-10:]

    try:
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-4",
            messages=chat_contexts[streamer],
            max_tokens=50
        )

        reply = response["choices"][0]["message"]["content"]

        # Запоминаем ответ бота
        chat_contexts[streamer].append({"role": "assistant", "content": reply})

        logging.info(f"💬 [ChatGPT] Ответ для {streamer}: {reply}")
        return reply
    except openai.error.OpenAIError as e:
        logging.error(f"❌ Ошибка OpenAI: {e}")
        return "Произошла ошибка, попробуйте позже."

async def process_messages(sock):
    """📩 Обрабатывает очередь сообщений и отправляет ответы"""
    while True:
        streamer, keyword, context = await message_queue.get()  # Берём сообщение из очереди
        reply = await generate_response(streamer, keyword, context)  # Генерируем ответ
        if reply:
            await send_message(sock, streamer, reply)  # Отправляем в чат
        await asyncio.sleep(2)  # Антиспам (2 секунды)

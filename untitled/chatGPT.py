import openai
import sqlite3
import asyncio
from bot import send_message  # Используем бот для отправки сообщений

# 🔥 API-ключ OpenAI
OPENAI_API_KEY = "your-api-key"
openai.api_key = OPENAI_API_KEY

# 📂 Подключаем БД
DB_PATH = "streamer_voice_log.db"

# 🎙️ Очередь сообщений для многопоточной обработки
message_queue = asyncio.Queue()

# 🔥 Храним контексты диалогов (чтобы бот "помнил" о чём говорит)
chat_contexts = {}

async def get_latest_voice_logs():
    """Получает последние голосовые сообщения из БД"""
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

async def generate_response(streamer, keyword, context):
    """Генерирует ответ ChatGPT с сохранением контекста беседы"""
    if streamer not in chat_contexts:
        chat_contexts[streamer] = [
            {"role": "system", "content": "Ты дружелюбный бот, общающийся с стримерами на Twitch."}
        ]

    # Добавляем последнее сообщение стримера в контекст
    chat_contexts[streamer].append({"role": "user", "content": f"{streamer} сказал: {context}"})

    response = await asyncio.to_thread(openai.ChatCompletion.create,
                                       model="gpt-4",
                                       messages=chat_contexts[streamer],
                                       max_tokens=50
                                       )

    reply = response["choices"][0]["message"]["content"]

    # Запоминаем ответ бота (чтобы продолжать беседу)
    chat_contexts[streamer].append({"role": "assistant", "content": reply})

    print(f"💬 [ChatGPT] Ответ для {streamer}: {reply}")
    return reply

async def process_messages(sock):
    """Обрабатывает очередь сообщений и отправляет ответы"""
    while True:
        streamer, keyword, context = await message_queue.get()  # Берём сообщение из очереди
        reply = await generate_response(streamer, keyword, context)  # Генерируем ответ
        await send_message(sock, streamer, reply)  # Отправляем в чат
        await asyncio.sleep(2)  # Чтобы бот не спамил слишком быстро

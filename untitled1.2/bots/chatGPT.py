import openai
import sqlite3
import asyncio
from bots.bot import send_message



OPENAI_API_KEY = ""
openai.api_key = OPENAI_API_KEY

DB_PATH = "streamer_voice_log.db"
message_queue = asyncio.Queue()
chat_contexts = {}



async def generate_response(streamer, message):
    if streamer not in chat_contexts:
        chat_contexts[streamer] = [{"role": "system", "content": "Ты дружелюбный бот на Twitch"}]

    chat_contexts[streamer].append({"role": "user", "content": message})

    try:
        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-4",
            messages=chat_contexts[streamer],
            max_tokens=50
        )

        reply = response["choices"][0]["message"]["content"]
        chat_contexts[streamer].append({"role": "assistant", "content": reply})
        return reply
    except openai.error.OpenAIError:
        return "ChatGPT временно недоступен."

def get_latest_voice_logs():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT streamer, full_text FROM voice_logs ORDER BY timestamp DESC LIMIT 5")
    logs = cursor.fetchall()
    conn.close()

    return logs

async def process_messages(sock):
    """Обрабатывает очередь сообщений и отправляет ответы"""
    while True:
        streamer, message = await message_queue.get()
        reply = await generate_response(streamer, message)
        await send_message(sock, streamer, reply)

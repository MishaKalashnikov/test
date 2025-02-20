import socket
import random
import asyncio
from database import get_channels_by_type  # Получаем список стримеров с открытым чатом

async def connect_to_twitch():
    print("🔗 Подключение к Twitch...")
    # Здесь должен быть код подключения бота к Twitch
    return "twitch_socket"

# 🔥 ДАННЫЕ БОТА
BOT_NICK = "YourBotUsername"  # Имя бота (замени на своё)
BOT_TOKEN = "oauth:xxxxxxxxxxxxxxxxxxxxxx"  # Твой OAuth-токен
SERVER = "irc.chat.twitch.tv"
PORT = 6667

# 🔥 БЕРЁМ СПИСОК СТРЕМИРОВ С ОТКРЫТЫМ ЧАТОМ
BOT_CHANNELS = [channel[1] for channel in get_channels_by_type("open")]

# 🔥 СПИСОК СООБЩЕНИЙ (бот периодически отправляет их)
MESSAGES = [
    "Привет! 😊 Как у вас настроение?",
    "Этот бот помогает чату быть активнее!",
    "Крутой стрим! 🚀",
    "Не забудьте подписаться!",
    "Какой сегодня контент?",
    "Я просто бот, но мне нравится ваш чат! 😎"
]

# 🔥 АСИНХРОННОЕ ПОДКЛЮЧЕНИЕ К TWITCH IRC
async def connect_to_twitch():
    sock = socket.socket()
    sock.connect((SERVER, PORT))
    sock.send(f"PASS {BOT_TOKEN}\n".encode("utf-8"))
    sock.send(f"NICK {BOT_NICK}\n".encode("utf-8"))
    print("✅ Бот подключился к Twitch!")
    return sock

# 🔥 ФУНКЦИЯ ОТПРАВКИ СООБЩЕНИЯ В ЧАТ
async def send_message(sock, channel, message):
    """Отправляет сообщение в чат Twitch"""
    sock.send(f"PRIVMSG #{channel} :{message}\n".encode("utf-8"))
    print(f"💬 [Отправлено в #{channel}]: {message}")

# 🔥 ФУНКЦИЯ ОТПРАВКИ ОТВЕТОВ CHATGPT
async def send_chatgpt_reply(sock, streamer, reply):
    """Отправляет сгенерированный ChatGPT-ответ в чат"""
    await send_message(sock, streamer, reply)

# 🔥 ФУНКЦИЯ ДЛЯ ФОНОВОГО ОТПРАВЛЕНИЯ СООБЩЕНИЙ
async def bot_loop():
    sock = await connect_to_twitch()

    while True:
        for channel in BOT_CHANNELS:
            message = random.choice(MESSAGES)  # Выбираем случайное сообщение
            await send_message(sock, channel, message)
            await asyncio.sleep(random.randint(30, 90))  # Пауза перед следующим сообщением

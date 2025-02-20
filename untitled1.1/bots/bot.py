import socket
import random
import asyncio
import logging
from database import get_channels_by_type  # Получаем список стримеров с открытым чатом

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

# 🛠️ Логирование
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

async def connect_to_twitch():
    """🔗 Подключение к Twitch IRC (с авто-переподключением)"""
    while True:
        try:
            sock = socket.socket()
            sock.connect((SERVER, PORT))
            sock.send(f"PASS {BOT_TOKEN}\n".encode("utf-8"))
            sock.send(f"NICK {BOT_NICK}\n".encode("utf-8"))

            for channel in BOT_CHANNELS:
                sock.send(f"JOIN #{channel}\n".encode("utf-8"))
                logging.info(f"✅ Бот подключился к #{channel}")

            print("✅ Бот подключился к Twitch!")
            return sock
        except Exception as e:
            logging.error(f"❌ Ошибка подключения: {e}")
            print(f"⚠️ Ошибка подключения, пробуем снова через 10 секунд...")
            await asyncio.sleep(10)  # Если ошибка — ждём 10 секунд и пробуем снова

async def send_message(sock, channel, message):
    """💬 Отправляет сообщение в чат Twitch"""
    try:
        sock.send(f"PRIVMSG #{channel} :{message}\n".encode("utf-8"))
        print(f"💬 [Отправлено в #{channel}]: {message}")
        logging.info(f"💬 [#{channel}] {message}")
    except Exception as e:
        logging.error(f"❌ Ошибка отправки сообщения в {channel}: {e}")

async def send_chatgpt_reply(sock, streamer, reply):
    """🤖 Отправляет ответ ChatGPT в чат"""
    await send_message(sock, streamer, reply)

async def keep_alive(sock):
    """🛠️ Отправляет PONG-сообщение, чтобы Twitch не отключил бота"""
    while True:
        try:
            sock.send("PONG :tmi.twitch.tv\n".encode("utf-8"))
            await asyncio.sleep(300)  # Отправляем раз в 5 минут
        except Exception as e:
            logging.error(f"❌ Ошибка отправки PONG: {e}")

async def listen_to_chat(sock):
    """🎙️ Слушает чат и реагирует на сообщения"""
    while True:
        try:
            response = sock.recv(2048).decode("utf-8")

            if "PING" in response:
                sock.send("PONG :tmi.twitch.tv\n".encode("utf-8"))  # Отвечаем на PING от Twitch

            for channel in BOT_CHANNELS:
                if f"@{BOT_NICK}" in response:
                    await send_message(sock, channel, "Вы позвали меня? 😊")

        except Exception as e:
            logging.error(f"❌ Ошибка чтения чата: {e}")

async def bot_loop():
    """♻️ Основной цикл бота"""
    sock = await connect_to_twitch()

    # Создаём фоновые задачи
    asyncio.create_task(keep_alive(sock))
    asyncio.create_task(listen_to_chat(sock))

    while True:
        for channel in BOT_CHANNELS:
            message = random.choice(MESSAGES)  # Выбираем случайное сообщение
            await send_message(sock, channel, message)
            await asyncio.sleep(random.randint(30, 90))  # Пауза перед следующим сообщением

if __name__ == "__main__":
    asyncio.run(bot_loop())

import os
from dotenv import load_dotenv


# Загружаем переменные окружения из `.env`
load_dotenv()

# 🔥 Twitch-бот
BOT_NICK = os.getenv("BOT_NICK", "YourBotUsername")  # Имя бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "oauth:xxxxxxxxxxxxxxxxxxxxxx")  # OAuth-токен
SERVER = "irc.chat.twitch.tv"
PORT = 6667

# 🔥 OpenAI (ChatGPT)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key")

# 🔥 Настройки базы данных
DB_PATH = "database/streamer_voice_log.db"

# 🔥 Тайминги и настройки бота
MESSAGE_INTERVAL = (30, 90)  # Интервал отправки сообщений (секунды)
MAX_CHAT_CONTEXT = 10  # Максимальное количество сообщений в памяти ChatGPT

# 🔥 Настройки голосового анализа
SAMPLERATE = 44100
DEVICE = None  # Если OBS → 'CABLE Output (VB-Audio Virtual Cable)'

# 🔥 Ключевые слова для голосового анализа
KEYWORDS = {"discord", "faceit", "link", "steam"}

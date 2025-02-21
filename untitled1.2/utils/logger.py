import logging
import os


# 🔥 Создаём папку logs (если её нет)
if not os.path.exists("logs"):
    os.makedirs("logs")

def setup_logger(name, log_file, level=logging.INFO):
    """Настраивает логгер для записи в файл"""
    logger = logging.getLogger(name)
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

# 🔥 Создаём логгеры для разных сервисов
bot_logger = setup_logger("bot", "logs/bot.log")
chat_logger = setup_logger("chatGPT", "logs/chatGPT.log")
voice_logger = setup_logger("voice", "logs/voice_scanner.log")
db_logger = setup_logger("database", "logs/database.log")

import asyncio
import logging
import requests
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from database import get_all_channels, get_channels_by_type, insert_or_update_channel, delete_channel
from bot import bot_loop, send_chatgpt_reply, connect_to_twitch
from voice_scanner import start_voice_scanner
from chatGPT import process_messages, get_latest_voice_logs

# 🔥 Логирование
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# 🔥 Порты для подключения браузеров
PORTS = [9222, 9223]

# 🔥 User-Agent
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"

# 🔥 Проверка доступности порта
def is_port_available(port):
    try:
        response = requests.get(f"http://127.0.0.1:{port}/json", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

# 🔥 Настройка Selenium (для ручного подключения по портам)
def setup_driver(port):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent={USER_AGENT}")
    options.debugger_address = f"127.0.0.1:{port}"

    # ✅ Оптимизированные параметры
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")

    # ✅ Подключение к уже запущенному браузеру (DevTools)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 30)
    return driver, wait

# 🔥 Запуск Twitch-бота, голосового мониторинга и ChatGPT через браузеры по портам
async def start_services():
    for port in PORTS:
        print(f"🚀 Проверяем доступность браузера на порту {port}")

        if is_port_available(port):
            print(f"🚀 Подключение к браузеру на порту {port}")
            logging.info(f"🚀 Подключение к браузеру на порту {port}")

            driver, wait = setup_driver(port)
            print(f"✅ Браузер на порту {port} подключен.")

            # 🔥 Запускаем бота, голосовой мониторинг и ChatGPT
            sock = await connect_to_twitch()  # Подключаемся к Twitch

            await asyncio.gather(
                bot_loop(),                # Бот отправляет сообщения в чат
                start_voice_scanner(sock), # Голосовой мониторинг
                get_latest_voice_logs(),   # Проверка БД на новые сообщения
                process_messages(sock)     # ChatGPT отвечает в чат
            )

            driver.quit()  # Закрываем браузер после выполнения
        else:
            print(f"⚠️ Порт {port} недоступен. Пропускаем.")
            logging.warning(f"⚠️ Порт {port} недоступен. Пропускаем.")

# 🔥 Работа с БД: просмотр и удаление каналов
def manage_database():
    print("\n📌 Загружаем каналы из БД...")
    channels = get_all_channels()

    if channels:
        for channel in channels:
            print(channel)
    else:
        print("⚠️ В базе данных пока нет каналов.")

    # 📌 Добавление тестового канала (можно удалить)
    insert_or_update_channel("example_channel", "followers")
    print("\n✅ Канал 'example_channel' добавлен или обновлён в БД!")

    # 📌 Удаление канала (по желанию)
    channel_name = input("\nВведите канал для удаления (или Enter для пропуска): ")
    if channel_name:
        delete_channel(channel_name)

    # 📌 Вывод всех каналов (отсортированных)
    print("\n📌 Все каналы (отсортированы по типу):")
    channels = get_all_channels()
    if channels:
        for row in channels:
            print(row)
    else:
        print("⚠️ В базе нет каналов после удаления.")

    print("\n📌 Каналы только для 'followers':")
    followers = get_channels_by_type("followers")
    print(followers if followers else "❌ Нет каналов.")

    print("\n📌 Открытые каналы ('open'):")
    open_channels = get_channels_by_type("open")
    print(open_channels if open_channels else "❌ Нет каналов.")

    print("\n📌 Каналы с верификацией ('verified'):")
    verified = get_channels_by_type("verified")
    print(verified if verified else "❌ Нет каналов.")

    print("\n✅ Работа с базой данных завершена!")

if __name__ == "__main__":
    print("📌 Выберите режим работы:")
    print("1️⃣ - Запустить бота, голосовой мониторинг и ChatGPT через браузеры")
    print("2️⃣ - Управление базой данных")

    choice = input("Выберите действие: ")

    if choice == "1":
        asyncio.run(start_services())  # Запускаем все сервисы через порты
    elif choice == "2":
        manage_database()
    else:
        print("❌ Неверный ввод. Запустите программу снова.")

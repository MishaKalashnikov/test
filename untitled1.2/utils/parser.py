import sys
import os

# Добавляем корневую директорию проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import threading
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from utils.database import insert_or_update_channel, clear_channels  # Запись в БД

# 🔥 Теперь `utils.database` будет найден правильно!


# 🔥 Логирование
logging.basicConfig(
    filename="parser.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ✅ Доступные языки для выбора
LANGUAGES = {
    "1": "en", "2": "ru", "3": "es", "4": "de", "5": "fr",
    "6": "pt", "7": "pl", "8": "it", "9": "tr", "10": "ja"
}

# ✅ Настройки Selenium
def create_driver():
    """Создает новый экземпляр браузера"""
    chrome_options = Options()
    chrome_options.headless = True  # Запускаем браузер в скрытом режиме
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # ✅ Увеличенный таймаут WebDriver
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)

    return driver

def select_languages():
    """Позволяет пользователю выбрать несколько языков"""
    print("\n🔹 Выберите языки для парсинга (через запятую):")
    for key, lang in LANGUAGES.items():
        print(f"{key}. {lang}")

    while True:
        choices = input("\nВведите номера языков (например, 1,2,5 для English, Russian, French): ").strip()
        selected_languages = {LANGUAGES[num] for num in choices.split(",") if num in LANGUAGES}

        if selected_languages:
            return list(selected_languages)
        else:
            print("❌ Ошибка! Введите корректные номера языков.")

def get_stream_links(language, results):
    """Загружает Twitch и собирает ссылки на стримы"""
    driver = create_driver()
    url = f"https://www.twitch.tv/directory/category/counter-strike?sort=VIEWER_COUNT_ASC&lang={language}"

    try:
        driver.get(url)
        time.sleep(5)  # Даем время загрузиться контенту

        # 🔹 Прокручиваем страницу для подгрузки стримов
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

        # 🔹 Получаем ссылки на стримы
        streams = driver.find_elements(By.TAG_NAME, "a")
        raw_links = [stream.get_attribute("href") for stream in streams if stream.get_attribute("href")]

        # 🔹 Фильтруем только ссылки на стримы и оставляем только имена каналов
        filtered_names = list(set(
            link.replace("https://www.twitch.tv/", "").strip() for link in raw_links
            if link.startswith("https://www.twitch.tv/") and
            not any(x in link for x in ["/directory", "/videos", "/clips"])
        ))

        print(f"✅ Загружены {len(filtered_names)} стримов для языка: {language}")
        results.extend(filtered_names)
        logging.info(f"{language}: {len(filtered_names)} каналов загружено.")

    except Exception as e:
        print(f"❌ Ошибка загрузки для языка {language}: {e}")
        logging.error(f"{language}: Ошибка - {e}")

    driver.quit()  # Закрываем браузер после обработки

def main():
    """Основной алгоритм"""
    results = []

    # ✅ Спрашиваем пользователя, нужно ли очистить БД перед парсингом
    choice = input("\n📌 Очистить базу данных перед парсингом? (yes/no): ").strip().lower()
    if choice == "yes":
        clear_channels()  # Очищаем БД
        print("✅ База данных очищена перед обновлением!")

    selected_languages = select_languages()
    print(f"\n🔹 Вы выбрали языки: {', '.join(selected_languages).upper()}")

    threads = []
    for language in selected_languages:
        thread = threading.Thread(target=get_stream_links, args=(language, results))
        thread.start()
        threads.append(thread)

    # ✅ Ждем завершения всех потоков
    for thread in threads:
        thread.join()

    # ✅ Записываем данные в БД
    for channel in results:
        insert_or_update_channel(channel, "open")

    print("\n✅ База данных обновлена новыми каналами!")
    logging.info("База данных обновлена новыми каналами.")

if __name__ == "__main__":
    main()

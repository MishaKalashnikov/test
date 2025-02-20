from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import threading

# ✅ Настройки Selenium
def create_driver():
    """Создает новый экземпляр браузера"""
    chrome_options = Options()
    chrome_options.headless = False  # Отключаем headless, чтобы видеть процесс
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    # ✅ Оптимизация загрузки
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--blink-settings=imagesEnabled=false")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-notifications")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # ✅ Увеличенный таймаут WebDriver
    driver.set_page_load_timeout(60)
    driver.set_script_timeout(60)

    return driver

# ✅ Разбиваем языки на группы (можно добавить больше)
languages_groups = [
    ["bg", "cs", "da", "de", "el", "es", "es-mx", "fi", "fr"],
    ["hu", "it", "ja", "ko", "nl", "no", "pl", "pt", "pt-br"],
    ["ro", "ru", "sk", "sv", "th", "tr", "vi", "zh-cn", "zh-tw"]
]

def get_stream_links(driver, languages, results):
    """Загружает Twitch для каждого языка и собирает ссылки на стримы"""
    for lang in languages:
        url = f"https://www.twitch.tv/directory/category/counter-strike?sort=VIEWER_COUNT_ASC&lang={lang}"

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

            print(f"✅ Загружены {len(filtered_names)} стримов для языка: {lang}")
            results.extend(filtered_names)

        except Exception as e:
            print(f"❌ Ошибка загрузки для языка {lang}: {e}")

    driver.quit()  # Закрываем браузер после обработки всех языков

def main():
    """Основной алгоритм (запуск 1 браузера)"""
    results = []

    # ✅ Запускаем Selenium
    driver = create_driver()
    get_stream_links(driver, languages_groups[0], results)

    # ✅ Записываем все каналы в `filtered_streams.txt`
    with open("filtered_streams.txt", "w", encoding="utf-8") as file:
        for channel in results:
            file.write(channel + "\n")

    print("✅ Готово! Результаты сохранены в `filtered_streams.txt`.")

if __name__ == "__main__":
    main()

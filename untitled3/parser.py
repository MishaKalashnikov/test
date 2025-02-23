import os
import time
import logging
import easyocr
from PIL import Image, UnidentifiedImageError
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === 🔥 Настройка логирования ===
logging.basicConfig(
    filename="parser.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# === 📌 OCR для распознавания текста ===
reader = easyocr.Reader(['en'], gpu=False)

# === 📂 Папка для скриншотов ===
screenshot_folder = "twitter_usernames_screenshots"
os.makedirs(screenshot_folder, exist_ok=True)

# === 🔥 Лимит количества никнеймов ===
TARGET_USERNAMES = 120
usernames = set()

# === 🔄 Восстановление никнеймов из файла ===
if os.path.exists("twitter_usernames.txt"):
    with open("twitter_usernames.txt", "r", encoding="utf-8") as file:
        usernames.update(line.strip() for line in file)

# === 🚀 Настройки Chrome ===
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.debugger_address = "127.0.0.1:9222"

# === 🚀 Подключение к браузеру ===
try:
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    time.sleep(3)
    logging.info("✅ Успешно подключен к браузеру.")
except Exception as e:
    logging.error(f"❌ Ошибка подключения к браузеру: {e}")
    exit()

# === 🔍 Открываем Twitter поиск ===
try:
    search_url = "https://x.com/search?q=CEO&src=typeahead_click&f=user"
    logging.info(f"🔍 Переход на страницу: {search_url}")
    driver.get(search_url)

    # Ожидание загрузки элементов на странице
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(5)

except Exception as e:
    logging.error(f"❌ Ошибка загрузки Twitter: {e}")

scroll_count = 0

try:
    while len(usernames) < TARGET_USERNAMES:
        scroll_count += 1
        logging.info(f"🔄 Прокрутка {scroll_count} (Собрано: {len(usernames)}/{TARGET_USERNAMES})")

        # 📜 Прокрутка страницы
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5)

        # 📸 Скриншот
        screenshot_path = os.path.join(screenshot_folder, f"scroll_{scroll_count}.png")
        driver.save_screenshot(screenshot_path)

        # === ✂️ Обрезка области с никнеймами ===
        try:
            img = Image.open(screenshot_path)
            width, height = img.size
            cropped_img = img.crop((0, 0, width - 600, height))
            cropped_img_path = os.path.join(screenshot_folder, f"cropped_{scroll_count}.png")
            cropped_img.save(cropped_img_path)

            # === 🔍 Распознаем текст с EasyOCR ===
            text_results = reader.readtext(cropped_img_path)

            # === 🔍 Фильтруем только @username ===
            for text in text_results:
                detected = text[1].strip()
                if detected.startswith("@") and detected not in usernames:
                    usernames.add(detected)
                    logging.info(f"📌 Найден @username: {detected}")

                    # === 📝 Сохранение никнеймов в реальном времени ===
                    with open("twitter_usernames.txt", "w") as file:
                        file.writelines("\n".join(usernames))

        except UnidentifiedImageError:
            logging.error(f"❌ Ошибка: Не удалось обработать скриншот {screenshot_path}. Пропускаем.")
            continue

        if len(usernames) >= TARGET_USERNAMES:
            logging.info(f"✅ Достигнуто {TARGET_USERNAMES} никнеймов! Останавливаем парсер.")
            break

except Exception as e:
    logging.error(f"❌ Ошибка парсинга: {e}")

finally:
    # === 🗑️ Удаление всех скриншотов ===
    for file in os.listdir(screenshot_folder):
        os.remove(os.path.join(screenshot_folder, file))
    logging.info("🗑️ Все временные скриншоты удалены.")

    driver.quit()
    logging.info("🚪 Браузер закрыт.")

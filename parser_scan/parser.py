import os
import time
import easyocr
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# === 📌 Создаем объект EasyOCR ===
reader = easyocr.Reader(['en'])

# === 🚀 Подключение к открытому браузеру (порт 9222) ===
chrome_options = Options()
chrome_options.debugger_address = "127.0.0.1:9222"
driver = webdriver.Chrome(options=chrome_options)

# === 🔍 Открываем Twitter (X) поиск ===
search_url = "https://x.com/search?q=CEO&src=typeahead_click&f=user"
print(f"🔍 Переход на страницу: {search_url}")
driver.get(search_url)
time.sleep(8)

# === 📂 Создание папки для скриншотов никнеймов ===
screenshot_folder = "twitter_usernames_screenshots"
if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)

# === 🔄 Прокрутка + обрезка скриншотов ===
scroll_count = 5  # Количество прокруток
usernames = []

for i in range(scroll_count):
    # 📜 Прокрутка страницы
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(5)
    print(f"🔄 Прокрутка {i+1}/{scroll_count} завершена...")

    # 📸 Полный скриншот страницы
    full_screenshot_path = os.path.join(screenshot_folder, f"full_scroll_{i+1}.png")
    driver.save_screenshot(full_screenshot_path)
    print(f"✅ Полный скриншот сохранен: {full_screenshot_path}")

    # === ✂️ Обрезка скриншота до области никнеймов ===
    img = Image.open(full_screenshot_path)
    width, height = img.size

    # Устанавливаем координаты обрезки (Задай свои, если не подходит)
    x1, y1 = 0, 0  # Верхний левый угол
    x2, y2 = width - 500, height - 0  # Нижний правый угол

    cropped_img = img.crop((x1, y1, x2, y2))

    # Сохраняем обрезанный скриншот
    cropped_screenshot_path = os.path.join(screenshot_folder, f"cropped_scroll_{i+1}.png")
    cropped_img.save(cropped_screenshot_path)
    print(f"✅ Обрезанный скриншот сохранен: {cropped_screenshot_path}")

    # === 🔍 Распознаем текст с EasyOCR ===
    text_results = reader.readtext(cropped_screenshot_path)

    # === 🔍 Фильтруем только @username ===
    for text in text_results:
        detected_text = text[1].strip()
        if detected_text.startswith("@") and len(detected_text) > 1:
            usernames.append(detected_text)
            print(f"📌 Найден @username: {detected_text}")

# === 🔻 Закрытие браузера ===
driver.quit()
print("🚪 Браузер закрыт.")

# === 📝 Сохранение никнеймов в TXT ===
with open("twitter_usernames.txt", "w", encoding="utf-8") as file:
    file.writelines("\n".join(usernames))

print("✅ Парсинг завершен! Все @usernames сохранены в **twitter_usernames.txt**, обрезанные скриншоты в **twitter_usernames_screenshots/** 🎉")

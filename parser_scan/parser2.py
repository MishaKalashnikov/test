import os
import time
import easyocr
import pandas as pd
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# === 📌 Создаем объект EasyOCR ===
reader = easyocr.Reader(['en'])

# === 📌 Читаем @username из файла ===
with open("twitter_usernames.txt", "r", encoding="utf-8") as file:
    usernames = [line.strip() for line in file.readlines()]

# === 📂 Создание папки для скриншотов профилей ===
screenshot_folder = "twitter_profiles_screenshots"
if not os.path.exists(screenshot_folder):
    os.makedirs(screenshot_folder)

# === 🚀 Подключение к открытому браузеру (порт 9222) ===
chrome_options = Options()
chrome_options.debugger_address = "127.0.0.1:9222"
driver = webdriver.Chrome(options=chrome_options)

# === 📋 Создание списка для хранения данных ===
profile_data = []

try:
    # === 🔄 Обход всех профилей ===
    for i, username in enumerate(usernames):
        profile_url = f"https://x.com/{username}"
        print(f"🔍 Открываем профиль: {profile_url}")
        driver.get(profile_url)
        time.sleep(5)

        # 📸 Полный скриншот профиля
        full_screenshot_path = os.path.join(screenshot_folder, f"full_profile_{i+1}.png")
        driver.save_screenshot(full_screenshot_path)
        print(f"✅ Полный скриншот сохранен: {full_screenshot_path}")

        # === ✂️ Обрезка скриншота до области никнейма и описания ===
        img = Image.open(full_screenshot_path)
        width, height = img.size

        # Примерные координаты заголовка и описания (Настроить под свой экран)
        x1, y1 = 300, 200  # Верхний левый угол
        x2, y2 = width - 500, height - 250  # Нижний правый угол

        cropped_img = img.crop((x1, y1, x2, y2))

        # Сохраняем обрезанный скриншот
        cropped_screenshot_path = os.path.join(screenshot_folder, f"cropped_profile_{i+1}.png")
        cropped_img.save(cropped_screenshot_path)
        print(f"✅ Обрезанный скриншот сохранен: {cropped_screenshot_path}")

        # === 🔍 Распознаем текст с EasyOCR ===
        text_results = reader.readtext(cropped_screenshot_path)

        # === 📌 Фильтруем название и описание канала ===
        profile_name = "Не найдено"
        profile_description = "Не найдено"

        if len(text_results) > 0:
            profile_name = text_results[0][1].strip()  # Название (первый найденный текст)
        if len(text_results) > 1:
            profile_description = " ".join([text[1].strip() for text in text_results[1:]])  # Все остальное - описание


        print(f"📝 Описание: {profile_description}")

        # === 📝 Добавляем данные в список ===
        profile_data.append([username, profile_description])

except KeyboardInterrupt:
    print("\n⛔ Принудительная остановка! Сохраняем данные в Excel...")

except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    print("⛔ Остановка парсера. Сохраняем данные...")

finally:
    # === 🔻 Закрытие браузера ===
    driver.quit()
    print("🚪 Браузер закрыт.")

    # === 📊 Сохранение данных в Excel ===
    df = pd.DataFrame(profile_data, columns=["Username", "Описание"])
    excel_path = "twitter_profiles.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"✅ Данные сохранены в **{excel_path}** 🎉")

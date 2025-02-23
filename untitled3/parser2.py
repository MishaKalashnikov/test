import os
import time
import easyocr
import pandas as pd
from PIL import Image, UnidentifiedImageError
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# === 📌 Создаем объект EasyOCR ===
reader = easyocr.Reader(['en'])

# === 📌 Проверяем, существует ли `twitter_usernames.txt` ===
if not os.path.exists("twitter_usernames.txt"):
    print("❌ Файл twitter_usernames.txt не найден! Сначала запусти parser.py.")
    exit()

# === 📌 Читаем @username из файла ===
with open("twitter_usernames.txt", "r", encoding="utf-8") as file:
    usernames = [line.strip() for line in file.readlines()]

# === 📂 Создание папки для скриншотов профилей ===
screenshot_folder = "twitter_profiles_screenshots"
os.makedirs(screenshot_folder, exist_ok=True)

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

        # ⏳ Ожидание загрузки страницы
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//h2"))  # Примерный заголовок страницы
            )
        except:
            print(f"⚠️ Страница {profile_url} загрузилась некорректно. Пропускаем.")
            continue

        time.sleep(3)  # Небольшая пауза для полной загрузки

        # 📸 Полный скриншот профиля
        full_screenshot_path = os.path.join(screenshot_folder, f"full_profile_{i+1}.png")
        driver.save_screenshot(full_screenshot_path)
        print(f"✅ Полный скриншот сохранен: {full_screenshot_path}")

        # === ✂️ Обрезка скриншота до области никнейма и описания ===
        try:
            img = Image.open(full_screenshot_path)
            width, height = img.size
            x1, y1 = 300, 200  # Верхний левый угол
            x2, y2 = width - 500, height - 250  # Нижний правый угол
            cropped_img = img.crop((x1, y1, x2, y2))

            # Сохраняем обрезанный скриншот
            cropped_screenshot_path = os.path.join(screenshot_folder, f"cropped_profile_{i+1}.png")
            cropped_img.save(cropped_screenshot_path)
            print(f"✅ Обрезанный скриншот сохранен: {cropped_screenshot_path}")

        except UnidentifiedImageError:
            print(f"❌ Ошибка: Не удалось открыть скриншот {full_screenshot_path}. Пропускаем.")
            continue

        # === 🔍 Распознаем текст с EasyOCR ===
        text_results = reader.readtext(cropped_screenshot_path)

        # === 📌 Фильтруем название и описание канала ===
        profile_description = "Нет описания"

        if len(text_results) > 0:
            profile_description = " ".join([text[1].strip() for text in text_results])

        print(f"📌 Описание: {profile_description}")

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

    # === 📝 Сохранение данных в Excel ===
    df = pd.DataFrame(profile_data, columns=["Username", "Описание"])
    excel_path = "twitter_profiles.xlsx"
    df.to_excel(excel_path, index=False)
    print(f"✅ Данные сохранены в **{excel_path}** 🎉")

    # === 🗑️ Удаление всех скриншотов ===
    for file in os.listdir(screenshot_folder):
        os.remove(os.path.join(screenshot_folder, file))
    print("🗑️ Все скриншоты удалены.")

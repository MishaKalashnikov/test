import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Файл с логинами и паролями
CREDENTIALS_FILE = "parser.txt"
CHECKED_ACCOUNTS_FILE = "checked_accounts.txt"


# URL для работы с аккаунтом
LOGIN_URL = "https://www.stanleybet.ro/conectare"
BALANCE_URL = "https://www.stanleybet.ro/casier/detalii-sold"
DEPOSIT_URL = "https://www.stanleybet.ro/casier/fonduri/depunere"
RET_URL = "https://www.stanleybet.ro/casier/fonduri/retrageri-in-asteptare"

# Координаты кнопок PyAutoGUI (обновите при необходимости)
OK_X, OK_Y = 1056, 462
ACCEPT_X, ACCEPT_Y = 795, 665

# Настройки браузера
chrome_options = Options()
chrome_options.debugger_address = "127.0.0.1:9222"

print("🚀 Подключаемся к Chrome через порт 9222...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 10)

# ✅ Функция записи в файл
def write_to_file(text):
    """Записывает текст в файл `results.txt`"""
    with open(CHECKED_ACCOUNTS_FILE, "a", encoding="utf-8") as file:
        file.write(text + "\n")

# ✅ Функция чтения логинов и паролей
def read_credentials(file_path):
    """Читает логины и пароли из файла и возвращает список (логин, пароль)."""
    credentials = []
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                parts = line.strip().split(":")
                if len(parts) == 2:
                    credentials.append((parts[0], parts[1]))  # (логин, пароль)
    except FileNotFoundError:
        write_to_file(f"❌ Ошибка: Файл {file_path} не найден.")
    return credentials

def get_checked_accounts():
    """Загружает уже проверенные аккаунты из `checked_accounts.txt`"""
    try:
        with open(CHECKED_ACCOUNTS_FILE, "r", encoding="utf-8") as file:
            return set(line.strip() for line in file if line.strip())
    except FileNotFoundError:
        return set()

# ✅ Функция закрытия всплывающего окна (если есть)
def close_popup():
    """Закрывает всплывающее окно через PyAutoGUI (если есть)"""
    time.sleep(3)
    pyautogui.click(x=OK_X, y=OK_Y)
    pyautogui.click(x=ACCEPT_X, y=ACCEPT_Y)

# ✅ Функция очистки куков
def clear_cookies():
    """Очищает куки и локальное хранилище"""
    write_to_file("\n🧹 Очищаем куки и данные хранилища...")
    try:
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")
        driver.execute_script("window.sessionStorage.clear();")
    except Exception as e:
        write_to_file(f"❌ Ошибка при очистке данных: {e}")

# ✅ Читаем логины и пароли
credentials = read_credentials(CREDENTIALS_FILE)

# ✅ Обрабатываем каждый аккаунт
for username, password in credentials:
    try:
        pyautogui.click(x=OK_X, y=OK_Y)
        pyautogui.click(x=ACCEPT_X, y=ACCEPT_Y)
        driver.get(LOGIN_URL)
        close_popup()
        time.sleep(2)

        username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
        password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
        auth_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))

        username_input.send_keys(username)
        password_input.send_keys(password)
        auth_button.click()

        time.sleep(5)

        # ✅ После входа сразу идем на баланс
        driver.get(BALANCE_URL)
        time.sleep(3)

        # ✅ Получаем баланс
        try:
            balance_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//span[contains(@class, 'text-xl') and contains(text(), 'LEI')]")))
            balance = balance_element.text
            write_to_file(f"💰 Баланс для {username}: {balance}")
        except:
            write_to_file(f"⚠ Не удалось получить баланс для {username}. Пропускаем аккаунт...")
            continue  # ❌ Пропускаем аккаунт, если баланс не найден

        # ✅ Проверяем наличие ожидаемых выводов
        driver.get(RET_URL)
        pyautogui.click(x=OK_X, y=OK_Y)
        pyautogui.click(x=ACCEPT_X, y=ACCEPT_Y)
        time.sleep(3)

        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//h1[contains(text(), 'Nu există informații disponibile')]")))
            write_to_file(f"✅ Ожидаемых выводов средств НЕТ для {username}.")
        except:
            write_to_file(f"⚠ Есть ожидаемые выводы средств для {username}!")

        # ✅ Пополнение баланса
        driver.get(DEPOSIT_URL)
        time.sleep(5)

        try:
            deposit_button = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'btn-2xl') and contains(text(), '200,00 LEI')]")))
            deposit_button.click()
            write_to_file(f"Выбрана сумма пополнения 200 LEI.")
        except Exception as e:
            write_to_file(f"Ошибка при выборе суммы пополнения: {e}")

        time.sleep(3)

        try:
            confirm_deposit_button = wait.until(EC.element_to_be_clickable(
                (By.CLASS_NAME, "tr_cashier_deposit_page_deposit_button")))
            driver.execute_script("arguments[0].scrollIntoView();", confirm_deposit_button)
            driver.execute_script("arguments[0].click();", confirm_deposit_button)
            write_to_file("Пополнение подтверждено.")
        except Exception as e:
            write_to_file(f"Ошибка подтверждения пополнения: {e}")
        time.sleep(5)

        iframes = driver.find_elements(By.TAG_NAME, "iframe")

        if len(iframes) > 7:
            driver.switch_to.frame(iframes[7])
            try:
                card_binding = wait.until(EC.presence_of_element_located(
                    (By.CLASS_NAME, "user_pm.payment_header.noselect")))
                write_to_file("3) Привязанная карта найдена.")
            except:
                write_to_file("3) Привязанная карта не найдена.")
            driver.switch_to.default_content()

    except Exception as e:
        write_to_file(f"Общая ошибка: {e}")

    # ✅ Очищаем куки перед следующим аккаунтом
    clear_cookies()

# ✅ Финальная очистка после завершения всех аккаунтов
clear_cookies()

write_to_file("✅ Скрипт завершил работу.")
driver.quit()

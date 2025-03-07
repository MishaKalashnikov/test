import time
import signal
import sys
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchWindowException, WebDriverException, SessionNotCreatedException, InvalidSessionIdException

# Константы
LOGIN_URL = "https://www.stanleybet.ro/conectare"
RESULTS_FILE = "results.txt"
LOGPASS_FILE = "LogPass.txt"

OK_X, OK_Y = 1056, 462
ACCEPT_X, ACCEPT_Y = 795, 665

# Флаг для корректного завершения
stop_script = False
driver = None
wait = None
tab_index = 0  # Переменная для переключения между вкладками (0 или 1)

# Обработчик сигнала для Ctrl+C
def signal_handler(sig, frame):
    global stop_script
    print("\n🚨 Принудительная остановка! Завершаем работу...")
    stop_script = True

signal.signal(signal.SIGINT, signal_handler)

# Функция для запуска или переподключения к браузеру
def start_driver():
    global driver, wait
    print("🚀 Запуск или переподключение к Chrome...")

    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        wait = WebDriverWait(driver, 10)
        print("✅ Браузер подключен!")
    except (SessionNotCreatedException, WebDriverException) as e:
        print(f"❌ Ошибка запуска браузера: {e}")
        sys.exit()

# Загружаем уже обработанные аккаунты
def get_processed_accounts():
    processed = {}
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(": ")
                if len(parts) == 2:
                    processed[parts[0].strip()] = parts[1].strip()
    except FileNotFoundError:
        return {}
    return processed

# Читаем логины и пароли
def get_accounts():
    pyautogui.click(x=OK_X, y=OK_Y)
    pyautogui.click(x=ACCEPT_X, y=ACCEPT_Y)
    accounts = []
    try:
        with open(LOGPASS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(":", 1)
                if len(parts) == 2:
                    username = parts[0].strip()
                    password = parts[1].strip()
                    accounts.append((username, password))
    except FileNotFoundError:
        print("❌ Файл LogPass.txt не найден!")
    except Exception as e:
        print(f"❌ Ошибка при чтении LogPass.txt: {e}")
    return accounts

def save_result(username, status):
    """Записывает результат в файл results.txt"""
    with open(RESULTS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{username}: {status}\n")
    print(f"📄 {username} → {status} записан в results.txt")

def accept_cookies():
    """Принимает куки, если окно появилось"""
    try:
        print("🍪 Проверяем всплывающее окно с куками...")
        cookie_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Permitere toate')]")))
        driver.execute_script("arguments[0].click();", cookie_button)
        print("✅ Куки приняты!")
        pyautogui.click(x=OK_X, y=OK_Y)
        pyautogui.click(x=ACCEPT_X, y=ACCEPT_Y)
        time.sleep(2)
    except:
        print("❌ Окно с куками не найдено или уже закрыто.")

def clear_cookies():
    """Очищает куки и локальное хранилище"""
    try:
        pyautogui.click(x=OK_X, y=OK_Y)
        pyautogui.click(x=ACCEPT_X, y=ACCEPT_Y)
        print("\n🧹 Очищаем куки и данные...")
        driver.delete_all_cookies()
        driver.execute_script("window.localStorage.clear();")  # Очищаем localStorage
        driver.execute_script("window.sessionStorage.clear();")  # Очищаем sessionStorage
        print("✅ Куки и данные очищены.")
        time.sleep(2)
    except WebDriverException as e:
        print(f"❌ Ошибка при очистке кук: {e}")

def setup_tabs():
    """Создает две вкладки для работы"""
    while len(driver.window_handles) < 2:
        driver.execute_script("window.open('about:blank', '_blank');")
    print("✅ Проверены вкладки, готовы к работе.")

def switch_to_tab(index):
    """Переключается на указанную вкладку, пересоздает вкладку при необходимости"""
    global driver
    try:
        # Если вкладка исчезла, создаем новую
        if index >= len(driver.window_handles):
            driver.execute_script("window.open('about:blank', '_blank');")
            print(f"✅ Вкладка {index + 1} была потеряна, создана новая.")
        driver.switch_to.window(driver.window_handles[index])
    except WebDriverException:
        print(f"❌ Ошибка переключения на вкладку {index + 1}. Попытка восстановления...")
        setup_tabs()
        driver.switch_to.window(driver.window_handles[index])

def login(username, password):
    """Чередует авторизацию между двумя вкладками"""
    global driver, tab_index

    try:
        print(f"🔑 Авторизация для {username} во вкладке {tab_index + 1}...")

        # Переключаемся на нужную вкладку (поочередно)
        switch_to_tab(tab_index)

        driver.get(LOGIN_URL)
        time.sleep(3)

        # ✅ Очищаем куки перед авторизацией
        clear_cookies()

        accept_cookies()

        if "conectare" in driver.current_url:
            print("🔐 Требуется авторизация, выполняем вход...")

            try:
                username_input = wait.until(EC.presence_of_element_located((By.ID, "username")))
                password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
                auth_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']")))

                username_input.send_keys(username)
                password_input.send_keys(password)
                auth_button.click()
                time.sleep(5)

                if driver.current_url != LOGIN_URL:
                    print("✅ Авторизация успешна!")
                    save_result(username, "True")
                else:
                    print(f"❌ {username} не смог авторизоваться. Записываем как False.")
                    save_result(username, "False")

            except NoSuchWindowException:
                print("❌ Ошибка: Окно браузера закрыто.")
                save_result(username, "False")

        # 🔄 Переключаемся на другую вкладку для следующего аккаунта
        tab_index = 1 - tab_index  # Переключаем между 0 и 1

    except InvalidSessionIdException:
        print("⚠️ Потеряна сессия браузера. Перезапускаем...")
        start_driver()
        login(username, password)  # Повторный вход

    except WebDriverException as e:
        print(f"❌ Ошибка при входе для {username}: {e}")
        save_result(username, "False")

# --- Основной запуск ---
start_driver()  # Запуск драйвера перед началом работы
setup_tabs()  # Создаем 2 вкладки

processed_accounts = get_processed_accounts()
accounts = get_accounts()

if not accounts:
    print("❌ В файле LogPass.txt нет аккаунтов для обработки!")
    sys.exit()

for USERNAME, PASSWORD in accounts:
    if stop_script:
        break

    if USERNAME in processed_accounts:
        print(f"⚠️ {USERNAME} уже записан в results.txt. Пропускаем...")
        continue

    login(USERNAME, PASSWORD)

print("\nЗакрываем браузер.")
driver.quit()

import requests
import pandas as pd
import os
import random
import time
import urllib.parse
import signal
import sys

API_KEYS_FILE = "api_keys.txt"
KEYWORDS_FILE = "keywords.txt"
LOG_FILE = "log.txt"
OUTPUT_FILE = "youtube_channels.csv"

RUSSIAN_WORDS = ["подписчиков", "канал", "видео", "просмотры", "нажмите", "подписка", "комментарии", "ютуб", "лучшие", "новости"]

def load_api_keys():
    if not os.path.exists(API_KEYS_FILE):
        print(f"Файл {API_KEYS_FILE} не найден!")
        sys.exit(1)
    with open(API_KEYS_FILE, "r", encoding="utf-8") as f:
        keys = [line.strip() for line in f.readlines() if line.strip()]
    if not keys:
        print("Файл с API-ключами пуст!")
        sys.exit(1)
    return keys

API_KEYS = load_api_keys()
current_key_index = 0
all_results = []

def switch_api_key():
    global current_key_index
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    print(f"Переключаемся на новый API-ключ ({current_key_index + 1}/{len(API_KEYS)})")

def signal_handler(sig, frame):
    print("\nПринудительная остановка. Сохранение данных...")
    save_results()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def safe_request(url, retries=3, delay=5):
    global current_key_index
    for attempt in range(retries * len(API_KEYS)):
        api_key = API_KEYS[current_key_index]
        request_url = f"{url}&key={api_key}"
        try:
            response = requests.get(request_url, timeout=10)
            if response.status_code in [400, 403]:
                print(f"Ошибка {response.status_code}: Переключаем API-ключ...")
                switch_api_key()
                continue
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Ошибка запроса: {e}. Попытка {attempt + 1}/{retries * len(API_KEYS)}")
            if (attempt + 1) % retries == 0:
                switch_api_key()
            time.sleep(delay)
    return None

def read_logged_keywords():
    if not os.path.exists(LOG_FILE):
        return set()
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def log_keyword(keyword):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(keyword + "\n")

def read_keywords():
    if not os.path.exists(KEYWORDS_FILE):
        print(f"Файл {KEYWORDS_FILE} не найден!")
        return []
    with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
        keywords = [line.strip() for line in f.readlines() if line.strip()]
    random.shuffle(keywords)
    return keywords

def search_channels(query, max_results=10):
    query = urllib.parse.quote_plus(query)
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=channel&maxResults={max_results}"
    data = safe_request(url)
    if not data:
        return []
    channels = []
    for item in data.get("items", []):
        channel_id = item["snippet"]["channelId"]
        title = item["snippet"]["title"]
        handle = item["snippet"].get("customUrl", "").replace("https://www.youtube.com/", "")
        description = item["snippet"].get("description", "").lower()

        if any(word in title.lower() for word in RUSSIAN_WORDS) or any(word in description for word in RUSSIAN_WORDS):
            print(f"Пропущен (русский контент): {title}")
            continue

        channels.append({"channel_id": channel_id, "title": title, "handle": handle})
    return channels

def get_channel_details(channel_ids, min_subs):
    if not channel_ids:
        return []
    ids = ",".join(channel_ids)
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics,brandingSettings&id={ids}"
    data = safe_request(url)
    if not data:
        return []
    channel_data = []
    for item in data.get("items", []):
        title = item["snippet"]["title"]
        handle = item["snippet"].get("customUrl", "").replace("https://www.youtube.com/", "")
        subscribers = int(item["statistics"].get("subscriberCount", 0))
        views = int(item["statistics"].get("viewCount", 0))
        videos = int(item["statistics"].get("videoCount", 0))
        country = item.get("brandingSettings", {}).get("channel", {}).get("country", "Неизвестно")
        creation_date = item["snippet"].get("publishedAt", "Неизвестно")[:10]

        if subscribers < min_subs:
            print(f"Пропущен (неподходящий канал): {title}")
            continue

        channel_data.append({
            "title": title,
            "handle": handle,
            "subscribers": f"{subscribers:,}",
            "views": f"{views:,}",
            "videos": videos,
            "registration_date": creation_date,
            "country": country
        })
    return channel_data

def save_results():
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv(OUTPUT_FILE, index=False, mode='a', header=not os.path.exists(OUTPUT_FILE))
        print(f"Данные сохранены в {OUTPUT_FILE}")
    else:
        print("Нет данных для сохранения")

def main():
    min_subs = int(input("Минимальное количество подписчиков (по умолчанию 10000): ") or 10000)
    max_results = int(input("Сколько каналов искать (по умолчанию 10): ") or 10)
    logged_keywords = read_logged_keywords()
    keywords = read_keywords()
    for keyword in keywords:
        if keyword in logged_keywords:
            print(f"Пропускаем {keyword}, так как он уже обработан.")
            continue
        print(f"Парсим каналы по запросу: {keyword}")
        channels = search_channels(keyword, max_results)
        channel_ids = [c["channel_id"] for c in channels]
        if not channel_ids:
            print(f"Каналы по запросу '{keyword}' не найдены!")
            continue
        details = get_channel_details(channel_ids, min_subs)
        all_results.extend(details)
        save_results()
        log_keyword(keyword)

if __name__ == "__main__":
    main()

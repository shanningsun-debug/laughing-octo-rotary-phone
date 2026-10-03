import os
import json
import requests
from bs4 import BeautifulSoup

# Шаг 1: Загружаем настройки каналов
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Шаг 2: Функция парсинга последних сообщений из Telegram-канала
def fetch_telegram_news(channel_name):
    url = f"https://t.me/s/{channel_name}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Ищем блоки сообщений в веб-версии Telegram
            messages = soup.find_all('div', class_='tgme_widget_message_text')
            
            # Собираем текст последних 5 постов
            latest_posts = [msg.get_text(separator=" ") for msg in messages[-5:]]
            return latest_posts
    except Exception as e:
        print(f"Ошибка при чтении канала {channel_name}: {e}")
    return []

# Шаг 3: Основная логика сборщика
def main():
    config = load_config()
    all_collected_news = []
    
    print("🤖 Запуск ИИ-агента по сбору новостей...")
    
    for channel in config['channels']:
        print(f"📡 Читаю канал: @{channel}...")
        posts = fetch_telegram_news(channel)
        all_collected_news.extend(posts)
        
    print(f"✅ Успешно собрано постов: {len(all_collected_news)}")
    print("\n--- ПРИМЕР СОБРАННОГО МАТЕРИАЛА ---")
    if all_collected_news:
        print(all_collected_news[0][:200] + "...") # выведем кусочек первого поста
    else:
        print("Пока нет новых постов.")

if __name__ == "__main__":
    main()

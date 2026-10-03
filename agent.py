import os
import json
import requests
from bs4 import BeautifulSoup

# Шаг 1: Загружаем настройки каналов
def load_config():
    with open('config.json', 'r', encoding='utf-8') as f:
        return json.load(f)

# Шаг 2: Функция парсинга последних сообщений из Telegram
def fetch_telegram_news(channel_name):
    url = f"https://t.me{channel_name}"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message_text')
            # Забираем последние 5 постов из каждого канала
            return [msg.get_text(separator=" ") for msg in messages[-5:]]
    except Exception as e:
        print(f"Ошибка при чтении канала {channel_name}: {e}")
    return []

# Шаг 3: Отправка собранного контента в ChatGPT API
def ask_chatgpt_to_summarize(raw_text):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Ошибка: Не найден OPENAI_API_KEY в переменных окружения!")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Формируем жесткое ТЗ для нейросети
    prompt = f"""
    Ты — профессиональный финансовый аналитик и главный редактор инвест-канала.
    Твоя задача — изучить массив сырого текста новостей за сегодня и составить ОДИН качественный, емкий, структурированный дайджест.
    
    Обязательно разбей текст строго по этим 5 блокам:
    1. **Геополитика** — главные мировые события, влияющие на рынки.
    2. **Экономика мира** — макроданные, отчеты, решения центробанков (ФРС, ЕЦБ и др.).
    3. **Россия** — состояние экономики РФ и корпоративные новости фондового рынка (Мосбиржа).
    4. **Драгметаллы и Биткоин** — динамика цен на золото, серебро и криптовалюту, важные триггеры.
    5. **Короткий итог для инвестора** — финальный вывод, фокус дня или краткое резюме.

    Пиши лаконично, убирай "воду", используй понятный язык инвесторов. Не придумывай факты, используй только данные из текста.
    
    Вот сырые новости для анализа:
    {raw_text}
    """

    data = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.3
    }

    print("🤖 Отправляю данные в ChatGPT для генерации дайджеста...")
    try:
        response = requests.post("https://https://proxyapi.ru", headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            print(f"❌ Ошибка API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Ошибка при запросе к OpenAI: {e}")
    return None

# Шаг 4: Основная логика
def main():
    config = load_config()
    all_collected_news = []
    
    print("🤖 Запуск ИИ-агента...")
    for channel in config['channels']:
        print(f"📡 Сбор новостей из: @{channel}...")
        posts = fetch_telegram_news(channel)
        all_collected_news.extend(posts)
        
    if not all_collected_news:
        print("❌ Новых новостей не найдено.")
        return

    # Объединяем все посты в один большой текст
    full_raw_text = "\n--- НОВАЯ ЗАПИСЬ ---\n".join(all_collected_news)
    
    # Передаем текст в ChatGPT
    final_digest = ask_chatgpt_to_summarize(full_raw_text)
    
    if final_digest:
        print("\n✨ ГОТОВЫЙ ДАЙДЖЕСТ ДЛЯ ПУБЛИКАЦИИ ✨\n")
        print(final_digest)

if __name__ == "__main__":
    main()

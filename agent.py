import os
import json
import requests
from bs4 import BeautifulSoup

def load_config():
    # Если файла настроек нет, используем встроенный список тем
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"keywords": ["russia economy", "fed rate", "stocks market", "bitcoin", "gold price"]}

def fetch_google_news(keyword):
    # Безопасный глобальный поиск новостей через Google RSS
    url = f"https://google.com{keyword}&hl=ru&gl=RU&ceid=RU:ru"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'xml')
            items = soup.find_all('item')
            results = [item.find('title').get_text() for item in items[:4] if item.find('title')]
            return results
    except Exception as e:
        print(f"Ошибка поиска Google по теме {keyword}: {e}")
    return []

def ask_chatgpt_to_summarize(raw_text):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ Ошибка: Не найден OPENAI_API_KEY в переменных окружения вашего компьютера!")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Ты — профессиональный финансовый аналитик и главный редактор инвест-канала.
    Твоя задача — изучить массив сырого текста мировых и российских новостей за сегодня и составить ОДИН качественный, емкий, структурированный дайджест НА РУССКОМ ЯЗЫКЕ.
    
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

    print("🤖 Отправляю данные в ChatGPT через ProxyAPI для генерации дайджеста...")
    try:
        response = requests.post("https://proxyapi.ru", headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['choices']['message']['content']
        else:
            print(f"❌ Ошибка API: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Ошибка при запросе: {e}")
    return None

def main():
    all_collected_news = []
    
    # Набор железобетонных латинских тем для стабильного поиска новостей
    safe_keywords = ["russia economy", "fed rate", "stocks market", "bitcoin", "gold price", "geopolitics markets"]
    
    print("🤖 Запуск ИИ-агента...")
    for keyword in safe_keywords:
        print(f"📡 Сбор новостей Google по теме: {keyword}...")
        news = fetch_google_news(keyword)
        all_collected_news.extend(news)
        
    if not all_collected_news:
        print("❌ Новых новостей в сети не найдено.")
        return

    full_raw_text = "\n--- НОВАЯ ЗАПИСЬ ---\n".join(all_collected_news)
    final_digest = ask_chatgpt_to_summarize(full_raw_text)
    
    if final_digest:
        print("\n✨ ГОТОВЫЙ ДАЙДЖЕСТ ДЛЯ ПУБЛИКАЦИИ ✨\n")
        print(final_digest)

if __name__ == "__main__":
    main()



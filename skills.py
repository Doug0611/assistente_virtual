import locale
from typing import Optional
from datetime import datetime
import wikipedia
import aiohttp
import json


class Skills:
    def current_time(self) -> str:
        return 'agora são ' + datetime.now().strftime('%H:%M')

    def current_date(self) -> str:
        return 'hoje é ' + datetime.now().strftime('%A, %d de %B de %Y')

    def quest(self, quest_term: str) -> str:
        try:
            wikipedia.set_lang(locale.getlocale()[0][:2])
            wikipedia.set_rate_limiting(rate_limit=True)
            return wikipedia.summary(title=quest_term, sentences=2)
        except wikipedia.exceptions.DisambiguationError:
            ...
        except wikipedia.exceptions.PageError:
            ...

    async def get_top_headlines(self, query: Optional[str] = '', page_size: Optional[int] = 5, lang: Optional[str] = 'pt') -> dict:
        with open('auth.json', encoding='utf-8') as auth:
            data_key = json.loads(auth.read())
        async with aiohttp.ClientSession() as session:
            API_KEY = data_key['news_api']['api_key']
            URL = '''https://newsapi.org/v2/top-headlines/?q={}&pageSize={}&language={}&apiKey={}'''.format(
                query,
                page_size,
                lang,
                API_KEY)
            async with session.get(URL) as response:
                return await response.json()

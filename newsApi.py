from dataclasses import dataclass
from typing import Optional
from random import randint
import aiohttp
import json
import asyncio


@dataclass
class NewsApi:
    lang: str = "pt"
    start_date: str = ""
    end_date: str= ""
    region: str = "br"
    page_size: int = 5

    def set_lang(self, lang: str) -> None:
        self.lang = lang

    def set_time_range(self, start: str, end: str) -> None:
        self.start = start
        self.end = end

    def set_region(self, region: str) -> None:
        self.region = region

    def get_page(self, page: int) -> None:
        self.page_size = page

    async def get_news(self, key: Optional[str] = "") -> dict:
        with open('auth.json', encoding='utf-8') as auth:
            data_key = json.loads(auth.read())

        URL = "https://newsapi.org/v2/everything?"
        API_KEY = data_key['news_api']['api_key']
        keywords = [
            'brasil',
            'mundo',
            'covid',
            'ciências e tecnolgias',
            'entreterimento',
            'esportes',
            'saúde',
            'principais notícias']

        query = f"q={key}" if key else f"q={keywords[randint(0, 7)]}"
        language = f"&language={self.lang}".lower()
        pageSize = f"&pageSize={self.page_size}"
        apiKey = f"&apiKey={API_KEY}"

        FULL_URL = URL + query + language + pageSize + apiKey

        if self.start_date and self.end_date:
            date_range = f"&from={self.start_date}&to={self.end_date}"
            FULL_URL = URL + query + date_range + language + pageSize + apiKey

        async with aiohttp.ClientSession() as session:
            async with session.get(FULL_URL) as response:
                return await response.json()

    def get_texts() -> list:
        ...


news = NewsApi()
loop = asyncio.get_event_loop()
api = loop.run_until_complete(news.get_news())


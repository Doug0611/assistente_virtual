from dataclasses import dataclass, field
from typing import Optional, List, Tuple
from random import randint
import aiohttp
import json
import asyncio


@dataclass
class NewsApi:
    lang: str = "pt"
    start_date: str = field(
        default_factory=str,
        repr=False
    )
    end_date: str = field(
        default_factory=str,
        repr=False
    )
    region: str = "br"
    page_size: int = field(
        default=5,
        repr=False
    )

    __URL_TOP_HEDLINES: str = "https://newsapi.org/v2/top-headlines?"
    __URL_TOP_EVERYTHING: str = "https://newsapi.org/v2/everything?"

    def set_lang(self, lang: str) -> None:
        if not isinstance(lang, str):
            raise TypeError("lang must be string")
        self.lang = lang

    def set_date_range(self, start: str, end: str) -> None:
        if not isinstance((start, end), str):
            raise TypeError("start_date and end_date must be string")
        self.start = start
        self.end = end

    def set_region(self, region: str) -> None:
        if not isinstance(region, str):
            raise TypeError("region must be string")
        self.region = region

    def get_page(self, page: int) -> None:
        if not isinstance(page, int):
            raise TypeError("page must be an integer")
        self.page_size = page

    def get_category_options(self) -> List[str]:
        return [
            "business",
            "entertainment",
            "general",
            "healths",
            "cience",
            "sports",
            "technology"]

    @staticmethod
    def __get_api_key(api_service: str) -> dict:
        with open('auth.json', encoding='utf-8') as auth:
            data_json = json.loads(auth.read())
            return data_json[api_service]

    async def get_news(self, news_category: Optional[str] = "general") -> None:
        if not isinstance(news_category, str):
            raise ValueError("news_category must be string")

        API_KEY = self.__get_api_key('news_api')
        category = f"category={news_category}"
        language = f"&language={self.lang}".lower()
        pageSize = f"&pageSize={self.page_size}"
        apiKey = f"&apiKey={API_KEY['key']}"
        country = f"&country={self.region}".lower()

        FULL_URL = self.__URL_TOP_HEDLINES + '{}{}{}{}{}'.format(
            category,
            language,
            pageSize,
            country,
            apiKey
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(FULL_URL) as response:
                return await response.json()

    def results(self) -> List[dict]:
        loop = asyncio.get_event_loop()
        resp = self.get_news()
        result = loop.run_until_complete(resp)
        return result['articles']

    def get_texts(self) -> List[str]:
        articles = self.results()
        headlines = [article['title'] for article in articles]
        return headlines

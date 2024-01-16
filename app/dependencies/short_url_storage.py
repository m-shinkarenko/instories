
from pydantic import HttpUrl
from app.metaclasses import SingletonMeta
from app.dependencies.url import UrlID


class ShortUrlStorage(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._data: dict[UrlID, HttpUrl] = {}

    def create(self, url_id: UrlID, long_url: HttpUrl) -> None:
        self._data[url_id] = long_url

    def get_long_url(self, url_id: UrlID) -> HttpUrl | None:
        return self._data.get(url_id)

    def delete(self, url_id: UrlID) -> None:
        self._data.pop(url_id, None)


async def get_short_url_storage() -> ShortUrlStorage:
    return ShortUrlStorage()

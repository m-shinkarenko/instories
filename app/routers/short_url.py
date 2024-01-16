from pydantic_core import Url
from app.dependencies.stats_storage import StatsStorage, get_stats_storage
from app.settings import settings
from pydantic import BaseModel, HttpUrl, validator
from app.dependencies.url import gen_short_url_id, url_to_url_id
from app.dependencies.short_url_storage import ShortUrlStorage, get_short_url_storage
from http import client as http
from fastapi import Depends
from fastapi import APIRouter

from app.utils import raise_err


router = APIRouter(
    prefix="/short-url",
)


class AppEpmtyResBody(BaseModel):
    pass


class CreateShortURLReqBody(BaseModel):
    long_url: HttpUrl


class CreateShortURLResBody(BaseModel):
    short_url: HttpUrl


@router.post("/")
async def create_short_url(
    body: CreateShortURLReqBody,
    short_url_storage: ShortUrlStorage = Depends(get_short_url_storage),
) -> CreateShortURLResBody:
    for _ in range(settings.num_attempts_gen_id):
        url_id = gen_short_url_id(settings.id_len)
        if not short_url_storage.get_long_url(url_id):
            short_url_storage.create(url_id, body.long_url)
            return CreateShortURLResBody(short_url=HttpUrl(str(settings.base_path) + url_id))

    raise_err(http.INTERNAL_SERVER_ERROR,
              "Something went wrong try again later")


class GetShortURLResBody(BaseModel):
    long_url: HttpUrl


@router.delete('/{short_url:path}')
def delete_short_url(
    short_url: HttpUrl,
    short_url_storage: ShortUrlStorage = Depends(get_short_url_storage),
) -> AppEpmtyResBody:
    url_id = url_to_url_id(short_url)
    short_url_storage.delete(url_id)
    return AppEpmtyResBody()


class UpdateShortURLReqBody(BaseModel):
    new_short_url: HttpUrl

    @validator("new_short_url")
    def check_new_short_url_domain(cls, v: HttpUrl) -> HttpUrl:
        if v.host != settings.base_path.host:
            raise ValueError(
                f"new_short_url must have a domain {settings.base_path.host}")
        return v


@router.put('/{short_url:path}')
def update_short_url(
    short_url: HttpUrl,
    body: UpdateShortURLReqBody,
    short_url_storage: ShortUrlStorage = Depends(get_short_url_storage),
) -> AppEpmtyResBody:
    old_url_id = url_to_url_id(short_url)
    new_url_id = url_to_url_id(body.new_short_url)

    long_url = short_url_storage.get_long_url(old_url_id)
    if long_url is None:
        raise_err(http.NOT_FOUND, "url not found")

    if short_url_storage.get_long_url(new_url_id):
        raise_err(http.CONFLICT, "new short url already exists")

    short_url_storage.create(new_url_id, long_url)
    short_url_storage.delete(old_url_id)
    return AppEpmtyResBody()


class GetShortURLStatsResBody(BaseModel):
    requested: int


@router.get('/{short_url:path}/rough-stats')
def get_short_url_rough_stats(
    short_url: HttpUrl,
    stats_storage: StatsStorage = Depends(dependency=get_stats_storage),
) -> GetShortURLStatsResBody:
    url_id = url_to_url_id(short_url)
    return GetShortURLStatsResBody(requested=stats_storage.get_rough(url_id))


@router.get('/{short_url:path}/accurate-stats')
def get_short_url_accurate_stats(
    short_url: HttpUrl,
    stats_storage: StatsStorage = Depends(dependency=get_stats_storage),
) -> GetShortURLStatsResBody:
    url_id = url_to_url_id(short_url)
    return GetShortURLStatsResBody(requested=stats_storage.get_accurate(url_id))


@router.get("/{short_url:path}")
def get_long_url(
        short_url: HttpUrl,
        short_url_storage: ShortUrlStorage = Depends(get_short_url_storage),
        stats_storage: StatsStorage = Depends(dependency=get_stats_storage),
) -> GetShortURLResBody:
    url_id = url_to_url_id(short_url)
    long_url = short_url_storage.get_long_url(url_id)

    if isinstance(long_url, Url):
        stats_storage.inc(url_id)
        return GetShortURLResBody(long_url=long_url)
    else:
        raise_err(http.NOT_FOUND,
                  "url not found")

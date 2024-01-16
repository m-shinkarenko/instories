import random
import string
from typing import Iterator, cast

from pydantic import HttpUrl

UrlID = str


def url_to_url_id(url: HttpUrl) -> UrlID:
    return UrlID(cast(str, url.path)[1:])


def gen_short_url_id(id_len: int) -> UrlID:
    rand_str: Iterator[str] = (
        random.choice(string.ascii_letters+string.digits)
        for _ in range(id_len)
    )
    return UrlID(''.join(rand_str))

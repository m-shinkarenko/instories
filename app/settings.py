
from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    base_path: HttpUrl = Field(default=HttpUrl("http://example.com/"))
    num_attempts_gen_id: int = Field(default=3)
    id_len: int = Field(default=8)


settings = Settings()

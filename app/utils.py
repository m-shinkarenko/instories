
from typing import NoReturn
from fastapi import HTTPException


def raise_err(status_code: int, details: str) -> NoReturn:
    raise HTTPException(
        status_code=status_code,
        detail=details,
    )

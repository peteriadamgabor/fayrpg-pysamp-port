from typing import Annotated

from fastapi import Header, HTTPException

from config import settings

async def get_token_header(x_api_token: Annotated[str, Header()]):
    if x_api_token != settings.API_KEY:
        raise HTTPException(status_code=400, detail="X-Token header invalid")

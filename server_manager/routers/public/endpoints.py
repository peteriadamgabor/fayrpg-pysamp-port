from http import HTTPStatus
from fastapi import APIRouter

router = APIRouter(
    prefix="/public",
    tags=["public"],
    responses={404: {"description": "Not found"}},
)


@router.get("/health")
async def health_check():
    return {"Status": "Ok"}

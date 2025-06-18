from fastapi import FastAPI, WebSocket
from fastapi import APIRouter

router = APIRouter(
    prefix="/internal",
    tags=["internal"],
    responses={404: {"description": "Not found"}},
)

@router.get("/health")
async def health_check():
    return {"Status": "Ok"}


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")

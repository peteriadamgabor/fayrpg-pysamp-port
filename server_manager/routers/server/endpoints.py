from threading import Timer
from fastapi import APIRouter, Depends
from dependencies import get_token_header
from .functions import check_server_running, restart_server_function, start_server, kill_server

router = APIRouter(
    prefix="/server",
    tags=["server"],
    dependencies=[Depends(get_token_header)],
    responses={404: {"description": "Not found"}},
)


@router.get("/staus")
async def server_status():
    return {"Status": check_server_running()}


@router.get("/restart/{time}")
async def server_restart(time: int):
    Timer(time, restart_server_function).start()
    return {"Status": "Server restart started successfully"}


@router.get("/start")
async def server_start():
    if check_server_running():
        return {"Status": "Server is already running"}
    else:
        start_server()
        return {"Status": "Server started successfully"}


@router.get("/stop/{time}")
async def server_start(time: int, ):
    if not check_server_running():
        return {"Status": "Server is not running"}

    else:
        Timer(time, kill_server).start()
        return {"Status": "Server shutdown started successfully"}

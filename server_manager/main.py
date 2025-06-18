import uvicorn
from fastapi import FastAPI
from routers import server, public

app = FastAPI()
app.include_router(server.endpoints.router)
app.include_router(public.endpoints.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=7999)

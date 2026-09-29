from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import uvicorn
from web.handlers import web_router
from api.router import api_router

app = FastAPI(title="SMR Catalog App")

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(web_router)
app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)
import api
import uvicorn
from core.config import setting
from fastapi import FastAPI

app = FastAPI()
app.include_router(api.router, prefix=setting.api.prefix)


if __name__ == "__main__":
    uvicorn.run("main:app", host=setting.run.host, port=setting.run.port, reload=True)

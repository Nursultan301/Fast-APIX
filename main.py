from contextlib import asynccontextmanager

import uvicorn

from fastapi import FastAPI

from core.congif import settings
from api_v1 import router as router_v1
from items_views import router as items_router
from users.views import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(router=router_v1, prefix=settings.api_v1_prefix)

app.include_router(items_router)
app.include_router(users_router)


@app.get("/")
def hello_index():
    return {"message": "Hello World"}


@app.get("/hello")
def hello(name):
    name = name.split().title()
    return {"message": f"Hello {name}"}


@app.get("/calc/add/")
def calc(a: int, b: int):
    return {"a": a, "b": b, "result": a + b}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)

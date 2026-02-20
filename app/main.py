from fastapi import FastAPI
from app.config import settings
from app.database import init_pool, close_connection_pool
from app.routers.get import router as router_get
from app.routers.upload import router as router_upload


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    docs_url="/api/docs",
)

@app.on_event("startup")
async def startup():
    await init_pool()

@app.on_event("shutdown")
async def shutdown():
    await close_connection_pool()

@app.get("/")
async def root():
    return {"message": "Добро пожаловать! ЗАГЛУШКА!!! ДОПИШУ ПОЗЖЕ!!!"}

app.include_router(router_get)

app.include_router(router_upload)
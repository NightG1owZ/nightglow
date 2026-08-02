from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import database
from app.exceptions import BusinessException, ErrorCode
from app.routers import health
from app.utils.session import init_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    await init_redis()
    print(f"mysql & redis connected: {settings.database_url}, {settings.redis_url}")
    yield

    await database.disconnect()
    await close_redis()
    print("application closed")

app = FastAPI(
    title="BLOG",
    description="Blog",
    version="0.0.1",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(BusinessException)
async def business_exception_handler(request: Request, exc: BusinessException):
    return JSONResponse(
        status_code=200,
        content={
            "code": ErrorCode.SYSTEM_ERROR.code,
            "data": None,
            "message": f"System Error: {str(exc)}",
        }
    )

app.include_router(health.router, prefix="/health", tags=["Health"])

@app.get("/")
async def root():
    return {
        "message": "Hello My Blog",
        "version": "0.0.1",
        "docs": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True
    )

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import database
from app.exceptions import BusinessException, ErrorCode
from app.routers import (
    health, user, category, tag, article, article_tag,
    article_like, article_view, comment, file, config, operation_log,
)
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
    code = exc.code.code if hasattr(exc.code, "code") else exc.code
    message = exc.message or (exc.code.message if hasattr(exc.code, "message") else "error")
    return JSONResponse(
        status_code=200,
        content={"code": code, "data": None, "message": message}
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=200,
        content={"code": ErrorCode.PARAMS_ERROR.code, "data": None, "message": "请求参数错误"}
    )


app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(user.router)
app.include_router(category.router)
app.include_router(tag.router)
app.include_router(article.router)
app.include_router(article_tag.router)
app.include_router(article_like.router)
app.include_router(article_view.router)
app.include_router(comment.router)
app.include_router(file.router)
app.include_router(config.router)
app.include_router(operation_log.router)

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

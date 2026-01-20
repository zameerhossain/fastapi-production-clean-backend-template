from typing import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from mangum import Mangum

from src.middleware import Middleware
from src.routers import routers

app = FastAPI(version="1.0.0", title="FastAPI", docs_url="/docs", redoc_url="/redoc")


# TODO add middleware


# Wrap responses only for /api routes
@app.middleware("http")
async def api_response_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    path: str = request.scope["path"]

    if path.startswith("/api"):
        return await Middleware.wrap_response(request, call_next)

    return await call_next(request)


# Global exception handler
@app.exception_handler(Exception)
async def api_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return await Middleware.error_handler(request, exc)


app.include_router(routers)

handler = Mangum(app)

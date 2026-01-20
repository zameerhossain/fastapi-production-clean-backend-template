import json
from typing import Any, Awaitable, Callable, Optional

from fastapi import Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel


class APIResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict, excluding `error` if success."""
        d = super().model_dump(exclude_none=True)
        if d.get("success") and "error" in d:
            d.pop("error")
        return d


def success_response(data: Any = None, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        content=jsonable_encoder(APIResponse(success=True, data=data).to_dict()),
        status_code=status_code,
    )


def error_response(error: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(
        content=jsonable_encoder(APIResponse(success=False, error=error).to_dict()),
        status_code=status_code,
    )


async def wrap_response_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    response: Response = await call_next(request)

    # If already wrapped response, return as is
    if isinstance(response, JSONResponse):
        return response

    # Skip non-JSON responses (file, stream, html, etc)
    content_type = response.headers.get("content-type", "")
    if "application/json" not in content_type:
        return response

    # Safely read body
    body_data: Any = None
    if hasattr(response, "body_iterator"):
        body_bytes = b""
        async for chunk in response.body_iterator:
            body_bytes += chunk
        try:
            body_text = body_bytes.decode()
            body_data = jsonable_encoder(json.loads(body_text))
        except Exception:
            body_data = body_bytes.decode()

    return success_response(
        data=body_data,
        status_code=getattr(response, "status_code", 200),
    )

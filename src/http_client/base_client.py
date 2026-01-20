from typing import Optional

from aiohttp import ClientTimeout, FormData
from aiohttp_retry import ExponentialRetry, RetryClient


class HTTPClientError(Exception):
    """Custom exception for HTTP client errors."""


class HTTPClient:
    def __init__(
        self,
        base_url: str,
        headers: Optional[dict] = None,
        timeout: int = 30,
        retries: int = 3,
    ):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.timeout = ClientTimeout(total=timeout)
        self.retry_options = ExponentialRetry(attempts=retries)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict | None = None,
        json_body: dict | None = None,
        data: dict | FormData | None = None,
        headers: dict | None = None,
    ):
        url = f"{self.base_url}/{path.lstrip('/')}"
        merged_headers = {**self.headers, **(headers or {})}

        async with RetryClient(
            timeout=self.timeout,
            retry_options=self.retry_options,
            raise_for_status=False,
        ) as session:
            async with session.request(
                method=method,
                url=url,
                params=params,
                json=json_body,
                data=data,
                headers=merged_headers,
            ) as response:

                if response.status >= 400:
                    text = await response.text()
                    raise HTTPClientError(
                        f"{method} {url} failed with status {response.status}: {text}"
                    )

                content_type = response.headers.get("Content-Type", "")

                if "application/json" in content_type:
                    return await response.json()

                return await response.text()

    # ---------- Public Methods ----------

    async def get(
        self, path: str, params: dict | None = None, headers: dict | None = None
    ):
        return await self._request("GET", path, params=params, headers=headers)

    async def post(
        self,
        path: str,
        *,
        json: dict | None = None,
        data: dict | None = None,
        headers: dict | None = None,
    ):
        return await self._request(
            "POST",
            path,
            json_body=json,
            data=data,
            headers=headers,
        )

    async def post_form(
        self,
        path: str,
        *,
        form_data: dict,
        headers: dict | None = None,
    ):
        """
        POST request with multipart/form-data.
        `form_data` should be a dictionary of key-values.
        """
        form = FormData()
        for key, value in form_data.items():
            form.add_field(key, str(value))

        return await self._request(
            "POST",
            path,
            data=form,
            headers=headers,
        )

    async def put(
        self, path: str, json: dict | None = None, headers: dict | None = None
    ):
        return await self._request("PUT", path, json_body=json, headers=headers)

    async def patch(
        self, path: str, json: dict | None = None, headers: dict | None = None
    ):
        return await self._request("PATCH", path, json_body=json, headers=headers)

    async def delete(self, path: str, headers: dict | None = None):
        return await self._request("DELETE", path, headers=headers)

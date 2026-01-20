from src.http_client.base_client import HTTPClient


class DemoClient:
    def __init__(self):
        self.client = HTTPClient(
            base_url="http://localhost:8080",
            headers={"Authorization": "Bearer token"},
        )

    async def create_user(self) -> dict:
        try:
            result = await self.client.post("/users", data={"name": ""})
            return result
        except Exception as e:
            # TODO need to replace with logger
            print(f"Error occurred demoClient:create_user: {e}")

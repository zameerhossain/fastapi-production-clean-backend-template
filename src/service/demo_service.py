from typing import Optional

from fastapi import Request

from src.config import ApiSettings, api_settings
from src.database.database import Base as BaseModel
from src.repository.demo_repository import DemoRepository
from src.schemas.demo_schema import DemoUserCreate, DemoUserRecord
from src.service.base_service import BaseService


class DemoService(BaseService):

    def __init__(
        self, settings: ApiSettings = api_settings, auth_token: Optional[str] = None
    ) -> None:
        super().__init__(settings=settings)
        self.auth_token = auth_token
        self.repository = DemoRepository(settings)

    @classmethod
    def get_instance(cls, request: Request) -> "DemoService":
        auth_token = request.headers.get("Authorization", None)
        return cls(settings=api_settings, auth_token=auth_token)

    @classmethod
    def model_to_details(cls, model: BaseModel) -> DemoUserRecord:
        return DemoUserRecord(**model.__dict__)

    async def create_demo_user(self, payload: DemoUserCreate) -> DemoUserRecord:
        user_model = await self.repository.create_demo_user(payload)
        return self.model_to_details(user_model)

    async def get_demo_user(self, user_id: int) -> DemoUserRecord:
        user_model = await self.repository.get_demo_user(user_id)
        return self.model_to_details(user_model)

    async def demo_user_all(self) -> list[DemoUserRecord]:
        models = await self.repository.demo_user_all()
        return list(map(self.model_to_details, models))

    async def update_demo_user(self, user_id: int) -> None:
        pass

    async def patch_demo_user(self, user_id: int) -> None:
        pass

    async def delete_demo_user(self, user_id: int) -> dict[str, bool]:
        result = await self.repository.delete_demo_user(user_id)
        return {"deleted": result}

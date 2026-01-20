from typing import Optional

from sqlalchemy import delete, select

from src.config import ApiSettings, api_settings
from src.database.database import Database
from src.models.demo_model import DemoUserModel
from src.schemas.demo_schema import DemoUserCreate


class DemoRepository:
    def __init__(self, settings: ApiSettings = api_settings):
        self.connection = Database(settings.demo_database_url).get_async

    async def create_demo_user(self, payload: DemoUserCreate) -> DemoUserModel:
        demo_user_model = DemoUserModel(**payload.model_dump())
        async with self.connection() as session:
            session.add(demo_user_model)
            await session.commit()
            await session.refresh(demo_user_model)
            return demo_user_model

    async def get_demo_user(self, user_id: int) -> Optional[DemoUserModel]:
        async with self.connection() as session:
            query = select(DemoUserModel).where(DemoUserModel.id == user_id)
            result = await session.execute(query)
            return result.scalar_one_or_none()

    async def demo_user_all(self) -> list[DemoUserModel]:
        async with self.connection() as session:
            query = select(DemoUserModel).order_by(DemoUserModel.id)
            result = await session.execute(query)
            return result.scalars().all()

    async def update_demo_user(self, user_id: int):
        async with self.connection():
            pass

    async def patch_demo_user(self, user_id: int):
        pass

    async def delete_demo_user(self, user_id: int) -> bool:
        async with self.connection() as session:
            stmt = delete(DemoUserModel).where(DemoUserModel.id == user_id)
            result = await session.execute(stmt)
            await session.commit()
            return bool(result.rowcount > 0)

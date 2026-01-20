from http import HTTPStatus

from fastapi import APIRouter, Request
from fastapi_utils.cbv import cbv

from src.controller.base_controller import BaseController
from src.schemas.demo_schema import DemoUserCreate, DemoUserRecord
from src.service.demo_service import DemoService

router = APIRouter()


@cbv(router)
class DemoController(BaseController):

    # Place static routes at the top for predictable routing order
    @router.get(
        "/user/all", status_code=HTTPStatus.OK, response_model=list[DemoUserRecord]
    )
    async def get_demo_user_all(self, request: Request) -> list[DemoUserRecord]:
        service = DemoService.get_instance(request)
        return await service.demo_user_all()

    @router.post("/user", status_code=HTTPStatus.CREATED, response_model=DemoUserRecord)
    async def create_demo_user(
        self, request: Request, payload: DemoUserCreate
    ) -> DemoUserRecord:
        service = DemoService.get_instance(request)
        return await service.create_demo_user(payload)

    @router.get(
        "/user/{user_id}", status_code=HTTPStatus.OK, response_model=DemoUserRecord
    )
    async def get_demo_user(self, request: Request, user_id: int) -> DemoUserRecord:
        service = DemoService.get_instance(request)
        return await service.get_demo_user(user_id)

    @router.put("/user/{user_id}")
    async def update_demo_user(self, request: Request, user_id: int) -> None:
        service = DemoService.get_instance(request)
        return await service.update_demo_user(user_id)

    @router.patch("/user/{user_id}")
    async def patch_demo_user(self, request: Request, user_id: int) -> None:
        service = DemoService.get_instance(request)
        return await service.patch_demo_user(user_id)

    @router.delete("/user/{user_id}", status_code=HTTPStatus.OK)
    async def delete_demo_user(self, request: Request, user_id: int) -> dict[str, bool]:
        service = DemoService.get_instance(request)
        return await service.delete_demo_user(user_id)

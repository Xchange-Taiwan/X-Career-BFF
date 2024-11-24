import logging as log

import httpx
from fastapi import APIRouter, Path
from pydantic import UUID4

from src.config.constant import MICRO_SERVICE_URL
from src.domain.file.model.file_info_model import FileInfoVO
from src.domain.file.service.file_service import FileService
from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from src.router.res.response import idempotent_response, res_success

log.basicConfig(filemode='w', level=log.INFO)

router = APIRouter(
    prefix='/file',
    tags=['file'],
    responses={404: {'description': 'Not found'}},
)
_file_service = FileService(
    AsyncServiceApiAdapter(),
    None
)


# Resquest obj is used to access router path
@router.get('/{user_id}/{file_id}',
            responses=idempotent_response('get_file_info_by_id', FileInfoVO))
async def get_file_info_by_id(
        user_id: int = Path(...),
        file_id: str = Path(...),
):
    res: FileInfoVO = await _file_service.get_file_by_id(user_id, file_id)
    return res_success(data=res.json())

import json
import logging as log
from typing import List, Optional

import httpx
from fastapi import APIRouter, Path
from fastapi.params import Body
from pydantic import UUID4

from src.app.template.service_response import ServiceApiResponse
from src.config.constant import MICRO_SERVICE_URL
from src.domain.file.model.file_info_model import FileInfoVO, FileInfoListVO, FileInfoDTO
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


@router.get('/{user_id}',
            responses=idempotent_response('get_file_info_by_user_id', FileInfoListVO))
async def get_file_info_by_user_id(
        user_id: int = Path(...)):
    res: FileInfoListVO = await _file_service.get_file_info_by_user_id(user_id)
    return res_success(data=res.json())


@router.post('/',
             responses=idempotent_response('create_file_info', FileInfoVO))
async def create_file_info(
        body: FileInfoDTO = Body(...)):
    res: FileInfoVO = await _file_service.create_file_info(body)
    return res_success(data=res.json())

@router.put('/{user_id}',
             responses=idempotent_response('update_file_info', FileInfoVO))
async def update_file_info(
        user_id: int = Path(...),
        body: FileInfoDTO = Body(...)):
    res: FileInfoVO = await _file_service.update_file_info(user_id, body)
    return res_success(data=res.json())

@router.delete('/{user_id}/{file_id}',
             responses=idempotent_response('delete_file_info', bool
                                           ))
async def delete_file_info(
        user_id: int = Path(...),
        file_id: str = Path(...)):
    res: bool = await _file_service.delete_file_info(user_id, file_id)
    return res_success(data=res)

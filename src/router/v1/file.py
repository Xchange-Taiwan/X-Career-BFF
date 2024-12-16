import logging as log

from fastapi import APIRouter, Path
from fastapi.params import Body

from src.domain.file.model.file_info_model import FileInfoVO, FileInfoListVO, FileInfoDTO
from src.domain.file.service.file_service import file_service_singleton
from src.router.res.response import idempotent_response, res_success

log.basicConfig(filemode='w', level=log.INFO)

router = APIRouter(
    prefix='/file',
    tags=['file'],
    responses={404: {'description': 'Not found'}},
)


# Resquest obj is used to access router path
@router.get('/{user_id}/{file_id}',
            responses=idempotent_response('get_file_info_by_id', FileInfoVO))
async def get_file_info_by_id(
        user_id: int = Path(...),
        file_id: str = Path(...),
):
    res: FileInfoVO = await file_service_singleton.get_file_by_id(user_id, file_id)
    return res_success(data=res.json())


@router.get('/{user_id}',
            responses=idempotent_response('get_file_info_by_user_id', FileInfoListVO))
async def get_file_info_by_user_id(
        user_id: int = Path(...)):
    res: FileInfoListVO = await file_service_singleton.get_file_info_by_user_id(user_id)
    return res_success(data=res.json())


@router.post('/',
             responses=idempotent_response('create_file_info', FileInfoVO))
async def create_file_info(
        body: FileInfoDTO = Body(...)):
    res: FileInfoVO = await file_service_singleton.create_file_info(body)
    return res_success(data=res.json())


@router.put('/{user_id}',
            responses=idempotent_response('update_file_info', FileInfoVO))
async def update_file_info(
        user_id: int = Path(...),
        body: FileInfoDTO = Body(...)):
    res: FileInfoVO = await file_service_singleton.update_file_info(user_id, body)
    return res_success(data=res.json())


@router.delete('/{user_id}/{file_id}',
               responses=idempotent_response('delete_file_info', bool
                                             ))
async def delete_file_info(
        user_id: int = Path(...),
        file_id: str = Path(...)):
    res: bool = await file_service_singleton.delete_file_info(user_id, file_id)
    return res_success(data=res)

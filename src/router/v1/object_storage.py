from typing import List

import boto3
from fastapi import File, UploadFile, APIRouter

from src.domain.file.model.file_info_model import FileInfoVO, FileInfoListVO
from src.domain.file.service.file_service import file_service_singleton
from src.infra.storage.global_object_storage import GlobalObjectStorage
from src.router.res.response import idempotent_response, res_success

_s3 = boto3.resource('s3')
_obj_store = GlobalObjectStorage(_s3, file_service_singleton)

router = APIRouter(
    prefix='/storage',
    tags=['storage'],
    responses={404: {'description': 'Not found'}},
)


@router.post('/', responses=idempotent_response('upload_file', FileInfoListVO))
async def upload(file: UploadFile = File(...), user_id: int = -1):
    res: FileInfoListVO = await _obj_store.upload_avatar(file, user_id)
    return res_success(data=res.json())

@router.delete('/', responses=idempotent_response('delete_file', bool))
async def delete(user_id: int = -1, file_name: str = ''):
    res: bool = await _obj_store.delete_file(user_id, file_name)
    return res_success(data=res)

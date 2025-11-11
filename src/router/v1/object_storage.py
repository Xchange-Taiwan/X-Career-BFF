import boto3
from fastapi import File, UploadFile, APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends

from src.app._di.injection import _file_service
from src.config.exception import ForbiddenException
from src.domain.file.model.file_info_model import FileInfoListVO
from src.infra.storage.global_object_storage import GlobalObjectStorage
from src.router.res.response import idempotent_response, res_success, post_success

_s3 = boto3.resource('s3')
_obj_store = GlobalObjectStorage(_s3, _file_service)

router = APIRouter(
    prefix='/storage',
    tags=['storage'],
    responses={404: {'description': 'Not found'}},
)


def validate_image(file: UploadFile = File(...)):
    # 檢查 content_type 是否以 "image/" 開頭
    if not file.content_type.startswith("image/"):
        raise ForbiddenException(msg="Only image files are allowed")
    return file


@router.post('/', responses=idempotent_response('upload_avatar', FileInfoListVO), status_code=201)
async def upload_avatar(user_id: int, file: UploadFile = Depends(validate_image)):
    # 驗證 user_id 是否有效
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user_id. Must be a positive integer.")
    
    res: FileInfoListVO = await _obj_store.upload_avatar(file, user_id)
    return post_success(data=jsonable_encoder(res))


@router.delete('/avatar', responses=idempotent_response('delete_avatar', bool))
async def delete_avatar(user_id: int):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user_id. Must be a positive integer.")
    
    res: bool = await _obj_store.delete_avatar(user_id)
    return res_success(data=jsonable_encoder(res))


# this endpoint is available for deleting any file
@router.delete('/', responses=idempotent_response('delete_file', bool))
async def delete_file(user_id: int, file_name: str):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user_id. Must be a positive integer.")
    if not file_name.strip():
        raise HTTPException(status_code=400, detail="file_name is required.")
    
    res: bool = await _obj_store.delete_file(user_id, file_name)
    return res_success(data=jsonable_encoder(res))


@router.get('/size', responses=idempotent_response('get_bucket_size', FileInfoListVO))
async def get_bucket_size(user_id: int):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="Invalid user_id. Must be a positive integer.")
    
    res: int = _obj_store.get_user_storage_size(user_id)
    return res_success(data=jsonable_encoder(res))

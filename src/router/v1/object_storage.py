import boto3
from fastapi import File, UploadFile, APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends

from src.app._di.injection import _file_service
from src.config.exception import ForbiddenException
from src.domain.file.model.file_info_model import FileInfoListVO
from src.infra.storage.global_object_storage import GlobalObjectStorage
from src.router.res.response import idempotent_response, res_success

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


@router.post('/', responses=idempotent_response('upload_avatar', FileInfoListVO))
async def upload_avatar(file: UploadFile = Depends(validate_image), user_id: int = -1):
    res: FileInfoListVO = await _obj_store.upload_avatar(file, user_id)
    return res_success(data=jsonable_encoder(res))


@router.delete('/avatar', responses=idempotent_response('delete_avatar', bool))
async def delete_avatar(user_id: int = -1):
    res: bool = await _obj_store.delete_avatar(user_id)
    return res_success(data=jsonable_encoder(res))


# this endpoint is available for deleting any file
@router.delete('/', responses=idempotent_response('delete_file', bool))
async def delete_file(user_id: int = -1, file_name: str = ''):
    res: bool = await _obj_store.delete_file(user_id, file_name)
    return res_success(data=jsonable_encoder(res))


@router.get('/size', responses=idempotent_response('get_bucket_size', FileInfoListVO))
async def get_bucket_size(user_id: int = -1):
    res: int = _obj_store.get_user_storage_size(user_id)
    return res_success(data=jsonable_encoder(res))

import boto3
from fastapi import File, UploadFile, APIRouter

from src.domain.file.model.file_info_model import FileInfoVO
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


@router.post('/', responses=idempotent_response('upload_file', FileInfoVO))
async def upload(file: UploadFile = File(...), user_id: int = -1):
    res: FileInfoVO = await _obj_store.upload(file, user_id)
    return res_success(data=res.json())

from typing import Optional, Any, Dict, Generic, TypeVar

from fastapi import status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    code: str = '0'
    msg: str = 'ok'
    data: Optional[T] = None


def idempotent_response(route: str, model: Any) -> Dict:
    return {
        200: {
            'model': ApiResponse[model]
        }
    }


def post_response(route: str, model: Any) -> Dict:
    return {
        201: {
            'model': ApiResponse[model]
        }
    }


def post_success(data=None, msg='ok', code='0'):
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            'code': code,
            'msg': msg,
            'data': data,
        })


def res_success(data=None, msg='ok', code='0'):
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'code': code,
            'msg': msg,
            'data': data,
        })


def res_err_format(data=None, msg='error', code='1'):
    return {
        'code': code,
        'msg': msg,
        'data': data,
    }


class ResponseVO(BaseModel):
    code: str = '0'
    msg: str = 'ok'
    data: Optional[Any] = None


'''[delete-Any]'''


class DeleteVO(ResponseVO):
    data: Optional[bool] = None

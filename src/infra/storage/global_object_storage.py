import io
import json
from datetime import datetime

from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from fastapi import UploadFile, File, HTTPException

from ...config.conf import XC_BUCKET
from ...config.exception import ServerException, NotFoundException

import logging as log

from src.domain.file.model.file_info_model import FileInfoDTO
from ...domain.file.service.file_service import FileService

log.basicConfig(filemode='w', level=log.INFO)


class GlobalObjectStorage:
    def __init__(self, s3, file_service: FileService):
        self.s3 = s3
        self.file_service = file_service
        self.__cls_name = self.__class__.__name__

    def init(self, bucket, version):
        file = None
        key = None
        try:
            file = json.dumps({'version': version})
            key = ''.join([str(bucket), '/email_info.json'])
            obj = self.s3.Object(XC_BUCKET, key)
            obj.put(Body=file)

            return version

        except Exception as e:
            log.error(f'{self.__cls_name}.init [init file error]\
                bucket:%s, version:%s, file:%s, key:%s, err:%s', 
                bucket, version, file, key, e.__str__())
            raise ServerException(msg='init file fail')


    def update(self, bucket, version, newdata):
        data = None
        result = None
        key = None
        try:
            data = self.find(bucket)
            if data is None:
                raise NotFoundException(msg=f'file:{bucket} not found')
            
            if 'version' in data and data['version'] != version:
                raise NotFoundException(msg='no version there OR invalid version')

            data.update(newdata)
            result = json.dumps(data)

            key = ''.join([str(bucket), '/email_info.json'])
            obj = self.s3.Object(XC_BUCKET, key)
            obj.put(Body=result)
            return result
        
        except NotFoundException as e:
            log.error(f'{self.__cls_name}.update [no version found] \
                bucket:%s, version:%s, newdata:%s, data:%s, result:%s, key:%s, err:%s', 
                bucket, version, newdata, data, result, key, e.__str__())
            raise NotFoundException(msg=e.msg)

        except Exception as e:
            log.error(f'{self.__cls_name}.update [update file error] \
                bucket:%s, version:%s, newdata:%s, data:%s, result:%s, key:%s, err:%s', 
                bucket, version, newdata, data, result, key, e.__str__())
            raise ServerException(msg='update file fail')


    def delete(self, bucket):
        key = None
        result = False
        try:
            key = ''.join([str(bucket), '/email_info.json'])
            self.s3.Object(XC_BUCKET, key).delete()
            result = True
            return result

        except Exception as e:
            log.error(f'{self.__cls_name}.delete [delete file error] \
                bucket:%s, key:%s, result:%s, err:%s', 
                bucket, key, result, e.__str__())
            raise ServerException(msg='delete file fail')


    '''
        return {
            'email': 'abc@gmail.com',
            'region': 'jp',
        }, None
    '''

    def find(self, bucket):
        key = None
        result = None
        try:
            key = ''.join([str(bucket), '/email_info.json'])
            obj = self.s3.Object(XC_BUCKET, key)

            file_stream = io.BytesIO()
            obj.download_fileobj(file_stream)
            file_stream.seek(0)
            string = file_stream.read().decode('utf-8')
            result = json.loads(string)
            
            return result
        
        except ClientError as e:
            # file does not exist
            if e.response['Error']['Code'] == '404':
                return None
            else:
                log.error(f'{self.__cls_name}.find [req error] \
                    bucket:%s, key:%s, result:%s, err:%s', 
                    bucket, key, result, e.__str__())
                raise ServerException(msg='req error of find file')

        except Exception as e:
            err = e.__str__()
            log.error(f'{self.__cls_name}.find [find file error] \
                bucket:%s, key:%s, result:%s, err:%s', 
                bucket, key, result, err)
            raise ServerException(msg='find file fail')

    async def upload(self, file: UploadFile = File(...)) -> FileInfoDTO:
        try:
            # Read file contents
            file_content = await file.read()

            # Upload file to S3
            self.s3.Bucket(XC_BUCKET).put_object(
                Key=file.filename,
                Body=file_content,
                ContentType=file.content_type
            )
            file_dto = FileInfoDTO(
                file_name=file.filename,
                file_size=len(file_content),
                content_type=file.content_type,
                create_time=datetime.now(),
                update_time=datetime.now()
            )

            # call service in x career user to save the file info
            # Return file info
            return file_dto

        except (NoCredentialsError, PartialCredentialsError) as e:
            raise HTTPException(status_code=400, detail="AWS credentials not found or incomplete")
        except Exception as e:
            raise HTTPException(status_code=500, detail="An error occurred during file upload")
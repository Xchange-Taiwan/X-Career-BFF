import io
import json
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError

from ...config.conf import XC_BUCKET
from ...config.exception import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class GlobalObjectStorage:
    def __init__(self, s3):
        self.s3 = s3
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


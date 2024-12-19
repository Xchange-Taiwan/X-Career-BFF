import asyncio
import io
import json
import logging as log

from PIL import Image
from botocore.exceptions import NoCredentialsError, PartialCredentialsError, ClientError
from fastapi import UploadFile, File, HTTPException

from src.domain.file.model.file_info_model import FileInfoDTO, FileInfoListVO
from ...config.conf import XC_BUCKET, LOCAL_REGION, MAX_STORAGE_SIZE, MAX_WIDTH, MAX_HEIGHT
from ...config.exception import ServerException, NotFoundException
from ...domain.file.service.file_service import FileService
from ...domain.user.model.user_model import ProfileVO, ProfileDTO
from ...domain.user.service import user_service
from ...domain.user.service.user_service import user_service

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

    async def upload_avatar(self, file: UploadFile = File(...), user_id: int = -1) -> FileInfoListVO:
        try:
            # Read file contents
            avatar = await file.read()
            content_type = file.content_type
            file_type = file.content_type[6:]
            avatar_name = f'avatar.{file_type}'
            avatar_key = self.__get_obj_key(avatar_name, user_id)
            minor_avatar = self.__get_resized_obj(avatar, file_type)
            minor_avatar_name = f'minor_avatar.{file_type}'
            minor_avatar_key = self.__get_obj_key(minor_avatar_name, user_id)

            if self.get_user_storage_size(user_id) + len(avatar)+len(minor_avatar) > MAX_STORAGE_SIZE:
                raise HTTPException(status_code=400, detail="File size too large")

            avatar_dto = \
                await self.__upload_avatar_and_info(avatar,
                                                    avatar_key,
                                                    avatar_name,
                                                    content_type,
                                                    user_id)
            minor_avatar_dto = \
                await self.__upload_avatar_and_info(minor_avatar,
                                                    minor_avatar_key,
                                                    minor_avatar_name,
                                                    content_type,
                                                    user_id)

            res = await asyncio.gather(avatar_dto, minor_avatar_dto)
            # Return file info
            res = list(res)
            res.sort(key=lambda x: x.file_size)
            return FileInfoListVO(file_info_vo_list=res)

        except (NoCredentialsError, PartialCredentialsError) as e:
            raise HTTPException(status_code=400, detail="AWS credentials not found or incomplete")
        except Exception as e:
            raise HTTPException(status_code=500, detail="An error occurred during file upload_avatar")

    async def delete_file(self, user_id: int, file_name: str) -> bool:
        try:
            self.s3.Object(XC_BUCKET, self.__get_obj_key(file_name, user_id)).delete()
            res = await self.file_service.delete_file_info(user_id, file_name)
            if not res:
                raise NotFoundException(msg=f'file:{file_name} not found in db')
            return True
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise HTTPException(status_code=400, detail="AWS credentials not found or incomplete")
        except NotFoundException as e:
            raise HTTPException(status_code=404, detail=e.msg)
        except Exception as e:
            print(e)
            raise HTTPException(status_code=500, detail="An error occurred during file delete")

    async def delete_avatar(self, user_id: int) -> bool:
        try:
            profile_vo: ProfileVO = await user_service.get_user_profile(user_id)
            avatar_name: str = profile_vo.avatar.split('/')[-1]
            minor_avatar_name: str = 'minor_' + avatar_name
            delete_tasks = [
                self.delete_file(user_id, avatar_name),
                self.delete_file(user_id, minor_avatar_name)
            ]
            await asyncio.gather(*delete_tasks)

            profile_dto = ProfileDTO.from_vo(profile_vo)
            profile_dto.avatar = ''
            await user_service.upsert_user_profile(user_id, profile_dto)
            return True
        except (NoCredentialsError, PartialCredentialsError) as e:
            raise HTTPException(status_code=400, detail="AWS credentials not found or incomplete")
        except Exception as e:
            raise HTTPException(status_code=500, detail="An error occurred during file delete")

    async def __upload_avatar_and_info(self, avatar: bytes, avatar_key: str, file_name: str, content_type: str,
                                       user_id: int):
        # Upload file to S3
        self.s3.Bucket(XC_BUCKET).put_object(
            Key=avatar_key,
            Body=avatar,
            ContentType=content_type
        )
        avatar_url: str = self.__get_obj_url(file_name, user_id, LOCAL_REGION)
        file_dto = FileInfoDTO(
            file_name=file_name,
            file_size=len(avatar),
            content_type=content_type,
            create_user_id=user_id,
            url=avatar_url
        )
        avatar_dto = self.file_service.create_file_info(file_dto)
        return avatar_dto

    def __get_obj_key(self, file_name: str, user_id: int) -> str:
        return 'files/' + str(user_id) + '/' + file_name

    def __get_obj_url(self, file_name: str, user_id: int, region: str) -> str:
        return f'https://{XC_BUCKET}.s3.{region}.amazonaws.com/{self.__get_obj_key(file_name, user_id)}'

    def __get_resized_obj(self, content: bytes, content_type: str = 'jpeg') -> bytes:
        image = Image.open(io.BytesIO(content))

        # Resize the image to the specified dimensions
        width, height = image.size
        if width > MAX_WIDTH or height > MAX_HEIGHT:
            new_width, new_height = MAX_WIDTH, MAX_HEIGHT
            if width > height:
                new_height = int(height * MAX_WIDTH / width)
            else:
                new_width = int(width * MAX_HEIGHT / height)
            image = image.resize((new_width, new_height))

        # Save the resized image to a BytesIO buffer
        buffer = io.BytesIO()
        image.save(buffer, format=content_type.lower())
        buffer.seek(0)

        return buffer.getvalue()

    def __get_total_file_size(self, bucket_name, prefix):
        try:
            bucket = self.s3.Bucket(bucket_name)
            total_size = 0

            # Iterate over objects filtered by the prefix
            for obj in bucket.objects.filter(Prefix=prefix):
                total_size += obj.size

            if 0 == total_size:
                raise HTTPException(status_code=404, detail="No files found under the specified directory.")

            return total_size

        except ClientError as e:
            raise HTTPException(status_code=500, detail=f"Error interacting with S3: {e.response['Error']['Message']}")

    def get_user_storage_size(self, user_id: int):
        return self.__get_total_file_size(XC_BUCKET, f'files/{user_id}/')

"""
此為 lambda 函數 avatar-thumb-generator 的程式碼，用於處理 S3 上傳事件，生成使用者頭像縮圖並上傳回 S3。
"""
import boto3
import logging
import os
import uuid
from urllib.parse import unquote_plus
from PIL import Image, ImageOps

log = logging.getLogger()
log.setLevel(logging.INFO)
         
s3_client = boto3.client('s3')

STAGE = os.environ["STAGE"]
XC_USER_BUCKET = os.environ["XC_USER_BUCKET"]
ENV_PREFIX = f"{STAGE}/" if STAGE != "prod" else ""

# 縮圖最大寬高
MAX_WIDTH = 300
MAX_HEIGHT = 300

def resize_image(src_path, dst_path):
    with Image.open(src_path) as image:
        original_size = image.size

        # 自動依 EXIF 修正方向
        image = ImageOps.exif_transpose(image)

        # 轉 RGB
        if image.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            if image.mode in ('RGBA', 'LA'):
                background.paste(image, mask=image.split()[-1])
                image = background
            else:
                image = image.convert('RGB')

        width, height = image.size

        # 只縮大圖，保持比例
        if width > MAX_WIDTH or height > MAX_HEIGHT:
            if width > height:
                new_width = MAX_WIDTH
                new_height = int(height * MAX_WIDTH / width)
            else:
                new_height = MAX_HEIGHT
                new_width = int(width * MAX_HEIGHT / height)

            # 使用 Pillow 最新方式 LANCZOS 重採樣
            resample = Image.Resampling.LANCZOS
            image = image.resize((new_width, new_height), resample)
            resized_size = (new_width, new_height)
        else:
            resized_size = original_size  # 小圖不放大

        # 儲存 JPEG，quality=75
        image.save(dst_path, format="JPEG", quality=85)

    return original_size, resized_size

def is_valid_avatar_key(key: str) -> bool:
    expected_prefix = f"{ENV_PREFIX}files/"
    if not key.startswith(expected_prefix):
        return False
    if not key.endswith("/avatar"):
        return False

    relative_key = key[len(ENV_PREFIX):]
    parts = relative_key.split("/")
    return len(parts) == 3 and bool(parts[1])


def lambda_handler(event, context):
    log.info("Lambda invoked | recordCount=%s", len(event.get("Records", [])))

    for record in event.get("Records", []):
        bucket = None
        key = None
        user_id = None
        download_path = None
        upload_path = None

        try:
            bucket = record["s3"]["bucket"]["name"]
            key = unquote_plus(record["s3"]["object"]["key"])

            log.info("S3 event received | bucket=%s | key=%s", bucket, key)

            if bucket != XC_USER_BUCKET:
                log.info("Skip event | reason=invalid_bucket | bucket=%s", bucket)
                continue

            if not is_valid_avatar_key(key):
                log.info("Skip event | reason=invalid_key | key=%s", key)
                continue

            relative_key = key[len(ENV_PREFIX):]
            user_id = relative_key.split("/")[1]

            download_path = f"/tmp/{uuid.uuid4()}"
            upload_path = f"/tmp/avatar-thumb-{uuid.uuid4()}"
            thumb_key = f"{ENV_PREFIX}files/{user_id}/avatar-thumb"

            s3_client.download_file(bucket, key, download_path)

            original_size, resized_size = resize_image(
                download_path, upload_path
            )

            with Image.open(upload_path) as img:
                content_type = f"image/{img.format.lower()}"
            s3_client.upload_file(upload_path, bucket, thumb_key, ExtraArgs={'ContentType': content_type})

            log.info("Thumbnail success | userId=%s | src=%s | dst=%s | size=%sx%s -> %sx%s",
                user_id,
                key,
                thumb_key,
                original_size[0],
                original_size[1],
                resized_size[0],
                resized_size[1]
            )

        except Exception:
            log.exception("Thumbnail failed | userId=%s | key=%s",
                user_id,
                key
            )
            continue
        finally:
            for temp_path in (download_path, upload_path):
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)

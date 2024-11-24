from datetime import datetime, timezone
from typing import Optional

from pydantic import HttpUrl, BaseModel, UUID4


class FileInfoDTO(BaseModel):
    file_id: Optional[UUID4] # uuid
    file_name: str
    file_size: int
    content_type: Optional[str] = None
    url: Optional[HttpUrl] = "http://example.com"  # Validates URL if provided
    create_time: Optional[datetime] = datetime.now(timezone.utc)
    update_time: Optional[datetime] = datetime.now(timezone.utc)
    is_deleted: bool = False

class FileInfoVO(BaseModel):
    file_id: Optional[UUID4] # uuid
    file_name: str
    file_size: int
    content_type: Optional[str] = None
    url: Optional[HttpUrl] = "http://example.com"  # Validates URL if provided
    create_time: Optional[datetime] = datetime.now(timezone.utc)
    update_time: Optional[datetime] = datetime.now(timezone.utc)
    is_deleted: bool = False
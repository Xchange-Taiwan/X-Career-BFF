from datetime import datetime
from typing import Optional

from pydantic import HttpUrl, BaseModel


class FileInfoDTO(BaseModel):
    file_id: str  # uuid
    filename: str
    size: int
    content_type: Optional[str] = None
    url: Optional[HttpUrl] = None  # Validates URL if provided
    create_time: datetime
    update_time: datetime
    is_deleted: bool = False

from typing import List, Optional

from pydantic import BaseModel

from src.config.constant import TagIntent, TagKind


class UserTagVO(BaseModel):
    tag_id: int
    intent: str
    kind: str
    subject_group: Optional[str] = None
    language: Optional[str] = None
    subject: Optional[str] = ''


class UserTagListVO(BaseModel):
    user_tags: List[UserTagVO] = []


class UserTagsUpsertDTO(BaseModel):
    kind: TagKind
    intent: TagIntent
    subject_groups: List[str] = []
    language: Optional[str] = None


class UserTagsUpsertVO(BaseModel):
    user_id: int
    kind: str
    intent: str
    tag_ids: List[int] = []
    replaced: bool = True

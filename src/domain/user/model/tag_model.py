from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from src.config.constant import TagIntent, TagKind


class UserTagVO(BaseModel):
    tag_id: int
    intent: str
    kind: str
    subject_group: Optional[str] = None
    language: Optional[str] = None
    subject: Optional[str] = ''
    # Free-form per-tag metadata (icon, display hints, etc.) — mirrors the
    # User service Tag.desc JSONB column. Pass-through here.
    desc: Optional[Dict[str, Any]] = None


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

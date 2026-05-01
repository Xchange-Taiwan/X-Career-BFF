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
    # Two-layer hierarchy (#226): NULL on top-level group / industry rows,
    # non-NULL on leaf rows. Mirrors User-service Tag.parent_subject_group.
    parent_subject_group: Optional[str] = None


class UserTagListVO(BaseModel):
    user_tags: List[UserTagVO] = []


class UserTagBucketsVO(BaseModel):
    """Pre-grouped view of a user's tags, mirroring User-service shape so the
    BFF can pass the response through unchanged. Bucket → (kind, intent):
      want_skills    → (skill,    WANT)   "想多了解、加強的技能"
      offer_skills   → (skill,    OFFER)  "我能教的 expertise"
      want_topics    → (topic,    WANT)   "想多了解的主題"
      offer_topics   → (topic,    OFFER)  "我能聊的主題"
      want_positions → (position, WANT)   "有興趣多了解的職位"
    """
    want_skills: List[UserTagVO] = []
    offer_skills: List[UserTagVO] = []
    want_topics: List[UserTagVO] = []
    offer_topics: List[UserTagVO] = []
    want_positions: List[UserTagVO] = []


class UserTagBucketsInputDTO(BaseModel):
    """Input mirror of User-service `UserTagBucketsInputDTO`. Used as a
    nested field on PUT mentor_profile so caller can write multiple buckets
    in one shot. None per bucket = leave alone, [] = clear, [...] = replace
    with these LEAF subject_groups. BFF passes the dict through unchanged.
    """
    want_skills: Optional[List[str]] = None
    offer_skills: Optional[List[str]] = None
    want_topics: Optional[List[str]] = None
    offer_topics: Optional[List[str]] = None
    want_positions: Optional[List[str]] = None
    language: Optional[str] = None


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


class TagCatalogLeafVO(BaseModel):
    tag_id: int
    subject_group: str
    subject: str
    language: str
    desc: Optional[Dict[str, Any]] = None


class TagCatalogGroupVO(BaseModel):
    subject_group: str
    subject: str
    language: str
    desc: Optional[Dict[str, Any]] = None
    leaves: List[TagCatalogLeafVO] = []


class TagCatalogVO(BaseModel):
    kind: str
    language: str
    groups: List[TagCatalogGroupVO] = []

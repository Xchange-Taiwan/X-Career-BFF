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
    desc: Optional[Dict[str, Any]] = None
    # NULL on top-level group rows, non-NULL on leaf rows.
    parent_subject_group: Optional[str] = None


class UserTagListVO(BaseModel):
    user_tags: List[UserTagVO] = []


class UserTagBucketsVO(BaseModel):
    """Pre-grouped view of a user's tags, one bucket per (kind, intent)."""
    want_skills: List[UserTagVO] = []
    offer_skills: List[UserTagVO] = []
    want_topics: List[UserTagVO] = []
    offer_topics: List[UserTagVO] = []
    want_positions: List[UserTagVO] = []


class UserTagBucketsInputDTO(BaseModel):
    """Per bucket: None = leave alone, [] = clear, [...] = replace with these
    LEAF subject_groups. Language is intentionally omitted — User-service
    always uses the user's profile language to avoid forked selections
    across languages."""
    want_skills: Optional[List[str]] = None
    offer_skills: Optional[List[str]] = None
    want_topics: Optional[List[str]] = None
    offer_topics: Optional[List[str]] = None
    want_positions: Optional[List[str]] = None


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


class TagCatalogsVO(BaseModel):
    language: str
    catalogs: Dict[str, TagCatalogVO] = {}

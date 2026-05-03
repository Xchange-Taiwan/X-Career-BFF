from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class TagVO(BaseModel):
    """Mirror of X-Career-User TagVO. Each enriched bucket on
    MentorProfileVO is a list of these."""
    id: int
    kind: str
    subject_group: Optional[str] = None
    language: Optional[str] = None
    subject: Optional[str] = ''
    desc: Optional[Dict[str, Any]] = None
    parent_subject_group: Optional[str] = None


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

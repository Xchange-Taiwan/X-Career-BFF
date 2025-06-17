import logging as log
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from ...mentor.model.mentor_model import MentorProfileVO

log.basicConfig(filemode='w', level=log.INFO)


class SearchMentorProfileDTO(BaseModel):
    search_pattern: Optional[str] = None
    filter_positions: Optional[List[str]] = None
    filter_skills: Optional[List[str]] = None
    filter_topics: Optional[List[str]] = None
    filter_expertises: Optional[List[str]] = None
    filter_industries: Optional[List[str]] = None
    limit: int = 9
    cursor: Optional[datetime] = None

class SearchMentorProfileVO(MentorProfileVO):
    updated_at: Optional[int]
    views: Optional[int]


class SearchMentorProfileListVO(BaseModel):
    mentors: List[SearchMentorProfileVO]
    next_id: Optional[int]

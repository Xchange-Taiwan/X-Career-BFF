import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from datetime import datetime
from ...mentor.model.mentor_model import MentorProfileVO
from ....config.conf import *
from ....config.constant import *
import logging as log

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

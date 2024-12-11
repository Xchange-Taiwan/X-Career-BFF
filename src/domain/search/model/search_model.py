import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from ...mentor.model.mentor_model import MentorProfileVO
from ....config.conf import *
from ....config.constant import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class SearchMentorProfileDTO(BaseModel):
    search_patterns: List[str]
    filter_job_title: List[str]
    filter_skills: List[str]
    filter_topics: List[str]
    filter_expertises: List[str]
    filter_industries: List[str]
    sorting_by: SortingBy
    sorting: Sorting
    next_id: int


class SearchMentorProfileVO(MentorProfileVO):
    updated_at: Optional[int]
    views: Optional[int]


class SearchMentorProfileListVO(BaseModel):
    mentors: List[SearchMentorProfileVO]
    next_id: Optional[int]

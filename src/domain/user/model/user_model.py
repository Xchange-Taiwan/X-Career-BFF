import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from .common_model import ProfessionVO, InterestListVO
from ....config.constant import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class ProfileDTO(BaseModel):
    user_id: Optional[int]
    name: Optional[str] = ""
    avatar: Optional[str] = ""
    timezone: Optional[int] = 0
    industry: Optional[int] = 0
    job_title: Optional[str] = ""
    company: Optional[str] = ""
    linkedin_profile: Optional[str]
    interested_positions: Optional[List[int]] = []
    skills: Optional[List[int]] = []
    topics: Optional[List[int]] = []
    language: Optional[str] = 'CHT'


class ProfileVO(BaseModel):
    user_id: int
    name: Optional[str] = ""
    avatar: Optional[str] = ""
    timezone: Optional[int] = 0
    industry: Optional[ProfessionVO] = None
    job_title: Optional[str] = ""
    company: Optional[str] = ""
    linkedin_profile: Optional[str] = ""
    interested_positions: Optional[InterestListVO] = None
    skills: Optional[InterestListVO] = None
    topics: Optional[InterestListVO] = None
    language: Optional[str] = 'CHT'

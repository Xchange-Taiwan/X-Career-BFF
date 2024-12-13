import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from .common_model import ProfessionVO, InterestListVO
from ....config.constant import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)





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

    @staticmethod
    def from_vo(vo: ProfileVO) -> "ProfileDTO":
        """
        Converts a ProfileVO object to a ProfileDTO object.

        :param vo: ProfileVO instance
        :return: ProfileDTO instance
        """
        interest_ids = [position.id for position in vo.interested_positions.interests] if vo.interested_positions else []
        skill_ids = [skill.id for skill in vo.skills.interests] if vo.skills else []
        topic_ids = [topic.id for topic in vo.topics.interests] if vo.topics else []

        return ProfileDTO(
            user_id=vo.user_id,
            name=vo.name,
            avatar=vo.avatar,
            timezone=vo.timezone,
            industry=vo.industry.id if vo.industry else 0,
            job_title=vo.job_title,
            company=vo.company,
            linkedin_profile=vo.linkedin_profile,
            interested_positions=interest_ids,
            skills=skill_ids,
            topics=topic_ids,
            language=vo.language
        )
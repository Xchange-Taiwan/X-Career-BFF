import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from .common_model import ProfessionVO, InterestListVO, ProfessionListVO
from ....config.constant import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class ProfileVO(BaseModel):
    user_id: int
    name: Optional[str] = ''
    avatar: Optional[str] = ''
    job_title: Optional[str] = ''
    company: Optional[str] = ''
    years_of_experience: Optional[int] = 0
    region: Optional[str] = ''
    linkedin_profile: Optional[str] = ''
    interested_positions: Optional[InterestListVO] = None
    skills: Optional[InterestListVO] = None
    topics: Optional[InterestListVO] = None
    industries: Optional[ProfessionListVO] = None
    on_boarding: Optional[bool] = False
    language: Optional[str] = 'zh_TW'



class ProfileDTO(BaseModel):
    user_id: Optional[int]
    name: Optional[str] = ''
    avatar: Optional[str] = ''

    job_title: Optional[str] = ''
    company: Optional[str] = ''
    years_of_experience: Optional[int] = 0
    region: Optional[str] = ''
    linkedin_profile: Optional[str] = ''
    interested_positions: Optional[List[Union[str]]] = []
    skills: Optional[List[Union[str]]] = []
    topics: Optional[List[Union[str]]] = []
    industries: Optional[List[str]] = []
    language: Optional[str] = 'zh_TW'

    @staticmethod
    def from_vo(vo: ProfileVO) -> "ProfileDTO":
        """
        Converts a ProfileVO object to a ProfileDTO object.

        :param vo: ProfileVO instance
        :return: ProfileDTO instance
        """
        interest_subject_groups = [position.id for position in
                        vo.interested_positions.interests] if vo.interested_positions else []
        skill_subject_groups = [skill.id for skill in vo.skills.interests] if vo.skills else []
        topic_subject_groups = [topic.id for topic in vo.topics.interests] if vo.topics else []
        industries_subject_groups = [profession.subject_group for profession in vo.industries.professions] if vo.industries else [],
        return ProfileDTO(
            user_id=vo.user_id,
            name=vo.name,
            avatar=vo.avatar,
            job_title=vo.job_title,
            company=vo.company,
            linkedin_profile=vo.linkedin_profile,
            interested_positions=interest_subject_groups,
            skills=skill_subject_groups,
            topics=topic_subject_groups,
            language=vo.language,
            years_of_experience=vo.years_of_experience,
            region=vo.region,
            industries=industries_subject_groups
        )

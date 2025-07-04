import logging as log
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .common_model import ProfessionVO, InterestListVO
from ....config.conf import DEFAULT_LANGUAGE

log.basicConfig(filemode="w", level=log.INFO)


class ProfileVO(BaseModel):
    user_id: int
    name: Optional[str] = ''
    avatar: Optional[str] = ''
    job_title: Optional[str] = ''
    company: Optional[str] = ''
    years_of_experience: Optional[str] = '0'
    location: Optional[str] = ''
    interested_positions: Optional[InterestListVO] = None
    skills: Optional[InterestListVO] = None
    topics: Optional[InterestListVO] = None
    industry: Optional[ProfessionVO] = None
    onboarding: Optional[bool] = False
    is_mentor: Optional[bool] = False
    language: Optional[str] = DEFAULT_LANGUAGE


class ProfileDTO(BaseModel):
    user_id: Optional[int]
    name: Optional[str] = ''
    avatar: Optional[str] = ''
    job_title: Optional[str] = ''
    company: Optional[str] = ''
    years_of_experience: Optional[str] = '0'
    location: Optional[str] = ''
    interested_positions: Optional[List[str]] = Field(default_factory=list)
    skills: Optional[List[str]] = Field(default_factory=list)
    topics: Optional[List[str]] = Field(default_factory=list)
    industry: Optional[str] = ''
    language: Optional[str] = DEFAULT_LANGUAGE

    @staticmethod
    def from_vo(vo: Dict) -> "ProfileDTO":
        """
        Converts a ProfileVO object to a ProfileDTO object.

        :param vo: ProfileVO instance
        :return: ProfileDTO instance
        """
        interest_subject_groups = []
        if len(vo.get('interested_positions', [])) > 0:
            for position in vo.get('interested_positions', []).get('interests', {}):
                if 'subject_group' in position:
                    interest_subject_groups.append(position.get('subject_group'))

        skill_subject_groups = []
        if len(vo.get('skills', [])) > 0:
            for skill in vo.get('skills', []).get('interests', {}):
                if 'subject_group' in skill:
                    skill_subject_groups.append(skill.get('subject_group'))

        topic_subject_groups = []
        if len(vo.get('topics', [])) > 0:
            for topic in vo.get('topics', []).get('interests', {}):
                if 'subject_group' in topic:
                    topic_subject_groups.append(topic.get('subject_group'))

        return ProfileDTO(
            user_id=vo.get('user_id', 0),
            name=vo.get('name', ''),
            avatar=vo.get('avatar', ''),
            job_title=vo.get('job_title', ''),
            company=vo.get('company', ''),
            years_of_experience=vo.get('years_of_experience', '0'),
            location=vo.get('location', ''),
            interested_positions=interest_subject_groups,
            skills=skill_subject_groups,
            topics=topic_subject_groups,
            industry=vo.get('industry', ''),
            language=vo.get('language', DEFAULT_LANGUAGE),
        )

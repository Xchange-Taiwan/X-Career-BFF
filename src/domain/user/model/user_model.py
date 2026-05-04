import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from ....config.conf import DEFAULT_LANGUAGE

log = logging.getLogger(__name__)


class ProfileVO(BaseModel):
    user_id: int
    name: Optional[str] = ''
    avatar: Optional[str] = ''
    job_title: Optional[str] = ''
    company: Optional[str] = ''
    years_of_experience: Optional[str] = '0'
    location: Optional[str] = ''
    # BFF is a proxy — industry is passed through unmodified from the
    # User service (TagVO shape, kind='industry'). Not modeled here on
    # purpose: that detail belongs to the upstream contract.
    industry: Optional[Dict[str, Any]] = None
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
    industry: Optional[str] = ''
    language: Optional[str] = DEFAULT_LANGUAGE
    is_mentor: Optional[bool] = False

    model_config = {
        "from_attributes": True,
    }

    @staticmethod
    def from_vo(vo: Dict) -> "ProfileDTO":
        return ProfileDTO(
            user_id=vo.get('user_id', 0),
            name=vo.get('name', ''),
            avatar=vo.get('avatar', ''),
            job_title=vo.get('job_title', ''),
            company=vo.get('company', ''),
            years_of_experience=vo.get('years_of_experience', '0'),
            location=vo.get('location', ''),
            industry=vo.get('industry', ''),
            language=vo.get('language', DEFAULT_LANGUAGE),
            is_mentor=vo.get('is_mentor', False),
        )

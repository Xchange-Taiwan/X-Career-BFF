import logging
from typing import Dict, List, Optional

from pydantic import BaseModel

from ....config.constant import *

log = logging.getLogger(__name__) 


class ExperienceDTO(BaseModel):
    id: Optional[int] = None
    category: ExperienceCategory = None
    mentor_experiences_metadata: Dict = {}
    order: int = 0


class ExperienceVO(BaseModel):
    id: int
    category: ExperienceCategory = None
    mentor_experiences_metadata: Dict = {}
    order: int = 0

    @staticmethod
    def of(
        exp_id: int,
        category: ExperienceCategory,
        mentor_experiences_metadata: Dict,
        order: int,
    ) -> "ExperienceVO":
        return ExperienceVO(
            id=exp_id,
            category=category,
            mentor_experiences_metadata=mentor_experiences_metadata,
            order=order,
        )


class ExperienceListVO(BaseModel):
    experiences: List[ExperienceVO] = []

import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from ....config.constant import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class ExperienceDTO(BaseModel):
    id: Optional[int] = None
    desc: Dict = {}
    order: int = 0


class ExperienceVO(BaseModel):
    id: int
    category: ExperienceCategory
    desc: Dict
    order: int

    @staticmethod
    def of(exp_id: int, desc: Dict, order: int, category: ExperienceCategory) -> 'ExperienceVO':
        return ExperienceVO(id=exp_id, desc=desc, order=order, category=category)


class ExperienceListVO(BaseModel):
    language: Optional[str]
    experiences: List[ExperienceVO] = []

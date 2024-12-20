import json
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel
from ....config.constant import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class ExperienceDTO(BaseModel):
    id: Optional[int]
    language: Optional[str]
    desc: Dict
    order: int


class ExperienceVO(BaseModel):
    id: int
    language: Optional[str]
    category: ExperienceCategory
    desc: Dict
    order: int


class ExperienceListVO(BaseModel):
    language: Optional[str]
    experiences: List[ExperienceVO] = []

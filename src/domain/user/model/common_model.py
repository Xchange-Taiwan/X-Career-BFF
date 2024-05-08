import logging as log
from typing import Dict, List

from pydantic import BaseModel

from ....config.constant import *

log.basicConfig(filemode='w', level=log.INFO)


class InterestVO(BaseModel):
    id: int
    category: InterestCategory
    subject: str
    desc: Dict


class IndustryVO(BaseModel):
    id: int
    category: IndustryCategory
    subject: str
    desc: Dict


class IndustryListVO(BaseModel):
    industries: List[IndustryVO] = []


class InterestListVO(BaseModel):
    interests: List[InterestVO] = []


class ProfessionDTO(BaseModel):
    id: int
    profession_category: ProfessionCategory


class ProfessionVO(ProfessionDTO):
    subject: str
    metadata: Dict


class ProfessionListVO(BaseModel):
    professions: List[ProfessionVO] = []

import logging as log
from typing import Dict, List, Optional

from pydantic import BaseModel

from ....config.constant import *

log.basicConfig(filemode='w', level=log.INFO)


class InterestVO(BaseModel):
    id: int
    category: InterestCategory = None
    language: Optional[str] = None
    subject_group: str = 'unknown'
    subject: Optional[str] = ''
    desc: Optional[Dict] = {}


class InterestListVO(BaseModel):
    interests: List[InterestVO] = []
    language: Optional[str] = None


class ProfessionDTO(BaseModel):
    id: int
    category: ProfessionCategory
    language: Optional[str]


class ProfessionVO(ProfessionDTO):
    subject_group: str = 'unknown'
    subject: str = ''
    profession_metadata: Dict = {}
    language: Optional[str] = ''


class ProfessionListVO(BaseModel):
    professions: List[ProfessionVO] = []


class CountryVO(BaseModel):
    country_code: str # alpha_3
    country_name: str

class CountryListVO(BaseModel):
    countries: List[CountryVO] = []

class UniversityListVO(BaseModel):
    universities: List[str] = []

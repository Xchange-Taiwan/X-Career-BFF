import logging
from typing import List

from pydantic import BaseModel

log = logging.getLogger(__name__)


class CountryVO(BaseModel):
    country_code: str # alpha_3
    country_name: str

class CountryListVO(BaseModel):
    countries: List[CountryVO] = []

class UniversityListVO(BaseModel):
    universities: List[str] = []

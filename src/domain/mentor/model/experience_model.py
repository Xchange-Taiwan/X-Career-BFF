import logging
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from ....config.constant import *

log = logging.getLogger(__name__)


class ExperienceDTO(BaseModel):
    category: ExperienceCategory = None
    mentor_experiences_metadata: Dict[str, Any] = {}
    order: int = 0


class ExperienceVO(BaseModel):
    category: ExperienceCategory = None
    mentor_experiences_metadata: Dict[str, Any] = {}
    order: int = 0


class ExperienceListVO(BaseModel):
    experiences: List[ExperienceVO] = []

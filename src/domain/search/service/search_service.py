from typing import Optional, Dict, Any
from src.infra.template.service_api import IServiceApi
from src.infra.template.cache import ICache
from src.config.conf import SEARCH_SERVICE_URL
from ....domain.search.model import (
    search_model as search,
)

import logging as log


log.basicConfig(filemode='w', level=log.INFO)


class SearchService:
    def __init__(self, service_api: IServiceApi, cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: IServiceApi = service_api
        self.cache = cache

    async def search_mentor(self, query: search.SearchMentorProfileDTO) -> Dict:
        req_url = f"{SEARCH_SERVICE_URL}/v1/search/mentors"
        params = query.model_dump(exclude_none=True)
        res: Optional[Dict[str, Any]] = await self.service_api.simple_get(url=req_url, params=params)
        return res

    async def search_mentor_by_id(self, mentor_id: int) -> Dict:
        req_url = f"{SEARCH_SERVICE_URL}/v1/search/mentors/{mentor_id}"
        res: Optional[Dict[str, Any]] = await self.service_api.simple_get(url=req_url)
        return res

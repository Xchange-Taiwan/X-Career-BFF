import logging as log

from src.config.constant import MICRO_SERVICE_URL, USER_SERVICE_PREFIX, API_VERSION, MENTORS
from src.domain.cache import ICache
from ...infra.client.async_service_api_adapter import AsyncServiceApiAdapter

log.basicConfig(filemode='w', level=log.INFO)


class MentorService:
    def __init__(self, service_api: AsyncServiceApiAdapter, cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.service_api: AsyncServiceApiAdapter = service_api
        self.cache = cache

    async def get_mentor_profile(self, user_id: int):
        req_url = MICRO_SERVICE_URL + USER_SERVICE_PREFIX + API_VERSION + MENTORS + '/' + str(user_id) + '/profile'
        return self.service_api.get(url=req_url)

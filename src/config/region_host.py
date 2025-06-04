import logging as log
import os

from fastapi import HTTPException, status

log.basicConfig(filemode='w', level=log.INFO)


auth_region_hosts = {
    'default': os.getenv('REGION_HOST_AUTH', 'http://localhost:8008/auth-service/api'),
    'jp': os.getenv('JP_REGION_HOST_AUTH', 'http://localhost:8008/auth-service/api'),
    'ge': os.getenv('GE_REGION_HOST_AUTH', 'http://localhost:8008/auth-service/api'),
    'us': os.getenv('US_REGION_HOST_AUTH', 'http://localhost:8008/auth-service/api'),
}

user_region_hosts = {
    'default': os.getenv('REGION_HOST_USER', 'http://localhost:8009/user-service/api'),
    'jp': os.getenv('JP_REGION_HOST_USER', 'http://localhost:8009/user-service/api'),
    'ge': os.getenv('GE_REGION_HOST_USER', 'http://localhost:8009/user-service/api'),
    'us': os.getenv('US_REGION_HOST_USER', 'http://localhost:8009/user-service/api'),
}

search_region_hosts = {
    'default': os.getenv('REGION_HOST_SEARCH', 'http://localhost:8010/search-service/api'),
    'jp': os.getenv('JP_REGION_HOST_SEARCH', 'http://localhost:8010/search-service/api'),
    'ge': os.getenv('GE_REGION_HOST_SEARCH', 'http://localhost:8010/search-service/api'),
    'us': os.getenv('US_REGION_HOST_SEARCH', 'http://localhost:8010/search-service/api'),
}


class RegionException(HTTPException):
    def __init__(self, region: str):
        self.msg = f'invalid region: {region}'
        self.status_code = status.HTTP_400_BAD_REQUEST


def get_auth_region_host(region: str = 'default'):
    try:
        default_host = auth_region_hosts['default']
        return auth_region_hosts.get(region, default_host)
    except Exception as e:
        log.error(f'get_auth_region_host fail, region:%s err:%s', region, e.__str__())
        raise RegionException(region=region)

def get_user_region_host(region: str = 'default'):
    try:
        default_host = user_region_hosts['default']
        return user_region_hosts.get(region, default_host)
    except Exception as e:
        log.error(f'get_user_region_host fail, region:%s err:%s', region, e.__str__())
        raise RegionException(region=region)

def get_search_region_host(region: str = 'default'):
    try:
        default_host = search_region_hosts['default']
        return search_region_hosts.get(region, default_host)
    except Exception as e:
        log.error(f'get_search_region_host fail, region:%s err:%s', region, e.__str__())
        raise RegionException(region=region)

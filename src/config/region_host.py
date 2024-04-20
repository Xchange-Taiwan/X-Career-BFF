import os
from fastapi import HTTPException, status
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


auth_region_hosts = {
    'default': os.getenv('REGION_HOST_AUTH', 'http://localhost:8007/auth/api/v1'),
    'jp': os.getenv('JP_REGION_HOST_AUTH', 'http://localhost:8007/auth/api/v1'),
    'ge': os.getenv('GE_REGION_HOST_AUTH', 'http://localhost:8007/auth/api/v1'),
    'us': os.getenv('US_REGION_HOST_AUTH', 'http://localhost:8007/auth/api/v1'),
}

user_region_hosts = {
    'default': os.getenv('REGION_HOST_USER', 'http://localhost:8008/user/api/v1'),
    'jp': os.getenv('JP_REGION_HOST_USER', 'http://localhost:8008/user/api/v1'),
    'ge': os.getenv('GE_REGION_HOST_USER', 'http://localhost:8008/user/api/v1'),
    'us': os.getenv('US_REGION_HOST_USER', 'http://localhost:8008/user/api/v1'),
}

search_region_hosts = {
    'default': os.getenv('REGION_HOST_SEARCH', 'http://localhost:8009/search/api/v1'),
    'jp': os.getenv('JP_REGION_HOST_SEARCH', 'http://localhost:8009/search/api/v1'),
    'ge': os.getenv('GE_REGION_HOST_SEARCH', 'http://localhost:8009/search/api/v1'),
    'us': os.getenv('US_REGION_HOST_SEARCH', 'http://localhost:8009/search/api/v1'),
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

import os
import time
import json
from datetime import datetime, timedelta
from typing import Any, List, Set, Optional
from ..template.cache import ICache
from ...config.dynamodb import dynamodb
from ...config.conf import TABLE_CACHE
from ...config.exception import ServerException
from ...infra.util.time_util import gen_ttl_secs
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class DynamoDbCacheAdapter(ICache):
    def __init__(self, dynamodb: Any):
        self.db = dynamodb
        self.__cls_name = self.__class__.__name__

    def is_json_obj(self, val: Any) -> (bool):
        return (val[0] == '{' and val[-1] == '}') or \
            (val[0] == '[' and val[-1] == ']')

    async def get(self, key: str, with_ttl: bool = False):
        res = None
        result = None
        try:
            table = self.db.Table(TABLE_CACHE)
            res = table.get_item(Key={'cache_key': key})
            if 'Item' in res and 'value' in res['Item']:
                val = res['Item']['value']
                if self.is_json_obj(val):
                    result = json.loads(val)
                    if with_ttl and 'ttl' in res['Item']:
                        result.update({'ttl': res['Item']['ttl']})
                else:
                    result = val

            return result

        except Exception as e:
            log.error(f'cache {self.__cls_name}.get fail \
                key:%s, res:%s, result:%s, err:%s',
                      key, res, result, e.__str__())
            raise ServerException(msg='d2_server_error')

    async def set(self, key: str, val: Any, ex: int = None):
        res = None
        result = False
        try:
            val_type = type(val)
            if val_type == dict or val_type == list:
                val = json.dumps(val)

            table = self.db.Table(TABLE_CACHE)
            item = {
                'cache_key': key,
                'value': val,
            }
            if ex:
                ttl = gen_ttl_secs(seconds=ex)
                item.update({'ttl': ttl})

            res = table.put_item(Item=item)
            result = True
            return result

        except Exception as e:
            log.error(f'cache {self.__cls_name}.set fail \
                    key:%s, val:%s, ex:%s, res:%s, result:%s, err:%s',
                      key, val, ex, res, result, e.__str__())
            raise ServerException(msg='d2_server_error')

    async def delete(self, key: str):
        try:
            table = self.db.Table(TABLE_CACHE)
            table.delete_item(Key={'cache_key': key})
        except Exception as e:
            log.error(f'cache {self.__cls_name}.set fail \
                    key:%s, err:%s',
                      key, e.__str__())
            raise ServerException(msg='d2_server_error')

    async def smembers(self, key: str) -> (Optional[Set[Any]]):
        values = await self.get(key)
        if values is None:
            return None

        if not isinstance(values, list):
            raise ServerException(msg='invalid set-members type')

        return set(values)

    async def sismember(self, key: str, value: Any) -> (bool):
        set_members = await self.smembers(key)
        if set_members is None:
            return False

        return value in set_members

    async def sadd(self, key: str, values: List[Any], ex: int = None) -> (int):
        if not isinstance(values, list):
            raise ServerException(
                msg='invalid input type, values should be list')

        set_values = set(values)

        update_count = 0
        set_members = self.smembers(key)
        if set_members is None:
            await self.set(key, list(set_values), ex)

        else:
            new_set_members = set_members | set_values
            await self.set(key, list(new_set_members), ex)

        update_count = len(values)
        return update_count

    async def srem(self, key: str, value: Any) -> (int):
        update_count = 0
        set_members = await self.smembers(key)
        if set_members is None:
            return update_count

        if value in set_members:
            set_members.remove(value)
            await self.set(key, list(set_members))
            update_count = 1
        else:
            update_count = 0

        return update_count


def get_cache():
    try:
        cache = DynamoDbCacheAdapter(dynamodb)
        yield cache
    except Exception as e:
        log.error(e.__str__())
        raise
    finally:
        pass

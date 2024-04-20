import time
from ...domain.cache import ICache
from ...config.constant import SERIAL_KEY
from ...config.exception import ServerException
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


def gen_confirm_code():
    code = int(time.time() ** 6 % 1000000)
    code = code if (code > 100000) else code + 100000
    log.info(f'confirm_code: {code}')
    return code


def get_serial_num(cache: ICache, role_id: str):
    user = cache.get(role_id)
    if not user or not SERIAL_KEY in user:
        log.error(f'get_serial_num fail: [user has no \'SERIAL_KEY\'], role_id:%s', role_id)
        raise ServerException(msg='user has no authrozanization')

    return user[SERIAL_KEY]

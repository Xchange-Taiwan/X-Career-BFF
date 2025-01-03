import functools
import time
from typing import Dict

import pycountry
from babel import Locale
from starlette import status

from ..template.cache import ICache
from ...config.constant import SERIAL_KEY, Language
from ...config.exception import (
    ServerException,
    ClientException,
    UnauthorizedException,
    ForbiddenException,
    NotFoundException,
    NotAcceptableException,
)
import logging as log

log.basicConfig(filemode="w", level=log.INFO)


def gen_confirm_code():
    code = int(time.time() ** 6 % 1000000)
    code = code if (code > 100000) else code + 100000
    log.info(f"confirm_code: {code}")
    return code


def get_serial_num(cache: ICache, user_id: str):
    user = cache.get(user_id)
    if not user or not SERIAL_KEY in user:
        log.error(
            f"get_serial_num fail: [user has no 'SERIAL_KEY'], user_id:%s", user_id
        )
        raise ServerException(msg="user has no authrozanization")

    return user[SERIAL_KEY]


locale_to_countries = {language.value: {} for language in Language}


def get_localized_territories_alpha_3(language: Language):
    try:
        # 使用 Babel 翻譯
        loc = Locale.parse(language.value)
        if (
            not language.value in locale_to_countries
            or len(locale_to_countries.get(language.value)) == 0
        ):
            locale_to_countries[language.value] = {}
            for k, v in loc.territories.items():
                country = pycountry.countries.get(alpha_2=k.upper())
                if country:
                    locale_to_countries.get(language.value)[country.alpha_3] = v

        return locale_to_countries.get(language.value)

    except KeyError:
        return f"Invalid locale {language.value}."

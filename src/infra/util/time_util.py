import time
from datetime import datetime, timedelta

def shift_decimal(number, places):
    return number * (10 ** places)

def gen_timestamp():
    return int(shift_decimal(time.time(), 3))

def current_seconds():
    return int(time.time())

def gen_ttl_secs(seconds: int):
    ttl = datetime.now() + timedelta(seconds=seconds)
    return int(ttl.timestamp())


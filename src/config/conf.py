import os

AWS_PROFILE = os.getenv('AWS_PROFILE', 'xc') # xc default
STAGE = os.getenv('STAGE', 'local')
TESTING = os.getenv('TESTING', 'local')

XC_BUCKET = os.getenv('XC_BUCKET', 'x-career')

JWT_SECRET = os.getenv('JWT_SECRET', None)
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
# TODO: default = 60 mins (3600 secs)
TOKEN_EXPIRE_TIME = int(os.getenv('TOKEN_EXPIRE_TIME', 30))

BATCH = int(os.getenv('BATCH', '10'))

# default = 8 secs
REQUEST_INTERVAL_TTL = int(os.getenv('REQUEST_INTERVAL_TTL', 8))
# TODO: default = 30 mins (1800 secs)
SHORT_TERM_TTL = int(os.getenv('SHORT_TERM_TTL', 1800))
# default = 3 days (3 * 86400 secs)
LONG_TERM_TTL = int(os.getenv('LONG_TERM_TTL', 3 * 86400))


# cache
# dynamodb
TABLE_CACHE = os.getenv('TABLE_CACHE', 'dev_x_career_bff_cache')
# redis
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_USER = os.getenv('REDIS_USERNAME', None)
REDIS_PASS = os.getenv('REDIS_PASSWORD', None)


# schedule
SCHEDULE_YEAR = int(os.getenv('SCHEDULE_YEAR', '-1'))
SCHEDULE_MONTH = int(os.getenv('SCHEDULE_MONTH', '-1'))
SCHEDULE_DAY_OF_MONTH = int(os.getenv('SCHEDULE_DAY_OF_MONTH', '-1'))
SCHEDULE_DAY_OF_WEEK = int(os.getenv('SCHEDULE_DAY_OF_WEEK', '-1'))

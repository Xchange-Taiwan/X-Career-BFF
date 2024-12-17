import os

LOCAL_REGION = os.getenv('AWS_REGION', 'ap-northeast-1')
AWS_PROFILE = os.getenv('AWS_PROFILE', 'default') # xc default
STAGE = os.getenv('STAGE', 'local')
TESTING = os.getenv('TESTING', 'local')

XC_BUCKET = os.getenv('XC_BUCKET', 'x-career')

JWT_SECRET = os.getenv('JWT_SECRET', None)
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
# TODO: default = 30 mins (1800 secs)
TOKEN_EXPIRE_TIME = int(os.getenv('TOKEN_EXPIRE_TIME', 1800))

BATCH = int(os.getenv('BATCH', '10'))

# default = 8 secs
REQUEST_INTERVAL_TTL = int(os.getenv('REQUEST_INTERVAL_TTL', 8))
# TODO: default = 30 mins (1800 secs)
SHORT_TERM_TTL = int(os.getenv('SHORT_TERM_TTL', 1800))
# default = 3 days (3 * 86400 secs)
LONG_TERM_TTL = int(os.getenv('LONG_TERM_TTL', 3 * 86400))
# default = 30 days (30 * 86400 secs)
REFRESH_TOKEN_TTL = int(os.getenv('REFRESH_TOKEN_TTL', 2592000))

# filter auth response fields
AUTH_RESPONSE_FIELDS = os.getenv('AUTH_RESPONSE_FIELDS', 'email,account_type,region,online')
AUTH_RESPONSE_FIELDS = AUTH_RESPONSE_FIELDS.strip().split(',')


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

# micro service
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://127.0.0.1:8000/user-service/api')
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://127.0.0.1:8008/auth-service/api')

# storage
MAX_WIDTH = os.getenv('MAX_WIDTH', 300)
MAX_HEIGHT = os.getenv('MAX_HEIGHT', 300)
MAX_STORAGE_SIZE = os.getenv('MAX_STORAGE_SIZE', 15 * 1024 * 1024)  # give 15 MB to users

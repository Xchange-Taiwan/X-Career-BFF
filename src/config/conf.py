import os
from src.config.constant import Language

DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'zh_TW')
DEFAULT_LANGUAGE_ENUM = Language(DEFAULT_LANGUAGE)
LOCAL_REGION = os.getenv('AWS_REGION', 'ap-northeast-1')
S3_REGION = os.getenv('S3_REGION', 'ap-northeast-1')
STAGE = os.getenv('STAGE', 'local')
TESTING = os.getenv('TESTING', 'local')

XC_BUCKET = os.getenv('XC_BUCKET', 'x-career-user-dev-serverlessdeploymentbucket-bmz2uc2exezm')
XC_USER_BUCKET = os.getenv('XC_USER_BUCK', 'x-career-multimedia')

BATCH = int(os.getenv('BATCH', '10'))

# default = 8 secs
REQUEST_INTERVAL_TTL = int(os.getenv('REQUEST_INTERVAL_TTL', 8))
# TODO: default = 30 mins (1800 secs)
SHORT_TERM_TTL = int(os.getenv('SHORT_TERM_TTL', 1800))
# default = 3 days (3 * 86400 secs)
LONG_TERM_TTL = int(os.getenv('LONG_TERM_TTL', 3 * 86400))
# JWT
JWT_SECRET = os.getenv('JWT_SECRET', None)
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
# default = 30 mins (1800 secs)
ACCESS_TOKEN_TTL = int(os.getenv('ACCESS_TOKEN_TTL', 1800))
# default = 30 days (30 * 86400 secs)
REFRESH_TOKEN_TTL = int(os.getenv('REFRESH_TOKEN_TTL', 2592000))

# filter auth response fields
AUTH_RESPONSE_FIELDS = os.getenv('AUTH_RESPONSE_FIELDS', 'email,account_type,region,online')
AUTH_RESPONSE_FIELDS = AUTH_RESPONSE_FIELDS.strip().split(',')

# cache
# default cache ttl: 5 minutes
CACHE_TTL = int(os.getenv('CACHE_TTL', 300))
# dynamodb
TABLE_CACHE = os.getenv('TABLE_CACHE', 'dev_x_career_bff_cache')
# redis
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
REDIS_USER = os.getenv('REDIS_USERNAME', None)
REDIS_PASS = os.getenv('REDIS_PASSWORD', None)


# micro service
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://127.0.0.1:8008/auth-service/api')
USER_SERVICE_URL = os.getenv('USER_SERVICE_URL', 'http://127.0.0.1:8010/user-service/api')
SEARCH_SERVICE_URL = os.getenv('SEARCH_SERVICE_URL', 'http://127.0.0.1:8012/search-service/api')

# storage
MAX_WIDTH = int(os.getenv('MAX_WIDTH', 300))
MAX_HEIGHT = int(os.getenv('MAX_HEIGHT', 300))
MAX_STORAGE_SIZE = int(os.getenv('MAX_STORAGE_SIZE', 15 * 1024 * 1024))  # give 15 MB to users

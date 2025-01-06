from src.config.dynamodb import dynamodb
from src.infra.cache.dynamodb_cache_adapter import DynamoDbCacheAdapter
from src.infra.cache.local_cache_adapter import LocalCacheAdapter
from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from src.domain.auth.service.auth_service import AuthService
from src.domain.auth.service.oauth_service import OAuthService
from src.domain.user.service.user_service import UserService
from src.domain.mentor.service.mentor_service import MentorService
from src.domain.search.service.search_service import SearchService
from src.domain.file.service.file_service import FileService

service_client = AsyncServiceApiAdapter()
gw_cache = DynamoDbCacheAdapter(dynamodb)
local_cache = LocalCacheAdapter()

_auth_service: AuthService = AuthService(service_client, gw_cache)
_oauth_service: OAuthService = OAuthService(service_client, gw_cache)
_user_service: UserService = UserService(service_client, gw_cache, local_cache)
_mentor_service: MentorService = MentorService(service_client, gw_cache, local_cache)
_search_service: SearchService = SearchService(service_client, gw_cache)
_file_service: FileService = FileService(service_client, gw_cache)

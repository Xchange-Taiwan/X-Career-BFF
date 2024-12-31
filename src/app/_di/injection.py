from src.config.dynamodb import dynamodb
from src.infra.cache.dynamodb_cache_adapter import DynamoDbCacheAdapter
from src.infra.client.async_service_api_adapter import AsyncServiceApiAdapter
from src.domain.auth.service.auth_service import AuthService
from src.domain.user.service.user_service import UserService
from src.domain.file.service.file_service import FileService
from src.domain.mentor.service.mentor_service import MentorService
from src.domain.search.service.search_service import SearchService

service_client = AsyncServiceApiAdapter()
gw_cache = DynamoDbCacheAdapter(dynamodb)

_auth_service: AuthService = AuthService(service_client, gw_cache)
_user_service: UserService = UserService(service_client, gw_cache)
_file_service: FileService = FileService(service_client, gw_cache)
_mentor_service: MentorService = MentorService(service_client, gw_cache)
_search_service: SearchService = SearchService(service_client, gw_cache)

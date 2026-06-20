import asyncio
from urllib.parse import parse_qs, urlparse

from src.config.constant import AuthorizeType
from src.domain.auth.service.google_oauth_service import GoogleOAuthService
from src.infra.cache.local_cache_adapter import LocalCacheAdapter


def test_signup_authorization_url_forces_account_selection_and_consent():
    service = GoogleOAuthService(req=None, cache=LocalCacheAdapter())

    result = asyncio.run(service.get_authorization_url(AuthorizeType.SIGNUP))
    query = parse_qs(urlparse(result['authorization_url']).query)

    assert query['redirect_uri'] == ['http://localhost:3000']
    assert set(query['prompt'][0].split()) == {'select_account', 'consent'}
    assert query['scope'] == ['openid email profile']
    assert query['access_type'] == ['offline']
    assert query['include_granted_scopes'] == ['true']

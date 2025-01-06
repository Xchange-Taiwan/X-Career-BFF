from fastapi.responses import JSONResponse

from src.config.constant import USER_SERVICE_PREFIX, USERS
from src.config.conf import *
from src.config.exception import *
from src.router.req.authorization import (
    gen_token,
    gen_refresh_token,
    valid_refresh_token,
)
from src.domain.auth.service.auth_service import AuthService
from src.domain.auth.model.auth_model import *
from src.infra.util.time_util import current_seconds
from src.infra.template.cache import ICache
from src.infra.template.service_api import IServiceApi
import logging as log

log.basicConfig(filemode="w", level=log.INFO)


class OAuthService(AuthService):
    def __init__(self, req: IServiceApi, cache: ICache):
        self.cls_name = self.__class__.__name__
        self.req = req
        self.cache = cache
        self.ttl_secs = {"ttl_secs": REQUEST_INTERVAL_TTL}

    async def signup_oauth_google(self, body: SignupOauthDTO):
        auth_res = await self.req.simple_post(
            f"{AUTH_SERVICE_URL}/v1/signup/oauth/GOOGLE",
            json={
                "region": LOCAL_REGION,
                "email": body.email,
                "oauth_id": body.oauth_id,
                "access_token": body.access_token,
            },
        )
        user_id = auth_res.get('user_id', None)
        if user_id is None:
            raise ServerException(msg="signup fail", data=self.ttl_secs)
        
        # Initialize user profile
        await self.init_user_profile(user_id)
        # cache auth data
        await self.cache_auth_res(str(user_id), auth_res)
        auth_res = self.apply_token(auth_res)
        auth_res = self.filter_auth_res(auth_res)
        return {
            'auth': auth_res,
        }


    async def login_oauth_google(self, body: LoginOauthDTO, language: str):
        auth_res = await self.__req_google_login(body)
        user_id = auth_res.get("user_id")

        # cache auth data
        await self.cache_auth_res(
            str(user_id), auth_res, removed_fields={"refresh_token"}
        )
        auth_res = self.apply_token(auth_res)
        user_res = await self.get_user_profile(user_id, language)
        auth_res = self.filter_auth_res(auth_res)
        return {
            "auth": auth_res,
            "user": user_res,
        }

    async def __req_google_login(self, body: LoginOauthDTO):
        auth_res = await self.req.simple_post(
            f"{AUTH_SERVICE_URL}/v1/login/oauth/GOOGLE", json=body.model_dump()
        )
        if not auth_res or not "user_id" in auth_res:
            raise UnauthorizedException(msg="Invalid user.")
        return auth_res

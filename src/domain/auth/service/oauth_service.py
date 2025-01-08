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
from src.infra.template.service_response import ServiceApiResponse
import logging as log

log.basicConfig(filemode="w", level=log.INFO)


class OAuthService(AuthService):
    def __init__(self, req: IServiceApi, cache: ICache):
        self.cls_name = self.__class__.__name__
        self.req = req
        self.cache = cache
        self.ttl_secs = {"ttl_secs": REQUEST_INTERVAL_TTL}


    async def signup_oauth_google_and_send_email(self, body: SignupOauthDTO):
        email = body.email
        await self.cache_check_for_signup(email)
        # check google oauth token
        tokeninfo = await self.__get_google_tokeninfo(body.access_token)
        if email != tokeninfo.get("email", None):
            raise ServerException(msg="Invalid Google email")

        auth_res = await self.req_send_signup_confirm_email(email)
        if not "token" in auth_res:
            raise ServerException(msg="Google signup fail", data=self.ttl_secs)

        token = auth_res["token"]
        await self.__cache_google_oauth_id(email, body.oauth_id, token)
        data = self.ttl_secs.copy()
        if STAGE == TESTING:
            data.update({"token": token})
        return data


    async def login_oauth_google(self, body: LoginOauthDTO, language: str):
        tokeninfo = await self.__get_google_tokeninfo(body.access_token)
        oauth_id = str(tokeninfo.get("sub", None))
        if oauth_id != body.oauth_id:
            raise ServerException(msg="Invalid Google oauth id")

        email = tokeninfo.get("email", None)
        if email is None:
            raise ServerException(msg="Invalid Google email")
        auth_res = await self.__req_google_login(body, email)
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


    async def __req_google_login(self, body: LoginOauthDTO, email: EmailStr):
        payload = body.model_dump()
        payload.update({"email": email})
        auth_res = await self.req.simple_post(
            f"{AUTH_SERVICE_URL}/v1/login/oauth/GOOGLE", json=payload
        )
        if not auth_res or not "user_id" in auth_res:
            raise UnauthorizedException(msg="Invalid user.")
        return auth_res

    async def __cache_google_oauth_id(self, email: str, oauth_id: str, token: str):
        email_payload = {
            "email": email,
            "oauth_id": oauth_id,
            'auth_route': '/v1/signup/oauth/GOOGLE',
        }
        await self.cache.set(token, email_payload, ex=REQUEST_INTERVAL_TTL)
        await self.cache.set(email, {"token": token}, ex=REQUEST_INTERVAL_TTL)

    async def __get_google_tokeninfo(self, access_token: str) -> Optional[Dict]:
        response_json: ServiceApiResponse = await self.req.get(
            f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={access_token}"
        )
        if response_json.res_json.get("email_verified") != "true":
            raise ServerException(
                msg="Google oauth verification failed", data=self.ttl_secs
            )
        return response_json.res_json

import logging
import secrets
import string
from typing import Dict
from urllib.parse import urlencode

from src.config.conf import *
from src.config.constant import AuthorizeType, REFRESH_TOKEN_KEY
from src.config.exception import *
from src.domain.auth.model.auth_model import *
from src.domain.auth.service.auth_service import AuthService
from src.infra.template.cache import ICache
from src.infra.template.service_api import IServiceApi
from src.infra.template.service_response import ServiceApiResponse
from src.infra.util.time_util import current_seconds

log = logging.getLogger(__name__)


class GoogleOAuthService(AuthService):
    def __init__(self, req: IServiceApi, cache: ICache):
        self.cls_name = self.__class__.__name__
        self.req = req
        self.cache = cache
        self.ttl_secs = {'ttl_secs': REQUEST_INTERVAL_TTL}

        # Google OAuth2 配置
        self.google_client_id = GOOGLE_CLIENT_ID
        self.google_client_secret = GOOGLE_CLIENT_SECRET

        self.google_redirect_uri = f'{FRONTEND_REDIRECT_URL}'
        self.google_auth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        self.google_token_url = 'https://oauth2.googleapis.com/token'


    async def get_authorization_url_by_signup(self) -> Dict[str, str]:
        """生成 Google 授權 URL 用於註冊"""
        return await self.get_authorization_url(AuthorizeType.SIGNUP)

    async def get_authorization_url_by_login(self) -> Dict[str, str]:
        """生成 Google 授權 URL 用於登入"""
        return await self.get_authorization_url(AuthorizeType.LOGIN)


    async def get_authorization_url(self, authType: AuthorizeType) -> Dict[str, str]:
        """生成 Google 授權 URL"""
        # 生成 state 參數（用於防止 CSRF 攻擊）
        state = await self.__generate_state(authType)

        # 構建授權 URL 參數
        params = {
            'client_id': self.google_client_id,
            'redirect_uri': self.google_redirect_uri,
            'response_type': 'code',
            # Include openid so Google token endpoint returns OIDC id_token.
            'scope': 'openid email profile',
            'state': state,
            'access_type': 'offline',
            'prompt': 'consent',
        }

        # 生成授權 URL
        auth_url = f'{self.google_auth_url}?{urlencode(params)}'

        return {
            'authorization_url': auth_url,
            'state': state
        }


    async def handle_callback(self, code: str, state: str) -> Dict[str, Any]:
        """處理 Google 回調"""
        # 驗證 state
        state_data = await self.__verify_state(state)
        if not state_data:
            raise ServerException(msg='Invalid state parameter')

        # 交換授權碼獲取 token
        token_data = await self.__exchange_code_for_token(code)

        # 獲取用戶信息
        user_info = await self.__get_user_info(token_data['access_token'])

        id_token = token_data.get('id_token')
        google_oauth_data = {
            'oauth_id': user_info['sub'],
            'email': user_info['email'],
            'access_token': token_data['access_token'],
            REFRESH_TOKEN_KEY: token_data.get(REFRESH_TOKEN_KEY)
        }

        # 檢查用戶是否已存在
        if state_data.get('auth_type') == AuthorizeType.SIGNUP.value:
            signup_body = SignupOauthDTO.model_validate(google_oauth_data)
            signup_res = await self.signup_oauth_and_send_email(signup_body)
            signup_res['name'] = user_info.get('name')
            signup_res['avatar'] = user_info.get('picture')
            if id_token:
                signup_res['id_token'] = id_token
            return signup_res

        if state_data.get('auth_type') == AuthorizeType.LOGIN.value:
            signin_body = LoginOauthDTO.model_validate(google_oauth_data)
            # 帶上 Google 帳號的 name/picture，作為 onboarding 預設值的來源；
            # login_oauth 只會在 DB profile 還沒填的欄位上回填，使用者已自訂的不會被覆蓋。
            return await self.login_oauth(
                signin_body,
                language=DEFAULT_LANGUAGE,
                id_token=id_token,
                default_name=user_info.get('name'),
                default_avatar=user_info.get('picture'),
            )

        raise ServerException(msg='Invalid authorization type provided')


    async def __generate_state(self, authType: AuthorizeType) -> str:
        """生成並存儲 state

        使用 secrets 模組生成安全的隨機 token，包含：
        - 32 個字符的隨機字符串
        - 使用字母、數字和特殊字符
        - 使用系統的加密隨機數生成器
        """
        # 定義字符集
        alphabet = string.ascii_letters + string.digits + '-_'
        # 生成 32 個字符的隨機字符串
        state = ''.join(secrets.choice(alphabet) for _ in range(32))

        # 存儲 state 到緩存
        await self.cache.set(
            f'google_oauth_state:{state}',
            {
                'created_at': current_seconds(),
                'auth_type': authType.value,
            },
            ex=CACHE_TTL
        )
        return state

    async def __verify_state(self, state: str) -> Optional[str]:
        """驗證 state 並返回關聯的數據"""
        state_data = await self.cache.get(f'google_oauth_state:{state}')
        if not state_data:
            return None
        await self.cache.delete(f'google_oauth_state:{state}')
        return state_data

    async def __exchange_code_for_token(self, code: str) -> Dict[str, Any]:
        """使用授權碼交換 token"""
        return await self.req.post_req(
            url=self.google_token_url,
            json={
                'client_id': self.google_client_id,
                'client_secret': self.google_client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': self.google_redirect_uri
            })

    async def __get_user_info(self, access_token: str) -> Dict[str, Any]:
        """獲取 Google 用戶信息"""
        return await self.req.get_req(
            url='https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )






    async def signup_oauth_and_send_email(self, body: SignupOauthDTO):
        email = body.email
        await self.cache_check_for_signup(email)
        # check google oauth token
        tokeninfo = await self.__get_tokeninfo(body.access_token)
        if email != tokeninfo.get("email", None):
            raise ServerException(msg="Invalid Google email")

        auth_res = await self.req_send_signup_confirm_email(email)
        if not "token" in auth_res:
            raise ServerException(msg="Google signup fail", data=self.ttl_secs)

        token = auth_res["token"]
        await self.__cache_oauth_id(email, body.oauth_id, token)
        if STAGE == TESTING:
            auth_res.update({
                "token": token,
                "email": email,
            })
        else:
            auth_res.update({
                "email": email,
            })

        data = self.ttl_secs.copy()
        data.update({
            "auth_type": AuthorizeType.SIGNUP.value,
            "auth": auth_res,
        })
        return data


    async def login_oauth(
        self,
        body: LoginOauthDTO,
        language: str = DEFAULT_LANGUAGE,
        id_token: Optional[str] = None,
        default_name: Optional[str] = None,
        default_avatar: Optional[str] = None,
    ):
        tokeninfo = await self.__get_tokeninfo(body.access_token)
        oauth_id = str(tokeninfo.get("sub", None))
        if oauth_id != body.oauth_id:
            raise ServerException(msg="Invalid Google oauth id")

        email = tokeninfo.get("email", None)
        if email is None:
            raise ServerException(msg="Invalid Google email")
        auth_res = await self.__req_login(body, email, language)
        user_id = auth_res.get("user_id")
        user_id_key = str(user_id)
        prev = await self.cache.get(user_id_key)
        prev_rt = prev.get(REFRESH_TOKEN_KEY) if prev else None

        # cache auth data（refresh 僅經 Set-Cookie 下發，不進 JSON）
        cookie_refresh = await self.cache_auth_res(
            user_id_key,
            auth_res,
            removed_fields={REFRESH_TOKEN_KEY},
            revoke_previous_refresh=prev_rt,
        )
        auth_res = self.apply_token(auth_res)
        user_res = await self.get_user_profile(user_id, language)
        # 首次登入(尚未 onboarding)時，DB profile 的 name/avatar 會是空字串。
        # 用 Google 帳號的 name/picture 作為 onboarding 預設值回填——
        # 一旦使用者自訂過 profile，DB 即為唯一真實來源，這裡不會覆蓋。
        user_res = self.__apply_google_profile_defaults(
            user_res, default_name, default_avatar
        )
        auth_res = self.filter_auth_res(auth_res)
        if cookie_refresh:
            auth_res[REFRESH_TOKEN_KEY] = cookie_refresh
        res = {
            "auth_type": AuthorizeType.LOGIN.value,
            "auth": auth_res,
            "user": user_res,
        }
        if id_token:
            res["id_token"] = id_token
        return res

    @staticmethod
    def __apply_google_profile_defaults(
        user_res: Any,
        default_name: Optional[str],
        default_avatar: Optional[str],
    ):
        if not isinstance(user_res, dict):
            return user_res
        if default_name and not user_res.get("name"):
            user_res["name"] = default_name
        if default_avatar and not user_res.get("avatar"):
            user_res["avatar"] = default_avatar
        return user_res


    async def __req_login(self, body: LoginOauthDTO, email: EmailStr, language: str):
        payload = body.model_dump()
        payload.update({"email": email})
        auth_res = await self.req.simple_post(
            f"{AUTH_SERVICE_URL}/v1/login/oauth/GOOGLE?language={language}", json=payload
        )
        if not auth_res or not "user_id" in auth_res:
            raise UnauthorizedException(msg="Invalid user.")
        return auth_res

    async def __cache_oauth_id(self, email: EmailStr, oauth_id: str, token: str):
        email_payload = {
            "email": email,
            "oauth_id": oauth_id,
            'auth_route': '/v1/signup/oauth/GOOGLE',
        }
        await self.cache.set(token, email_payload, ex=REQUEST_INTERVAL_TTL)
        await self.cache.set(email, {"token": token}, ex=REQUEST_INTERVAL_TTL)

    async def __get_tokeninfo(self, access_token: str) -> Optional[Dict]:
        response_json: ServiceApiResponse = await self.req.get(
            f"https://www.googleapis.com/oauth2/v3/tokeninfo?access_token={access_token}"
        )
        if response_json.res_json.get("email_verified") != "true":
            raise ServerException(
                msg="Google oauth verification failed", data=self.ttl_secs
            )
        return response_json.res_json

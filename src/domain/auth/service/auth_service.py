import logging
from typing import Dict, Optional, Set

from ..model.auth_model import *
from ....config.conf import *
from ....config.constant import REFRESH_TOKEN_KEY, USERS
from ....config.exception import *
from ....infra.template.cache import ICache
from ....infra.template.service_api import IServiceApi
from ....infra.util.time_util import current_seconds
from ....router.req.authorization import (
    gen_token,
    gen_refresh_token,
    valid_refresh_token,
)

log = logging.getLogger(__name__)

# refresh_token -> user_id（字串）對照，供 OAuth refresh grant 依 token 查 session，無需在 body 傳 user_id
REFRESH_TOKEN_INDEX_PREFIX = 'rt:'


def _refresh_token_index_key(refresh_token: str) -> str:
    return f'{REFRESH_TOKEN_INDEX_PREFIX}{refresh_token}'


class AuthService:
    def __init__(self, req: IServiceApi, cache: ICache):
        self.cls_name = self.__class__.__name__
        self.req = req
        self.cache = cache
        self.ttl_secs = {'ttl_secs': REQUEST_INTERVAL_TTL}

    @staticmethod
    def auth_response(data: Dict, msg='ok', code='0'):
        auth: Dict = data.get('auth', None)
        if not auth:
            raise ServerException(msg='Invalid user')

        refresh_token = auth.pop(REFRESH_TOKEN_KEY, None)

        user = data.get('user')
        if isinstance(user, dict):
            user.pop(REFRESH_TOKEN_KEY, None)

        response = JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                'code': code,
                'msg': msg,
                'data': data,
            })

        if not refresh_token:
            return response

        # 設定 Set-Cookie Header（名稱與 REFRESH_TOKEN_KEY 一致）
        response.set_cookie(
            key=REFRESH_TOKEN_KEY,
            value=refresh_token,
            httponly=True,              # 防止 JavaScript 訪問，防範 XSS 攻擊
            secure=True,                # 僅限 HTTPS 傳輸
            samesite='Strict',          # 防範 CSRF 攻擊
            max_age=REFRESH_TOKEN_TTL   # Cookie 有效時間 (秒)
        )

        return response

    '''
    signup
    '''

    async def signup(self, body: SignupDTO):
        email = body.email
        await self.cache_check_for_signup(email)
        auth_res = await self.req_send_signup_confirm_email(email)
        if not 'token' in auth_res:
            raise ServerException(msg='signup fail', data=self.ttl_secs)

        token = auth_res['token']
        await self.__cache_signup_token(email, body.password, token)
        data = self.ttl_secs.copy()
        if STAGE == TESTING:
            data.update({'token': token})
        return data


    async def cache_check_for_signup(self, email: str):
        data = await self.cache.get(email, True)
        if data and data.get('ttl', 0) > current_seconds():
            log.error(f'{self.cls_name}.cache_check_for_signup:[too many reqeusts error],\
                email:%s, cache data:%s', email, data)
            raise TooManyRequestsException(
                msg='frequently request', data=self.ttl_secs)

        if data:
            await self.cache.delete(email)
            if 'token' in data:
                await self.cache.delete(data.get('token'))

    # return status_code, msg, err
    async def req_send_signup_confirm_email(self, email: str):
        try:
            auth_res = await self.req.simple_post(
                f'{AUTH_SERVICE_URL}/v1/signup/email',
                json={
                    'email': email,
                    'exist': False,
                })
            if auth_res is None:
                raise ServerException(msg='Connect to auth service fail.')
            return auth_res

        except NotAcceptableException or DuplicateUserException as e:
            await self.cache.set(email, {}, ex=REQUEST_INTERVAL_TTL)
            err_msg = getattr(e, 'msg', 'Email registered.')
            raise DuplicateUserException(msg=err_msg, data=self.ttl_secs)

        except Exception as e:
            log.error(f'{self.cls_name}.req_send_signup_confirm_email:[request exception], \
                host:%s, email:%s, error:%s', AUTH_SERVICE_URL, email, e)
            await self.cache.set(email, {}, ex=REQUEST_INTERVAL_TTL)
            err_msg = getattr(e, 'msg', 'Email could not be delivered.')
            raise_http_exception(e, err_msg, data=self.ttl_secs)

    async def __cache_signup_token(self, email: EmailStr, password: str, token: str):
        # TODO: region 記錄在???
        email_payload = {
            'email': email,
            'password': password,
            'auth_route': '/v1/signup',
        }
        await self.cache.set(token, email_payload, ex=REQUEST_INTERVAL_TTL)
        await self.cache.set(email, {'token': token}, ex=REQUEST_INTERVAL_TTL)

    '''
    email resend check
    '''

    async def __cache_check_for_token(self, email: str):
        data = await self.cache.get(email, True)
        if data and data.get('ttl', 0) > current_seconds():
            log.error(f'{self.cls_name}.__cache_check_for_resend:[too many reqeusts error],\
                email:%s, cache data:%s', email, data)
            raise TooManyRequestsException(
                msg='Frequently request.', data=self.ttl_secs)

        if not data or not 'token' in data:
            log.error(f'{self.cls_name}.__cache_check_for_resend:[no token error],\
                email:%s, cache data:%s', email, data)
            raise NotFoundException(msg='Email not found.')

        return data.get('token')

    '''
    signup_email_resend
    '''

    async def signup_email_resend(self, email: EmailStr):
        old_token = await self.__cache_check_for_token(email)
        auth_res = await self.req_send_signup_confirm_email(email)
        if not 'token' in auth_res:
            raise ServerException(msg='Signup fail', data=self.ttl_secs)

        new_token = auth_res['token']
        await self.regenerate_signup_token(old_token, new_token)

        data = self.ttl_secs.copy()
        if STAGE == TESTING:
            data.update({'token': new_token})
        return data

    async def regenerate_signup_token(self, old_token: str, new_token: str):
        data = await self.cache.get(old_token)
        # 一般 email 註冊快取 password；Google OAuth 註冊快取 oauth_id（見 google_oauth_service）
        if (
            not data
            or 'email' not in data
            or ('password' not in data and 'oauth_id' not in data)
        ):
            raise NotFoundException(msg='Email or password not found')

        await self.cache.set(new_token, data, ex=REQUEST_INTERVAL_TTL)
        await self.cache.delete(old_token)

        email = data.get('email')
        data = await self.cache.get(email)
        data.update({'token': new_token})
        await self.cache.set(email, data, ex=REQUEST_INTERVAL_TTL)

    # # return status_code, msg, err
    # async def __req_send_confirmcode_by_email(self, email: str, code: str):
    #     auth_res = await self.req.simple_post(f'{AUTH_SERVICE_URL}/v1/sendcode/email', json={
    #         'email': email,
    #         'code': code,
    #         'exist': False,
    #     })

    #     return auth_res

    # async def __cache_confirmcode(self, email: EmailStr, password: str, code: str):
    #     # TODO: region 記錄在???
    #     email_payload = {
    #         'email': email,
    #         'password': password,
    #         'code': code,
    #     }
    #     await self.cache.set(email, email_payload, ex=REQUEST_INTERVAL_TTL)

    '''
    confirm_signup
    '''

    async def confirm_signup(self, token: str):
        # xc email-payload: {email, password, region, auth_route}
        # google email-payload: {email, oauth_id, region, auth_route}
        email_payload: Dict = await self.cache.get(token)
        await self.verify_confirm_token(token, email_payload)

        auth_route = email_payload.pop('auth_route', None)
        if not auth_route:
            raise NotFoundException(msg='Auth route not found.')

        auth_url =  f'{AUTH_SERVICE_URL}{auth_route}'
        email_payload.update({"region": LOCAL_REGION})
        auth_res = await self.req.simple_post(
            url=auth_url,
            json=email_payload,
        )

        # init user profile
        user_id = auth_res.get('user_id', None)
        if user_id is None:
            raise ServerException(msg="signup fail", data=self.ttl_secs)

        await self.init_user_profile(user_id)
        # cache auth data（新帳號無舊 refresh 需撤銷；refresh 僅經 Set-Cookie，不進 JSON）
        prev = await self.cache.get(str(user_id))
        prev_rt = prev.get(REFRESH_TOKEN_KEY) if prev else None
        cookie_refresh = await self.cache_auth_res(
            str(user_id),
            auth_res,
            removed_fields={REFRESH_TOKEN_KEY},
            revoke_previous_refresh=prev_rt,
        )
        auth_res = self.apply_token(auth_res)
        auth_res = self.filter_auth_res(auth_res)
        if cookie_refresh:
            auth_res[REFRESH_TOKEN_KEY] = cookie_refresh
        return {
            'auth': auth_res,
        }

    async def init_user_profile(self, user_id: int):
        try:
            user_service_url = f"{USER_SERVICE_URL}/v1/{USERS}/profile"
            user_res = await self.req.simple_put(
                url=user_service_url,
                json={'user_id': user_id}
            )
            return user_res

        except Exception as e:
            log.error(f'{self.cls_name}.init_user_profile:[request exception], \
                user_id:%s, error:%s', user_id, e)
            err_msg = getattr(e, 'msg', 'Unable to initial user profile.')
            raise_http_exception(e, err_msg)

    async def verify_confirm_token(self, token: str, user: Dict):
        if not user or not 'email' in user:
            raise ClientException(msg='Invalid or expired token.')

        if user == {}:
            raise DuplicateUserException(msg='registering')

        await self.cache.delete(token)
        if 'email' in user:
            await self.cache.delete(user.get('email'))

    def __verify_confirmcode(self, code: str, user: Any):
        if not user or not 'code' in user:
            raise NotFoundException(msg='no signup data')

        if user == {}:
            raise DuplicateUserException(msg='registering')

        if code != str(user['code']):
            raise ClientException(msg='wrong confirm_code')

    def apply_token(self, res: Dict):
        # gen jwt token
        token = gen_token(res, ['region', 'user_id'])
        res.update({'token': token})
        return res

    def filter_auth_res(self, res: Dict):
        return {
            k: res[k]
            for k in res
            if k not in AUTH_RESPONSE_FIELDS and k != REFRESH_TOKEN_KEY
        }

    '''
    login preload process:
    若有機會在異地登入，則將登入流程改為 email 和 password 拆開：
        1) preload process API A => 用戶輸入 `email` => function login_preload_by_email
        2) preload process API B => 用戶輸入 `password` => login_preload_by_email_and_password (輸入其實包含 email 和 password; email 由前端緩存, 用戶以為只送 password)
    '''

    '''
    preload process API A:
    1. frontend: 用戶輸入 `email`
    2. backend: 透過 email 請求 `auth service` 存取[本地]用戶資料，
        若存在，則
            1) 緩存用戶資料(整個 table account, 包含 user_id, pass_hash, pass_salt)
            2) 返回 frontend: `200 OK` 
        若不存在，
            表示用戶不在本地，走 step 3
            
    3. backend: gateway 訪問 S3, 取得該 email 的註冊地，
        若存在於 S3，則
            1) 透過 email, 註冊地(從S3找到的) 請求 `auth service` 存取[註冊地]用戶資料 ([本地] auth service 透過 kakfa 取得遠端的用戶資料?????)
            2) 緩存用戶資料(整個 table account, 包含 user_id, pass_hash, pass_salt)
            3) 透過 user_id, current_region(gateway env param) 請求 `user service` 從註冊地異步的複製到`目前所在地`的資料庫([本地] user service 透過 kafka)
            4) 返回 frontend: `200 OK`
        若不存在於 S3，則
            表示用戶不存在，返回 frontend: `404 Not Found`
    '''

    # preload process API A => 用戶輸入 `email`(找用戶資料在哪裡)
    def login_preload_by_email(self, body: LoginDTO):
        pass

    '''
    preload process API B:
    4. frontend: 用戶輸入 `password`(輸入其實包含 email 和 password; email 由前端緩存, 用戶以為只送 password)
    5. backend:
        1) 在 gateway 透過緩存的用戶資料驗證密碼，
        2) 若密碼正確則允許登入，可在`目前所在地`存取用戶資料
        3) 刪除緩存的用戶[敏感]資料(pass_hash, pass_salt)
        此時不管用戶是否登入成功，該用戶資料早已 `透過 step 3` 複製到`目前所在地`的資料庫
    6. 將 region (registration region) 緩存至手機或網頁(local storage)
        以便及早做 step 2 (在異地複製用戶資料)
    '''

    # preload process API B => 用戶輸入 `password`(異步的複製資料；輸入其實包含 email 和 password)
    def login_preload_by_email_and_password(self, body: LoginDTO):
        pass

    '''
    login
    有了 login preload process, login 可一律視為本地登入
    '''

    async def login(self, body: LoginDTO, language: str = DEFAULT_LANGUAGE):
        auth_res = await self.__req_login(body)
        user_id = auth_res.get('user_id')
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
        auth_res = self.filter_auth_res(auth_res)
        if cookie_refresh:
            auth_res[REFRESH_TOKEN_KEY] = cookie_refresh
        return {
            'auth': auth_res,
            'user': user_res,
        }


    async def __req_login(self, body: LoginDTO):
        auth_res = await self.req.simple_post(
            f'{AUTH_SERVICE_URL}/v1/login', json=body.model_dump())
        if not auth_res or not 'user_id' in auth_res:
            raise UnauthorizedException(msg='Invalid user.')
        return auth_res

    async def get_user_profile(self, user_id: int, language: str):
        try:
            user_service_url = f"{USER_SERVICE_URL}/v1/{USERS}/{user_id}/{language}/profile"
            # 育志看一下這 API
            return await self.req.simple_get(user_service_url)

        except Exception as e:
            log.error(f'{self.cls_name}.get_user_profile:[request exception], \
                user_id:%s, error:%s', user_id, e)
            err_msg = getattr(e, 'msg', 'User not found.')
            raise_http_exception(e, err_msg)

    async def cache_auth_res(
        self,
        user_id_key: str,
        auth_res: Dict,
        removed_fields: Set = set(),
        revoke_previous_refresh: Optional[str] = None,
    ) -> Optional[str]:
        """寫入快取並從 auth_res 剔除敏感欄位。若 removed_fields 含 refresh_token，回傳該值供 auth_response 設 HttpOnly cookie。

        並維護 Redis `rt:{refresh}` -> user_id_key，供 OAuth refresh grant 查詢；輪替或重登時傳 revoke_previous_refresh 撤銷舊索引。
        """
        if revoke_previous_refresh:
            await self.cache.delete(_refresh_token_index_key(revoke_previous_refresh))

        auth_res.update({
            'online': True,
            REFRESH_TOKEN_KEY: gen_refresh_token(),
        })
        new_refresh = auth_res.get(REFRESH_TOKEN_KEY)
        updated = await self.cache.set(
            user_id_key, auth_res, ex=LONG_TERM_TTL)
        if not updated:
            log.error(f'{self.cls_name}.__cache_auth_res fail: [cache set],\
                user_id_key:%s, auth_res:%s, ex:%s, cache data:%s',
                      user_id_key, auth_res, LONG_TERM_TTL, updated)
            raise ServerException(msg='server_error')

        await self.cache.set(
            _refresh_token_index_key(new_refresh),
            user_id_key,
            ex=LONG_TERM_TTL,
        )

        # remove sensitive data: 'aid' & removed_fields
        to_remove = set(removed_fields)
        to_remove.add('aid')
        cookie_refresh: Optional[str] = None
        if REFRESH_TOKEN_KEY in to_remove:
            cookie_refresh = auth_res.get(REFRESH_TOKEN_KEY)
        for field in to_remove:
            auth_res.pop(field, None)
        return cookie_refresh

    '''
    gen new token and refresh_token
    '''

    async def get_new_token_pair(self, refresh_token: str) -> Dict:
        """OAuth 2.0 refresh_token grant：僅依 refresh_token 查 session 並輪替 refresh（rotation）。"""
        user_id_key = await self.cache.get(_refresh_token_index_key(refresh_token))
        if not user_id_key:
            raise UnauthorizedException(msg='invalid_grant')

        user = await self.cache.get(user_id_key)
        if not user:
            await self.cache.delete(_refresh_token_index_key(refresh_token))
            raise UnauthorizedException(msg='invalid_grant')

        cached_refresh_token = user.get(REFRESH_TOKEN_KEY, None)
        if cached_refresh_token != refresh_token or not valid_refresh_token(cached_refresh_token):
            raise UnauthorizedException(msg='invalid_grant')

        await self.cache_auth_res(
            user_id_key,
            user,
            revoke_previous_refresh=refresh_token,
        )
        res = self.apply_token(user)
        new_rt = user.get(REFRESH_TOKEN_KEY)
        auth_res = {k: res[k] for k in ['user_id', 'token'] if k in res}
        if new_rt:
            auth_res[REFRESH_TOKEN_KEY] = new_rt
        return {
            'auth': auth_res,
        }

    '''
    logout
    '''

    async def logout(self, user_id: int):
        user_id_key = str(user_id)
        user = await self.__cache_check_for_auth(user_id_key)
        prev_rt = user.get(REFRESH_TOKEN_KEY)
        if prev_rt:
            await self.cache.delete(_refresh_token_index_key(prev_rt))
        user_logout_status = self.__logout_status(user)

        # 'LONG_TERM_TTL' for redirct notification
        await self.__cache_logout_status(user_id_key, user_logout_status)
        return (None, 'successfully logged out')

    @staticmethod
    async def is_login(cache: ICache, visitor: BaseAuthDTO = None) -> (bool):
        if visitor is None:
            return False

        user_id_key = str(visitor.user_id)
        user: Dict = cache.get(user_id_key)
        if user is None:
            return False

        return user.get('online', False)

    async def __cache_check_for_auth(self, user_id_key: str):
        user = await self.cache.get(user_id_key)
        if not user or not user.get('online', False):
            raise ClientException(msg='logged out')

        return user

    def __logout_status(self, user: Dict):
        user_id = user['user_id']
        region = user.get('region', None)

        return {
            'user_id': user_id,
            'region': region,
            'online': False,
        }

    async def __cache_logout_status(self, user_id_key: str, user_logout_status: Dict):
        updated = await self.cache.set(
            user_id_key, user_logout_status, ex=LONG_TERM_TTL)
        if not updated:
            log.error(f'{self.cls_name}.__cache_logout_status fail: [cache set],\
                user_id_key:%s, user_logout_status:%s, ex:%s, cache data:%s',
                      user_id_key, user_logout_status, LONG_TERM_TTL, updated)
            raise ServerException(msg='server_error')

    '''
    password
    '''

    async def send_reset_password_comfirm_email(self, email: EmailStr):
        await self.__cache_check_for_reset_password(email)
        data = await self.__req_send_reset_password_comfirm_email(email)
        if data != None and 'token' in data:
            token = data['token']
            await self.__cache_token_by_reset_password(token, email)
        else:
            token = email + ':not_exist'

        data = self.ttl_secs.copy()
        if STAGE == TESTING:
            data.update({'token': token})
        return data

    async def reset_passwrod(self, verify_token: str, body: ResetPasswordBodyDTO):
        """Email 僅由 cache (verify_token -> email) 取得，不依賴 client 傳入，降低資安風險。"""
        checked_email = await self.cache.get(verify_token)
        if not checked_email:
            raise UnauthorizedException(msg='invalid token')
        payload = ResetPasswordDTO(
            register_email=checked_email,
            password=body.password,
            confirm_password=body.confirm_password,
        )
        await self.__req_reset_password(payload)
        await self.__cache_remove_by_reset_password(verify_token, checked_email)

    async def __cache_check_for_reset_password(self, email: EmailStr):
        data = await self.cache.get(f'reset_pw:{email}', True)
        if data and data.get('ttl', 0) > current_seconds():
            log.error(f'{self.cls_name}.__cache_check_for_reset_password:[too many reqeusts error],\
                email:%s, cache data:%s', email, data)
            raise TooManyRequestsException(
                msg='frequently request', data=self.ttl_secs)

        if data:
            await self.cache.delete(f'reset_pw:{email}')
            # 將用不到的 verify_token 刪除
            verify_token = data.get('token', None)
            if verify_token:
                await self.cache.delete(verify_token)

    async def __cache_token_by_reset_password(self, verify_token: str, email: EmailStr):
        await self.cache.set(f'reset_pw:{email}', {'token': verify_token}, REQUEST_INTERVAL_TTL)
        await self.cache.set(verify_token, email, REQUEST_INTERVAL_TTL)

    async def __cache_remove_by_reset_password(self, verify_token: str, email: EmailStr):
        await self.cache.delete(f'reset_pw:{email}')
        await self.cache.delete(verify_token)

    async def update_password(self, user_id: int, body: UpdatePasswordDTO):
        await self.__cache_check_for_email_validation(user_id, body.register_email)
        await self.__req_update_password(body)

    async def __req_send_reset_password_comfirm_email(self, email: EmailStr):
        try:
            return await self.req.simple_get(f'{AUTH_SERVICE_URL}/v1/password/reset/email', params={'email': email})
        except Exception as e:
            log.error(f'{self.cls_name}.__req_send_reset_password_comfirm_email:[request exception], \
                host:%s, email:%s, error:%s', AUTH_SERVICE_URL, email, e)
            return None

    async def __cache_check_for_email_validation(self, user_id: int, register_email: EmailStr):
        user_id_key = str(user_id)
        data = await self.cache.get(user_id_key)
        if data is None or not 'email' in data or str(register_email) != data['email']:
            raise UnauthorizedException(msg='invalid email')

    async def __req_update_password(self, body: UpdatePasswordDTO):
        return await self.req.simple_put(
            f'{AUTH_SERVICE_URL}/v1/password/update', json=body.model_dump())

    async def __req_reset_password(self, body: ResetPasswordDTO):
        return await self.req.simple_put(
            f'{AUTH_SERVICE_URL}/v1/password/update', json=body.model_dump())

    '''
    delete account
    '''

    async def delete_account(self, body: DeleteAccountDTO):
        user_id = body.user_id
        email = body.email

        # 1. Step-up: determine account_type and verify identity
        account_type = None
        cached_data = await self.cache.get(str(user_id))
        if cached_data:
            account_type = cached_data.get('account_type')
            cached_email = cached_data.get('email')
            if not cached_email or cached_email != email:
                raise UnauthorizedException(msg='Email does not match current session')
        else:
            raise UnauthorizedException(msg='Invalid session')

        if account_type is None:
            if body.password:
                account_type = 'XC'
            elif body.id_token:
                account_type = 'GOOGLE'

        if account_type == 'XC':
            if not body.password:
                raise UnauthorizedException(msg='Password is required for XC account')
            login_body = LoginDTO(email=email, password=body.password)
            await self.__req_login(login_body)
        elif account_type == 'GOOGLE':
            if not body.id_token:
                raise UnauthorizedException(msg='id_token is required for Google account')
            await self.__verify_google_id_token(body.id_token, email)
        else:
            raise UnauthorizedException(msg='Unable to determine account type')

        # 2. Reservation blocking check
        res = await self.req.simple_get(
            f'{USER_SERVICE_URL}/v1/internal/users/{user_id}/has-active-reservations')
        if res and res.get('has_active'):
            raise ConflictException(
                msg='尚有未結束或未來的預約，無法刪除帳號。請先取消或處理相關預約後再試。',
                code='ACCOUNT_DELETE_BLOCKED_ACTIVE_RESERVATIONS',
            )

        # 3. Delete user data (Postgres + SQS if mentor)
        await self.req.simple_delete(
            url=f'{USER_SERVICE_URL}/v1/internal/users/{user_id}')

        # 4. Delete auth account (DynamoDB)
        try:
            await self.req.simple_delete(
                url=f'{AUTH_SERVICE_URL}/v1/accounts',
                json={"email": email})
        except Exception as e:
            log.error(
                f'{self.cls_name}.delete_account: Auth deletion failed after User deletion succeeded. '
                f'user_id={user_id}, email={email}, error={e}. Manual compensation required.'
            )
            raise ServerException(msg='Account deletion partially failed. Please contact support.')

        # 5. Clear BFF cache
        rt = cached_data.get(REFRESH_TOKEN_KEY) if cached_data else None
        if rt:
            await self.cache.delete(_refresh_token_index_key(rt))
        await self.cache.delete(str(user_id))

    async def __verify_google_id_token(self, id_token: str, email: str):
        try:
            tokeninfo = await self.req.simple_get(
                'https://oauth2.googleapis.com/tokeninfo',
                params={'id_token': id_token},
            )
            if not tokeninfo:
                raise UnauthorizedException(msg='Google identity verification failed')

            token_email = tokeninfo.get('email')
            if token_email != email:
                raise UnauthorizedException(msg='Google identity verification failed')

            # Google tokeninfo returns audience in `aud`.
            aud = tokeninfo.get('aud')
            if aud != GOOGLE_CLIENT_ID:
                raise UnauthorizedException(msg='Google identity verification failed')

            iss = tokeninfo.get('iss')
            if iss not in {'accounts.google.com', 'https://accounts.google.com'}:
                raise UnauthorizedException(msg='Google identity verification failed')

            exp = tokeninfo.get('exp')
            if not exp or int(exp) <= current_seconds():
                raise UnauthorizedException(msg='Google identity verification failed')

            # tokeninfo may return string values like "true"
            if str(tokeninfo.get('email_verified', '')).lower() != 'true':
                raise UnauthorizedException(msg='Google identity verification failed')
        except Exception as e:
            log.error(f'{self.cls_name}.__verify_google_id_token failed, email={email}, err={e}')
            err_msg = getattr(e, 'msg', 'Google identity verification failed')
            raise UnauthorizedException(msg=err_msg)

from typing import Any, List, Dict
from ....router.req.authorization import (
    gen_token, 
    gen_refresh_token, 
    valid_refresh_token,
)
from ..model.auth_model import *
from ...cache import ICache
from ...service_api import IServiceApi
from ....infra.util.util import gen_confirm_code
from ....infra.util.time_util import gen_timestamp
from ....config.conf import *
from ....config.constant import PREFETCH
from ....config.exception import *
import logging as log

log.basicConfig(filemode='w', level=log.INFO)


class AuthService:
    def __init__(self, req: IServiceApi, cache: ICache):
        self.__cls_name = self.__class__.__name__
        self.req = req
        self.cache = cache

    '''
    signup
    '''

    async def signup(self, host: str, body: SignupDTO):
        email = body.email
        self.__cache_check_for_duplicates(email)

        code = gen_confirm_code()
        status_code = self.__req_send_confirmcode_by_email(
            host, email, code)

        if status_code <= 200:
            self.__cache_confirmcode(email, body.password, code)

            # FIXME: remove the res here('code') during production
            return {
                'for_testing_only': code
            }

        else:
            self.cache.set(email, {'avoid_freq_email_req_and_hit_db': 1}, SHORT_TERM_TTL)
            raise DuplicateUserException(msg='email_registered')

    def __cache_check_for_duplicates(self, email: str):
        data = self.cache.get(email)
        if data:
            log.error(f'{self.__cls_name}.__cache_check_for_duplicates:[business error],\
                email:%s, cache data:%s', email, data)
            raise DuplicateUserException(msg='registered or registering')

    def __req_send_confirmcode_by_email(self, host: str, email: str, code: str):
        auth_res, msg, status_code, err = self.req.post_with_statuscode(f'{host}/sendcode/email', json={
            'email': email,
            'code': code,
            'exist': False,
        })
        log.info(f'__req_send_confirmcode_by_email auth_res: %s, msg: %s, status_code: %d, err: %s', auth_res, msg, status_code, err)
        
        if status_code >= 400 or msg or err:
            log.error(f'{self.__cls_name}.__req_send_confirmcode_by_email:[request exception], \
                host:%s, email:%s, code:%s, auth_res:%s, msg:%s, status_code:%s, err:%s',
                host, email, code, auth_res, msg, status_code, err)
            self.cache.set(email, {'avoid_freq_email_req_and_hit_db': 1}, SHORT_TERM_TTL)

        return status_code

    def __cache_confirmcode(self, email: EmailStr, password: str, code: str):
        # TODO: region 記錄在???
        email_playload = {
            'email': email,
            'password': password,
            'code': code,
        }
        self.cache.set(email, email_playload, ex=SHORT_TERM_TTL)

    '''
    confirm_signup
    '''

    async def confirm_signup(self, host: str, body: SignupConfirmDTO):
        email = body.email
        code = body.code
        # user: {email, passowrd, code}
        user = self.cache.get(email)
        self.__verify_confirmcode(code, user)

        # 'registering': empty data, but TTL=30sec
        self.cache.set(email, {}, ex=30)
        auth_res = self.req.simple_post(f'{host}/signup',
                                        json={
                                            'region': body.region,
                                            'email': email,
                                            'password': user['password'],
                                        })

        user_id_key = str(auth_res['user_id'])
        self.cache_auth_res(user_id_key, auth_res)
        auth_res = self.apply_token(auth_res)
        return {'auth': auth_res}

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
    def login_preload_by_email(self, auth_host: str, body: LoginDTO):
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
    def login_preload_by_email_and_password(self, auth_host: str, user_host: str, body: LoginDTO):
        pass


    '''
    login
    有了 login preload process, login 可一律視為本地登入
    '''

    async def login(self, auth_host: str, user_host: str, body: LoginDTO):
        auth_res = self.__req_login(auth_host, body)

        # cache auth data
        user_id_key = str(auth_res['user_id'])
        self.cache_auth_res(user_id_key, auth_res)
        auth_res = self.apply_token(auth_res)

        # request user/professional data
        user_res = None
        # TODO: user service API 尚未調整
        # self.req_user_data(
        #     user_host,
        #     user_id_key,
        # )

        return {
            'auth': auth_res,
            'user': user_res,
        }

    def __req_login(self, auth_host: str, body: LoginDTO):
        return self.req.simple_post(
            f'{auth_host}/login', json=body.dict())
        

    def cache_auth_res(self, user_id_key: str, auth_res: Dict):
        auth_res.update({
            'online': True,
            'refresh_token': gen_refresh_token(),
        })
        updated = self.cache.set(
            user_id_key, auth_res, ex=LONG_TERM_TTL)
        if not updated:
            log.error(f'{self.__cls_name}.__cache_auth_res fail: [cache set],\
                user_id_key:%s, auth_res:%s, ex:%s, cache data:%s',
                user_id_key, auth_res, LONG_TERM_TTL, updated)
            raise ServerException(msg='server_error')
        
        # remove sensitive data: aid
        auth_res.pop('aid', None)


    def req_user_data(self, user_host: str, user_id_key: str):            
        user_res = self.req.simple_get(
            # TODO: user service API 尚未調整
            url=f'{user_host}{user_id_key}/userdata',
            params={
                'size': size,
            }
        )

        return user_res


    '''
    gen new token and refresh_token
    '''
    async def get_new_token_pair(self, body: NewTokenDTO) -> (str):
        user_id_key = str(body.user_id)
        user = self.cache.get(user_id_key)
        if not user:
            raise UnauthorizedException(msg='Invalid user')
        
        cached_refresh_token = user.get('refresh_token', None)
        if cached_refresh_token != body.refresh_token or \
            not valid_refresh_token(cached_refresh_token):
            raise UnauthorizedException(msg='Invalid User')

        self.cache_auth_res(user_id_key, user)
        res = self.apply_token(user)
        return {k: res[k] for k in ['token', 'refresh_token'] if k in res}


    '''
    logout
    '''

    async def logout(self, user_id: int):
        user_id_key = str(user_id)
        user = self.__cache_check_for_auth(user_id_key)
        user_logout_status = self.__logout_status(user)

        # 'LONG_TERM_TTL' for redirct notification
        self.__cache_logout_status(user_id_key, user_logout_status)
        return (None, 'successfully logged out')
    
    @staticmethod
    def is_login(cache: ICache, visitor: BaseAuthDTO = None) -> (bool):
        if visitor is None:
            return False

        user_id_key = str(visitor.user_id)
        user: Dict = cache.get(user_id_key)
        if user is None:
            return False

        return user.get('online', False)

    def __cache_check_for_auth(self, user_id_key: str):
        user = self.cache.get(user_id_key)
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

    def __cache_logout_status(self, user_id_key: str, user_logout_status: Dict):
        updated = self.cache.set(
            user_id_key, user_logout_status, ex=LONG_TERM_TTL)
        if not updated:
            log.error(f'{self.__cls_name}.__cache_logout_status fail: [cache set],\
                user_id_key:%s, user_logout_status:%s, ex:%s, cache data:%s',
                user_id_key, user_logout_status, LONG_TERM_TTL, updated)
            raise ServerException(msg='server_error')

    '''
    password
    '''
    async def send_reset_password_comfirm_email(self, auth_host: str, email: EmailStr):
        self.__cache_check_for_reset_password(email)
        data = self.__req_send_reset_password_comfirm_email(auth_host, email)
        if data != None and 'token' in data:
            token = data['token']
        else:
            token = email + ':not_exist'
        
        self.__cache_token_by_reset_password(token, email)
        #TEST: log
        return f'''send_email_success {token}'''

    async def reset_passwrod(self, auth_host: str, verify_token: str, body: ResetPasswordDTO):
        checked_email = self.cache.get(verify_token)
        if not checked_email:
            raise UnauthorizedException(msg='invalid token') 
        if checked_email != body.register_email:
            raise UnauthorizedException(msg='invalid user')
        self.__req_reset_password(auth_host, body)
        self.__cache_remove_by_reset_password(verify_token, checked_email)

    
    def __cache_check_for_reset_password(self, email: EmailStr):
        data = self.cache.get(f'{email}:reset_pw')
        if data:
            log.error(f'{self.__cls_name}.__cache_check_for_reset_password:[too many reqeusts error],\
                email:%s, cache data:%s', email, data)
            raise TooManyRequestsException(msg='frequent_requests')
    
    def __cache_token_by_reset_password(self, verify_token: str, email: EmailStr):
        self.cache.set(f'{email}:reset_pw', '1', REQUEST_INTERVAL_TTL)
        self.cache.set(verify_token, email, SHORT_TERM_TTL)
        
    def __cache_remove_by_reset_password(self, verify_token: str, email: EmailStr):
        self.cache.delete(f'{email}:reset_pw')
        self.cache.delete(verify_token)
        

    async def update_password(self, auth_host: str, user_id: int, body: UpdatePasswordDTO):
        self.__cache_check_for_email_validation(user_id, body.register_email)
        self.__req_update_password(auth_host, body)

    def __req_send_reset_password_comfirm_email(self, auth_host: str, email: EmailStr):
        try:
            return self.req.simple_get(f'{auth_host}/password/reset/email', params={'email': email}) 
        except Exception as e:
            log.error(f'{self.__cls_name}.__req_send_reset_password_comfirm_email:[request exception], \
                host:%s, email:%s, error:%s', auth_host, email, e)
            return None

    def __cache_check_for_email_validation(self, user_id: int, register_email: EmailStr):
        user_id_key = str(user_id)
        data = self.cache.get(user_id_key)
        if data is None or not 'email' in data or str(register_email) != data['email']:
            raise UnauthorizedException(msg='invalid email')

    def __req_update_password(self, auth_host: str, body: UpdatePasswordDTO):
        return self.req.simple_put(
            f'{auth_host}/password/update', json=body.dict())

    def __req_reset_password(self, auth_host: str, body: ResetPasswordDTO):
        return self.req.simple_put(
            f'{auth_host}/password/update', json=body.dict()) 
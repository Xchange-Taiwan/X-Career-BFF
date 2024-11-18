from typing import Any, List, Dict, Tuple
from ....router.req.authorization import (
    gen_token, 
    gen_refresh_token, 
    valid_refresh_token,
)
from ..model.auth_model import *
from ...cache import ICache
from ....app.template.service_api import IServiceApi
from ....infra.util.util import gen_confirm_code
from ....infra.util.time_util import gen_timestamp, current_seconds
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
        self.ttl_secs = {'ttl_secs': REQUEST_INTERVAL_TTL}


    '''
    signup
    '''
    async def signup(self, host: str, body: SignupDTO):
        email = body.email
        self.__cache_check_for_signup(email)
        auth_res = self.__req_send_signup_confirm_email(host, email)
        if not 'token' in auth_res:
            raise ServerException(msg='signup fail', data=self.ttl_secs)

        token = auth_res['token']
        self.__cache_signup_token(email, body.password, token)
        data = self.ttl_secs.copy()
        if STAGE == TESTING:
            data.update({'token': token})
        return data


    def __cache_check_for_signup(self, email: str):
        data = self.cache.get(email, True)
        if data and data.get('ttl', 0) > current_seconds():
            log.error(f'{self.__cls_name}.__cache_check_for_signup:[too many reqeusts error],\
                email:%s, cache data:%s', email, data)
            raise TooManyRequestsException(msg='frequently request', data=self.ttl_secs)
        
        if data:
            self.cache.delete(email)
            if 'token' in data:
                self.cache.delete(data.get('token'))


    # return status_code, msg, err
    def __req_send_signup_confirm_email(self, host: str, email: str):
        try:
            auth_res = self.req.simple_post(f'{host}/v1/signup/email', json={
                'email': email,
                'exist': False,
            })
            return auth_res

        except NotAcceptableException or DuplicateUserException as e:
            self.cache.set(email, {}, ex=REQUEST_INTERVAL_TTL)
            raise DuplicateUserException(msg='Email registered.', data=self.ttl_secs)

        except Exception as e:
            log.error(f'{self.__cls_name}.__req_send_signup_confirm_email:[request exception], \
                host:%s, email:%s, error:%s', host, email, e)
            self.cache.set(email, {}, ex=REQUEST_INTERVAL_TTL)
            raise_http_exception(e, 'Email could not be delivered.', data=self.ttl_secs)
            


    def __cache_signup_token(self, email: EmailStr, password: str, token: str):
        # TODO: region 記錄在???
        email_playload = {
            'email': email,
            'password': password,
        }
        self.cache.set(token, email_playload, ex=REQUEST_INTERVAL_TTL)
        self.cache.set(email, {'token':token}, ex=REQUEST_INTERVAL_TTL)

    '''
    email resend check
    '''
    def __cache_check_for_token(self, email: str):
        data = self.cache.get(email, True)
        if data and data.get('ttl', 0) > current_seconds():
            log.error(f'{self.__cls_name}.__cache_check_for_resend:[too many reqeusts error],\
                email:%s, cache data:%s', email, data)
            raise TooManyRequestsException(msg='Frequently request.', data=self.ttl_secs)
        
        if not data or not 'token' in data:
            log.error(f'{self.__cls_name}.__cache_check_for_resend:[no token error],\
                email:%s, cache data:%s', email, data)
            raise NotFoundException(msg='Email not found.')

        return data.get('token')

    '''
    signup_email_resend
    '''
    async def signup_email_resend(self, host: str, email: EmailStr):
        old_token = self.__cache_check_for_token(email)
        auth_res = self.__req_send_signup_confirm_email(host, email)
        if not 'token' in auth_res:
            raise ServerException(msg='Signup fail', data=self.ttl_secs)

        new_token = auth_res['token']
        self.regenerate_signup_token(old_token, new_token)
        
        data = self.ttl_secs.copy()
        if STAGE == TESTING:
            data.update({'token': new_token})
        return data

    def regenerate_signup_token(self, old_token: str, new_token: str):
        data = self.cache.get(old_token)
        if not data or not 'email' in data or not 'password' in data:
            raise NotFoundException(msg='Email or password not found')
        
        self.cache.set(new_token, data, ex=REQUEST_INTERVAL_TTL)
        self.cache.delete(old_token)

        email = data.get('email')
        data = self.cache.get(email)
        data.update({'token': new_token})
        self.cache.set(email, data, ex=REQUEST_INTERVAL_TTL)


    # return status_code, msg, err
    def __req_send_confirmcode_by_email(self, host: str, email: str, code: str):
        auth_res = self.req.simple_post(f'{host}/v1/sendcode/email', json={
            'email': email,
            'code': code,
            'exist': False,
        })

        return auth_res

    def __cache_confirmcode(self, email: EmailStr, password: str, code: str):
        # TODO: region 記錄在???
        email_playload = {
            'email': email,
            'password': password,
            'code': code,
        }
        self.cache.set(email, email_playload, ex=REQUEST_INTERVAL_TTL)

    '''
    confirm_signup
    '''

    async def confirm_signup(self, host: str, token):
        # token: {email, passowrd}
        user = self.cache.get(token)
        self.__verify_confirm_token(token, user)

        # 'registering': empty data
        email = user.get('email', None)
        auth_res = self.req.simple_post(f'{host}/v1/signup',
                                        json={
                                            'region': LOCAL_REGION,
                                            'email': email,
                                            'password': user['password'],
                                        })
        user_res = self.req.simple_post(f'{user_host}/mentors/mentor_profile/create',
                                        json={
                                            'region': body.region,
                                            'email': body:,
                                        })

        user_id_key = str(auth_res['user_id'])
        self.cache_auth_res(user_id_key, auth_res)
        auth_res = self.apply_token(auth_res)
        auth_res = self.filter_auth_res(auth_res)
        return {'auth': auth_res}
    
    def __verify_confirm_token(self, token: str, user: Dict):
        if not user or not 'email' in user:
            raise ClientException(msg='Invalid or expired token.')

        if user == {}:
            raise DuplicateUserException(msg='registering')

        self.cache.delete(token)
        if 'email' in user:
            self.cache.delete(user.get('email'))


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
        return {k: res[k] for k in res if not k in AUTH_RESPONSE_FIELDS}
    
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
        auth_res = self.filter_auth_res(auth_res)

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
            f'{auth_host}/v1/login', json=body.dict())
        

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
        data = self.ttl_secs.copy()
        if STAGE == TESTING:
            data.update({'token': token})
        return data

    async def reset_passwrod(self, auth_host: str, verify_token: str, body: ResetPasswordDTO):
        checked_email = self.cache.get(verify_token)
        if not checked_email:
            raise UnauthorizedException(msg='invalid token') 
        if checked_email != body.register_email:
            raise UnauthorizedException(msg='invalid user')
        self.__req_reset_password(auth_host, body)
        self.__cache_remove_by_reset_password(verify_token, checked_email)

    
    def __cache_check_for_reset_password(self, email: EmailStr):
        data = self.cache.get(f'reset_pw:{email}', True)
        if data and data.get('ttl', 0) > current_seconds():
            log.error(f'{self.__cls_name}.__cache_check_for_reset_password:[too many reqeusts error],\
                email:%s, cache data:%s', email, data)
            raise TooManyRequestsException(msg='frequently request', data=self.ttl_secs)
        
        if data:
            self.cache.delete(f'reset_pw:{email}')
            # 將用不到的 verify_token 刪除
            verify_token = data.get('token', None)
            if verify_token:
                self.cache.delete(verify_token)


    def __cache_token_by_reset_password(self, verify_token: str, email: EmailStr):
        self.cache.set(f'reset_pw:{email}', {'token':verify_token}, REQUEST_INTERVAL_TTL)
        self.cache.set(verify_token, email, REQUEST_INTERVAL_TTL)
        
    def __cache_remove_by_reset_password(self, verify_token: str, email: EmailStr):
        self.cache.delete(f'reset_pw:{email}')
        self.cache.delete(verify_token)
        

    async def update_password(self, auth_host: str, user_id: int, body: UpdatePasswordDTO):
        self.__cache_check_for_email_validation(user_id, body.register_email)
        self.__req_update_password(auth_host, body)

    def __req_send_reset_password_comfirm_email(self, auth_host: str, email: EmailStr):
        try:
            return self.req.simple_get(f'{auth_host}/v1/password/reset/email', params={'email': email}) 
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
            f'{auth_host}/v1/password/update', json=body.dict())

    def __req_reset_password(self, auth_host: str, body: ResetPasswordDTO):
        return self.req.simple_put(
            f'{auth_host}/v1/password/update', json=body.dict()) 
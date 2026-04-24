# 刪除帳號（Delete Account）— Task Breakdown

> 狀態：Draft  
> 依賴：`plan.md`、`spec.md`（同目錄）  
> 開發順序：Phase 1 → 2 → 3（X-Career-User）→ Phase 4（X-Career-Auth）→ Phase 5（X-Career-BFF）→ Phase 6（驗收）

---

## Phase 1 — X-Career-User：Repository 層

### 1-A　`reservation_repository.py` — 新增阻擋查詢

- [ ] **T-1** `X-Career-User/src/domain/user/dao/reservation_repository.py`
  - 新增方法 `has_active_or_future_reservations(self, db: AsyncSession, user_id: int) -> bool`
  - 需新增 import：`from sqlalchemy import exists`（現有已有 `and_`、`select` 等）
  - `current_seconds` 已透過 `from src.infra.db.orm.init.user_init import *` 間接引入（`user_init.py` 有 `from src.infra.util.time_util import current_seconds`），**無需額外 import**
  - 使用 SQLAlchemy `exists()` + `scalar()` **單次查詢**（不回傳 list）：
    ```python
    stmt = select(exists().where(
        and_(
            Reservation.my_user_id == user_id,
            Reservation.dtend >= current_seconds(),
            Reservation.my_status != BookingStatus.REJECT,
            Reservation.status != BookingStatus.REJECT,
        )
    ))
    result = await db.scalar(stmt)
    return bool(result)
    ```
  - 與 `get_user_reservations` 中 UPCOMING／PENDING 的過濾語意對齊（見 spec.md §3）

### 1-B　`mentor_experience_repository.py` — 新增批次刪除

- [ ] **T-2** `X-Career-User/src/domain/user/dao/mentor_experience_repository.py`
  - 新增方法 `delete_all_by_user_id(self, db: AsyncSession, user_id: int) -> int`
  - 使用 `delete(MentorExperience).where(MentorExperience.user_id == user_id)` 批次刪除
  - 回傳刪除列數（`result.rowcount`）；0 列也視為成功（冪等）
  - **不** `commit()`，由上層 Application 統一 commit

### 1-C　`schedule_repository.py` — 新增批次刪除

- [ ] **T-3** `X-Career-User/src/domain/mentor/dao/schedule_repository.py`
  - 新增方法 `delete_all_by_user_id(self, db: AsyncSession, user_id: int) -> int`
  - 使用 `delete(MentorSchedule).where(MentorSchedule.user_id == user_id)` 批次刪除
  - 回傳刪除列數；0 列也視為成功（冪等）
  - **不** `commit()`，由上層 Application 統一 commit

### 1-D　`profile_repository.py` — 新增 `find_by_user_id`、修正 `delete_profile`

- [ ] **T-4** `X-Career-User/src/domain/user/dao/profile_repository.py`
  - 檔案頂部新增 import：`from sqlalchemy import delete, select, Select`（現有只有 `select, Select`，需加 `delete`）
  - **新增方法** `find_by_user_id`（供 `DeleteAccount` 冪等判斷使用，不拋例外）：
    ```python
    async def find_by_user_id(self, db: AsyncSession, user_id: int) -> Optional[ProfileDTO]:
        stmt: Select = select(Profile).filter(Profile.user_id == user_id)
        query: Optional[Profile] = await get_first_template(db, stmt)
        if query is None:
            return None
        return ProfileDTO.model_validate(query)
    ```
    > 現有 `get_by_user_id` 在查無資料時會 `raise NotFoundException`，不適用於刪帳的冪等場景（profile 已刪時應視為成功而非報錯）。
  - **修正** `delete_profile`：現有版本有兩個問題：
    1. `get_first_template(db, stmt)` 缺少 `await`（bug）
    2. 自帶 `db.commit()`，與 `DeleteAccount` 的「統一 commit」設計衝突
  - 修正並調整簽名為 `delete_profile(self, db: AsyncSession, user_id: int) -> None`：
    ```python
    stmt = delete(Profile).where(Profile.user_id == user_id)
    await db.execute(stmt)
    # 不 commit，由上層統一 commit
    ```
  - 移除原先的 `select → db.delete(mentor) → db.commit()` 模式
  - **確認**：現有程式碼中**無其他 caller** 呼叫 `delete_profile`，改簽名（`user_id: str` → `int`）不會破壞現有功能
  - **注意**：改用 `delete()` statement 前，需確認 Profile ORM 無 `cascade="all, delete-orphan"` relationship 依賴 ORM-aware 刪除。若有 cascade relationship，應保留 ORM-aware 方式（先 `await get_first_template(db, stmt)` 取得 entity 再 `await db.delete(entity)`），但修正缺失的 `await` 並移除 `db.commit()`

### 1-E　`canned_message` — 新增 Repository

- [ ] **T-5** `X-Career-User/src/domain/mentor/dao/canned_message_repository.py`（`CannedMessageDTO` 位於 `mentor/model/mentor_model.py`，故 Repository 置於 `mentor/dao/`）
  - 新增檔案 `canned_message_repository.py`
  - 實作 `delete_all_by_user_id(self, db: AsyncSession, user_id: int) -> int`：
    ```python
    stmt = delete(CannedMessage).where(CannedMessage.user_id == user_id)
    result = await db.execute(stmt)
    return result.rowcount
    # 不 commit
    ```

### 1-F　`file_repository.py` — 新增軟刪除

- [ ] **T-5.5** `X-Career-User/src/domain/file/dao/file_repository.py`
  - 新增方法 `soft_delete_all_by_user_id(self, db: AsyncSession, user_id: int) -> int`：
    ```python
    stmt = update(FileInfo).where(
        FileInfo.create_user_id == user_id
    ).values(is_deleted=True)
    result = await db.execute(stmt)
    return result.rowcount
    # 不 commit
    ```
  - 若 `FileInfo` ORM model 中欄位名稱不同，依實際 ORM 調整
  - S3 物件由排程或 lifecycle 清除，此處僅做 DB 軟刪

### 1-G　`reservation_repository.py` — 新增帳號刪除用的匿名化方法

- [ ] **T-6** `X-Career-User/src/domain/user/dao/reservation_repository.py`
  - 需新增 import：`from sqlalchemy import update`（現有已有 `update`，確認即可）
  - 新增方法 `anonymize_by_my_user_id(self, db: AsyncSession, user_id: int) -> int`（自身視角匿名化）：
    ```python
    stmt = update(Reservation).where(
        Reservation.my_user_id == user_id
    ).values(my_user_id=-user_id)
    result = await db.execute(stmt)
    return result.rowcount
    # 不 commit
    ```
  - 將自身視角的 `my_user_id` 設為 **`-user_id`**（負數 sentinel value），**保留歷史記錄**供稽核
  - 使用 `-user_id` 而非固定值 `0`，避免多位已刪除使用者匿名化後違反 `uidx_reservation_user_dtstart_dtend_schedule_id_user_id` unique index（見 spec.md §7）
  - 前端 / 後端可透過 `my_user_id < 0` 判斷「已刪除使用者」，並以 `abs(my_user_id)` 反推原始 user_id 供稽核
  - 回傳更新列數；0 列也視為成功（冪等）；**不** `commit()`

- [ ] **T-6.5** `X-Career-User/src/domain/user/dao/reservation_repository.py`
  - 新增方法 `anonymize_by_user_id(self, db: AsyncSession, user_id: int) -> int`（對方視角匿名化）：
    ```python
    stmt = update(Reservation).where(
        Reservation.user_id == user_id
    ).values(user_id=-user_id)
    result = await db.execute(stmt)
    return result.rowcount
    # 不 commit
    ```
  - 將**對方**預約記錄中引用已刪除使用者的 `user_id` 設為 **`-user_id`**，防止 dangling reference 並保持 unique 約束
  - 阻擋檢查已確保僅剩 HISTORY 記錄，此 UPDATE 不影響任何進行中的業務流程
  - 回傳更新列數；0 列也視為成功（冪等）；**不** `commit()`

---

## Phase 2 — X-Career-User：Domain Service 層

- [ ] **T-7** 新增 `X-Career-User/src/domain/user/service/delete_account_service.py`
  ```python
  class DeleteAccountService:
      def __init__(self, reservation_repository: ReservationRepository):
          self.__reservation_repo = reservation_repository

      async def has_active_or_future_reservations(
          self, db: AsyncSession, user_id: int
      ) -> bool:
          return await self.__reservation_repo.has_active_or_future_reservations(db, user_id)
  ```
  - 此 Service 只負責「判斷是否可刪除」，**不觸碰 mentor domain**
  - 命名與介面設計需讓未來加入其他「刪除前置檢查」時可擴充

---

## Phase 3 — X-Career-User：Application 層、Presentation 層、DI

### 3-A　Application Use Case

- [ ] **T-8** 新增目錄與檔案 `X-Career-User/src/app/account/delete.py`
  ```python
  class DeleteAccount:
      def __init__(
          self,
          delete_account_service: DeleteAccountService,
          experience_repository: MentorExperienceRepository,
          schedule_repository: ScheduleRepository,
          canned_message_repository: CannedMessageRepository,
          reservation_repository: ReservationRepository,
          profile_repository: ProfileRepository,
          file_repository: FileRepository,
          notify_service: NotifyService,
      ): ...

      async def execute(self, db: AsyncSession, user_id: int) -> None:
          # 1. 查詢 profile：使用 find_by_user_id（回傳 Optional，不拋例外）
          #    若 None → profile 已刪除，直接 return（冪等成功）
          #    若有 → 取得 is_mentor 供步驟 10 判斷
          # 2. 刪除 mentor_schedules（批次硬刪）
          # 3. 刪除 mentor_experiences（批次硬刪）
          # 4. 刪除 canned_messages（批次硬刪）
          # 5. 匿名化 reservations 自身視角（anonymize_by_my_user_id：my_user_id → -user_id）
          # 6. 匿名化 reservations 對方視角（anonymize_by_user_id：user_id → -user_id）
          # 7. 軟刪 file_info（is_deleted = TRUE，依 create_user_id = user_id）
          # 8. 刪除 profiles（硬刪）
          # 上述 2-8 同一 AsyncSession，最後統一：
          # 9. await db.commit()
          # 10. commit 後，若 is_mentor，呼叫 notify_service.notify_delete_mentor_profile(user_id)
  ```
  - **冪等設計**：步驟 1 使用 `ProfileRepository.find_by_user_id`（見 T-4 新增），回傳 `Optional[ProfileDTO]`。若 `None` 表示 profile 已刪除，直接 `return`，不執行後續步驟。**不可使用** `get_by_user_id`（會拋 `NotFoundException`）
  - 步驟 2-8 均呼叫 Repository 方法（不 commit），步驟 9 統一 `await db.commit()`
  - 步驟 10（SQS）在 commit 後執行，避免訊息送出但 DB 未 commit

- [ ] **T-9** `X-Career-User/src/domain/mentor/service/notify_service.py`
  - 新增方法 `notify_delete_mentor_profile(self, user_id: int) -> None`：
    ```python
    payload = {
        "action": "DELETE_MENTOR_PROFILE",
        "user_id": user_id,
    }
    await self.mq_adapter.publish_message(payload, group_id=str(user_id))
    ```
  - `group_id=str(user_id)` 為 SQS FIFO queue 的 `MessageGroupId`，與既有 `updated_mentor_profile` / `updated_user_profile` 一致
  - 依現有 `updated_mentor_profile` 模式實作，加 `try/except` 並記錄 error log

### 3-B　Presentation 層（internal 端點）

- [ ] **T-10** `X-Career-User/src/router/v1/user.py`（或新增 `src/router/v1/account.py`）
  - 新增端點一：
    ```
    GET /v1/internal/users/{user_id}/has-active-reservations
    回應：{ "data": { "has_active": true } }  →  res_success(data={"has_active": ...})
    ```
    - 依賴注入：`DeleteAccountService = Depends(get_delete_account_service)`
    - **不需 access token**（internal 端點，可加 internal header 驗證，見 T-11）
  - 新增端點二：
    ```
    DELETE /v1/internal/users/{user_id}
    成功回 204 No Content
    ```
    - 依賴注入：`DeleteAccount = Depends(get_delete_account_app)`
    - 呼叫 `await delete_account_app.execute(db, user_id)`
    - 查無 profile 也回 `204`（冪等）

- [ ] **T-11** Internal 端點保護（可選，依部署安全需求）
  - 若 User 服務未在 VPC 內部隔離，對 T-10 兩個 internal 端點加入 `X-Internal-Token` header 驗證
  - 實作為 FastAPI `Depends` 函式，放至 `src/router/req/` 中（與既有 `authorization.py` 同層）

### 3-C　DI 組裝

- [ ] **T-12** `X-Career-User/src/app/_di/injection.py`
  - 新增工廠函式（每個一個，不合併）：
    ```python
    def get_canned_message_dao() -> CannedMessageRepository:
        return CannedMessageRepository()

    def get_delete_account_service(
        reservation_repository: ReservationRepository = Depends(get_reservation_dao),
    ) -> DeleteAccountService:
        return DeleteAccountService(reservation_repository)

    def get_delete_account_app(
        delete_account_service: DeleteAccountService = Depends(get_delete_account_service),
        experience_repository: MentorExperienceRepository = Depends(get_experience_dao),
        schedule_repository: ScheduleRepository = Depends(get_schedule_dao),
        canned_message_repository: CannedMessageRepository = Depends(get_canned_message_dao),
        reservation_repository: ReservationRepository = Depends(get_reservation_dao),
        profile_repository: ProfileRepository = Depends(get_profile_dao),
        file_repository: FileRepository = Depends(get_file_dao),
        notify_service: NotifyService = Depends(get_notify_service),
    ) -> DeleteAccount:
        return DeleteAccount(
            delete_account_service,
            experience_repository,
            schedule_repository,
            canned_message_repository,
            reservation_repository,
            profile_repository,
            file_repository,
            notify_service,
        )
    ```

---

## Phase 4 — X-Career-Auth

### 4-A　Domain Service 層

- [ ] **T-13** `X-Career-Auth/src/domain/auth/service/auth_service.py`
  - 新增方法 `delete_account(self, db, email: str) -> int`：
    1. 呼叫 `await self.auth_repo.find_account_by_email(db, email)` 取得 `AccountEntity`
    2. 若查無帳戶，回傳 `0`（冪等，不拋錯）
    3. 呼叫 `await self.auth_repo.delete_account_by_email(db, account_entity)`（**介面與 DynamoDB 實作均已存在**；注意第二參數為 `AccountEntity`，非 `email: str`，DynamoDB 實作內部以 `account_entity.email` 組 `Key` 刪除）
    4. 成功回傳 `1`
  - Service 方法接受 `email: str`，內部先 `find_account_by_email` 取得 `AccountEntity` 再傳入 `delete_account_by_email`；避免建立 DynamoDB GSI（見 plan.md §5.1）

### 4-B　Presentation 層

- [ ] **T-14** `X-Career-Auth/src/router/v1/auth.py`
  - 新增端點：
    ```
    DELETE /v1/accounts
    Body: { "email": str }   ← BFF 從 Client 傳入的 DeleteAccountDTO 取得 email
    成功回 200 res_success(msg="deleted") 或 204
    查無帳戶也回 200/204（冪等）
    ```
  - 呼叫 `await _auth_service.delete_account(db, payload.email)`
  - 僅供 BFF 內部呼叫，可加 internal header 驗證（與 T-11 同模式）

---

## Phase 5 — X-Career-BFF

### 5-pre　Infrastructure 層（前置）

- [ ] **T-15.5** `X-Career-BFF/src/infra/client/async_service_api_adapter.py`
  - 修改 `delete` 與 `simple_delete` 方法，新增 `json` 參數以支援 DELETE 請求帶 JSON body（現有僅支援 `params` query string）
  - 修改 `simple_delete` 簽名：
    ```python
    async def simple_delete(self, url: str, params: Dict = None,
                            json: Dict = None, headers: Dict = None
    ) -> Optional[Dict[str, Any]]:
        service_api_response = await self.delete(url, params, json, headers)
        if service_api_response:
            return service_api_response.data
        return None
    ```
  - 修改 `delete` 簽名與實作：
    ```python
    @check_response_code('delete', 200)
    async def delete(self, url: str, params: Dict = None,
                     json: Dict = None, headers: Dict = None
    ) -> Optional[ServiceApiResponse]:
        result = None
        response = None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(url, params=params, json=json, headers=headers)
                result = ServiceApiResponse.parse(response)
        except Exception as e:
            err_msg = getattr(e, 'msg', str(e))
            err_data = getattr(e, 'data', None)
            log.error(f"simple_delete request error, url:%s, params:%s, json:%s, headers:%s, resp:%s, err:%s",
                      url, params, json, headers, response, err_msg)
            raise_http_exception(e=e, msg=err_msg, data=err_data)
        return result
    ```
  - 向後相容：原有呼叫 `simple_delete(url, params)` 不受影響（`json` 預設 `None`）
  - `httpx.AsyncClient.delete()` 原生支援 `json` 參數，此修改僅將其暴露至 adapter 層
  - **此 task 為 T-16 步驟 4（Auth 帳戶刪除）的前置條件**

### 5-A　Domain Model 層

- [ ] **T-15** `X-Career-BFF/src/domain/auth/model/auth_model.py`
  - 新增：
    ```python
    class DeleteAccountDTO(BaseModel):
        user_id: Optional[int] = None     # 由 token 覆寫，前端不需傳
        email: str                        # 帳戶登入信箱（供 step-up 驗證與 Auth DynamoDB 刪除使用）
        password: Optional[str] = None    # XC 帳戶：目前密碼，用於 step-up 驗證
        id_token: Optional[str] = None    # Google 帳戶：id_token，用於 step-up 驗證
    ```

### 5-B　Domain Service 層

- [ ] **T-16** `X-Career-BFF/src/domain/auth/service/auth_service.py`
  - 新增方法 `delete_account(self, body: DeleteAccountDTO) -> None`，依序：
    1. **取得帳戶類型並執行 Step-up 驗證**：
       - `email` 來自 `body.email`（Client 傳入），**不依賴 cache**。
       - **判斷 `account_type`**：優先從 BFF cache（`await self.cache.get(str(body.user_id))`）取得 `account_type`。若 cache miss，以 `body.password` / `body.id_token` 擇一非空推斷（有 `password` → XC，有 `id_token` → GOOGLE）。
       - **XC 帳戶**：以 `body.email` + `body.password` 組成 `LoginDTO`，呼叫 `__req_login` 驗證。
       - **Google 帳戶**：以 `body.id_token` 呼叫 Auth/OAuth 既有驗證端點。
       - 驗證失敗：拋 `UnauthorizedException`（401）。
    2. **預約阻擋檢查**：`GET {USER_SERVICE_URL}/v1/internal/users/{user_id}/has-active-reservations`
       - `has_active == true`：拋 `ConflictException`（409），msg 為 `ACCOUNT_DELETE_BLOCKED_ACTIVE_RESERVATIONS`
    3. **User 資料刪除**：`DELETE {USER_SERVICE_URL}/v1/internal/users/{user_id}`
    4. **Auth 帳戶刪除**：使用 `self.req.simple_delete(url=f'{AUTH_SERVICE_URL}/v1/accounts', json={"email": body.email})`（需先完成 T-15.5 擴充 `simple_delete` 的 `json` 參數）
       - 若步驟 4 失敗，記錄 `log.error(...)` 並拋 `ServerException`（500）；步驟 3 已完成，需人工補償（見 spec.md §5.2）
    5. **BFF Cache 清除**：呼叫 `await self.cache.delete(str(body.user_id))`（清 session key）；依現有 `AuthService` cache key 模式補全其餘 key

- [ ] **T-17** `X-Career-BFF/src/config/exception.py`（**已確認：`ConflictException` 不存在，需新增**）
  - 新增 `ConflictException` class（依現有 pattern）：
    ```python
    class ConflictException(HTTPException, ErrorLogger):
        def __init__(self, msg: str, code: str = '40900', data: Any = None):
            self.msg = msg
            self.code = code
            self.data = data
            self.status_code = status.HTTP_409_CONFLICT

        def __str__(self) -> str:
            return self.msg
    ```
  - 新增 handler `__conflict_exception_handler`（同其他 handler pattern）
  - `include_app()` 中註冊：`app.add_exception_handler(ConflictException, __conflict_exception_handler)`
  - `raise_http_exception()` 中加入 `isinstance(e, ConflictException)` 分支
  - `status_code_mapping` 加入 `409: ConflictException`

### 5-C　Token 驗證（新增 Depends）

- [ ] **T-17.5** `X-Career-BFF/src/router/req/authorization.py`
  - 新增 `verify_token_for_delete_account` Depends 函式
  - **背景**：現有 `__verify_token_in_auth(user_id, credentials, err_msg)` 需要 `user_id` 作為第一個參數來建構 JWT secret（`f'secret{str(user_id)[::-1]}'`），但 `DELETE /v1/auth/account` 路徑無 `{user_id}` 片段，無法從 URL path 取得 `user_id`
  - **解法**：先不驗簽解碼 JWT 取出 `user_id`，再以該 `user_id` 完成完整簽名驗證（安全性不受影響：攻擊者偽造 `user_id` 會在 Step 2 因 secret 不匹配而失敗）
  - 實作：
    ```python
    def verify_token_for_delete_account(
        credentials: HTTPAuthorizationCredentials = Depends(auth_scheme),
    ) -> int:
        token = parse_token(credentials)
        # Step 1: 不驗簽解碼，僅從 payload 取 user_id
        try:
            unverified = jwt_util.decode(
                token,
                options={"verify_signature": False},
                algorithms=[JWT_ALGORITHM],
            )
        except Exception:
            raise UnauthorizedException(msg='invalid token')

        user_id = unverified.get('user_id')
        if not user_id:
            raise UnauthorizedException(msg='user_id not found in token')
        user_id = int(user_id)

        # Step 2: 以 user_id 建構 secret，完整驗證簽名與 exp
        __verify_token_in_auth(user_id, credentials, 'access denied')
        return user_id
    ```
  - 需確認 `jwt_util`（即 `import jwt as jwt_util`）已在檔案頂部 import（現有已有）
  - 需確認 `JWT_ALGORITHM` 已從 `config.conf` import（現有已有）

### 5-D　Presentation 層

- [ ] **T-18** `X-Career-BFF/src/router/v1/auth.py`
  - 新增端點：
    ```
    DELETE /v1/auth/account
    依賴：verify_token_for_delete_account（從 JWT 取得 user_id，見 T-17.5）
    Body：DeleteAccountDTO（user_id 由 token 覆寫，email 必填，password 或 id_token 擇一）
    成功回 204 No Content
    ```
  - 呼叫 `await _auth_service.delete_account(body)`
  - `ConflictException` 由全域 handler 攔截，回 409 含標準 body（見 T-17）

---

## Phase 6 — 驗收與收尾

- [ ] **T-19** Smoke Test — 正常刪除（Email 帳戶）
  - 建立 XC 帳戶 → 確認 DynamoDB、Postgres `profiles` 均有資料
  - 建立一筆已過期的歷史預約（確保匿名化有作用對象）
  - 呼叫 `DELETE /v1/auth/account`（帶 `email` + 正確 `password`）
  - 驗證：DynamoDB item 已刪、`profiles` 已刪、BFF Cache 無該 user_id session
  - 驗證：`reservations` 中該使用者的 `my_user_id` 與對方記錄的 `user_id` 均已匿名化為 `-user_id`（負數 sentinel）

- [ ] **T-20** Smoke Test — 正常刪除（Google OAuth 帳戶）
  - 建立 Google 帳戶 → 呼叫 `DELETE /v1/auth/account`（帶 `email` + 有效 `id_token`）
  - 驗證同 T-19

- [ ] **T-21** Smoke Test — 預約阻擋
  - 建立帳戶 → 建立一筆未來且雙方 ACCEPT 的預約 → 呼叫刪除
  - 驗證：回 **409**，DynamoDB 與 Postgres 資料**均未被刪除**

- [ ] **T-22** Smoke Test — Mentor OpenSearch 清除（非同步）
  - 建立 Mentor 帳戶（`is_mentor = true`）→ 無未來預約 → 呼叫刪除
  - 等待 SQS consumer 處理完成（或直接查 Search `GET /v1/internal/mentor/{user_id}`）
  - 驗證：OpenSearch `profiles` index 中已無該 `user_id` 文件

- [ ] **T-23** Smoke Test — 冪等性
  - 完成正常刪除後，再次呼叫 `DELETE /v1/auth/account`
  - 驗證：回 **204**（或 404），**不拋 500**

- [ ] **T-24** 確認 Search Consumer 冪等：搜尋刪除後，重複消費 `DELETE_MENTOR_PROFILE`（手動送 SQS 訊息）
  - 驗證：OpenSearch `_delete` on non-existing doc → Consumer log 視為成功，不拋錯

---

**文件結束**

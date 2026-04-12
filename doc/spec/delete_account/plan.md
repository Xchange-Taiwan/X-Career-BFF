# 刪除帳號（Delete Account）實作計畫

**對應規格**：`spec.md`（同目錄）  
**版本**：1.0

---

## 1. 開發準則（DDD）

本專案採用 **DDD（領域驅動設計）** 分層架構。實作「刪除帳號」功能時，所有新增程式必須符合下列層級規範。**違反分層的程式碼不得合入主線。**

### 1.1 各服務分層對應

| 層級 | 目錄（以 `X-Career-User` 為例） | 職責 | 禁止事項 |
|------|-------------------------------|------|---------|
| **Presentation** | `router/v1/` | 解析 HTTP request、呼叫 Application 或 Domain Service、回傳 HTTP response | 不得含業務邏輯、不得直接操作 DB/MQ |
| **Application** | `app/<use_case>/` | 編排跨 Domain 的 Service、管理交易邊界、觸發非同步任務 | 不得直接操作 DB，需透過 Domain Service；BFF 無此層（BFF 本身即編排器） |
| **Domain Model** | `domain/<aggregate>/model/` | DTO、VO、Entity、Value Object、介面定義 | 不得包含 I/O 或 infra 相依 |
| **Domain Service** | `domain/<aggregate>/service/` | 單一領域的業務邏輯（重複使用、可測試） | 不得跨越多個 Aggregate 的完整流程（交給 Application 層） |
| **Repository (DAO)** | `domain/<aggregate>/dao/` | 資料存取介面（interface）或 Repository 方法 | 不得含業務邏輯；複雜 query 以 method 封裝，不散落於 service |
| **Infrastructure** | `infra/` | DB Session、ORM model、MQ adapter、HTTP client 實作 | 不得被 Domain 層直接相依（透過介面/DI 注入） |
| **DI 組裝** | `app/_di/injection.py` | 將 Repository、Service、Application 組裝為 FastAPI Depends | 不得含業務邏輯；每個可注入單元一個工廠函式 |

### 1.2 Aggregate 邊界

本功能涉及以下 Aggregate（DDD 概念上的一致性邊界）：

| Aggregate | 主鍵 | 所在服務 |
|-----------|------|---------|
| **Account** | `email`（DDB Partition Key） | X-Career-Auth |
| **Profile** | `user_id` | X-Career-User |
| **Reservation** | `(my_user_id, dtstart, dtend, schedule_id, user_id)` | X-Career-User |
| **MentorSchedule** | `id` | X-Career-User |
| **MentorExperience** | `id` | X-Career-User |
| **CannedMessage** | `id` | X-Career-User |
| **SearchDocument** | `user_id`（OpenSearch doc） | X-Career-Search（via SQS） |

### 1.3 跨服務編排規則

- **BFF** 負責跨服務編排（Step-up → 預約檢查 → User 刪除 → Auth 刪除 → Cache 清除）；SQS 由 User 服務內部在 DB commit 後發送。
- **各下游服務**只提供自身 Aggregate 的操作端點或方法，不感知其他服務。
- BFF 呼叫下游均透過 `AsyncServiceApiAdapter`（`infra/client/`），對應 `domain/<x>/service/` 中的方法，**不得在 `router/` 直接 import `infra/client`**。

---

## 2. 變更範圍總覽

| 服務 | 變更量 | 摘要 |
|------|--------|------|
| **X-Career-BFF** | 新增 | 端點、DTO、AuthService 編排方法 |
| **X-Career-User** | 新增 | 預約阻擋 query、刪除帳號 use case、受保護端點 |
| **X-Career-Auth** | 新增 | Auth router 端點、AuthService `delete_account` 方法（Repository 介面與 DynamoDB 實作已存在） |
| **X-Career-Search** | **無需變更** | `DELETE_MENTOR_PROFILE` action 與 `SearchService` 已完備 |

---

## 3. X-Career-BFF

### 3.1 Presentation 層

**修改檔案**：`src/router/v1/auth.py`

- 新增端點：`DELETE /v1/auth/account`（或 `POST /v1/auth/account/delete`，視產品決策）。
- 從 access token 取得 `user_id`：**不可**沿用現有 `verify_token_by_update_password`（該函式從 URL path 取 `user_id`，但 `/v1/auth/account` 路徑無 `{user_id}` 片段）。須**新增** `verify_token_for_delete_account` Depends。因 JWT secret 為 `f'secret{str(user_id)[::-1]}'`（需先有 `user_id` 才能驗簽），實作上須先以 `jwt.decode(token, options={"verify_signature": False})` **不驗簽解碼**取得 payload 中的 `user_id`，再以該 `user_id` 建構 secret 呼叫 `__verify_token_in_auth(user_id, credentials, err_msg)` 完成完整簽名驗證。
- Request body 含 `DeleteAccountDTO`（見 3.2）。
- 成功回 `204 No Content`；預約阻擋回 `409`。
- **不含業務邏輯**，直接呼叫 `_auth_service.delete_account()`。

### 3.2 Domain Model 層

**修改檔案**：`src/domain/auth/model/auth_model.py`

新增：
```python
class DeleteAccountDTO(BaseModel):
    user_id: Optional[int] = None  # 由 token 覆寫，前端不需傳
    email: str                     # 帳戶登入信箱（供 step-up 驗證與 Auth 刪除使用）
    # XC 帳戶：提供目前密碼
    password: Optional[str] = None
    # Google 帳戶：提供 id_token（與 OAuth 流程約定）
    id_token: Optional[str] = None
```

### 3.3 Domain Service 層

**修改檔案**：`src/domain/auth/service/auth_service.py`

新增 `delete_account(self, body: DeleteAccountDTO) -> None`，編排以下步驟（**BFF 是唯一知道完整順序的地方**）：

1. **取得帳戶資訊與 Step-up 驗證**：`email` 由 Client 在 `DeleteAccountDTO` 中傳入（見 §3.2），不依賴 cache。依 `account_type` 判斷驗證方式：
   - **判斷 `account_type`**：優先從 BFF cache（`self.cache.get(str(user_id))`）取得 `account_type`（login 時已快取 `auth_res`，含 `account_type` 欄位）。若 cache miss，則以 `body.password` 或 `body.id_token` 擇一非空來推斷帳戶類型（有 `password` → XC，有 `id_token` → GOOGLE）。
   - **XC 帳戶**：以 `email` + `password` 組成 `LoginDTO`，呼叫 `__req_login` 驗證。驗證成功即通過 step-up。
   - **Google 帳戶**：以 `id_token` 呼叫 Auth／OAuth 既有驗證端點確認身分。
   - 驗證失敗：拋 `UnauthorizedException`（401）。
   - **`email` 全程保留**，供步驟 5（Auth 刪除）使用。
2. **預約阻擋檢查**：呼叫 User 服務受保護端點 `GET /v1/internal/users/{user_id}/has-active-reservations`。
   - 回 `true` → 拋 `ConflictException`（409），**流程結束**。
3. **User 資料刪除**：呼叫 User 服務 `DELETE /v1/internal/users/{user_id}`。User 服務內部完成 DB 刪除後，若曾為 mentor，自行發送 SQS `DELETE_MENTOR_PROFILE`（見 §4.3 步驟 9）。
4. **Auth DynamoDB 刪除**：呼叫 Auth 服務 `DELETE /v1/accounts`，body `{ "email": body.email }`（email 來自 Client 傳入的 `DeleteAccountDTO`）。需先擴充 `AsyncServiceApiAdapter.delete` / `simple_delete` 方法，新增 `json` 參數以支援 DELETE 請求帶 JSON body（現有實作僅支援 `params` query string，與 `simple_post`/`simple_put` 不對齊）。
5. **BFF Cache 清除**：使用既有 `self.cache.delete(...)` 清除該 `user_id` 相關所有 key（session、signup token 等）。

> **補償策略**：步驟 3（User 刪除）成功但步驟 4（Auth 刪除）失敗時，需告警，供運維補償腳本重試 Auth 刪除。BFF 對 Client 回 `500`。

### 3.4 DI 組裝

`src/app/_di/injection.py`（BFF 使用 singleton 模式）：無需新增 class，`_auth_service` 已注入，僅在 `auth_service.py` 新增方法即可。

---

## 4. X-Career-User

### 4.1 Repository 層（Domain DAO）

**修改檔案**：`src/domain/user/dao/reservation_repository.py`

新增方法：
```python
async def has_active_or_future_reservations(
    self, db: AsyncSession, user_id: int
) -> bool:
    """
    EXISTS query：my_user_id = user_id
    AND dtend >= current_seconds()
    AND NOT (my_status = REJECT OR status = REJECT)
    """
```

- 使用 SQLAlchemy `exists()` / `scalar()` **單次查詢**，不回傳列表。
- 與 `get_user_reservations` 中的 UPCOMING／PENDING 過濾邏輯語意對齊（詳見 spec.md §3）。

### 4.2 Domain Service 層

**新增檔案**：`src/domain/user/service/delete_account_service.py`

```
DeleteAccountService
  依賴：ReservationRepository
  方法：
    has_active_or_future_reservations(db, user_id) -> bool
      → 委派給 ReservationRepository
```

> 此 Service 只負責「判斷是否可刪除」，**不跨越 mentor domain**；跨 domain 的刪除流程交給 Application 層（見 4.3）。

### 4.3 Application 層（跨 Domain Use Case）

**新增檔案**：`src/app/account/delete.py`

```
DeleteAccount（Use Case class）
  依賴（直接注入 Repository，因現有 Service 方法會自行 commit，不適合批次交易場景）：
    DeleteAccountService（user domain — 預約阻擋檢查）
    MentorExperienceRepository（mentor domain dao）
    ScheduleRepository（mentor domain dao）
    CannedMessageRepository（mentor domain dao，路徑 `src/domain/mentor/dao/canned_message_repository.py`，因 CannedMessageDTO 位於 `mentor/model/`）
    ReservationRepository（user domain dao）
    ProfileRepository（user domain dao）
    FileRepository（file domain dao）
    NotifyService（MQ，mentor domain；注意其 constructor 注入 MentorService、ExperienceService、SqsMqAdapter，DI 較重，但刪帳僅需呼叫其中 SQS 發送方法，可接受）
  方法：
    execute(db, user_id) -> None
      1. 查詢 profiles 取得 is_mentor 標記（使用 find_by_user_id 回傳 Optional；若 None 表示已刪除，直接 return — 冪等成功）
      2. 刪除 mentor_schedules（ScheduleRepository.delete_all_by_user_id）
      3. 刪除 mentor_experiences（MentorExperienceRepository.delete_all_by_user_id）
      4. 刪除 canned_messages（CannedMessageRepository.delete_all_by_user_id）
      5. 匿名化 reservations 自身視角（ReservationRepository.anonymize_by_my_user_id）：將 my_user_id 設為 -user_id
      6. 匿名化 reservations 對方視角（ReservationRepository.anonymize_by_user_id）：將 user_id 設為 -user_id
      7. 軟刪 file_info（FileRepository.soft_delete_all_by_user_id，依 create_user_id = user_id）
      8. 刪除 profiles（ProfileRepository.delete_profile）
      9. await db.commit()
      10. 若 is_mentor，發送 SQS DELETE_MENTOR_PROFILE（NotifyService）
```

> **交易邊界**：步驟 2-8 均不 `commit()`，統一在步驟 9 `commit()`；步驟 10（SQS）在 commit 後發送（避免訊息發出但 DB 未 commit）。
>
> **冪等設計**：步驟 1 使用 `ProfileRepository.find_by_user_id`（回傳 `Optional[ProfileDTO]`，不拋例外），若回傳 `None` 表示 profile 已刪除，直接 `return`。現有 `get_by_user_id` 會拋 `NotFoundException`，不適用於此場景。

### 4.4 Presentation 層

**修改檔案**：`src/router/v1/user.py`（或新增 `account.py`，依慣例）

新增兩個受保護端點（供 BFF internal 呼叫，可加 internal token / header 驗證）：

```
GET  /v1/internal/users/{user_id}/has-active-reservations
  → 回 { "has_active": true/false }

DELETE /v1/internal/users/{user_id}
  → 呼叫 DeleteAccount.execute(db, user_id)
  → 成功回 204
```

### 4.5 DI 組裝

**修改檔案**：`src/app/_di/injection.py`

新增：
```python
def get_delete_account_service(
    reservation_repository: ReservationRepository = Depends(get_reservation_dao),  # 注意：原始碼拼字為 get_reservation_dao
) -> DeleteAccountService: ...

def get_delete_account_app(
    delete_account_service: DeleteAccountService = Depends(get_delete_account_service),
    experience_repository: MentorExperienceRepository = Depends(get_experience_dao),
    schedule_repository: ScheduleRepository = Depends(get_schedule_dao),
    canned_message_repository: CannedMessageRepository = Depends(get_canned_message_dao),
    reservation_repository: ReservationRepository = Depends(get_reservation_dao),
    profile_repository: ProfileRepository = Depends(get_profile_dao),
    file_repository: FileRepository = Depends(get_file_dao),
    notify_service: NotifyService = Depends(get_notify_service),
) -> DeleteAccount: ...
```

---

## 5. X-Career-Auth

### 5.1 Domain Service 層

**修改檔案**：`src/domain/auth/service/auth_service.py`

新增 `delete_account(self, db, email: str) -> int`：

1. 呼叫 `await self.auth_repo.find_account_by_email(db, email)` 取得 `AccountEntity`。
2. 若查無帳戶（`AccountEntity is None`），回傳 `0`（冪等，不拋錯）。
3. 呼叫 `await self.auth_repo.delete_account_by_email(db, account_entity)`（**介面與 DynamoDB 實作均已存在**）。注意：`delete_account_by_email` 的第二參數為 **`AccountEntity`**（非 `email: str`），實作內部以 `account_entity.email` 組 DynamoDB `Key` 進行刪除。
4. 成功回傳 `1`。

> 接受 `email`（DDB partition key）而非 `user_id`，避免建立 DynamoDB GSI。BFF 在 `DeleteAccountDTO` 中已持有 Client 傳入之 `email`，隨 Auth 刪除請求傳入。

### 5.2 Repository 層（既有實作補充）

`IAuthRepository.delete_account_by_email` 已存在，`DynamoDBAuthRepository` 已實作。

**不需新增** `find_account_by_user_id`：BFF 在 step-up 驗證時已取得 `email`，隨 Auth 刪除請求傳入，直接以 `email`（DDB partition key）刪除即可，無需建立 DynamoDB GSI。

### 5.3 Presentation 層

**修改檔案**：`src/router/v1/auth.py`

新增：
```
DELETE /v1/accounts
  body: { email: str }  (BFF 傳入，供 DDB partition key 刪除)
  → auth_service.delete_account(db, email)
  → 成功回 200/204；查無帳戶回 204（冪等）
```

---

## 6. X-Career-Search（無需變更）

SQS consumer 已支援 `DELETE_MENTOR_PROFILE`：

```python
# X-Career-Search/src/domain/search/service/search_service.py
MentorAction.DELETE_MENTOR_PROFILE: self._delete_mentor_by_event
```

BFF/User 發送的 SQS 訊息格式：
```json
{
  "action": "DELETE_MENTOR_PROFILE",
  "user_id": 12345
}
```

---

## 7. 資料刪除策略（X-Career-User）

| 資料表 | 策略 | 備註 |
|--------|------|------|
| `profiles` | **硬刪** | 主體資料，刪帳後無需留存 |
| `mentor_experiences` | **硬刪** | 依 `user_id` 刪全部 |
| `mentor_schedules` | **硬刪** | 依 `user_id` 刪全部 |
| `canned_messages` | **硬刪** | 依 `user_id` 刪全部 |
| `reservations`（自身視角） | **匿名化**：`UPDATE reservations SET my_user_id = -:user_id WHERE my_user_id = :user_id` | 阻擋檢查已確保僅剩 HISTORY 列；`-user_id` 為負數 sentinel value，避免 unique index 衝突（見 spec.md §7） |
| `reservations`（對方視角） | **匿名化**：`UPDATE reservations SET user_id = -:user_id WHERE user_id = :user_id` | 防止對方查看歷史預約時 dangling reference；使用 `-user_id` 保持 unique 約束 |
| `file_info` | **軟刪**：`is_deleted = TRUE`（依 `create_user_id = user_id`）；S3 object 由排程或 lifecycle 處理 | 納入刪除交易內；避免立即刪除造成 CDN 快取問題 |

> **已決策**：`reservations` 歷史列採**匿名化**策略（自身與對方視角均處理），不硬刪，保留歷史記錄供稽核。

---

## 8. 冪等性設計

| 情境 | 處理 |
|------|------|
| User 資料已刪，重送 `DELETE /v1/internal/users/{user_id}` | 查無資料時回 `204`，不拋錯 |
| DynamoDB 已刪，重送 Auth 刪除 | `delete_item` 本身冪等，回 `204` |
| SQS `DELETE_MENTOR_PROFILE` 重複消費 | OpenSearch `_delete` 在文件不存在時回 `404`，Consumer 應視為成功（已刪） |
| BFF 重複呼叫刪帳 | User 查無 profile（`find_by_user_id` 回傳 `None`）→ 跳過 User 刪除；Auth 冪等刪除；Cache 清除冪等；整體回 `204` |

---

## 9. 風險與決策點

| 項目 | 風險 / 問題 | 建議決策 |
|------|------------|---------|
| Auth DDB 以 email 為 partition key | `user_id → email` 需一次 Auth 查詢 | Client 在 `DeleteAccountDTO` 中直接傳入 `email`，BFF 隨 Auth 刪除請求傳入；不依賴 cache 或額外查詢 |
| User 資料刪除與 Auth 刪除的原子性 | 非分散式交易，存在不一致視窗 | User 先刪，Auth 後刪；失敗告警，補償腳本重試 Auth 刪除 |
| SQS 非同步，短暫仍可搜尋到 | 搜尋結果延遲清除 | 可接受；若不可接受，改為 User 刪除後同步呼叫 Search 刪除 API |
| `reservations` 歷史列是否保留 | 法遵／稽核需求未定 | **已決策**：匿名化（自身 `my_user_id` 與對方 `user_id` 均設為 `-user_id`），保留記錄供稽核 |

---

## 10. 新增檔案清單（一覽）

| 服務 | 類型 | 路徑 |
|------|------|------|
| X-Career-BFF | 修改 | `src/router/v1/auth.py` |
| X-Career-BFF | 修改 | `src/router/req/authorization.py`（新增 `verify_token_for_delete_account`） |
| X-Career-BFF | 修改 | `src/domain/auth/model/auth_model.py` |
| X-Career-BFF | 修改 | `src/domain/auth/service/auth_service.py` |
| X-Career-BFF | 修改 | `src/config/exception.py`（新增 `ConflictException`、409 handler） |
| X-Career-BFF | 修改 | `src/infra/client/async_service_api_adapter.py`（`delete`/`simple_delete` 新增 `json` 參數） |
| X-Career-User | **新增** | `src/domain/user/service/delete_account_service.py` |
| X-Career-User | 修改 | `src/domain/user/dao/reservation_repository.py` |
| X-Career-User | 修改 | `src/domain/user/dao/mentor_experience_repository.py` |
| X-Career-User | 修改 | `src/domain/mentor/dao/schedule_repository.py` |
| X-Career-User | 修改 | `src/domain/user/dao/profile_repository.py`（新增 `find_by_user_id`、修正 `delete_profile`） |
| X-Career-User | **新增** | `src/domain/mentor/dao/canned_message_repository.py` |
| X-Career-User | **新增** | `src/app/account/delete.py` |
| X-Career-User | 修改 | `src/router/v1/user.py`（或新增 `account.py`） |
| X-Career-User | 修改 | `src/app/_di/injection.py` |
| X-Career-Auth | 修改 | `src/router/v1/auth.py` |
| X-Career-Auth | 修改 | `src/domain/auth/service/auth_service.py` |
| X-Career-Auth | 不需變更 | `src/domain/auth/dao/i_auth_repository.py`（`delete_account_by_email` 已存在） |
| X-Career-Search | 無需變更 | — |

---

**文件結束**

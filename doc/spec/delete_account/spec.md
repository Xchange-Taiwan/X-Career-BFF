# 刪除帳號（Delete Account）規格

**版本**：1.0  
**狀態**：草案（供 BFF / Auth / User / Search 對齊實作）  
**主導服務**：X-Career-BFF（編排）；資料刪除分散於 X-Career-Auth、X-Career-User、非同步 X-Career-Search。

---

## 1. 目標與範圍

### 1.1 目標

- 讓**已驗證身分**的使用者能**永久終止**本平台帳號（含登入與個人資料），並盡可能清除下游索引與快取。
- **業務規則**：使用者若尚有**未結束或未來的預約**（見第 3 節），**不得**刪除帳號；須先處理完預約（取消、拒絕、或待時段結束）後再申請刪除。

### 1.2 範圍內

- BFF API 設計、驗證、錯誤碼、編排順序建議。
- 與 **X-Career-Auth**（DynamoDB 帳戶）、**X-Career-User**（PostgreSQL 個人／預約／檔案等）、**X-Career-Search**（OpenSearch，經 SQS）的責任切分。
- 預約**阻擋刪除**的判定規則（與現有 `ReservationRepository.get_user_reservations` 狀態語意對齊）。

### 1.3 範圍外（可另開規格）

- 法遵／會計強制留存資料（匿名化與保留年限）。
- 金流、發票、第三方合約（若日後有）。
- 寄送「刪除確認信」與冷卻期（可選產品需求）。

---

## 2. 名詞與識別

| 名詞 | 說明 |
|------|------|
| `user_id` | 全系統主鍵；JWT／登入回應中的使用者 ID。刪除流程以 **`user_id` 為唯一軸**，不以 email／oauth_id 作為 API 查詢主鍵。 |
| 帳戶（Auth） | X-Career-Auth DynamoDB 帳戶資料（email、密碼雜湊、oauth_id、refresh_token、`user_id` 等）。 |
| 使用者資料（User） | X-Career-User PostgreSQL：`profiles`、`mentor_experiences`、`mentor_schedules`、`reservations`、`canned_messages`、`file_info` 等。 |
| Mentor 搜尋文件 | OpenSearch `profiles` index，文件 ID 為 `user_id`；更新／刪除經 SQS（`MentorAction`，含 `DELETE_MENTOR_PROFILE`）。 |

---

## 3. 預約阻擋規則（核心）

### 3.1 資料視角

- 預約表為 `reservations`（見 `X-Career-User` schema）。
- 每位使用者只透過 **`my_user_id = user_id`** 的列參與列表與業務（與現有 API 一致）。

### 3.2 「尚有未結束或未來的預約」定義

對給定 `user_id`，若存在**至少一筆**滿足下列條件的列（`my_user_id = user_id`）：

1. **`dtend >= now`**（`now` 為伺服器 Unix epoch 秒，與現有 `current_seconds()` 語意一致）。
2. **尚未進入「歷史／已拒絕」終態**：  
   - **不**滿足：`my_status = REJECT` **或** `status = REJECT`。

則視為**仍有未結束或未來預約**，**禁止刪除帳號**。

### 3.3 與現有列表狀態的對應（非規範，供實作對齊）

- **MENTOR_UPCOMING / MENTEE_UPCOMING**：雙方 `ACCEPT` 且 `dtend >= now` → **阻擋刪除**。
- **MENTOR_PENDING / MENTEE_PENDING**：任一方仍為 `PENDING` 且 `dtend >= now` → **阻擋刪除**。
- **HISTORY**：`REJECT` 或 `dtend < now` → **不阻擋**（僅歷史或未來已取消者）。

> **註**：上述 enum 為 `X-Career-User/src/config/constant.py` 中的 `ReservationListState`（含 MENTOR_/MENTEE_ 前綴），**非** `X-Career-Search` 同名但簡化版的 enum。

### 3.4 實作建議

- 在 **X-Career-User** 提供內部或受保護端點／repository 方法，例如：  
  `has_active_or_future_reservations(user_id: int) -> bool`  
  使用**單次查詢**（`EXISTS`）避免競態下誤刪：刪除帳號交易內可再次檢查或對相關列加鎖（依 ORM／交易策略而定）。
- BFF 在編排刪除**之前**必須先呼叫此檢查；若為 `true`，回傳 **409 Conflict**（見第 6 節），**不呼叫** Auth 刪除。

---

## 4. 身分驗證（刪除前必須「再證明一次」）

刪除帳號屬高風險操作，**僅憑未過期 access token 不足**時，產品可要求 **step-up**；本規格建議最低限度如下。

### 4.1 共通

- 呼叫刪除 API 時須帶有效 **access token**（或等效），以取得 `user_id`。
- 可選：`Idempotency-Key` header，避免重複提交造成重試風暴。

### 4.2 XC（Email／密碼）帳戶

- Request body 帶入 **`email`**（帳戶登入信箱）與 **目前密碼**。`email` 用於 BFF 向 Auth 進行 step-up 驗證（`POST /v1/login`）及後續 Auth 帳戶刪除（DynamoDB partition key）。即使 BFF cache 中可能已有 `email`，仍**以 Client 傳入為準**，避免 cache miss 時無法完成驗證。
- BFF 轉呼叫 **X-Career-Auth** 驗證密碼或簽發「刪除許可」短期 token（依 Auth 實作能力）。

### 4.3 Google OAuth 帳戶

- Request body 帶入 **`email`**（帳戶登入信箱）與 **`id_token`**（Google OAuth 再授權結果）。`email` 用途同 §4.2；`id_token` 由前端完成 **Sign in with Google** 後取得。
- **不得**要求使用者提供「Google 密碼」；以 Google 回傳的身分與綁定之 `oauth_id`／email 對齊既有登入流程。

---

## 5. 端到端流程（建議順序）

以下為**建議編排**；實作可採 Saga／補償，但需記錄失敗與人工修復程序。

```
┌─────────┐     ┌─────────┐     ┌───────────────────────────────────────────┐
│ Client  │────▶│   BFF   │────▶│ 1) 驗證 access token → user_id            │
└─────────┘     └────┬────┘     │ 2) Step-up（密碼 / OAuth）→ 取得 email     │
                     │          │ 3) User：has_active_reservations?          │
                     │          │    若 true → 409，結束                      │
                     │          │ 4) User：刪除 Postgres 資料 + SQS(若mentor)│
                     │          │ 5) Auth：刪除 DynamoDB 帳戶（帶 email）     │
                     │          │ 6) BFF Cache：清 user 相關快取              │
                     └──────────│ 7) 回傳 204/200                            │
                                └───────────────────────────────────────────┘
```

### 5.1 步驟說明

| 步驟 | 負責 | 動作 |
|------|------|------|
| 1 | BFF | 解析 JWT，取得 `user_id`；無效則 401。 |
| 2 | BFF → Auth | 依帳戶類型完成 step-up；失敗則 401/403。 |
| 3 | BFF → User | 執行第 3 節阻擋規則；若阻擋則 **409**，body 帶標準化錯誤（見 §6）。**不得**進行後續刪除。 |
| 4 | User | 於**單一資料庫交易**（或明確子順序）內：刪除或匿名化該 `user_id` 相關列（`profiles`、`mentor_schedules`、`mentor_experiences`、`canned_messages`、`reservations` 中僅剩歷史時的處理策略見 §7）；並將 `file_info` 標記為 `is_deleted = TRUE`（見 §7）。**交易 commit 後**，若該使用者曾為 mentor（`is_mentor = true`），由 User 服務內部發送 SQS `DELETE_MENTOR_PROFILE`（見 §9）。 |
| 5 | Auth | 刪除 DynamoDB 中該 `user_id` 對應帳戶。BFF 以 Client 傳入之 `email` 呼叫 Auth `DELETE /v1/accounts`（body 帶 `email`）；Auth 內部先以 `email`（DynamoDB partition key）查得 `AccountEntity`，再呼叫 `delete_account_by_email(db, account_entity)` 完成刪除。並使 **refresh_token** 失效。 |
| 6 | BFF | 清除 Redis／快取中該使用者的 session、signup、reset password 等 key（與現有 `AuthService` 快取模式對齊）。 |
| 7 | BFF | 成功回應；Client 應清除本地 token 與 cookie。 |

### 5.2 失敗與一致性

- **建議順序**：先完成 User 側「可回滾」的檢查（步驟 3），再執行 User 資料變更（步驟 4），再 Auth（步驟 5）。若 Auth 刪除失敗但 User 已刪：屬**嚴重不一致**，需告警與補償腳本（或以「User 軟刪 + 重試 Auth」降低機率）。
- **Search**：非同步；使用者可能短暫仍搜尋到已刪 mentor，可接受或由 Search 同步刪除（進階）。

### 5.3 冪等性

- 同一 `user_id` 第二次呼叫刪除：應回傳 **204 No Content** 或 **404**（依「已刪除是否視為成功」產品決策）；建議 **204** 冪等成功。

---

## 6. BFF API 建議

### 6.1 端點（草案）

- `DELETE /v1/auth/account`  
  或 `POST /v1/auth/account/delete`（若需 body 帶密碼，部分部署不建議用 DELETE body）。

### 6.2 Request（範例）

- **Headers**：`Authorization: Bearer <access_token>`  
- **Body（XC）**：`{ "email": "<login_email>", "password": "<current_password>" }`  
- **Body（Google）**：`{ "email": "<login_email>", "id_token": "<google_id_token>" }`

### 6.3 回應

| HTTP | 說明 |
|------|------|
| 204 | 刪除成功（或已刪除之冪等成功）。 |
| 401 | Token 無效或未通過 step-up。 |
| 403 | 帳戶類型不支援此方式驗證等。 |
| 409 | **尚有未結束或未來預約**；不執行刪除。 |
| 500 | 非預期錯誤；可能需人工處理部分完成狀態。 |

### 6.4 409 錯誤 body（建議）

```json
{
  "code": "ACCOUNT_DELETE_BLOCKED_ACTIVE_RESERVATIONS",
  "msg": "尚有未結束或未來的預約，無法刪除帳號。請先取消或處理相關預約後再試。"
}
```

（`code`／`msg` 需與全站 `response` 包裝一致。）

---

## 7. X-Career-User：資料處理要點

- **`reservations`（自身視角）**：在通過阻擋檢查後，理論上僅剩 **HISTORY** 語意之列。採用**匿名化**策略：將 `my_user_id` 設為 **`-user_id`**（負數 sentinel value），保留歷史記錄供稽核。
- **`reservations`（對方視角）**：對方（counterparty）的預約記錄中 `user_id = 被刪除者` 的列，同樣將 `user_id` 設為 **`-user_id`**。**必須處理**，否則對方查看預約歷史時 `user_id` 指向不存在的 profile，會導致前端 404 或未來 JOIN 修正後出現 NULL crash。由於阻擋檢查已確保僅剩 HISTORY 記錄，此 UPDATE 不影響任何進行中的業務流程。
- **`mentor_schedules`**：硬刪該 `user_id` 之所有時段。
- **`mentor_experiences`、`profiles`、`canned_messages`**：硬刪。
- **`file_info`**：軟刪——將 `is_deleted` 設為 `TRUE`（依 `create_user_id = user_id`）；S3 物件由排程或 lifecycle 清除。

> **為何使用 `-user_id` 而非固定值 `0`？**  
> `reservations` 表存在 unique index `uidx_reservation_user_dtstart_dtend_schedule_id_user_id ON reservations(my_user_id, dtstart, dtend, schedule_id, user_id)`。若多位已刪除使用者的歷史預約恰好具有相同的 `(dtstart, dtend, schedule_id)` 與相同的對方 `user_id`，統一設為 `0` 將違反 unique constraint。使用 `-user_id`（每位使用者唯一的負數）可保證匿名化後仍滿足 unique 約束，同時可透過 `user_id < 0` 或 `my_user_id < 0` 判斷「已刪除使用者」，並可由 `abs(sentinel)` 反推原始 `user_id` 供稽核。

---

## 8. X-Career-Auth：資料處理要點

- 刪除 DynamoDB 帳戶 item（條件與專案現有 `email` 主鍵／GSI 設計一致）。
- 撤銷 **refresh_token**（DB 欄位清空或列入黑名單）。
- 若存在 **user_id → email** 對照快取，一併失效。

---

## 9. X-Career-Search

- 發送 SQS 訊息：`action: "DELETE_MENTOR_PROFILE"`，`user_id: <int>`（其餘欄位與現有 mentor event 慣例一致即可）。
- Consumer：`SearchService._delete_mentor_by_event` → `delete_mentor(user_id)`。

---

## 10. 安全與滥用

- 刪除 API **限流**（per IP / per user）。
- 僅 **HTTPS**；敏感 body 不寫入 log。
- 監控 409 比例與 5xx，避免惡意掃描。

---

## 11. 驗收清單（摘要）

- [ ] 有**未來且非 REJECT** 之 `reservations`（`my_user_id` 為該使用者）時，回 **409**，且 Auth／User 核心資料均**未被刪除**。
- [ ] 無上述預約時，通過 step-up 後可完成刪除；再次呼叫刪除 **冪等**成功。
- [ ] 刪除後，該使用者自身與對方視角的 `reservations` 中相關 `my_user_id` / `user_id` 均已匿名化為 `-user_id`（負數 sentinel）。
- [ ] Mentor 刪除後，SQS 觸發 OpenSearch 文件刪除（最終一致可接受延遲）。
- [ ] 舊 refresh token 無法再換發 access token。

---

## 12. 參考（程式碼錨點）

| 項目 | 路徑 |
|------|------|
| BFF Auth 路由 | `X-Career-BFF/src/router/v1/auth.py` |
| User 預約查詢條件 | `X-Career-User/src/domain/user/dao/reservation_repository.py`（`get_user_reservations`） |
| Search 刪除 mentor | `X-Career-Search/src/domain/search/service/search_service.py`（`DELETE_MENTOR_PROFILE`） |
| `MentorAction` | `X-Career-Search/src/config/constant.py` |
| DB schema | `X-Career-User/src/infra/db/sql/init/user_init.sql` |

---

**文件結束**

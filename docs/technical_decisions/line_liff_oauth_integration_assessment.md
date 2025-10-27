# LINE LIFF OAuth 整合技術評估報告

**文件版本**: v1.0
**建立日期**: 2025-10-20
**作者**: TaskMaster Hub / Claude Code AI
**狀態**: 決策完成 - 採用階段性實作策略

---

## 🎯 執行摘要

**決策**: 採用階段性實作策略，現階段（Sprint 1）暫不實作 LINE OAuth 整合，使用 Mock 模式支援開發。

**理由**:
1. LINE 整合非 Sprint 1 關鍵路徑
2. 後端認證架構已完成（已支援雙認證流程）
3. Mock 模式足以支援前端開發與測試
4. 節省 7h 開發時間，降低環境設定風險

**實作時程**:
- **Sprint 1 (當前)**: Mock 模式 (0.2h)
- **Sprint 2 Week 1**: Zeabur 部署 + 真實 LINE 整合 (3h)
- **Sprint 8**: 生產環境 Custom Domain (1h)

---

## 1. 技術架構分析

### 1.1 LINE LIFF OAuth 基本要求

| 項目 | 需求 | 原因 |
|------|------|------|
| **HTTPS** | 強制要求 | LINE 平台安全策略，不接受 HTTP |
| **公開網域** | 必須可從公網訪問 | LINE Server 需要回調 (callback) |
| **Redirect URI** | 必須預先在 LINE Developer Console 註冊 | 防止 OAuth 劫持 |
| **LIFF ID** | 必須建立 LIFF App | 綁定 LINE Channel |

### 1.2 本地開發環境挑戰

```
問題: localhost:8000 無法被 LINE Server 訪問
解決方案:
1. Docker + Nginx + ngrok (複雜度高，7h)
2. Docker + ngrok 直連 (簡化版，5h)
3. Zeabur 測試部署 (推薦，3h)
4. Mock 模式 + Zeabur 階段性 (最佳，4.2h)
```

---

## 2. 方案比較

### 方案 A: Docker + Nginx + ngrok（原始方案）

**架構**:
```
Public Internet → ngrok → Nginx → Docker FastAPI
```

**優缺點**:
- ✅ 完全本地控制
- ✅ 模擬生產環境
- ❌ 設定複雜（3 層）
- ❌ ngrok 免費版 URL 不固定
- ❌ 每次重啟需更新 LINE 設定

**工時**: 7h
**成本**: $24 (ngrok Pro 3個月)

---

### 方案 D: 混合方案（採用方案）⭐⭐⭐

**架構**:
```
本地開發: Docker FastAPI (Mock 模式)
LINE 測試: Zeabur staging (真實 LINE API)
生產環境: Zeabur production + Custom Domain
```

**優缺點**:
- ✅ 開發迭代快（無需等待 tunnel）
- ✅ URL 固定（Zeabur 自動 HTTPS）
- ✅ 接近生產環境
- ✅ CI/CD ready
- ⚠️ 需要網路訪問 Zeabur

**工時**: 4.2h
**成本**: $0 (Zeabur 免費層)
**節省**: 2.8h + $24

---

## 3. 階段性實作規劃

### 階段 1: Mock 模式（Sprint 1 - 當前）

**目標**: 支援前端開發，無需真實 LINE API

**實作** (0.2h):
```python
# backend/src/respira_ally/core/config.py
class Settings(BaseSettings):
    LINE_OAUTH_MOCK: bool = Field(default=True, env="LINE_OAUTH_MOCK")

# backend/src/respira_ally/application/auth/use_cases/login_use_case.py
class PatientLoginUseCase:
    async def execute(self, line_user_id: str, line_access_token: str | None = None):
        if settings.LINE_OAUTH_MOCK:
            # Mock mode: Accept any LINE User ID starting with U_MOCK_
            if not line_user_id.startswith("U_MOCK_"):
                raise UnauthorizedError("Mock mode: LINE User ID must start with U_MOCK_")
            display_name = f"Test Patient {line_user_id[-3:]}"
        else:
            # Real mode: Verify LINE access token
            profile = await self._verify_line_access_token(line_access_token)
            display_name = profile.get("displayName")

        # ... rest of the login logic
```

**測試用例**:
```bash
# Mock 模式測試
curl -X POST http://localhost:8000/api/v1/auth/patient/login \
  -H "Content-Type: application/json" \
  -d '{"line_user_id": "U_MOCK_001"}'
```

**環境變數**:
```bash
# .env.development
LINE_OAUTH_MOCK=true
```

---

### 階段 2: Zeabur 測試環境（Sprint 2 Week 1）

**目標**: 整合真實 LINE LIFF OAuth API

**工時**: 3h

#### Step 1: Zeabur 部署 (1h)

1. **連接 GitHub Repo**:
   - 登入 [Zeabur Dashboard](https://dash.zeabur.com/)
   - New Project → Import from GitHub
   - 選擇 `RespiraAlly_v2` repository
   - 選擇 `backend` 目錄

2. **設定環境變數**:
   ```
   ENVIRONMENT=staging
   DATABASE_URL=postgresql://...
   REDIS_URL=redis://...
   JWT_SECRET_KEY=...
   LINE_OAUTH_MOCK=false
   LINE_CHANNEL_ID=<待設定>
   LINE_CHANNEL_SECRET=<待設定>
   LINE_LIFF_ID=<待設定>
   ```

3. **自動獲得 HTTPS URL**:
   - 例: `https://respiraally-staging.zeabur.app`

#### Step 2: LINE LIFF 設定 (1h)

1. **LINE Developers Console**:
   - 登入 https://developers.line.biz/
   - Create Provider: "RespiraAlly"
   - Create Messaging API Channel:
     - Name: RespiraAlly COPD Assistant
     - Category: Medical/Healthcare

2. **建立 LIFF App**:
   - LIFF app name: RespiraAlly Patient Portal
   - Size: Full
   - Endpoint URL: `https://respiraally-staging.zeabur.app/liff`
   - Scope: `profile`, `openid`
   - 記錄 LIFF ID: `1234567890-AbCdEfGh`

3. **更新 Zeabur 環境變數**:
   - LINE_CHANNEL_ID
   - LINE_CHANNEL_SECRET
   - LINE_LIFF_ID

#### Step 3: 後端 LINE API 整合 (1h)

```python
# backend/src/respira_ally/infrastructure/external_apis/line_api_client.py
import httpx
from respira_ally.core.config import settings
from respira_ally.core.exceptions.application_exceptions import UnauthorizedError

class LineAPIClient:
    """LINE Messaging API Client"""

    BASE_URL = "https://api.line.me"

    async def verify_access_token(self, access_token: str) -> dict:
        """
        Verify LINE access token and get user profile

        Args:
            access_token: LINE access token from LIFF SDK

        Returns:
            User profile: {userId, displayName, pictureUrl, statusMessage}

        Raises:
            UnauthorizedError: If token is invalid
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.BASE_URL}/v2/profile",
                headers={"Authorization": f"Bearer {access_token}"},
                timeout=10.0
            )

            if response.status_code == 401:
                raise UnauthorizedError("Invalid LINE access token")

            if response.status_code != 200:
                raise UnauthorizedError(f"LINE API error: {response.status_code}")

            return response.json()

    async def verify_id_token(self, id_token: str) -> dict:
        """
        Verify LINE ID token (OpenID Connect)

        Args:
            id_token: LINE ID token from LIFF SDK

        Returns:
            Decoded token payload
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.BASE_URL}/oauth2/v2.1/verify",
                data={
                    "id_token": id_token,
                    "client_id": settings.LINE_CHANNEL_ID
                },
                timeout=10.0
            )

            if response.status_code != 200:
                raise UnauthorizedError("Invalid LINE ID token")

            return response.json()

# Singleton instance
line_api_client = LineAPIClient()
```

**更新 PatientLoginUseCase**:
```python
from respira_ally.infrastructure.external_apis.line_api_client import line_api_client

class PatientLoginUseCase:
    async def execute(self, line_user_id: str, line_access_token: str | None = None):
        if settings.LINE_OAUTH_MOCK:
            # Mock mode (local development)
            display_name = f"Test Patient {line_user_id[-3:]}"
        else:
            # Real mode (staging/production)
            if not line_access_token:
                raise UnauthorizedError("LINE access token is required")

            profile = await line_api_client.verify_access_token(line_access_token)

            # Verify LINE User ID matches
            if profile["userId"] != line_user_id:
                raise UnauthorizedError("LINE User ID mismatch")

            display_name = profile.get("displayName", "LINE User")

        # ... rest of the login logic (unchanged)
```

---

### 階段 3: 生產環境（Sprint 8）

**目標**: 使用 Custom Domain

**工時**: 1h

1. **購買域名** (如果需要):
   - 例: `app.respiraally.com`
   - 建議使用 Cloudflare/Namecheap ($12/年)

2. **Zeabur Custom Domain 設定**:
   - Zeabur Dashboard → Domains → Add Custom Domain
   - CNAME 指向 Zeabur
   - 自動配置 SSL 憑證

3. **更新 LINE LIFF Endpoint**:
   - 從 `https://respiraally-staging.zeabur.app`
   - 改為 `https://app.respiraally.com`

---

## 4. 前端 LIFF 整合參考

### 4.1 LIFF SDK 安裝

```bash
# frontend/liff-app (Vite + React)
npm install @line/liff
```

### 4.2 LIFF 初始化

```typescript
// src/services/liffService.ts
import liff from '@line/liff';

const LIFF_ID = import.meta.env.VITE_LINE_LIFF_ID;

export class LiffService {
  async init() {
    try {
      await liff.init({ liffId: LIFF_ID });

      if (!liff.isLoggedIn()) {
        liff.login();
      }
    } catch (error) {
      console.error('LIFF init failed', error);
      throw error;
    }
  }

  async getProfile() {
    const profile = await liff.getProfile();
    return {
      userId: profile.userId,
      displayName: profile.displayName,
      pictureUrl: profile.pictureUrl,
    };
  }

  getAccessToken() {
    return liff.getAccessToken();
  }

  async login() {
    const accessToken = this.getAccessToken();
    const profile = await this.getProfile();

    // 發送到後端登入
    const response = await fetch('/api/v1/auth/patient/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        line_user_id: profile.userId,
        line_access_token: accessToken,
      }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();

    // 儲存 JWT tokens
    localStorage.setItem('access_token', data.access_token);
    localStorage.setItem('refresh_token', data.refresh_token);

    return data;
  }
}

export const liffService = new LiffService();
```

### 4.3 React 組件使用

```tsx
// src/pages/LiffLogin.tsx
import { useEffect, useState } from 'react';
import { liffService } from '../services/liffService';

export function LiffLogin() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function initLiff() {
      try {
        await liffService.init();
        await liffService.login();

        // 登入成功，導向主頁
        window.location.href = '/';
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    initLiff();
  }, []);

  if (loading) return <div>載入中...</div>;
  if (error) return <div>登入失敗: {error}</div>;

  return null;
}
```

---

## 5. 測試策略

### 5.1 本地開發測試（Mock 模式）

```bash
# 後端測試
curl -X POST http://localhost:8000/api/v1/auth/patient/login \
  -H "Content-Type: application/json" \
  -d '{
    "line_user_id": "U_MOCK_001",
    "line_access_token": null
  }'

# 預期回應
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "user_id": "...",
    "role": "patient",
    "line_user_id": "U_MOCK_001",
    "display_name": "Test Patient 001",
    ...
  }
}
```

### 5.2 Zeabur 測試（真實 LINE）

1. **前端**:
   - 訪問 `https://liff.line.me/1234567890-AbCdEfGh`
   - LINE App 自動打開 LIFF 頁面
   - 授權後自動登入

2. **後端驗證**:
   - 檢查 Zeabur logs: `zeabur logs -f`
   - 確認 LINE API 調用成功
   - 確認 JWT 生成正確

---

## 6. 風險與緩解

| 風險 | 影響 | 機率 | 緩解策略 |
|------|------|------|----------|
| **LINE API 變更** | 中 | 低 | 鎖定 SDK 版本，監控官方公告 |
| **Zeabur 服務中斷** | 高 | 極低 | 準備備用部署方案 (Render/Railway) |
| **LIFF ID 洩漏** | 低 | 中 | LIFF ID 本身不敏感，Channel Secret 才需保護 |
| **Token 驗證失敗** | 中 | 低 | 實作降級機制（允許暫時 Mock） |

---

## 7. 成本分析

### 開發階段（3 個月）

| 項目 | Docker+ngrok | Zeabur 方案 | 節省 |
|------|-------------|------------|------|
| **工時** | 7h × $50 = $350 | 4.2h × $50 = $210 | $140 |
| **Hosting** | ngrok Pro $24 | Zeabur 免費 $0 | $24 |
| **總計** | **$374** | **$210** | **$164 (44%)** |

### 生產環境（年度）

| 項目 | 成本 |
|------|------|
| Zeabur Pro | $5/月 × 12 = $60 |
| Custom Domain | $12/年 |
| SSL Certificate | $0 (Zeabur 免費) |
| **總計** | **$72/年** |

---

## 8. 決策記錄

**決策日期**: 2025-10-20
**決策者**: TaskMaster Hub + 使用者確認
**決策**: 採用階段性實作策略（方案 D）

**決策依據**:
1. **投資報酬率**: 節省 44% 成本與時間
2. **風險控制**: 降低環境設定複雜度
3. **Sprint 1 優先級**: 前端基礎架構更重要
4. **技術可行性**: Mock 模式足以支援開發

**替代方案**: Docker + Nginx + ngrok（被拒絕）
**拒絕原因**:
- 設定複雜度高（7h vs 4.2h）
- ngrok 免費版 URL 不穩定
- 過度工程（本地開發不需要完整生產環境）

---

## 9. 行動計劃

### Sprint 1（本週）- 優先級 P0
- [x] ✅ 撰寫評估報告
- [ ] ⬜ 實作 Mock 模式 (0.2h)
- [ ] ⬜ 更新 .env.example
- [ ] ⬜ 撰寫測試文檔

### Sprint 2 Week 1 - 優先級 P1
- [ ] ⬜ Zeabur staging 部署 (1h)
- [ ] ⬜ LINE LIFF App 設定 (1h)
- [ ] ⬜ LINE API 整合實作 (1h)
- [ ] ⬜ E2E 測試驗證

### Sprint 8 - 優先級 P2
- [ ] ⬜ 生產環境 Custom Domain 設定 (1h)
- [ ] ⬜ 性能測試與優化

---

## 10. 參考資源

### 官方文檔
- [LINE LIFF 官方文檔](https://developers.line.biz/en/docs/liff/)
- [LINE Login API Reference](https://developers.line.biz/en/reference/line-login/)
- [Zeabur 部署指南](https://zeabur.com/docs)

### 工具與 SDK
- [@line/liff NPM Package](https://www.npmjs.com/package/@line/liff)
- [ngrok 文檔](https://ngrok.com/docs)
- [FastAPI HTTPS Deployment](https://fastapi.tiangolo.com/deployment/)

### 內部文檔
- `docs/06_api_design_specification.md` - API 設計規範
- `docs/technical_decisions/security/jwt_authentication_design.md` - JWT 認證設計
- `docs/16_wbs_development_plan.md` - 工作分解結構

---

**文件維護**: 本文檔應在每個實作階段完成後更新實際執行結果與經驗教訓。

**下次審查**: Sprint 2 Week 1 完成 LINE 整合後

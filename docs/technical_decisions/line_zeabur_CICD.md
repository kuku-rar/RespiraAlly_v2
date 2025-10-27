  # 📋 LINE LIFF OAuth 整合技術評估報告

  ### 🎯 執行摘要

  LINE LIFF (LINE Front-end Framework) OAuth 整合需要 HTTPS 公開 
  URL，這在本地開發環境中需要特殊處理。本報告分析技術架構、實作複雜度、風險，並提供多種實作策略建議。

  ---
  1. 技術架構分析

  1.1 LINE LIFF OAuth 基本要求

  | 項目           | 需求                              | 原因                          |
  |--------------|---------------------------------|-----------------------------|
  | HTTPS        | 強制要求                            | LINE 平台安全策略，不接受 HTTP        |
  | 公開網域         | 必須可從公網訪問                        | LINE Server 需要回調 (callback) |
  | Redirect URI | 必須預先在 LINE Developer Console 註冊 | 防止 OAuth 劫持                 |
  | LIFF ID      | 必須建立 LIFF App                   | 綁定 LINE Channel             |

  1.2 你提到的架構 (Docker + Nginx + ngrok)

  ┌─────────────────────────────────────────────────────────┐
  │  Public Internet (LINE Server)                          │
  └────────────────────┬────────────────────────────────────┘
                       │ HTTPS callback
                       ▼
           ┌───────────────────────┐
           │  ngrok Tunnel         │ https://xxxx.ngrok.io
           │  (Public HTTPS URL)   │
           └───────────┬───────────┘
                       │ HTTP proxy
                       ▼
           ┌───────────────────────┐
           │  Nginx (Reverse Proxy)│ localhost:80
           │  - SSL Termination?   │
           │  - Request Routing    │
           └───────────┬───────────┘
                       │
           ┌───────────▼───────────┐
           │  Docker Container     │
           │  FastAPI Backend      │ localhost:8000
           │  (RespiraAlly)        │
           └───────────────────────┘

  架構評估:
  - ✅ 可行: 技術上完全可行
  - ⚠️ 複雜度: 3 層 (ngrok + Nginx + Docker) 較為複雜
  - ⚠️ 成本: ngrok 免費版有限制（見下方分析）

  ---
  2. 實作複雜度評估

  2.1 開發環境 vs 生產環境

  | 環境   | HTTPS 方案               | 複雜度   | 建議                 |
  |------|------------------------|-------|--------------------|
  | 本地開發 | ngrok + Nginx (你提到的方案) | 🟡 中等 | 有更簡單的替代方案          |
  | 測試環境 | Zeabur 直接部署            | 🟢 低  | 推薦！Zeabur 自動 HTTPS |
  | 生產環境 | Zeabur + Custom Domain | 🟢 低  | 使用正式域名             |

  2.2 你提到方案的實作步驟

  Step 1: Docker Compose 設定

  services:
    backend:
      build: ./backend
      ports:
        - "8000:8000"
      environment:
        - DATABASE_URL=postgresql://...
        - REDIS_URL=redis://redis:6379
      depends_on:
        - postgres
        - redis

    nginx:
      image: nginx:alpine
      ports:
        - "80:80"
        - "443:443"  # 如果需要本地 SSL
      volumes:
        - ./nginx.conf:/etc/nginx/nginx.conf
      depends_on:
        - backend

  工時估計: 2h (配置 + 測試)

  Step 2: Nginx 配置

  server {
      listen 80;
      server_name localhost;

      location /api {
          proxy_pass http://backend:8000;
          proxy_set_header Host $host;
          proxy_set_header X-Real-IP $remote_addr;
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header X-Forwarded-Proto $scheme;
      }
  }

  工時估計: 1h (配置 + 測試)

  Step 3: ngrok 設定

  # 安裝 ngrok
  brew install ngrok  # macOS
  # 或 choco install ngrok  # Windows

  # 認證 (需註冊免費帳號)
  ngrok authtoken YOUR_AUTH_TOKEN

  # 啟動 tunnel
  ngrok http 80  # 指向 Nginx

  ⚠️ ngrok 免費版限制:
  - ❌ 每次重啟 URL 會變 (https://xxxx.ngrok.io 的 xxxx 會改變)
  - ❌ 每次都要到 LINE Developer Console 更新 Redirect URI
  - ❌ 連線數限制 (40 connections/min)
  - ✅ 付費版 ($8/月) 可固定 domain

  工時估計: 1h (安裝 + 配置)

  Step 4: LINE LIFF 設定

  1. 登入 https://developers.line.biz/
  2. 建立 LIFF App
  3. 設定 Endpoint URL: https://xxxx.ngrok.io/liff
  4. 取得 LIFF ID

  工時估計: 1h (首次設定 + 文檔閱讀)

  Step 5: 後端整合

  # src/respira_ally/application/auth/use_cases/line_oauth_use_case.py
  import httpx

  async def verify_line_access_token(access_token: str) -> dict:
      """Call LINE Profile API to verify token"""
      async with httpx.AsyncClient() as client:
          response = await client.get(
              "https://api.line.me/v2/profile",
              headers={"Authorization": f"Bearer {access_token}"}
          )
          if response.status_code != 200:
              raise UnauthorizedError("Invalid LINE access token")
          return response.json()  # {userId, displayName, pictureUrl}

  工時估計: 2h (實作 + 測試)

  ---
  3. 替代方案比較

  方案 A: Docker + Nginx + ngrok (你提到的)

  | 優點        | 缺點                  |
  |-----------|---------------------|
  | ✅ 完全本地控制  | ❌ 設定複雜（3 層）         |
  | ✅ 模擬生產環境  | ❌ ngrok 免費版 URL 不固定 |
  | ✅ 可離線開發後端 | ❌ 每次重啟需更新 LINE 設定   |

  總工時: 7h (設定 2h + Nginx 1h + ngrok 1h + LINE 設定 1h + 後端整合 2h)

  ---
  方案 B: Docker + ngrok 直連（簡化版）⭐ 推薦開發環境

  Public Internet → ngrok → Docker FastAPI (8000)

  省略 Nginx，直接用 ngrok 指向 Docker：

  # docker-compose.yml
  services:
    backend:
      ports:
        - "8000:8000"

  # 啟動
  docker-compose up -d
  ngrok http 8000

  | 優點          | 缺點                  |
  |-------------|---------------------|
  | ✅ 設定簡單（2 層） | ❌ ngrok 免費版 URL 不固定 |
  | ✅ 開發迭代快     | ❌ 無法測試 Nginx 配置     |
  | ✅ 少一層 debug | ⚠️ 每次重啟需更新 LINE     |

  總工時: 5h (設定 1h + ngrok 1h + LINE 設定 1h + 後端整合 2h)
  節省: 2h

  ---
  方案 C: Zeabur 測試部署 ⭐⭐ 強烈推薦

  直接部署到 Zeabur，自動獲得 HTTPS domain：

  Public Internet → Zeabur (自動 HTTPS) → FastAPI

  Zeabur 自動提供:
  - ✅ 固定 HTTPS URL: https://your-app.zeabur.app
  - ✅ 自動 SSL 憑證
  - ✅ 環境變數管理
  - ✅ 一鍵部署（GitHub integration）
  - ✅ 免費 tier 足夠開發測試

  設定步驟:
  1. Push code to GitHub
  2. Zeabur 連接 GitHub repo
  3. 設定環境變數（DATABASE_URL, REDIS_URL, JWT_SECRET）
  4. 自動部署 → 獲得 https://respiraally.zeabur.app
  5. LINE Console 設定 Redirect URI: https://respiraally.zeabur.app/api/v1/auth/line/callback

  | 優點            | 缺點                       |
  |---------------|--------------------------|
  | ✅ 零配置 HTTPS   | ⚠️ 需要穩定網路                |
  | ✅ URL 固定不變    | ⚠️ 環境變數需在雲端管理            |
  | ✅ 接近生產環境      | ⚠️ debug 較不直觀（需看雲端 logs） |
  | ✅ 團隊協作友善      |                          |
  | ✅ CI/CD ready |                          |

  總工時: 3h (Zeabur 設定 1h + LINE 設定 1h + 後端整合 1h)
  節省: 4h

  ---
  方案 D: 混合方案（最佳實踐）⭐⭐⭐ 最推薦

  本地開發: 不整合 LINE（Mock 模式）
  LINE 測試: Zeabur 測試環境
  生產環境: Zeabur 正式環境 + Custom Domain

  實作策略:

  1. 本地開發模式

  # .env.local
  ENVIRONMENT=development
  LINE_OAUTH_MOCK=true

  # PatientLoginUseCase
  if settings.LINE_OAUTH_MOCK:
      # Mock LINE profile response
      user_profile = {"userId": "U123456", "displayName": "Test Patient"}
  else:
      # Real LINE API call
      user_profile = await verify_line_access_token(token)

  2. Zeabur 測試環境

  # Zeabur 環境變數
  ENVIRONMENT=staging
  LINE_CHANNEL_ID=...
  LINE_CHANNEL_SECRET=...
  LINE_LIFF_ID=...

  3. 生產環境

  ENVIRONMENT=production
  CUSTOM_DOMAIN=https://app.respiraally.com

  | 階段      | 方案                | LINE 整合     | 工時       |
  |---------|-------------------|-------------|----------|
  | 本地開發    | Docker only       | Mock 模式     | 0h (已完成) |
  | LINE 測試 | Zeabur staging    | 真實 LINE API | 3h       |
  | 生產部署    | Zeabur production | 真實 LINE API | 1h       |

  總工時: 4h
  節省: 3h

  ---
  4. 風險評估與緩解策略

  4.1 技術風險

  | 風險           | 影響  | 機率                 | 緩解策略                      |
  |--------------|-----|--------------------|---------------------------|
  | ngrok URL 變動 | 高   | 高（每次重啟）            | 使用 Zeabur 固定 URL          |
  | HTTPS 憑證問題   | 中   | 低（ngrok/Zeabur 處理） | 使用託管服務                    |
  | LINE API 變更  | 中   | 低                  | 參考官方文檔 + 版本鎖定             |
  | 網路延遲         | 低   | 中（ngrok tunnel）    | 使用 Zeabur 減少 hop          |
  | 環境變數洩漏       | 高   | 低                  | 使用 .env.local (gitignore) |

  4.2 開發流程風險

  | 風險                | 緩解策略                     |
  |-------------------|--------------------------|
  | 本地無法測試 LINE       | 使用 Mock 模式 + Zeabur 測試環境 |
  | 團隊成員環境不一致         | 統一使用 Zeabur staging      |
  | LINE Console 設定錯誤 | 建立設定檢查清單（見下方）            |

  ---
  5. 實作建議 ⭐ 我的推薦

  推薦方案: 方案 D (混合方案)

  第一階段: 跳過 LINE 整合（現階段）
  - ✅ 使用 Mock 模式完成後端其他功能
  - ✅ 病患登入暫時使用 Mock LINE User ID: "U_MOCK_PATIENT_001"
  - ✅ 專注完成 Sprint 1 其他任務（前端基礎架構）

  時程: 0h（當前）
  理由:
  1. LINE 整合非關鍵路徑（可延後）
  2. 後端 Auth 架構已完成（已支援雙認證流程）
  3. Mock 模式足以支援前端開發與測試

  ---
  第二階段: Zeabur 測試環境部署（Sprint 2 Week 1）
  - ✅ 部署到 Zeabur staging: https://respiraally-staging.zeabur.app
  - ✅ 設定 LINE LIFF App
  - ✅ 實作 LINE Profile API 整合
  - ✅ E2E 測試病患登入流程

  時程: 3h
  依賴: Task 3.5 (前端基礎架構) 完成後

  ---
  第三階段: 生產環境上線（Sprint 8）
  - ✅ Custom domain: https://app.respiraally.com
  - ✅ 更新 LINE LIFF Endpoint URL
  - ✅ 生產環境測試

  時程: 1h

  ---
  6. LINE LIFF 整合實作檢查清單

  6.1 LINE Developer Console 設定

  - 建立 Provider (如果沒有)
    - 名稱: RespiraAlly
    - Email: your-email@example.com
  - 建立 Messaging API Channel
    - Channel name: RespiraAlly COPD Assistant
    - Channel description: COPD 病患健康管理平台
    - Category: Medical/Healthcare
    - Subcategory: Health Management
  - 建立 LIFF App
    - LIFF app name: RespiraAlly Patient Portal
    - Size: Full
    - Endpoint URL: https://your-domain/liff
    - Scope: profile, openid
    - Bot link feature: On (推薦)
  - 記錄重要資訊
    - LINE Channel ID: 1234567890
    - LINE Channel Secret: xxxxxxxxxxxxxxxx
    - LINE LIFF ID: 1234567890-AbCdEfGh

  6.2 後端實作檢查清單

  - ✅ PatientLoginUseCase 已實作（支援 line_user_id）
  - ⬜ LINE Profile API 整合 (verify_line_access_token)
  - ⬜ 環境變數設定 (LINE_CHANNEL_ID, LINE_CHANNEL_SECRET, LINE_LIFF_ID)
  - ⬜ 錯誤處理（LINE API 失敗降級）

  6.3 前端實作檢查清單 (LIFF)

  - ⬜ LIFF SDK 安裝: npm install @line/liff
  - ⬜ LIFF init: liff.init({ liffId: 'YOUR_LIFF_ID' })
  - ⬜ 取得 Access Token: liff.getAccessToken()
  - ⬜ 取得 Profile: liff.getProfile()
  - ⬜ 發送 LINE User ID 到後端登入

  ---
  7. 成本分析

  7.1 開發階段成本（3 個月）

  | 項目             | 方案 A (ngrok 付費)   | 方案 D (Zeabur)     | 節省         |
  |----------------|-------------------|-------------------|------------|
  | Tunnel/Hosting | $8/月 × 3 = $24    | Zeabur 免費層 $0     | $24        |
  | 開發時間           | 7h × $50/h = $350 | 4h × $50/h = $200 | $150       |
  | 總成本            | $374              | $200              | $174 (46%) |

  7.2 生產環境成本（年度）

  | 項目              | 成本                           |
  |-----------------|------------------------------|
  | Zeabur Hosting  | $5/月 × 12 = $60/年 (Pro plan) |
  | Custom Domain   | $12/年 (.com domain)          |
  | SSL Certificate | $0 (Zeabur 免費)               |
  | 總計              | $72/年                        |

  ---
  8. 結論與建議

  8.1 立即行動（現階段）

  ✅ 建議: 暫不實作 LINE 整合

  理由:
  1. Sprint 1 優先級: 剩餘 15h 應專注於前端基礎架構（Task 3.5）
  2. 技術就緒: 後端已支援 LINE User ID 登入（PatientLoginUseCase）
  3. Mock 模式足夠: 可用 Mock 模式完成前後端對接
  4. 風險控制: 避免環境設定問題阻塞 Sprint 1 進度

  Mock 模式實作 (10 分鐘):
  # .env
  LINE_OAUTH_MOCK=true

  # PatientLoginUseCase
  if settings.LINE_OAUTH_MOCK:
      # 允許測試用 LINE User ID
      if line_user_id.startswith("U_MOCK_"):
          display_name = "Test Patient"
      else:
          raise UnauthorizedError("Mock mode: Use U_MOCK_* prefix")

  ---
  8.2 下一步規劃（Sprint 2）

  任務: Task 3.4.5 - LINE LIFF OAuth 整合 (3h)
  時程: Sprint 2 Week 1

  實作步驟:
  1. Zeabur 部署 (1h):
    - 部署 FastAPI 到 Zeabur staging
    - 獲得固定 HTTPS URL
    - 配置環境變數
  2. LINE LIFF 設定 (1h):
    - 建立 LIFF App
    - 設定 Endpoint URL
    - 記錄 LIFF ID 與 Channel credentials
  3. 後端整合 (1h):
    - 實作 LINE Profile API 調用
    - 移除 Mock 模式（Zeabur 環境）
    - E2E 測試

  ---
  8.3 最終建議

  🎯 推薦策略: 階段性實作

  | 階段              | 時程  | 方案                 | 工時   | 優先級       |
  |-----------------|-----|--------------------|------|-----------|
  | 當前 (Sprint 1)   | 本週  | Mock 模式            | 0.2h | 🔴 High   |
  | Sprint 2 Week 1 | 下週  | Zeabur + 真實 LINE   | 3h   | 🟡 Medium |
  | Sprint 8        | 上線前 | 生產環境 Custom Domain | 1h   | 🟢 Low    |

  總工時: 4.2h (vs 方案 A 的 7h，節省 40%)

  ---
  9. 問題與解答

  Q1: 為什麼不建議現在就用 Docker + Nginx + ngrok？

  A: 三個原因：
  1. 投資報酬率低: 7h 設定時間 vs 0.2h Mock 模式，獲益不明顯
  2. 環境不穩定: ngrok 免費版 URL 每次變動，需反覆更新 LINE 設定
  3. 過度工程: 本地開發不需要完整模擬生產環境 (YAGNI 原則)

  Q2: Zeabur 免費層真的足夠嗎？

  A: 開發測試階段完全足夠：
  - ✅ 256MB RAM (FastAPI 足夠)
  - ✅ 自動 HTTPS + 固定 URL
  - ✅ GitHub auto-deploy
  - ⚠️ 生產環境建議升級 Pro ($5/月)

  Q3: 如果一定要本地測試 LINE 怎麼辦？

  A: 使用 方案 B (Docker + ngrok 直連)：
  docker-compose up -d
  ngrok http 8000
  # 暫時更新 LINE Redirect URI → ngrok URL
  測試完成後切回 Zeabur URL。

  Q4: LINE LIFF SDK 前端怎麼整合？

  A: 前端流程（Task 3.5.6 - LIFF 註冊頁）:
  // 初始化 LIFF
  await liff.init({ liffId: 'YOUR_LIFF_ID' });

  // 取得 Access Token 與 Profile
  const accessToken = liff.getAccessToken();
  const profile = await liff.getProfile();

  // 發送到後端登入
  await axios.post('/api/v1/auth/patient/login', {
    line_user_id: profile.userId,
    line_access_token: accessToken
  });

  ---
  附錄: 參考資源

  - https://developers.line.biz/en/docs/liff/
  - https://ngrok.com/docs
  - https://zeabur.com/docs
  - https://fastapi.tiangolo.com/deployment/

  ---
  報告撰寫: Claude Code AI
  最後更新: 2025-10-20 22:45
  版本: v1.0

  ---
  你對這份評估有什麼看法？我建議我們採用「階段性實作」策略：現在先用 Mock 模式完成 Sprint 1，下個 Sprint 再部署到 Zeabur 做真實 LINE 
  整合。這樣可以節省 40% 時間並降低風險。你覺得如何？
  ⎿  SessionStart:compact hook error
  ⎿  UserPromptSubmit hook error
  ⎿  UserPromptSubmit hook error

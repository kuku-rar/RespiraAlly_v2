# 🚀 TaskMaster & Claude Code Collective

**人類主導的文檔導向智能協作開發平台**

> **核心理念**: 人類是鋼彈駕駛員，TaskMaster 是智能副駕駛

## 🎯 系統特色

- **📄 文檔導向流程** - Phase 1-2 先生成專案文檔供駕駛員審查，通過後才進入 Phase 3 開發
- **🤖⚔️ TaskMaster 協調** - Hub-and-Spoke 智能任務分配，人類保持最終決策權
- **📋 WBS Todo List** - 統一開發狀態管理，全程透明化追蹤
- **🎨 VibeCoding 範本** - 10 個企業級工作流程範本，JIT 智能載入
- **🪝 自動化 Hooks** - 偵測 CLAUDE_TEMPLATE.md 自動觸發，無縫整合現有工作流程
- **🔍 駕駛員審查閘道** - Phase 2.5 強制審查檢查點，確保文檔品質

## 🚀 **快速開始**

### 1️⃣ 獲得專案
```bash
# 下載專案到您的電腦
git clone [project-url]
cd claude-agentic-coding-template
```

### 2️⃣ 初始化設定
```bash
# 複製專案初始化範本
cp CLAUDE_TEMPLATE.md my-first-project.md
```

### 3️⃣ 啟動 Claude Code 並開啟專案
```bash
claude code
# 在 Claude Code 中開啟這個專案目錄
```

### 4️⃣ 自動 TaskMaster 初始化
- Claude Code 會自動偵測到 `CLAUDE_TEMPLATE.md` 檔案
- 系統會詢問：「我偵測到一個 TaskMaster 專案範本。您想要我初始化一個智能協作專案嗎？」
- **選擇「是」開始初始化流程**

### 5️⃣ VibeCoding 7問快速澄清 + TaskMaster 設定
完成專案需求分析後，TaskMaster 會自動：
- 📚 載入相關 VibeCoding 範本
- 🎯 生成智能任務列表
- 📊 評估專案複雜度
- 📋 建立 WBS Todo List
- 🤖 配置 Hub 協調策略

## 🎛️ **TaskMaster 控制模式**

### 🤖⚔️ **人類駕駛員模式** (預設)
- **觸發**: 系統預設模式
- **特色**: 您是鋼彈駕駛員，完全掌控所有決策，TaskMaster 提供智能建議

### 🎯 **建議密度控制**
- **HIGH**: 每個任務都需要人類確認
- **MEDIUM**: 關鍵決策點確認 (推薦新手)
- **LOW**: 僅重要里程碑確認
- **ADVISORY**: Hub 建議模式，最小干預

### 🛡️ **安全控制機制**
- **`/pause`**: 立即暫停所有自動化，完全手動接管
- **緊急停止**: 隨時可以中斷任何 TaskMaster 操作
- **狀態透明**: 所有執行狀態和決策過程完全可見

## 🤖 **TaskMaster 核心命令**

### 🎛️ **基本控制命令**
| 命令 | 功能 | 使用時機 |
|------|------|---------|
| **`/task-status`** 📊 | 查看完整專案狀態與 WBS Todo List | 隨時查看進度 |
| **`/task-next`** 🎯 | 獲得下個智能任務建議 | 不知道做什麼時 |
| **`/hub-delegate`** 🤖 | Hub 協調智能體委派執行 | 複雜任務委派 |
| **`/pause`** ⏸️ | 立即暫停所有自動化 | 想要手動控制時 |

### 🔧 **進階管理命令**
| 命令 | 功能 | 使用時機 |
|------|------|---------|
| **`/suggest-mode`** 🎛️ | 調整 TaskMaster 建議密度 | 控制干預頻率 |
| **`/review-code`** 🔍 | Hub 協調程式碼審查 | 品質檢查需求 |
| **`/task-init`** 🚀 | TaskMaster 專案初始化 | 新專案設定 |
| **`/task-skip`** ⏭️ | 跳過當前任務到下一個 | 任務優先級調整 |

### 🤖 **Claude Code 專業智能體整合**
TaskMaster Hub 會智能分析任務特性，自動建議最適合的專業智能體：
- **general-purpose** 🔧 - 通用任務處理
- **code-quality-specialist** 🔍 - 程式碼品質審查
- **test-automation-engineer** 🧪 - 測試自動化
- **security-infrastructure-auditor** 🔒 - 安全分析
- **deployment-expert** 🚀 - 部署專家
- **documentation-specialist** 📚 - 文檔專家
- **workflow-template-manager** ⭐ - 工作流程管理

## 📋 **WBS Todo List 系統**

### 🎯 **統一狀態管理**
```
📋 TaskMaster 控制中心:
├── 📋 總任務: 31個
├── ⏳ 待處理: 12個
├── 🔄 進行中: 1個
├── ✅ 已完成: 18個
└── 🎯 當前焦點: Task-019 實作用戶認證

🤖 Hub 狀態:
├── 可用智能體: 7個專業智能體
├── 協調模式: parallel-optimized
└── 建議信心: 92%
```

### ⚡ **持續同步更新**
- **任務狀態**: 即時追蹤每個任務的執行進度
- **全局透明**: 人類駕駛員隨時掌握專案全貌
- **智能協調**: Hub 根據 WBS 狀態智能建議下個任務
- **持久化存儲**: 所有狀態保存在 `.claude/taskmaster-data/`

## 📚 **完整文檔資源**

### 🚀 **新手必讀**
- **📋 [完整初學者指南](.claude/GETTING_STARTED.md)** - 從零開始的 8 步驟完整教學
- **🎯 [TaskMaster 初始化](.claude/commands/task-init.md)** - 專案初始化詳細流程

### 🔧 **技術文檔**
- **🤖 [TaskMaster 系統說明](.claude/TASKMASTER_README.md)** - 完整系統架構與功能說明
- **🔗 [Subagent 整合指南](.claude/SUBAGENT_INTEGRATION_GUIDE.md)** - 智能體整合機制說明
- **🆘 [故障排除指南](.claude/TROUBLESHOOTING.md)** - 常見問題解決方案

### 🎨 **VibeCoding 範本庫**
- **📊 [專案簡報與 PRD](VibeCoding_Workflow_Templates/01_project_brief_and_prd.md)**
- **🧪 [BDD 行為驅動開發](VibeCoding_Workflow_Templates/02_behavior_driven_development_guide.md)**
- **🏗️ [架構與設計文件](VibeCoding_Workflow_Templates/03_architecture_and_design_document.md)**
- **🔧 [API 設計規格](VibeCoding_Workflow_Templates/04_api_design_specification.md)**
- **📋 [模組規格與測試](VibeCoding_Workflow_Templates/05_module_specification_and_tests.md)**
- **🛡️ [安全與就緒檢查](VibeCoding_Workflow_Templates/06_security_and_readiness_checklists.md)**
- **📁 [專案結構指南](VibeCoding_Workflow_Templates/07_project_structure_guide.md)**

## ⚙️ **TaskMaster 專案結構**

```
📦 TaskMaster & Claude Code Collective
├── 📄 README.md                        # 🏠 本檔案 - 系統總覽
├── 📄 CLAUDE_TEMPLATE.md               # ⭐ 主初始化範本 (自動觸發 TaskMaster)
├── 📁 .claude/                         # 🤖 TaskMaster 核心系統
│   ├── 📄 taskmaster.js                # 🚀 TaskMaster 核心引擎
│   ├── 📄 GETTING_STARTED.md           # 📋 完整初學者指南
│   ├── 📄 TASKMASTER_README.md         # 🤖 系統技術文檔
│   ├── 📄 TROUBLESHOOTING.md           # 🆘 故障排除指南
│   ├── 📄 SUBAGENT_INTEGRATION_GUIDE.md # 🔗 智能體整合說明
│   ├── 📁 commands/                    # 🎛️ TaskMaster 指令系統
│   │   └── 📄 task-init.md             # 🎯 初始化指令文檔
│   └── 📁 taskmaster-data/             # 💾 專案資料存儲 (動態產生)
│       ├── 📄 project.json             # 專案配置
│       └── 📄 wbs-todos.json           # WBS Todo List
└── 📁 VibeCoding_Workflow_Templates/   # 🎨 企業級開發範本庫 (10個)
    ├── 📊 01_project_brief_and_prd.md
    ├── 🧪 02_behavior_driven_development_guide.md
    ├── 🏗️ 03_architecture_and_design_document.md
    ├── 🔧 04_api_design_specification.md
    ├── 📋 05_module_specification_and_tests.md
    ├── 🛡️ 06_security_and_readiness_checklists.md
    ├── 📁 07_project_structure_guide.md
    ├── 📝 08_code_review_and_refactoring_guide.md
    ├── 🚀 09_deployment_and_operations_guide.md
    └── 📚 10_documentation_and_maintenance_guide.md
```

## 🌟 **TaskMaster 核心優勢**

### ✅ **人類主導控制**
- **🤖⚔️ 鋼彈駕駛員理念** - 您始終是駕駛員，TaskMaster 是智能副駕駛
- **🛡️ 完全控制權** - 所有重要決策都由人類做出，AI 只提供建議
- **⏸️ 隨時暫停** - 任何時候都可以暫停系統，完全手動接管

### ✅ **智能協調系統**
- **🎯 Hub-and-Spoke 架構** - 智能分析任務特性，建議最適合的智能體
- **📋 WBS Todo List** - 統一管理所有任務狀態，全局透明掌控
- **🔄 持續同步** - 開發狀態即時更新，確保資訊一致性

### ✅ **企業級品質**
- **🎨 VibeCoding 範本整合** - 10個企業級開發流程範本，智能匹配需求
- **🤖 專業智能體協作** - 7個專業領域智能體，涵蓋開發生命週期
- **🔍 品質把關機制** - 內建 Linus 開發心法，技術債務預防

## 🚨 **重要注意事項**

### ⚠️ **初次使用必讀**
- [ ] **詳讀完整初學者指南**: 強烈建議閱讀 [.claude/GETTING_STARTED.md](.claude/GETTING_STARTED.md)
- [ ] **理解人類主導理念**: 您始終是駕駛員，TaskMaster 是副駕駛
- [ ] **熟悉核心命令**: 掌握 `/task-status`、`/task-next`、`/pause` 等基本命令

### ⚠️ **TaskMaster 使用原則**
- [ ] **保持控制權**: 重要決策都由您做出，不要過度依賴自動化
- [ ] **善用 WBS 系統**: 定期查看 `/task-status` 了解專案全貌
- [ ] **適時暫停**: 感到不確定時使用 `/pause` 暫停系統思考

### ⚠️ **Subagent 整合限制**
- [ ] **當前狀態**: Subagent 整合尚在開發中，部分功能使用模擬執行
- [ ] **參考文檔**: 詳細限制說明請查看 [SUBAGENT_INTEGRATION_GUIDE.md](.claude/SUBAGENT_INTEGRATION_GUIDE.md)
- [ ] **預期行為**: 系統會提示哪些功能正在模擬執行

## 📞 **支援與學習資源**

### 🆘 **遇到問題時**
- **🚀 新手問題**: 查看 [完整初學者指南](.claude/GETTING_STARTED.md)
- **🔧 技術問題**: 參考 [故障排除指南](.claude/TROUBLESHOOTING.md)
- **🤖 系統問題**: 檢查 [TaskMaster 技術文檔](.claude/TASKMASTER_README.md)

### 📚 **進階學習**
- **🎯 掌握所有命令**: 學會使用全部 8 個 TaskMaster 命令
- **🎨 客製化範本**: 根據團隊需求調整 VibeCoding 範本
- **🤖 智能體協作**: 深入了解 Hub-and-Spoke 協調機制

## 📚 文檔導航

### 🎯 核心文檔
- **[TaskMaster 系統說明](.claude/TASKMASTER_README.md)** - 完整技術文檔和文檔導向流程
- **[系統架構設計](.claude/ARCHITECTURE.md)** - 技術架構與設計分析
- **[初學者指南](.claude/GETTING_STARTED.md)** - 8 步驟完整設定教學
- **[Hooks 系統](.claude/hooks/README.md)** - 自動化 hooks 機制說明
- **[故障排除](.claude/TROUBLESHOOTING.md)** - 常見問題解決方案

### 🗂️ 專案組織
- **[專案結構](PROJECT_STRUCTURE.md)** - 完整目錄結構說明
- **[VibeCoding 範本](VibeCoding_Workflow_Templates/)** - 10 個企業級工作流程範本

## 📜 版本資訊

- **🚀 TaskMaster 版本**: v3.0
- **📅 更新日期**: 2025-09-25
- **🔗 相容性**: Claude Code v1.0+ (支援 Task tool 和專業智能體)
- **🏗️ 架構**: Human-Controlled TaskMaster + Hub-and-Spoke Coordination

---

## 🎉 **準備成為 TaskMaster 駕駛員！**

**🤖⚔️ 歡迎使用人類主導的智能開發協作系統！**

> 💡 **重要提醒**:
> - 您始終是駕駛員，TaskMaster 是您的智能副駕駛
> - 首次使用請務必閱讀 [完整初學者指南](.claude/GETTING_STARTED.md)
> - 隨時可以使用 `/pause` 暫停系統，完全手動接管
>
> **Ready to master your development workflow!** 🚀🤖⚔️
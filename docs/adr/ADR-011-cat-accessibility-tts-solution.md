# ADR-011: CAT 問卷無障礙 TTS 技術方案

**狀態**: ✅ 已批准 (Accepted)
**日期**: 2025-10-22
**決策者**: Frontend Lead, Accessibility Specialist, Technical Lead
**影響範圍**: LIFF 問卷頁 (Task 5.3, 5.6)、無障礙體驗、中老年用戶滿意度

---

## 📋 背景 (Context)

### 業務需求

RespiraAlly 的主要用戶是 **COPD 病患 (中老年人群)**，需提供無障礙的問卷填答體驗。

**用戶特徵**:
- 年齡: 55-80 歲
- 可能有視力退化 (老花眼、白內障)
- 可能有閱讀疲勞
- 需要清晰的視覺與聽覺輔助

**CAT 問卷**:
- 8 個問題，每題 6 個選項 (0-5 分)
- 繁體中文白話文描述
- 需要逐題填答

### 技術要求

1. **語音朗讀功能** (TTS - Text-to-Speech):
   - 自動朗讀問題 (進入頁面時)
   - 可重新朗讀 (按鈕觸發)
   - 繁體中文語音
   - 語速適合老年人 (稍慢)

2. **視覺無障礙**:
   - 高對比模式切換
   - 大字體 (20-28px)
   - 清晰的視覺層級

3. **觸控無障礙**:
   - 大按鈕 (易點擊)
   - 清晰的按壓反饋
   - 表情符號視覺提示

4. **ARIA 標籤支持**:
   - 螢幕閱讀器兼容

---

## 🎯 決策 (Decision)

### 採用 Web Speech API (瀏覽器原生)

**技術方案**: 使用瀏覽器原生的 `speechSynthesis` API，而非後端 TTS 服務。

**理由**:
- ✅ **零後端成本** - 無需 OpenAI TTS / Azure Speech / Google TTS
- ✅ **零額外依賴** - 瀏覽器原生支持
- ✅ **即時合成** - 無需音檔存儲與管理
- ✅ **跨平台支持** - iOS Safari, Android Chrome 都支持
- ✅ **離線可用** - 不依賴網路連線
- ✅ **工時節省** - 24h → 8h (減少 16h)

---

## 🔧 技術實作 (Technical Implementation)

### 1. useTTS React Hook

**檔案**: `frontend/liff/src/hooks/useTTS.ts`

```typescript
import { useState, useEffect } from 'react';

interface TTSOptions {
  lang?: string;
  rate?: number;
  pitch?: number;
  volume?: number;
}

export const useTTS = (options: TTSOptions = {}) => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [voices, setVoices] = useState<SpeechSynthesisVoice[]>([]);

  // 預設參數
  const defaultOptions: Required<TTSOptions> = {
    lang: options.lang || 'zh-TW',
    rate: options.rate || 0.9, // 稍慢，老年人友善
    pitch: options.pitch || 1.0,
    volume: options.volume || 1.0,
  };

  // 檢查瀏覽器支持
  useEffect(() => {
    if ('speechSynthesis' in window) {
      setIsSupported(true);
      loadVoices();

      // 監聽語音列表變化 (某些瀏覽器延遲載入)
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }
  }, []);

  // 載入可用語音
  const loadVoices = () => {
    const availableVoices = window.speechSynthesis.getVoices();
    setVoices(availableVoices);
  };

  // 朗讀文字
  const speak = (text: string) => {
    if (!isSupported) {
      console.warn('Web Speech API not supported in this browser');
      return;
    }

    // 停止任何正在進行的朗讀
    window.speechSynthesis.cancel();

    // 創建語音實例
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = defaultOptions.lang;
    utterance.rate = defaultOptions.rate;
    utterance.pitch = defaultOptions.pitch;
    utterance.volume = defaultOptions.volume;

    // 嘗試使用繁體中文語音
    const chineseVoice = voices.find(
      (voice) =>
        voice.lang.includes('zh-TW') ||
        voice.lang.includes('zh-CN') ||
        voice.lang.includes('cmn')
    );

    if (chineseVoice) {
      utterance.voice = chineseVoice;
    }

    // 狀態監聽
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = (event) => {
      console.error('Speech synthesis error:', event);
      setIsSpeaking(false);
    };

    // 開始朗讀
    window.speechSynthesis.speak(utterance);
  };

  // 停止朗讀
  const stop = () => {
    window.speechSynthesis.cancel();
    setIsSpeaking(false);
  };

  // 暫停朗讀
  const pause = () => {
    window.speechSynthesis.pause();
  };

  // 繼續朗讀
  const resume = () => {
    window.speechSynthesis.resume();
  };

  return {
    speak,
    stop,
    pause,
    resume,
    isSpeaking,
    isSupported,
    voices,
  };
};
```

### 2. CAT 問卷組件整合

**檔案**: `frontend/liff/src/pages/CATSurvey.tsx`

```typescript
import React, { useState, useEffect } from 'react';
import { useTTS } from '../hooks/useTTS';

// CAT 問題定義
const questions = [
  "請問您最近咳嗽的情形？",
  "您覺得肺裡面有痰卡住嗎？",
  "您有覺得胸口會悶、會緊嗎？",
  "您走樓梯或上坡會喘嗎？",
  "在家裡活動有沒有受到影響？",
  "您有信心自己出門走走嗎？",
  "最近睡眠情況怎麼樣？",
  "最近精神狀況如何？",
];

// 選項定義 (參考 cat_form.html)
const options = [
  [
    { score: 0, text: "✅ 完全沒咳嗽", description: "整天都沒有" },
    { score: 1, text: "😊 偶爾咳一下", description: "一天1~2次" },
    { score: 2, text: "😐 有時會咳", description: "不太影響" },
    { score: 3, text: "🙁 常常咳", description: "有點困擾" },
    { score: 4, text: "🤢 幾乎每天咳", description: "很不舒服" },
    { score: 5, text: "🥵 一直咳不停", description: "非常難受" },
  ],
  // ... 其他 7 題選項
];

export const CATSurvey: React.FC = () => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState<number[]>([]);
  const { speak, stop, isSpeaking, isSupported } = useTTS();

  // 自動朗讀問題 (進入新問題時)
  useEffect(() => {
    if (isSupported) {
      speak(questions[currentQuestion]);
    }
  }, [currentQuestion]);

  // 選擇答案
  const handleAnswer = (score: number) => {
    setAnswers([...answers, score]);

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // 完成問卷，提交答案
      submitSurvey();
    }
  };

  // 重新朗讀按鈕
  const handleReSpeak = () => {
    speak(questions[currentQuestion]);
  };

  return (
    <div className="cat-survey-container">
      <h2>{questions[currentQuestion]}</h2>

      {/* 朗讀控制按鈕 */}
      {isSupported && (
        <button
          onClick={handleReSpeak}
          disabled={isSpeaking}
          aria-label="重新朗讀問題"
          className="tts-button"
        >
          {isSpeaking ? '🔊 朗讀中...' : '🔊 朗讀題目'}
        </button>
      )}

      {/* 選項列表 */}
      <ul className="options-list" role="list">
        {options[currentQuestion].map((option, index) => (
          <li key={index} role="listitem">
            <button
              onClick={() => handleAnswer(option.score)}
              aria-label={`分數${option.score}：${option.text} ${option.description}`}
              className="option-button"
            >
              <div className="score-badge">{option.score}</div>
              <div className="option-content">
                <div className="option-text">{option.text}</div>
                <div className="option-description">{option.description}</div>
              </div>
            </button>
          </li>
        ))}
      </ul>

      {/* 進度提示 */}
      <p className="progress-text">
        題目 {currentQuestion + 1} / {questions.length}
      </p>
    </div>
  );
};
```

### 3. 樣式設計 (參考 cat_form.html)

**檔案**: `frontend/liff/src/pages/CATSurvey.module.css`

```css
/* 大字體 (老年人友善) */
.cat-survey-container {
  font-size: 20px;
  line-height: 1.5;
  padding: 20px;
}

.cat-survey-container h2 {
  font-size: 28px;
  font-weight: bold;
  color: #007bff;
  text-align: center;
  margin-bottom: 25px;
}

/* 朗讀按鈕 */
.tts-button {
  width: 100%;
  padding: 15px;
  font-size: 20px;
  background-color: #f0f7ff;
  border: 2px solid #007bff;
  border-radius: 10px;
  cursor: pointer;
  margin-bottom: 20px;
  transition: all 0.3s;
}

.tts-button:hover:not(:disabled) {
  background-color: #d4e6ff;
  transform: translateY(-2px);
}

.tts-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 選項按鈕 (大且易點擊) */
.option-button {
  width: 100%;
  padding: 20px 15px;
  font-size: 22px;
  border: none;
  border-radius: 10px;
  background-color: #f0f7ff;
  color: #333;
  text-align: left;
  cursor: pointer;
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
  transition: all 0.3s;
}

.option-button:hover {
  background-color: #d4e6ff;
  transform: translateY(-2px);
}

/* 分數徽章 */
.score-badge {
  font-size: 32px;
  font-weight: bold;
  color: #007bff;
  background-color: #e8f4f8;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 15px;
  flex-shrink: 0;
}

.option-content {
  flex: 1;
}

.option-text {
  font-size: 22px;
  font-weight: 600;
  margin-bottom: 5px;
}

.option-description {
  font-size: 18px;
  color: #666;
}

/* 進度提示 */
.progress-text {
  text-align: center;
  font-size: 18px;
  color: #666;
  margin-top: 20px;
}

/* 高對比模式 (可選) */
body.high-contrast .cat-survey-container {
  background-color: #000;
  color: #fff;
}

body.high-contrast .cat-survey-container h2 {
  color: #ffff00;
}

body.high-contrast .option-button {
  background-color: #000;
  color: #fff;
  border: 2px solid #fff;
}

body.high-contrast .score-badge {
  background-color: #333;
  color: #ffff00;
}
```

---

## 📊 技術規格 (Technical Specifications)

### 瀏覽器支持

| 瀏覽器 | 版本 | 支持程度 | 備註 |
|--------|------|----------|------|
| **iOS Safari** | 14.5+ | ✅ 完全支持 | LINE 內建瀏覽器基於 Safari |
| **Android Chrome** | 90+ | ✅ 完全支持 | 預設行動瀏覽器 |
| **Desktop Chrome** | 90+ | ✅ 完全支持 | 開發測試用 |
| **Desktop Edge** | 90+ | ✅ 完全支持 | 開發測試用 |
| **Desktop Firefox** | 92+ | ⚠️ 部分支持 | 語音選擇有限 |

### 語音參數

```typescript
interface TTSConfig {
  lang: 'zh-TW';          // 繁體中文
  rate: 0.9;               // 語速 (0.8-1.2, 預設 0.9)
  pitch: 1.0;              // 音調 (0.8-1.2, 預設 1.0)
  volume: 1.0;             // 音量 (0.0-1.0, 預設 1.0)
}
```

### 功能範圍

**✅ 包含**:
- 基本朗讀 (播放/停止)
- 繁體中文語音
- 語速調整 (0.9x, 老年人友善)
- 自動朗讀問題 (進入時)
- 重新朗讀按鈕
- 朗讀狀態指示 (按鈕文字變化)

**❌ 不包含** (簡化範圍):
- 語音選擇 (使用系統預設)
- 音檔存儲 (即時合成)
- 複雜播放控制 (進度條、拖曳)
- 後端 TTS API 整合

---

## 🧪 測試策略 (Testing Strategy)

### 1. 功能測試

**手動測試清單**:
- [ ] 進入頁面時自動朗讀問題
- [ ] 點擊"朗讀題目"按鈕重新朗讀
- [ ] 朗讀中按鈕顯示"朗讀中..."
- [ ] 朗讀完成後按鈕恢復"🔊 朗讀題目"
- [ ] 切換題目時自動朗讀新問題
- [ ] 中文語音清晰可理解
- [ ] 語速適合老年人 (不會太快)

### 2. 跨瀏覽器測試

**測試設備**:
- iPhone (iOS Safari) - LINE app 內
- Android (Chrome) - LINE app 內
- Desktop Chrome (開發測試)

**測試項目**:
- [ ] iOS Safari 語音正常
- [ ] Android Chrome 語音正常
- [ ] 不同設備音質差異可接受
- [ ] 網路斷線時仍可朗讀 (離線功能)

### 3. 無障礙測試

**WCAG 2.1 AA 標準**:
- [ ] ARIA 標籤正確 (`aria-label`, `role`)
- [ ] 鍵盤可操作 (Tab + Enter)
- [ ] 螢幕閱讀器兼容 (VoiceOver / TalkBack)
- [ ] 高對比模式正常 (可選功能)

### 4. 用戶測試

**目標用戶**: 55-80 歲 COPD 病患 (3-5 人)

**測試腳本**:
1. 進入 CAT 問卷頁
2. 聆聽自動朗讀
3. 點擊"朗讀題目"重新聆聽
4. 選擇答案，進入下一題
5. 完成 8 題問卷

**收集反饋**:
- 語音清晰度 (1-5 分)
- 語速適當性 (太快/適中/太慢)
- 按鈕大小與位置 (易用性)
- 整體滿意度 (1-5 分)

---

## ⚠️ 已知限制 (Known Limitations)

### 1. 語音品質

**限制**: 不同設備音質不同 (系統決定)

**影響**:
- iOS 使用 Siri 語音 (品質較好)
- Android 使用 Google TTS (品質中等)
- 部分老舊設備音質較差

**緩解措施**:
- 在測試階段評估可接受性
- 如用戶反饋音質差，考慮未來升級為後端 TTS

### 2. 用戶手勢要求

**限制**: iOS Safari 需用戶手勢觸發語音

**影響**:
- 自動朗讀可能在某些情況下失效
- 必須通過按鈕觸發

**緩解措施**:
- 提供明顯的"朗讀題目"按鈕
- 在 UI 提示用戶點擊朗讀

### 3. 語音選擇限制

**限制**: 無法選擇特定語音 (使用系統預設)

**影響**:
- 用戶無法切換男聲/女聲
- 無法調整音色

**緩解措施**:
- 接受此限制 (MVP 範圍內)
- 如用戶強烈要求，Sprint 6+ 考慮升級

### 4. 離線功能

**優點**: 不依賴網路，離線可用 ✅

**限制**: 首次載入需下載語音引擎 (瀏覽器自動)

---

## 🔄 未來優化方向 (Future Enhancements)

### Phase 1 (MVP - Sprint 3) ✅ 當前方案
- Web Speech API 基本朗讀
- 繁體中文語音
- 語速調整 (0.9x)

### Phase 2 (Post-MVP - Sprint 6+, 如需要)
- 語音選擇 (男聲/女聲)
- 音色調整
- 語速自訂 (0.5x - 1.5x)

### Phase 3 (未來, 如用戶反饋需要)
- 後端 TTS API (OpenAI TTS / Azure Speech)
- 高品質語音 (Neural Voice)
- 音檔快取 (減少延遲)
- 多語言支持 (台語、客語)

---

## 📚 參考資料 (References)

### 實作參考
- `docs/frontend/cat_form.html` - 無障礙設計與 TTS 實作參考
- [Web Speech API - MDN](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [SpeechSynthesis Interface](https://developer.mozilla.org/en-US/docs/Web/API/SpeechSynthesis)

### 無障礙標準
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [iOS Accessibility](https://developer.apple.com/accessibility/)
- [Android Accessibility](https://developer.android.com/guide/topics/ui/accessibility)

### 相關 ADR
- ADR-010: Sprint 3 MVP 範圍縮減決策
- ADR-XXX: LIFF 問卷頁架構設計 (待創建)

---

## 💬 備註 (Notes)

### 為什麼選擇 Web Speech API？

**Linus 的原則**: "Simple is better than complex"

1. **實用主義**: 解決 80% 的需求，用 20% 的成本
2. **零依賴**: 不增加系統複雜度
3. **快速交付**: 8h vs 24h，節省 16h
4. **用戶驗證**: MVP 先驗證需求，再決定是否升級

### 何時考慮升級為後端 TTS？

**升級條件**:
- ✅ 用戶反饋音質差 (>20% 用戶抱怨)
- ✅ 需要多語言支持 (台語、客語)
- ✅ 需要高品質 Neural Voice
- ✅ 用戶願意接受網路依賴

**不升級的情況**:
- ❌ 用戶滿意度 >80%
- ❌ Web Speech API 音質可接受
- ❌ 無特殊語音需求

---

**批准**: Frontend Lead, Accessibility Specialist
**生效日期**: 2025-10-22
**下次審查**: Sprint 3 結束 (2025-11-05)

---

**維護者**: RespiraAlly Frontend Team
**最後更新**: 2025-10-22

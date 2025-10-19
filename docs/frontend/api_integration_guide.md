# RespiraAlly - 前端視覺化 API 查詢範例

**文件版本**: v1.1
**最後更新**: 2025-10-18 (修訂版)
**目的**: 提供前端團隊快速整合 KPI 與趨勢圖表的 SQL 查詢範例

---

## 目錄

1. [病患基本資料查詢](#1-病患基本資料查詢)
2. [Dashboard 總覽頁](#2-dashboard-總覽頁)
3. [健康趨勢圖表](#3-健康趨勢圖表)
4. [問卷歷史分析](#4-問卷歷史分析)
5. [對比分析](#5-對比分析)
6. [API Endpoint 設計範例](#6-api-endpoint-設計範例)

---

## 1. 病患基本資料查詢

### 場景: 獲取病患完整檔案（含健康指標）

#### API Endpoint: `GET /api/patients/{patient_id}/profile`

#### SQL 查詢

```sql
-- 查詢 0: 病患基本資料 + 健康指標（使用 patient_health_summary 視圖）
SELECT
    p.user_id AS patient_id,
    p.name,
    p.birth_date,
    p.gender,

    -- 醫院整合資訊
    p.hospital_medical_record_number,

    -- 體徵數據
    p.height_cm,
    p.weight_kg,

    -- 吸菸史
    p.smoking_status,
    p.smoking_years,

    -- 計算欄位（從視圖）
    h.age,
    h.bmi,
    h.bmi_category,

    -- 治療師資訊
    t.name AS therapist_name,
    t.institution AS therapist_institution,

    -- 聯絡資訊與病史
    p.contact_info,
    p.medical_history
FROM patient_profiles p
LEFT JOIN patient_health_summary h ON p.user_id = h.user_id
LEFT JOIN therapist_profiles t ON p.therapist_id = t.user_id
WHERE p.user_id = :patient_id;
```

#### API 回應範例 (JSON)

```json
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "basic_info": {
    "name": "王小明",
    "birth_date": "1955-03-15",
    "age": 70,
    "gender": "MALE"
  },
  "medical_record": {
    "hospital_mrn": "H12345678",
    "copd_stage": "III",
    "comorbidities": ["高血壓", "糖尿病"],
    "medications": ["Spiriva", "Ventolin"]
  },
  "health_metrics": {
    "height_cm": 168,
    "weight_kg": 72.5,
    "bmi": 25.7,
    "bmi_category": "OVERWEIGHT",
    "smoking_status": "FORMER",
    "smoking_years": 30
  },
  "therapist": {
    "name": "李治療師",
    "institution": "台北榮總"
  },
  "contact_info": {
    "phone": "0912-345-678",
    "address": "台北市信義區...",
    "emergency_contact": {
      "name": "王太太",
      "phone": "0922-111-222"
    }
  }
}
```

#### 前端使用範例 (React)

```tsx
// components/PatientProfile.tsx
import { useQuery } from '@tanstack/react-query';

export function PatientProfile({ patientId }: { patientId: string }) {
  const { data: profile, isLoading } = useQuery({
    queryKey: ['patient-profile', patientId],
    queryFn: () => fetch(`/api/patients/${patientId}/profile`).then(r => r.json()),
  });

  if (isLoading) return <Skeleton />;

  return (
    <div className="space-y-6">
      {/* 基本資料 */}
      <section className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">基本資料</h2>
        <dl className="grid grid-cols-2 gap-4">
          <div>
            <dt className="text-sm text-gray-500">姓名</dt>
            <dd className="font-medium">{profile.basic_info.name}</dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500">年齡</dt>
            <dd className="font-medium">{profile.basic_info.age} 歲</dd>
          </div>
          <div>
            <dt className="text-sm text-gray-500">病歷號</dt>
            <dd className="font-medium font-mono">{profile.medical_record.hospital_mrn}</dd>
          </div>
        </dl>
      </section>

      {/* 健康指標 */}
      <section className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">健康指標</h2>
        <div className="grid grid-cols-3 gap-4">
          <HealthMetric
            label="身高"
            value={profile.health_metrics.height_cm}
            unit="cm"
          />
          <HealthMetric
            label="體重"
            value={profile.health_metrics.weight_kg}
            unit="kg"
          />
          <HealthMetric
            label="BMI"
            value={profile.health_metrics.bmi}
            category={profile.health_metrics.bmi_category}
          />
        </div>

        {/* 吸菸史標記 */}
        {profile.health_metrics.smoking_status !== 'NEVER' && (
          <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-sm text-yellow-800">
              ⚠️ {profile.health_metrics.smoking_status === 'CURRENT' ? '目前吸菸' : '曾吸菸'}
              （{profile.health_metrics.smoking_years} 年）
            </p>
          </div>
        )}
      </section>

      {/* 負責治療師 */}
      <section className="bg-white p-6 rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">負責治療師</h2>
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
            <span className="text-xl">👨‍⚕️</span>
          </div>
          <div>
            <p className="font-medium">{profile.therapist.name}</p>
            <p className="text-sm text-gray-500">{profile.therapist.institution}</p>
          </div>
        </div>
      </section>
    </div>
  );
}

function HealthMetric({ label, value, unit, category }: {
  label: string;
  value: number;
  unit?: string;
  category?: string;
}) {
  const categoryColors = {
    UNDERWEIGHT: 'text-blue-600',
    NORMAL: 'text-green-600',
    OVERWEIGHT: 'text-yellow-600',
    OBESE: 'text-red-600',
  };

  return (
    <div className="text-center">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold">
        {value}
        {unit && <span className="text-sm text-gray-400 ml-1">{unit}</span>}
      </p>
      {category && (
        <p className={`text-xs mt-1 ${categoryColors[category] || 'text-gray-500'}`}>
          {category}
        </p>
      )}
    </div>
  );
}
```

---

## 2. Dashboard 總覽頁

### 場景: 病患打開 LIFF，查看個人健康總覽

#### API Endpoint: `GET /api/patients/{patient_id}/dashboard`

#### SQL 查詢 (FastAPI Repository)

```sql
-- 查詢 1: 病患基本 KPI（從快取表讀取，極快 < 10ms）
SELECT
    total_logs_count,
    first_log_date,
    last_log_date,
    adherence_rate_7d,
    adherence_rate_30d,
    avg_water_intake_7d,
    avg_water_intake_30d,
    avg_steps_7d,
    avg_steps_30d,
    current_streak_days,
    longest_streak_days,
    latest_cat_score,
    latest_cat_date,
    latest_mmrc_score,
    latest_mmrc_date,
    latest_risk_score,
    latest_risk_level,
    latest_risk_date,
    symptom_occurrences_30d,
    last_calculated_at
FROM patient_kpi_cache
WHERE patient_id = :patient_id;
```

#### API 回應範例 (JSON)

```json
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "summary": {
    "total_logs": 156,
    "first_log_date": "2024-05-01",
    "last_log_date": "2025-10-17",
    "current_streak_days": 12,
    "longest_streak_days": 28
  },
  "adherence": {
    "rate_7d": 85,
    "rate_30d": 78
  },
  "health_metrics": {
    "water_intake_7d_avg": 1850,
    "water_intake_30d_avg": 1720,
    "steps_7d_avg": 5200,
    "steps_30d_avg": 4800
  },
  "latest_surveys": {
    "cat": {
      "score": 18,
      "date": "2025-10-10",
      "severity": "MODERATE"
    },
    "mmrc": {
      "score": 2,
      "date": "2025-10-05"
    }
  },
  "risk_assessment": {
    "score": 65,
    "level": "MEDIUM",
    "date": "2025-10-17"
  },
  "symptom_occurrences_30d": 8,
  "last_updated": "2025-10-17T14:30:00Z"
}
```

#### 前端使用範例 (React)

```tsx
// components/PatientDashboard.tsx
import { useQuery } from '@tanstack/react-query';

interface DashboardData {
  summary: {
    total_logs: number;
    current_streak_days: number;
  };
  adherence: {
    rate_7d: number;
    rate_30d: number;
  };
  // ... 其他欄位
}

export function PatientDashboard({ patientId }: { patientId: string }) {
  const { data, isLoading } = useQuery<DashboardData>({
    queryKey: ['dashboard', patientId],
    queryFn: () => fetch(`/api/patients/${patientId}/dashboard`).then(r => r.json()),
  });

  if (isLoading) return <Skeleton />;

  return (
    <div className="grid grid-cols-2 gap-4">
      <StatCard
        title="連續打卡"
        value={data.summary.current_streak_days}
        unit="天"
        icon="🔥"
      />
      <StatCard
        title="近7天依從率"
        value={data.adherence.rate_7d}
        unit="%"
        icon="💊"
        color={data.adherence.rate_7d >= 75 ? 'green' : 'yellow'}
      />
      {/* 更多統計卡片... */}
    </div>
  );
}
```

---

## 3. 健康趨勢圖表

### 場景 1: 近 30 天依從率折線圖

#### API Endpoint: `GET /api/patients/{patient_id}/trends/adherence?days=30`

#### SQL 查詢

```sql
-- 查詢 2: 每日依從率時間序列（使用視圖）
SELECT
    log_date,
    medication_taken,
    -- 計算滾動 7 天依從率（移動平均）
    CASE
        WHEN COUNT(*) OVER (
            PARTITION BY patient_id
            ORDER BY log_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) >= 7
        THEN ROUND(
            (COUNT(*) FILTER (WHERE medication_taken) OVER (
                PARTITION BY patient_id
                ORDER BY log_date
                ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
            )::NUMERIC / 7) * 100
        )
        ELSE NULL
    END AS adherence_rate_7d_rolling
FROM patient_health_timeline
WHERE patient_id = :patient_id
  AND log_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY log_date ASC;
```

#### API 回應範例

```json
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "period": {
    "start": "2025-09-17",
    "end": "2025-10-17",
    "days": 30
  },
  "data": [
    { "date": "2025-09-17", "medication_taken": true, "rolling_adherence": null },
    { "date": "2025-09-18", "medication_taken": false, "rolling_adherence": null },
    // ... 前 6 天 rolling_adherence 為 null
    { "date": "2025-09-24", "medication_taken": true, "rolling_adherence": 71 },
    { "date": "2025-09-25", "medication_taken": true, "rolling_adherence": 86 },
    // ... 更多數據點
    { "date": "2025-10-17", "medication_taken": true, "rolling_adherence": 85 }
  ]
}
```

#### 前端圖表範例 (Recharts)

```tsx
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export function AdherenceTrendChart({ patientId }: { patientId: string }) {
  const { data } = useQuery({
    queryKey: ['adherence-trend', patientId, 30],
    queryFn: () => fetch(`/api/patients/${patientId}/trends/adherence?days=30`).then(r => r.json()),
  });

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data?.data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString('zh-TW', { month: 'short', day: 'numeric' })} />
        <YAxis domain={[0, 100]} label={{ value: '依從率 (%)', angle: -90, position: 'insideLeft' }} />
        <Tooltip />
        <Line
          type="monotone"
          dataKey="rolling_adherence"
          stroke="#10b981"
          strokeWidth={2}
          dot={{ r: 3 }}
          connectNulls
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
```

---

### 場景 2: 近 30 天飲水量柱狀圖

#### API Endpoint: `GET /api/patients/{patient_id}/trends/water-intake?days=30`

#### SQL 查詢

```sql
-- 查詢 3: 每日飲水量時間序列（含移動平均線）
SELECT
    log_date,
    water_intake_ml,
    water_intake_7d_ma  -- 7 天移動平均（已在視圖中計算）
FROM patient_health_timeline
WHERE patient_id = :patient_id
  AND log_date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY log_date ASC;
```

#### 前端圖表範例 (組合圖: 柱狀 + 折線)

```tsx
import { ComposedChart, Bar, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';

export function WaterIntakeTrendChart({ patientId }: { patientId: string }) {
  const { data } = useQuery({
    queryKey: ['water-trend', patientId, 30],
    queryFn: () => fetch(`/api/patients/${patientId}/trends/water-intake?days=30`).then(r => r.json()),
  });

  return (
    <ComposedChart width={800} height={300} data={data?.data}>
      <CartesianGrid strokeDasharray="3 3" />
      <XAxis dataKey="date" />
      <YAxis label={{ value: '飲水量 (ml)', angle: -90, position: 'insideLeft' }} />
      <Tooltip />
      <Legend />
      <Bar dataKey="water_intake_ml" fill="#3b82f6" name="每日飲水量" />
      <Line type="monotone" dataKey="water_intake_7d_ma" stroke="#ef4444" name="7天平均" strokeWidth={2} dot={false} />
    </ComposedChart>
  );
}
```

---

## 4. 問卷歷史分析

### 場景: CAT 分數變化趨勢（近 6 次問卷）

#### API Endpoint: `GET /api/patients/{patient_id}/surveys/cat/trends?limit=6`

#### SQL 查詢

```sql
-- 查詢 4: CAT 問卷歷史趨勢（使用視圖）
SELECT
    survey_date,
    total_score,
    severity_level,
    score_change,  -- 與上次問卷的差異
    score_change_from_baseline,  -- 與首次問卷的差異
    survey_sequence  -- 第幾次問卷
FROM patient_survey_trends
WHERE patient_id = :patient_id
  AND survey_type = 'CAT'
ORDER BY submitted_at DESC
LIMIT :limit;
```

#### API 回應範例

```json
{
  "patient_id": "550e8400-e29b-41d4-a716-446655440000",
  "survey_type": "CAT",
  "history": [
    {
      "date": "2025-10-10",
      "score": 18,
      "severity": "MODERATE",
      "change_from_previous": -3,
      "change_from_baseline": -10,
      "sequence": 6
    },
    {
      "date": "2025-09-10",
      "score": 21,
      "severity": "MODERATE",
      "change_from_previous": -2,
      "change_from_baseline": -7,
      "sequence": 5
    },
    // ... 更早的問卷記錄
    {
      "date": "2025-05-10",
      "score": 28,
      "severity": "SEVERE",
      "change_from_previous": null,
      "change_from_baseline": 0,
      "sequence": 1
    }
  ]
}
```

#### 前端圖表範例 (折線圖 + 趨勢標記)

```tsx
export function CATTrendChart({ patientId }: { patientId: string }) {
  const { data } = useQuery({
    queryKey: ['cat-trends', patientId],
    queryFn: () => fetch(`/api/patients/${patientId}/surveys/cat/trends?limit=6`).then(r => r.json()),
  });

  // 反轉數據順序（從舊到新）
  const chartData = data?.history.slice().reverse();

  return (
    <div>
      <LineChart width={600} height={300} data={chartData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tickFormatter={(date) => new Date(date).toLocaleDateString('zh-TW', { month: 'short' })} />
        <YAxis domain={[0, 40]} label={{ value: 'CAT 分數', angle: -90, position: 'insideLeft' }} />
        <Tooltip
          content={({ active, payload }) => {
            if (active && payload && payload.length) {
              const data = payload[0].payload;
              return (
                <div className="bg-white p-2 border rounded shadow">
                  <p className="font-bold">第 {data.sequence} 次問卷</p>
                  <p>分數: {data.score}</p>
                  <p>嚴重度: {data.severity}</p>
                  {data.change_from_previous !== null && (
                    <p className={data.change_from_previous < 0 ? 'text-green-600' : 'text-red-600'}>
                      vs 上次: {data.change_from_previous > 0 ? '+' : ''}{data.change_from_previous}
                    </p>
                  )}
                </div>
              );
            }
            return null;
          }}
        />
        <Line type="monotone" dataKey="score" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 5 }} />
        {/* 參考線：分數越低越好 */}
        <ReferenceLine y={10} stroke="#10b981" strokeDasharray="3 3" label="輕度門檻" />
        <ReferenceLine y={20} stroke="#f59e0b" strokeDasharray="3 3" label="中度門檻" />
        <ReferenceLine y={30} stroke="#ef4444" strokeDasharray="3 3" label="嚴重門檻" />
      </LineChart>

      {/* 進步標記 */}
      {data?.history[0]?.change_from_baseline < 0 && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded">
          <p className="text-green-800">
            🎉 相較首次評估，您的 CAT 分數已改善 {Math.abs(data.history[0].change_from_baseline)} 分！
          </p>
        </div>
      )}
    </div>
  );
}
```

---

## 5. 對比分析

### 場景: 本週 vs 上週 KPI 對比

#### API Endpoint: `GET /api/patients/{patient_id}/comparison/weekly`

#### SQL 查詢

```sql
-- 查詢 5: 本週與上週 KPI 對比
WITH weekly_kpi AS (
    SELECT
        patient_id,
        -- 本週 (近 7 天)
        COUNT(*) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '7 days') AS this_week_logs,
        ROUND(AVG(water_intake_ml) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '7 days')) AS this_week_water_avg,
        ROUND(
            (COUNT(*) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '7 days' AND medication_taken)::NUMERIC /
             NULLIF(COUNT(*) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '7 days'), 0)) * 100
        ) AS this_week_adherence,

        -- 上週 (8-14 天前)
        COUNT(*) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '14 days' AND log_date < CURRENT_DATE - INTERVAL '7 days') AS last_week_logs,
        ROUND(AVG(water_intake_ml) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '14 days' AND log_date < CURRENT_DATE - INTERVAL '7 days')) AS last_week_water_avg,
        ROUND(
            (COUNT(*) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '14 days' AND log_date < CURRENT_DATE - INTERVAL '7 days' AND medication_taken)::NUMERIC /
             NULLIF(COUNT(*) FILTER (WHERE log_date >= CURRENT_DATE - INTERVAL '14 days' AND log_date < CURRENT_DATE - INTERVAL '7 days'), 0)) * 100
        ) AS last_week_adherence
    FROM daily_logs
    WHERE patient_id = :patient_id
    GROUP BY patient_id
)
SELECT
    patient_id,
    this_week_logs,
    last_week_logs,
    this_week_water_avg,
    last_week_water_avg,
    this_week_water_avg - last_week_water_avg AS water_change,
    this_week_adherence,
    last_week_adherence,
    this_week_adherence - last_week_adherence AS adherence_change
FROM weekly_kpi;
```

#### 前端對比卡片範例

```tsx
export function WeeklyComparisonCard({ patientId }: { patientId: string }) {
  const { data } = useQuery({
    queryKey: ['weekly-comparison', patientId],
    queryFn: () => fetch(`/api/patients/${patientId}/comparison/weekly`).then(r => r.json()),
  });

  return (
    <div className="grid grid-cols-3 gap-4">
      <ComparisonMetric
        title="打卡次數"
        thisWeek={data.this_week_logs}
        lastWeek={data.last_week_logs}
      />
      <ComparisonMetric
        title="依從率"
        thisWeek={data.this_week_adherence}
        lastWeek={data.last_week_adherence}
        unit="%"
        reverseColor  // 越高越好
      />
      <ComparisonMetric
        title="平均飲水量"
        thisWeek={data.this_week_water_avg}
        lastWeek={data.last_week_water_avg}
        unit="ml"
        reverseColor
      />
    </div>
  );
}

function ComparisonMetric({ title, thisWeek, lastWeek, unit = '', reverseColor = false }) {
  const change = thisWeek - lastWeek;
  const changePercent = lastWeek > 0 ? ((change / lastWeek) * 100).toFixed(1) : '0';
  const isPositive = reverseColor ? change > 0 : change < 0;

  return (
    <div className="p-4 bg-white rounded-lg shadow">
      <h3 className="text-sm text-gray-500">{title}</h3>
      <div className="mt-2 flex items-baseline justify-between">
        <span className="text-2xl font-bold">{thisWeek}{unit}</span>
        <span className={`text-sm ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
          {change > 0 ? '+' : ''}{change}{unit}
        </span>
      </div>
      <p className="mt-1 text-xs text-gray-400">vs 上週: {lastWeek}{unit}</p>
    </div>
  );
}
```

---

## 6. API Endpoint 設計範例

### FastAPI Backend 實作參考

```python
# backend/src/respira_ally/presentation/routers/patients.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from respira_ally.infrastructure.database import get_db
from respira_ally.application.schemas.patient import PatientDashboardResponse
from respira_ally.infrastructure.repositories.patient_kpi_repository import PatientKPIRepository

router = APIRouter(prefix="/api/patients", tags=["患者 KPI"])


@router.get("/{patient_id}/dashboard", response_model=PatientDashboardResponse)
async def get_patient_dashboard(
    patient_id: str,
    db: Session = Depends(get_db)
):
    """
    獲取病患 Dashboard 總覽數據（從 patient_kpi_cache 快取表讀取）

    - **極快查詢**: 單表查詢，無 JOIN，響應時間 < 50ms
    - **自動更新**: 透過觸發器自動維護快取
    """
    repo = PatientKPIRepository(db)
    kpi_data = repo.get_kpi_cache(patient_id)

    if not kpi_data:
        raise HTTPException(status_code=404, detail="Patient not found")

    return PatientDashboardResponse(
        patient_id=patient_id,
        summary={
            "total_logs": kpi_data.total_logs_count,
            "first_log_date": kpi_data.first_log_date,
            "last_log_date": kpi_data.last_log_date,
            "current_streak_days": kpi_data.current_streak_days,
            "longest_streak_days": kpi_data.longest_streak_days,
        },
        adherence={
            "rate_7d": kpi_data.adherence_rate_7d,
            "rate_30d": kpi_data.adherence_rate_30d,
        },
        health_metrics={
            "water_intake_7d_avg": kpi_data.avg_water_intake_7d,
            "water_intake_30d_avg": kpi_data.avg_water_intake_30d,
            "steps_7d_avg": kpi_data.avg_steps_7d,
            "steps_30d_avg": kpi_data.avg_steps_30d,
        },
        latest_surveys={
            "cat": {
                "score": kpi_data.latest_cat_score,
                "date": kpi_data.latest_cat_date,
            } if kpi_data.latest_cat_score else None,
            "mmrc": {
                "score": kpi_data.latest_mmrc_score,
                "date": kpi_data.latest_mmrc_date,
            } if kpi_data.latest_mmrc_score else None,
        },
        risk_assessment={
            "score": kpi_data.latest_risk_score,
            "level": kpi_data.latest_risk_level,
            "date": kpi_data.latest_risk_date,
        } if kpi_data.latest_risk_score else None,
        symptom_occurrences_30d=kpi_data.symptom_occurrences_30d,
        last_updated=kpi_data.last_calculated_at,
    )


@router.get("/{patient_id}/trends/adherence")
async def get_adherence_trend(
    patient_id: str,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    獲取依從率趨勢數據（從 patient_health_timeline 視圖查詢）

    - **支持時間窗口**: days 參數控制查詢範圍（7/30/90 天）
    - **包含移動平均**: 7 天滾動依從率
    """
    repo = PatientKPIRepository(db)
    timeline_data = repo.get_health_timeline(patient_id, days)

    return {
        "patient_id": patient_id,
        "period": {"start": ..., "end": ..., "days": days},
        "data": [
            {
                "date": row.log_date,
                "medication_taken": row.medication_taken,
                "rolling_adherence": ...,  # 計算邏輯
            }
            for row in timeline_data
        ]
    }
```

---

## 總結：數據層設計哲學

### ✅ 好設計的標準 (Linus 原則)

1. **消除特殊情況**
   - 統一的時間窗口查詢（7d/30d/90d）
   - 統一的視圖接口，前端無需關心底層複雜性

2. **好的數據結構**
   - 快取表（patient_kpi_cache）: 快速讀取統計
   - 視圖（patient_kpi_windows）: 靈活計算趨勢
   - 觸發器: 自動維護，減少應用層複雜度

3. **實用主義**
   - Dashboard API < 50ms（單表查詢）
   - 趨勢 API < 200ms（視圖查詢，有索引支持）
   - 自動刷新機制（觸發器 + 定時任務）

4. **簡潔性**
   - 前端只需 3 種查詢模式：
     1. 快速總覽（快取表）
     2. 時間序列（時間線視圖）
     3. 問卷趨勢（問卷視圖）

---

**下一步**:

1. 執行 Migration 腳本創建表與視圖
   ```bash
   # Migration 002: 新增病患健康欄位
   psql -U postgres -d respira_ally -f backend/alembic/versions/002_add_patient_health_fields.sql

   # Migration 003: 擴展 KPI 快取與視圖
   psql -U postgres -d respira_ally -f backend/alembic/versions/003_enhance_kpi_cache_and_views.sql
   ```

2. 初始化數據
   ```sql
   -- 刷新所有病患的 KPI 快取
   SELECT refresh_patient_kpi_cache();
   ```

3. 實作 FastAPI Repository 與 Router
   - PatientKPIRepository: 處理 KPI 快取查詢
   - PatientProfileRepository: 處理病患資料查詢
   - 實作 6 個主要 API Endpoint (參考本文件範例)

4. 前端整合 React Query + Recharts
   - 使用 TanStack Query (React Query) 管理數據獲取
   - 使用 Recharts 實作圖表視覺化
   - 實作響應式設計與骨架屏 (Skeleton)

5. 設置 pg_cron 定期刷新 KPI 快取
   ```sql
   CREATE EXTENSION IF NOT EXISTS pg_cron;

   SELECT cron.schedule(
     'refresh-patient-kpi',
     '0 * * * *',  -- 每小時執行一次
     $$SELECT refresh_patient_kpi_cache();$$
   );
   ```

---

## 附錄: 完整 API Endpoint 清單

| Endpoint | 方法 | 用途 | 數據來源 | 預期響應時間 |
|----------|------|------|---------|------------|
| `/api/patients/{id}/profile` | GET | 病患基本資料與健康指標 | patient_profiles + patient_health_summary | < 50ms |
| `/api/patients/{id}/dashboard` | GET | Dashboard 總覽 KPI | patient_kpi_cache | < 50ms |
| `/api/patients/{id}/trends/adherence` | GET | 依從率趨勢 | patient_health_timeline | < 200ms |
| `/api/patients/{id}/trends/water-intake` | GET | 飲水量趨勢 | patient_health_timeline | < 200ms |
| `/api/patients/{id}/surveys/cat/trends` | GET | CAT 問卷歷史 | patient_survey_trends | < 100ms |
| `/api/patients/{id}/comparison/weekly` | GET | 週度 KPI 對比 | daily_logs (CTE) | < 150ms |

---

**相關文件**:
- [DATABASE_SCHEMA_DESIGN.md](../database/schema_design_v1.0.md) - 資料庫完整設計文件
- [06_api_design_specification.md](./06_api_design_specification.md) - API 規範文件
- [Migration 002](../backend/alembic/versions/002_add_patient_health_fields.sql) - 病患健康欄位 Migration
- [Migration 003](../backend/alembic/versions/003_enhance_kpi_cache_and_views.sql) - KPI 快取與視圖 Migration

---

**版本記錄**:
- v1.1 (2025-10-18): 新增病患基本資料查詢章節,包含健康指標 (BMI、吸菸史)
- v1.0 (2025-10-18): 初始版本,包含 Dashboard、趨勢圖表、問卷分析、對比分析

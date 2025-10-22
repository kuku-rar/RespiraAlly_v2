/**
 * Daily Log Type Definitions
 * TypeScript interfaces matching backend Pydantic schemas
 */

/**
 * Daily Log mood enum
 */
export type DailyLogMood = "GOOD" | "NEUTRAL" | "BAD";

/**
 * Daily Log Response
 * Matches backend DailyLogResponse schema
 */
export interface DailyLog {
  log_id: string;
  patient_id: string;
  log_date: string; // ISO date format (YYYY-MM-DD)
  medication_taken: boolean | null;
  water_intake_ml: number | null;
  exercise_minutes: number | null;
  smoking_count: number | null;
  symptoms: string | null;
  mood: DailyLogMood | null;
  created_at: string; // ISO datetime
  updated_at: string; // ISO datetime
}

/**
 * Daily Log List Response (with pagination)
 * Matches backend DailyLogListResponse schema
 */
export interface DailyLogListResponse {
  items: DailyLog[];
  total: number;
  page: number; // 0-indexed
  page_size: number;
  has_next: boolean;
}

/**
 * Daily Log Statistics
 * Matches backend DailyLogStats schema
 */
export interface DailyLogStats {
  total_logs: number;
  medication_adherence_rate: number; // 0-100
  avg_water_intake_ml: number | null;
  avg_exercise_minutes: number | null;
  avg_smoking_count: number | null;
  mood_distribution: {
    GOOD: number;
    NEUTRAL: number;
    BAD: number;
  };
  date_range: {
    start: string; // ISO date
    end: string;   // ISO date
  };
}

/**
 * Daily Log Query Parameters
 * For filtering daily logs list
 */
export interface DailyLogQueryParams {
  patient_id?: string;
  start_date?: string; // ISO date (YYYY-MM-DD)
  end_date?: string;   // ISO date (YYYY-MM-DD)
  page?: number;       // Default: 0
  page_size?: number;  // Default: 30
}

/**
 * Daily Log Create Request
 */
export interface DailyLogCreateRequest {
  patient_id: string;
  log_date: string; // ISO date (YYYY-MM-DD)
  medication_taken?: boolean;
  water_intake_ml?: number;
  exercise_minutes?: number;
  smoking_count?: number;
  symptoms?: string;
  mood?: DailyLogMood;
}

/**
 * Daily Log Update Request
 * All fields optional for partial updates
 */
export interface DailyLogUpdateRequest {
  medication_taken?: boolean;
  water_intake_ml?: number;
  exercise_minutes?: number;
  smoking_count?: number;
  symptoms?: string;
  mood?: DailyLogMood;
}

/**
 * Chart data point for time series
 */
export interface DailyLogChartData {
  date: string; // ISO date or formatted date
  value: number | boolean | null;
  label?: string;
}

/**
 * Medication adherence chart data
 */
export interface MedicationChartData {
  date: string;
  taken: boolean;
  label: string; // "已服藥" or "未服藥"
}

/**
 * Mood trend chart data
 */
export interface MoodChartData {
  date: string;
  mood: DailyLogMood | null;
  moodScore: number; // GOOD=3, NEUTRAL=2, BAD=1, null=0
  label: string; // "良好", "普通", "不佳", "未記錄"
}

/**
 * Elder-First UI constants for charts
 */
export const CHART_CONSTANTS = {
  // Font sizes (Elder-First: ≥18px)
  FONT_SIZE_LARGE: 20,
  FONT_SIZE_MEDIUM: 18,
  FONT_SIZE_SMALL: 16,

  // Touch target size (Elder-First: ≥52px)
  TOUCH_TARGET_SIZE: 52,

  // Chart dimensions
  HEIGHT: 300,
  MARGIN: { top: 20, right: 30, bottom: 60, left: 60 },

  // Colors (High contrast for Elder-First)
  COLORS: {
    PRIMARY: "#3B82F6",      // Blue
    SUCCESS: "#10B981",      // Green
    WARNING: "#F59E0B",      // Amber
    DANGER: "#EF4444",       // Red
    NEUTRAL: "#6B7280",      // Gray
    GOOD: "#10B981",         // Green for mood
    BAD: "#EF4444",          // Red for mood
    NEUTRAL_MOOD: "#F59E0B", // Amber for neutral mood
  },
} as const;

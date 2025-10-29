/**
 * Task Type Definitions
 * TypeScript interfaces mirroring backend Pydantic schemas
 *
 * Backend Reference:
 * - backend/src/respira_ally/core/schemas/task.py
 * - backend/src/respira_ally/domain/entities/task.py
 *
 * Sprint 5 - Task Board UI
 */

// ============================================================================
// Task Enums (mirrored from backend)
// ============================================================================

/**
 * Task Status Lifecycle
 * Represents the current state of a task
 */
export enum TaskStatus {
  TODO = 'TODO',                // Task created, not started
  IN_PROGRESS = 'IN_PROGRESS',  // Task assigned and in progress
  DONE = 'DONE',                // Task completed
  CANCELLED = 'CANCELLED',      // Task cancelled (hidden from board)
}

/**
 * Task Priority Levels
 * Based on Alert Severity and GOLD ABE classification
 */
export enum TaskPriority {
  CRITICAL = 'CRITICAL',  // Alert: CRITICAL severity
  HIGH = 'HIGH',          // Alert: HIGH severity or GOLD Group E
  MEDIUM = 'MEDIUM',      // Alert: MEDIUM severity
  LOW = 'LOW',            // Alert: LOW severity or routine tasks
}

/**
 * Task Type - Auto-generated or Manual
 */
export enum TaskType {
  ALERT_TRIGGERED = 'ALERT_TRIGGERED',  // Auto-generated from Alert
  MANUAL = 'MANUAL',                    // Manually created by therapist
  SCHEDULED = 'SCHEDULED',              // Scheduled routine task
}

// ============================================================================
// Task Interfaces
// ============================================================================

/**
 * Task Response Schema
 * Represents a single task with all details
 *
 * Maps to backend TaskResponse schema
 */
export interface Task {
  // Core fields
  task_id: string           // UUID
  patient_id: string        // Patient UUID
  title: string             // Task title (1-200 chars)
  description?: string      // Task description (optional)

  // Classification
  task_type: TaskType       // Task type
  priority: TaskPriority    // Task priority level
  status: TaskStatus        // Task status

  // Assignment and relationships
  assigned_to?: string      // Assigned therapist UUID (optional)
  related_alert_id?: string // Related alert UUID (optional)

  // Metadata
  task_metadata?: Record<string, any> // Additional task context (GOLD group, scores, etc.)

  // Timestamps (ISO 8601 format)
  due_date?: string         // Due date (optional)
  completed_at?: string     // Completion timestamp (optional)
  created_at: string        // Creation timestamp
  updated_at: string        // Last update timestamp

  // Computed fields
  is_overdue: boolean       // Whether task is overdue
}

/**
 * Task List Response (Paginated)
 * Used for GET /api/v1/patients/{patient_id}/tasks endpoint
 */
export interface TaskListResponse {
  tasks: Task[]             // List of tasks
  total: number             // Total number of tasks matching filters
  page: number              // Current page number (0-indexed)
  page_size: number         // Number of items per page
  total_pages: number       // Total number of pages
}

/**
 * Task Statistics Response
 * Provides overview of task distribution and completion metrics
 */
export interface TaskStatsResponse {
  // Scope identifiers
  patient_id?: string       // Patient UUID (if patient stats)
  therapist_id?: string     // Therapist UUID (if therapist stats)

  // Status breakdown
  total_tasks: number       // Total tasks
  todo_count: number        // TODO tasks
  in_progress_count: number // IN_PROGRESS tasks
  done_count: number        // DONE tasks
  cancelled_count: number   // CANCELLED tasks

  // Priority breakdown
  critical_count: number    // CRITICAL priority tasks
  high_count: number        // HIGH priority tasks
  medium_count: number      // MEDIUM priority tasks
  low_count: number         // LOW priority tasks

  // Overdue tasks
  overdue_count: number     // Overdue tasks

  // Last activity
  last_task_date?: string   // Last task created date (ISO 8601)
  last_task_title?: string  // Last task title
}

// ============================================================================
// Task Request Schemas (for API calls)
// ============================================================================

/**
 * Task Create Request
 * Used for POST /api/v1/tasks endpoint
 */
export interface TaskCreateRequest {
  // Required fields
  patient_id: string
  title: string
  priority: TaskPriority
  task_type?: TaskType      // Defaults to MANUAL

  // Optional fields
  description?: string
  assigned_to?: string      // Therapist UUID
  related_alert_id?: string // Alert UUID
  due_date?: string         // ISO 8601
  task_metadata?: Record<string, any>
}

/**
 * Task Update Request
 * Used for PATCH /api/v1/tasks/{id} endpoint
 * All fields optional for partial updates
 */
export interface TaskUpdateRequest {
  title?: string
  description?: string
  priority?: TaskPriority
  assigned_to?: string      // Reassign to different therapist
  due_date?: string
  task_metadata?: Record<string, any>
}

/**
 * Task Assign Request
 * Used for POST /api/v1/tasks/{id}/assign endpoint
 */
export interface TaskAssignRequest {
  therapist_id: string      // Therapist UUID to assign to
}

/**
 * Task Cancel Request
 * Used for POST /api/v1/tasks/{id}/cancel endpoint
 */
export interface TaskCancelRequest {
  reason?: string           // Cancellation reason (optional)
}

// ============================================================================
// Task Filters (for UI filtering)
// ============================================================================

/**
 * Task Filters
 * Used for client-side filtering in TaskBoard
 */
export interface TaskFilters {
  priority?: TaskPriority   // Filter by priority
  task_type?: TaskType      // Filter by task type
  show_overdue_only?: boolean // Show only overdue tasks
}

// ============================================================================
// Priority Color Configurations
// ============================================================================

/**
 * Priority Color Config
 * Color scheme for priority badges and cards
 */
export interface PriorityColorConfig {
  bg: string        // Background color (Tailwind class)
  border: string    // Border color (Tailwind class)
  text: string      // Text color (Tailwind class)
  badge: string     // Badge color (Tailwind class)
}

/**
 * Priority color mapping
 * Used for visual representation of task priorities
 */
export const PRIORITY_COLORS: Record<TaskPriority, PriorityColorConfig> = {
  [TaskPriority.CRITICAL]: {
    bg: 'bg-red-50',
    border: 'border-red-500',
    text: 'text-red-700',
    badge: 'bg-red-500 text-white',
  },
  [TaskPriority.HIGH]: {
    bg: 'bg-orange-50',
    border: 'border-orange-500',
    text: 'text-orange-700',
    badge: 'bg-orange-500 text-white',
  },
  [TaskPriority.MEDIUM]: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-500',
    text: 'text-yellow-700',
    badge: 'bg-yellow-500 text-white',
  },
  [TaskPriority.LOW]: {
    bg: 'bg-blue-50',
    border: 'border-blue-500',
    text: 'text-blue-700',
    badge: 'bg-blue-500 text-white',
  },
}

// ============================================================================
// Task Type Icons
// ============================================================================

/**
 * Task type icon mapping
 */
export const TASK_TYPE_ICONS: Record<TaskType, string> = {
  [TaskType.ALERT_TRIGGERED]: '🔔',  // Auto-generated from alert
  [TaskType.MANUAL]: '✏️',            // Manually created
  [TaskType.SCHEDULED]: '📅',         // Scheduled routine
}

// ============================================================================
// Status Display Names (Traditional Chinese)
// ============================================================================

/**
 * Status display names in Traditional Chinese
 */
export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  [TaskStatus.TODO]: '待處理',
  [TaskStatus.IN_PROGRESS]: '進行中',
  [TaskStatus.DONE]: '已完成',
  [TaskStatus.CANCELLED]: '已取消',
}

/**
 * Priority display names in Traditional Chinese
 */
export const TASK_PRIORITY_LABELS: Record<TaskPriority, string> = {
  [TaskPriority.CRITICAL]: '緊急',
  [TaskPriority.HIGH]: '高',
  [TaskPriority.MEDIUM]: '中',
  [TaskPriority.LOW]: '低',
}

/**
 * Task type display names in Traditional Chinese
 */
export const TASK_TYPE_LABELS: Record<TaskType, string> = {
  [TaskType.ALERT_TRIGGERED]: '警示觸發',
  [TaskType.MANUAL]: '手動建立',
  [TaskType.SCHEDULED]: '排程任務',
}

// ============================================================================
// Helper Type Guards
// ============================================================================

/**
 * Check if a task is overdue
 */
export function isTaskOverdue(task: Task): boolean {
  if (!task.due_date) return false
  const dueDate = new Date(task.due_date)
  const now = new Date()
  return dueDate < now && task.status !== TaskStatus.DONE
}

/**
 * Check if a task can be started
 */
export function canStartTask(task: Task): boolean {
  return task.status === TaskStatus.TODO
}

/**
 * Check if a task can be completed
 */
export function canCompleteTask(task: Task): boolean {
  return task.status === TaskStatus.IN_PROGRESS
}

/**
 * Check if a task can be cancelled
 */
export function canCancelTask(task: Task): boolean {
  return task.status === TaskStatus.TODO || task.status === TaskStatus.IN_PROGRESS
}

/**
 * Get days until due date
 * Returns negative number if overdue
 */
export function getDaysUntilDue(task: Task): number | null {
  if (!task.due_date) return null
  const dueDate = new Date(task.due_date)
  const now = new Date()
  const diffTime = dueDate.getTime() - now.getTime()
  const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
  return diffDays
}

/**
 * Format due date display
 * Examples: "今天到期", "明天到期", "2 天後到期", "逾期 3 天"
 */
export function formatDueDate(task: Task): string {
  if (!task.due_date) return ''

  const days = getDaysUntilDue(task)
  if (days === null) return ''

  if (days === 0) return '今天到期'
  if (days === 1) return '明天到期'
  if (days > 1) return `${days} 天後到期`
  if (days === -1) return '逾期 1 天'
  return `逾期 ${Math.abs(days)} 天`
}

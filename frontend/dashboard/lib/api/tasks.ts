/**
 * Tasks API - Task management endpoints with Mock support
 * Implements Sprint 5 Task Board UI
 */

import { apiClient, isMockMode } from '../api-client'
import {
  Task,
  TaskListResponse,
  TaskStatsResponse,
  TaskCreateRequest,
  TaskUpdateRequest,
  TaskAssignRequest,
  TaskCancelRequest,
  TaskStatus,
  TaskPriority,
  TaskType,
} from '../types/task'

// ============================================================================
// Mock Data
// ============================================================================

const MOCK_TASKS: Task[] = [
  {
    task_id: '00000000-0000-0000-0000-task00000001',
    patient_id: '00000000-0000-0000-0000-000000000001',
    title: '緊急評估 GOLD Group E 病患',
    description: '病患評估結果顯示為 GOLD Group E，需要立即進行完整的臨床評估並調整治療計畫。',
    task_type: TaskType.ALERT_TRIGGERED,
    priority: TaskPriority.CRITICAL,
    status: TaskStatus.TODO,
    assigned_to: '00000000-0000-0000-0000-000000000999',
    related_alert_id: '00000000-0000-0000-0000-alert0000001',
    task_metadata: {
      gold_group: 'E',
      cat_score: 25,
      mmrc_score: 2,
      exacerbation_count_12m: 3,
    },
    due_date: new Date(Date.now() + 1 * 24 * 60 * 60 * 1000).toISOString(), // 明天
    created_at: '2025-10-26T10:30:00Z',
    updated_at: '2025-10-26T10:30:00Z',
    is_overdue: false,
  },
  {
    task_id: '00000000-0000-0000-0000-task00000002',
    patient_id: '00000000-0000-0000-0000-000000000001',
    title: '追蹤高 CAT 分數',
    description: '病患 CAT 分數為 25，超過警戒值 20，需要追蹤症狀變化並評估是否需要調整用藥。',
    task_type: TaskType.ALERT_TRIGGERED,
    priority: TaskPriority.HIGH,
    status: TaskStatus.IN_PROGRESS,
    assigned_to: '00000000-0000-0000-0000-000000000999',
    related_alert_id: '00000000-0000-0000-0000-alert0000002',
    task_metadata: {
      cat_score: 25,
      threshold: 20,
    },
    due_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(), // 3天後
    created_at: '2025-10-26T11:45:00Z',
    updated_at: '2025-10-27T09:15:00Z',
    is_overdue: false,
  },
  {
    task_id: '00000000-0000-0000-0000-task00000003',
    patient_id: '00000000-0000-0000-0000-000000000001',
    title: '每週用藥遵從性追蹤',
    description: '檢查病患本週的用藥紀錄，確認是否按時服藥，並了解是否有任何副作用。',
    task_type: TaskType.SCHEDULED,
    priority: TaskPriority.MEDIUM,
    status: TaskStatus.TODO,
    assigned_to: '00000000-0000-0000-0000-000000000999',
    task_metadata: {
      schedule_type: 'weekly',
      recurrence: 'every_monday',
    },
    due_date: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), // 2天後
    created_at: '2025-10-27T08:00:00Z',
    updated_at: '2025-10-27T08:00:00Z',
    is_overdue: false,
  },
  {
    task_id: '00000000-0000-0000-0000-task00000004',
    patient_id: '00000000-0000-0000-0000-000000000001',
    title: '電話訪談：呼吸訓練效果評估',
    description: '聯絡病患了解最近呼吸訓練的執行狀況，評估訓練效果並提供指導建議。',
    task_type: TaskType.MANUAL,
    priority: TaskPriority.LOW,
    status: TaskStatus.DONE,
    assigned_to: '00000000-0000-0000-0000-000000000999',
    task_metadata: {
      contact_method: 'phone',
      training_type: 'breathing_exercise',
    },
    due_date: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000).toISOString(), // 昨天（已完成）
    completed_at: '2025-10-27T14:30:00Z',
    created_at: '2025-10-26T16:20:00Z',
    updated_at: '2025-10-27T14:30:00Z',
    is_overdue: false,
  },
  {
    task_id: '00000000-0000-0000-0000-task00000005',
    patient_id: '00000000-0000-0000-0000-000000000002',
    title: '追蹤頻繁急性惡化病患',
    description: '病患過去12個月有4次急性惡化記錄，需要密切追蹤並制定預防計畫。',
    task_type: TaskType.ALERT_TRIGGERED,
    priority: TaskPriority.HIGH,
    status: TaskStatus.TODO,
    assigned_to: '00000000-0000-0000-0000-000000000999',
    related_alert_id: '00000000-0000-0000-0000-alert0000003',
    task_metadata: {
      exacerbation_count_12m: 4,
      threshold: 3,
    },
    due_date: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2天前（逾期）
    created_at: '2025-10-25T14:20:00Z',
    updated_at: '2025-10-25T14:20:00Z',
    is_overdue: true,
  },
  {
    task_id: '00000000-0000-0000-0000-task00000006',
    patient_id: '00000000-0000-0000-0000-000000000002',
    title: '月度健康檢查提醒',
    description: '提醒病患進行每月例行健康檢查，包括肺功能測試和血氧濃度測量。',
    task_type: TaskType.SCHEDULED,
    priority: TaskPriority.MEDIUM,
    status: TaskStatus.TODO,
    task_metadata: {
      schedule_type: 'monthly',
      check_items: ['lung_function', 'spo2'],
    },
    due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7天後
    created_at: '2025-10-27T10:00:00Z',
    updated_at: '2025-10-27T10:00:00Z',
    is_overdue: false,
  },
]

// ============================================================================
// API Functions
// ============================================================================

/**
 * Get tasks for a specific patient
 * GET /api/v1/patients/{patient_id}/tasks
 */
export async function fetchPatientTasks(
  patientId: string,
  params?: {
    status?: TaskStatus
    priority?: TaskPriority
    page?: number
    page_size?: number
  }
): Promise<TaskListResponse> {
  // Mock mode
  if (isMockMode) {
    const mockDelay = new Promise((resolve) => setTimeout(resolve, 500))
    await mockDelay

    let filteredTasks = MOCK_TASKS.filter((task) => task.patient_id === patientId)

    // Apply filters
    if (params?.status) {
      filteredTasks = filteredTasks.filter((task) => task.status === params.status)
    }

    if (params?.priority) {
      filteredTasks = filteredTasks.filter((task) => task.priority === params.priority)
    }

    // Apply pagination
    const page = params?.page ?? 0
    const pageSize = params?.page_size ?? 50
    const start = page * pageSize
    const end = start + pageSize
    const paginatedTasks = filteredTasks.slice(start, end)

    return {
      tasks: paginatedTasks,
      total: filteredTasks.length,
      page,
      page_size: pageSize,
      total_pages: Math.ceil(filteredTasks.length / pageSize),
    }
  }

  // Real API call
  const queryParams = new URLSearchParams()

  if (params?.status) queryParams.append('status', params.status)
  if (params?.priority) queryParams.append('priority', params.priority)
  if (params?.page !== undefined) queryParams.append('page', params.page.toString())
  if (params?.page_size !== undefined) queryParams.append('page_size', params.page_size.toString())

  const queryString = queryParams.toString()
  const url = `/patients/${patientId}/tasks${queryString ? `?${queryString}` : ''}`

  return apiClient.get<TaskListResponse>(url)
}

/**
 * Get task statistics for a patient
 * GET /api/v1/patients/{patient_id}/tasks/stats
 */
export async function getTaskStats(patientId: string): Promise<TaskStatsResponse> {
  // Mock mode
  if (isMockMode) {
    const mockDelay = new Promise((resolve) => setTimeout(resolve, 300))
    await mockDelay

    const patientTasks = MOCK_TASKS.filter((task) => task.patient_id === patientId)

    // Calculate statistics
    const stats: TaskStatsResponse = {
      patient_id: patientId,
      total_tasks: patientTasks.length,
      todo_count: patientTasks.filter((t) => t.status === TaskStatus.TODO).length,
      in_progress_count: patientTasks.filter((t) => t.status === TaskStatus.IN_PROGRESS).length,
      done_count: patientTasks.filter((t) => t.status === TaskStatus.DONE).length,
      cancelled_count: patientTasks.filter((t) => t.status === TaskStatus.CANCELLED).length,
      critical_count: patientTasks.filter((t) => t.priority === TaskPriority.CRITICAL).length,
      high_count: patientTasks.filter((t) => t.priority === TaskPriority.HIGH).length,
      medium_count: patientTasks.filter((t) => t.priority === TaskPriority.MEDIUM).length,
      low_count: patientTasks.filter((t) => t.priority === TaskPriority.LOW).length,
      overdue_count: patientTasks.filter((t) => t.is_overdue).length,
    }

    // Add last task info if exists
    if (patientTasks.length > 0) {
      const sortedTasks = [...patientTasks].sort(
        (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      )
      stats.last_task_date = sortedTasks[0].created_at
      stats.last_task_title = sortedTasks[0].title
    }

    return stats
  }

  // Real API call
  return apiClient.get<TaskStatsResponse>(`/patients/${patientId}/tasks/stats`)
}

/**
 * Create a new task
 * POST /api/v1/tasks
 */
export async function createTask(request: TaskCreateRequest): Promise<Task> {
  // Mock mode
  if (isMockMode) {
    const mockDelay = new Promise((resolve) => setTimeout(resolve, 500))
    await mockDelay

    const newTask: Task = {
      task_id: `00000000-0000-0000-0000-task${Date.now().toString().slice(-8)}`,
      patient_id: request.patient_id,
      title: request.title,
      description: request.description,
      task_type: request.task_type || TaskType.MANUAL,
      priority: request.priority,
      status: TaskStatus.TODO,
      assigned_to: request.assigned_to,
      related_alert_id: request.related_alert_id,
      task_metadata: request.task_metadata,
      due_date: request.due_date,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      is_overdue: false,
    }

    MOCK_TASKS.push(newTask)
    return newTask
  }

  // Real API call
  return apiClient.post<Task>('/tasks', request)
}

/**
 * Update a task
 * PATCH /api/v1/tasks/{task_id}
 */
export async function updateTask(taskId: string, request: TaskUpdateRequest): Promise<Task> {
  // Mock mode
  if (isMockMode) {
    const mockDelay = new Promise((resolve) => setTimeout(resolve, 500))
    await mockDelay

    const taskIndex = MOCK_TASKS.findIndex((t) => t.task_id === taskId)

    if (taskIndex === -1) {
      throw new Error(`Task ${taskId} not found`)
    }

    MOCK_TASKS[taskIndex] = {
      ...MOCK_TASKS[taskIndex],
      ...request,
      updated_at: new Date().toISOString(),
    }

    return MOCK_TASKS[taskIndex]
  }

  // Real API call
  return apiClient.patch<Task>(`/tasks/${taskId}`, request)
}

/**
 * Delete a task
 * DELETE /api/v1/tasks/{task_id}
 */
export async function deleteTask(taskId: string): Promise<void> {
  // Mock mode
  if (isMockMode) {
    const mockDelay = new Promise((resolve) => setTimeout(resolve, 500))
    await mockDelay

    const taskIndex = MOCK_TASKS.findIndex((t) => t.task_id === taskId)

    if (taskIndex === -1) {
      throw new Error(`Task ${taskId} not found`)
    }

    MOCK_TASKS.splice(taskIndex, 1)
    return
  }

  // Real API call
  return apiClient.delete<void>(`/tasks/${taskId}`)
}

/**
 * Start a task (change status to IN_PROGRESS)
 * POST /api/v1/tasks/{task_id}/start
 */
export async function startTask(taskId: string): Promise<Task> {
  // Mock mode
  if (isMockMode) {
    const mockDelay = new Promise((resolve) => setTimeout(resolve, 500))
    await mockDelay

    const taskIndex = MOCK_TASKS.findIndex((t) => t.task_id === taskId)

    if (taskIndex === -1) {
      throw new Error(`Task ${taskId} not found`)
    }

    if (MOCK_TASKS[taskIndex].status !== TaskStatus.TODO) {
      throw new Error(`Task ${taskId} cannot be started (current status: ${MOCK_TASKS[taskIndex].status})`)
    }

    MOCK_TASKS[taskIndex].status = TaskStatus.IN_PROGRESS
    MOCK_TASKS[taskIndex].updated_at = new Date().toISOString()

    return MOCK_TASKS[taskIndex]
  }

  // Real API call
  return apiClient.post<Task>(`/tasks/${taskId}/start`)
}

/**
 * Complete a task (change status to DONE)
 * POST /api/v1/tasks/{task_id}/complete
 */
export async function completeTask(taskId: string): Promise<Task> {
  // Mock mode
  if (isMockMode) {
    const mockDelay = new Promise((resolve) => setTimeout(resolve, 500))
    await mockDelay

    const taskIndex = MOCK_TASKS.findIndex((t) => t.task_id === taskId)

    if (taskIndex === -1) {
      throw new Error(`Task ${taskId} not found`)
    }

    if (MOCK_TASKS[taskIndex].status !== TaskStatus.IN_PROGRESS) {
      throw new Error(`Task ${taskId} cannot be completed (current status: ${MOCK_TASKS[taskIndex].status})`)
    }

    MOCK_TASKS[taskIndex].status = TaskStatus.DONE
    MOCK_TASKS[taskIndex].completed_at = new Date().toISOString()
    MOCK_TASKS[taskIndex].updated_at = new Date().toISOString()

    return MOCK_TASKS[taskIndex]
  }

  // Real API call
  return apiClient.post<Task>(`/tasks/${taskId}/complete`)
}

/**
 * Cancel a task
 * POST /api/v1/tasks/{task_id}/cancel
 */
export async function cancelTask(taskId: string, request?: TaskCancelRequest): Promise<Task> {
  // Mock mode
  if (isMockMode) {
    const mockDelay = new Promise((resolve) => setTimeout(resolve, 500))
    await mockDelay

    const taskIndex = MOCK_TASKS.findIndex((t) => t.task_id === taskId)

    if (taskIndex === -1) {
      throw new Error(`Task ${taskId} not found`)
    }

    if (MOCK_TASKS[taskIndex].status === TaskStatus.DONE || MOCK_TASKS[taskIndex].status === TaskStatus.CANCELLED) {
      throw new Error(`Task ${taskId} cannot be cancelled (current status: ${MOCK_TASKS[taskIndex].status})`)
    }

    MOCK_TASKS[taskIndex].status = TaskStatus.CANCELLED
    MOCK_TASKS[taskIndex].updated_at = new Date().toISOString()

    if (request?.reason) {
      MOCK_TASKS[taskIndex].task_metadata = {
        ...MOCK_TASKS[taskIndex].task_metadata,
        cancellation_reason: request.reason,
      }
    }

    return MOCK_TASKS[taskIndex]
  }

  // Real API call
  return apiClient.post<Task>(`/tasks/${taskId}/cancel`, request)
}

/**
 * Assign a task to a therapist
 * POST /api/v1/tasks/{task_id}/assign
 */
export async function assignTask(taskId: string, request: TaskAssignRequest): Promise<Task> {
  // Mock mode
  if (isMockMode) {
    const mockDelay = new Promise((resolve) => setTimeout(resolve, 500))
    await mockDelay

    const taskIndex = MOCK_TASKS.findIndex((t) => t.task_id === taskId)

    if (taskIndex === -1) {
      throw new Error(`Task ${taskId} not found`)
    }

    MOCK_TASKS[taskIndex].assigned_to = request.therapist_id
    MOCK_TASKS[taskIndex].updated_at = new Date().toISOString()

    return MOCK_TASKS[taskIndex]
  }

  // Real API call
  return apiClient.post<Task>(`/tasks/${taskId}/assign`, request)
}

// ============================================================================
// Export all functions
// ============================================================================

export const tasksAPI = {
  fetchPatientTasks,
  getTaskStats,
  createTask,
  updateTask,
  deleteTask,
  startTask,
  completeTask,
  cancelTask,
  assignTask,
}

/**
 * TaskBoard Component
 * Main Kanban board with drag-and-drop task management
 * Sprint 5 - Task Board UI
 */

'use client'

import { useState, useEffect, useCallback } from 'react'
import { DragDropContext, DropResult } from '@hello-pangea/dnd'
import TaskColumn from './TaskColumn'
import type { Task, TaskStatus } from '@/lib/types/task'
import { fetchPatientTasks, startTask, completeTask } from '@/lib/api/tasks'

interface TaskBoardProps {
  patientId: string
  onTaskClick?: (task: Task) => void
}

export default function TaskBoard({ patientId, onTaskClick }: TaskBoardProps) {
  // State management
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isUpdating, setIsUpdating] = useState(false)

  // Load tasks from API
  const loadTasks = useCallback(async () => {
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetchPatientTasks(patientId, {
        page: 0,
        page_size: 100, // Load all tasks for board view
      })
      setTasks(response.tasks)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks')
      console.error('Error loading tasks:', err)
    } finally {
      setIsLoading(false)
    }
  }, [patientId])

  // Load tasks on mount and when patientId changes
  useEffect(() => {
    loadTasks()
  }, [loadTasks])

  // Group tasks by status
  const groupedTasks = {
    TODO: tasks.filter((task) => task.status === 'TODO'),
    IN_PROGRESS: tasks.filter((task) => task.status === 'IN_PROGRESS'),
    DONE: tasks.filter((task) => task.status === 'DONE'),
  }

  // Handle drag end
  const handleDragEnd = async (result: DropResult) => {
    const { source, destination, draggableId } = result

    // Dropped outside a droppable area
    if (!destination) {
      return
    }

    // Dropped in the same position
    if (
      source.droppableId === destination.droppableId &&
      source.index === destination.index
    ) {
      return
    }

    const sourceStatus = source.droppableId as TaskStatus
    const destStatus = destination.droppableId as TaskStatus

    // No status change
    if (sourceStatus === destStatus) {
      return
    }

    // Find the task being moved
    const task = tasks.find((t) => t.task_id === draggableId)
    if (!task) {
      return
    }

    // Validate state transitions
    const isValidTransition = validateStatusTransition(task.status, destStatus)
    if (!isValidTransition) {
      alert(
        `無法將任務從「${task.status}」移動到「${destStatus}」\n` +
          `有效的狀態轉換：\n` +
          `- TODO → IN_PROGRESS (開始任務)\n` +
          `- IN_PROGRESS → DONE (完成任務)`
      )
      return
    }

    // Optimistic update: Update UI immediately
    const updatedTasks = tasks.map((t) =>
      t.task_id === draggableId ? { ...t, status: destStatus } : t
    )
    setTasks(updatedTasks)
    setIsUpdating(true)

    try {
      // Call appropriate API based on transition
      if (sourceStatus === 'TODO' && destStatus === 'IN_PROGRESS') {
        await startTask(draggableId)
      } else if (sourceStatus === 'IN_PROGRESS' && destStatus === 'DONE') {
        await completeTask(draggableId)
      }

      // Refresh tasks to ensure consistency
      await loadTasks()
    } catch (err) {
      // Rollback on error
      setTasks(tasks)
      alert(
        `更新任務狀態失敗：${err instanceof Error ? err.message : '未知錯誤'}\n` +
          `任務已恢復原狀態`
      )
      console.error('Error updating task status:', err)
    } finally {
      setIsUpdating(false)
    }
  }

  // Validate status transitions
  const validateStatusTransition = (
    fromStatus: TaskStatus,
    toStatus: TaskStatus
  ): boolean => {
    // Allow TODO → IN_PROGRESS
    if (fromStatus === 'TODO' && toStatus === 'IN_PROGRESS') {
      return true
    }

    // Allow IN_PROGRESS → DONE
    if (fromStatus === 'IN_PROGRESS' && toStatus === 'DONE') {
      return true
    }

    // Allow moving back: IN_PROGRESS → TODO
    if (fromStatus === 'IN_PROGRESS' && toStatus === 'TODO') {
      return true
    }

    // Allow moving back: DONE → IN_PROGRESS
    if (fromStatus === 'DONE' && toStatus === 'IN_PROGRESS') {
      return true
    }

    return false
  }

  // Handle refresh
  const handleRefresh = () => {
    loadTasks()
  }

  // Loading state
  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">載入任務看板中...</p>
        </div>
      </div>
    )
  }

  // Error state
  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="text-6xl mb-4">⚠️</div>
          <p className="text-red-600 font-semibold mb-2">載入任務失敗</p>
          <p className="text-gray-600 text-sm mb-4">{error}</p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            重新載入
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">任務看板</h2>
          <p className="text-sm text-gray-600 mt-1">
            拖曳任務卡片以更新狀態 • 共 {tasks.length} 個任務
          </p>
        </div>
        <button
          onClick={handleRefresh}
          disabled={isUpdating}
          className={`
            flex items-center gap-2 px-4 py-2 rounded-lg transition-colors
            ${
              isUpdating
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-white border border-gray-300 text-gray-700 hover:bg-gray-50'
            }
          `}
        >
          <svg
            className={`w-5 h-5 ${isUpdating ? 'animate-spin' : ''}`}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
            />
          </svg>
          <span>{isUpdating ? '更新中...' : '刷新'}</span>
        </button>
      </div>

      {/* Kanban Board */}
      <DragDropContext onDragEnd={handleDragEnd}>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <TaskColumn
            status="TODO"
            tasks={groupedTasks.TODO}
            onTaskClick={onTaskClick}
          />
          <TaskColumn
            status="IN_PROGRESS"
            tasks={groupedTasks.IN_PROGRESS}
            onTaskClick={onTaskClick}
          />
          <TaskColumn
            status="DONE"
            tasks={groupedTasks.DONE}
            onTaskClick={onTaskClick}
          />
        </div>
      </DragDropContext>

      {/* Empty State (when no tasks at all) */}
      {tasks.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <div className="text-6xl mb-4">📋</div>
          <p className="text-gray-600 font-medium mb-2">尚無任務</p>
          <p className="text-sm text-gray-500">
            此病患目前沒有任何任務紀錄
          </p>
        </div>
      )}
    </div>
  )
}

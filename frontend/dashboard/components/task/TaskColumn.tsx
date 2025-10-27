/**
 * TaskColumn Component
 * Displays a column of tasks with a specific status (Droppable container)
 * Sprint 5 - Task Board UI
 */

'use client'

import { Droppable } from '@hello-pangea/dnd'
import TaskCard from './TaskCard'
import type { Task, TaskStatus } from '@/lib/types/task'
import { TASK_STATUS_LABELS } from '@/lib/types/task'

interface TaskColumnProps {
  status: TaskStatus
  tasks: Task[]
  onTaskClick?: (task: Task) => void
}

export default function TaskColumn({ status, tasks, onTaskClick }: TaskColumnProps) {
  const statusLabel = TASK_STATUS_LABELS[status]

  // Define column styling based on status
  const getColumnStyle = (status: TaskStatus) => {
    switch (status) {
      case 'TODO':
        return {
          headerBg: 'bg-gray-100',
          headerText: 'text-gray-800',
          badgeBg: 'bg-gray-600',
          emptyIcon: '📝',
        }
      case 'IN_PROGRESS':
        return {
          headerBg: 'bg-blue-100',
          headerText: 'text-blue-800',
          badgeBg: 'bg-blue-600',
          emptyIcon: '⚙️',
        }
      case 'DONE':
        return {
          headerBg: 'bg-green-100',
          headerText: 'text-green-800',
          badgeBg: 'bg-green-600',
          emptyIcon: '✅',
        }
      default:
        return {
          headerBg: 'bg-gray-100',
          headerText: 'text-gray-800',
          badgeBg: 'bg-gray-600',
          emptyIcon: '📋',
        }
    }
  }

  const columnStyle = getColumnStyle(status)

  return (
    <div className="flex flex-col h-full bg-gray-50 rounded-lg">
      {/* Column Header */}
      <div className={`px-4 py-3 rounded-t-lg ${columnStyle.headerBg}`}>
        <div className="flex items-center justify-between">
          <h2 className={`font-bold text-lg ${columnStyle.headerText}`}>
            {statusLabel}
          </h2>
          <span
            className={`
              inline-flex items-center justify-center
              min-w-[24px] h-6 px-2
              rounded-full text-xs font-bold text-white
              ${columnStyle.badgeBg}
            `}
          >
            {tasks.length}
          </span>
        </div>
      </div>

      {/* Droppable Task List */}
      <Droppable droppableId={status}>
        {(provided, snapshot) => (
          <div
            ref={provided.innerRef}
            {...provided.droppableProps}
            className={`
              flex-1 p-4 overflow-y-auto
              min-h-[400px] transition-colors
              ${snapshot.isDraggingOver ? 'bg-blue-50' : 'bg-transparent'}
            `}
          >
            {/* Task Cards */}
            {tasks.length > 0 ? (
              tasks.map((task, index) => (
                <TaskCard
                  key={task.task_id}
                  task={task}
                  index={index}
                  onClick={onTaskClick}
                />
              ))
            ) : (
              /* Empty State */
              <div className="flex flex-col items-center justify-center h-full text-gray-400">
                <span className="text-6xl mb-3">{columnStyle.emptyIcon}</span>
                <p className="text-sm font-medium">
                  {status === 'TODO' && '目前沒有待處理任務'}
                  {status === 'IN_PROGRESS' && '目前沒有進行中任務'}
                  {status === 'DONE' && '尚無已完成任務'}
                </p>
                <p className="text-xs mt-1 text-gray-400">
                  拖曳任務卡片到此欄位
                </p>
              </div>
            )}
            {provided.placeholder}
          </div>
        )}
      </Droppable>
    </div>
  )
}

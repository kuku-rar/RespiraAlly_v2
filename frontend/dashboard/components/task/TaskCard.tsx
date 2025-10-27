/**
 * TaskCard Component
 * Displays a single task card with drag-and-drop support
 * Sprint 5 - Task Board UI
 */

'use client'

import { Draggable } from '@hello-pangea/dnd'
import type { Task } from '@/lib/types/task'
import {
  PRIORITY_COLORS,
  TASK_TYPE_ICONS,
  TASK_PRIORITY_LABELS,
  formatDueDate,
  getDaysUntilDue,
} from '@/lib/types/task'

interface TaskCardProps {
  task: Task
  index: number
  onClick?: (task: Task) => void
}

export default function TaskCard({ task, index, onClick }: TaskCardProps) {
  const priorityColors = PRIORITY_COLORS[task.priority]
  const typeIcon = TASK_TYPE_ICONS[task.task_type]
  const priorityLabel = TASK_PRIORITY_LABELS[task.priority]
  const dueText = formatDueDate(task)
  const daysUntilDue = getDaysUntilDue(task)

  // Determine if task is overdue or due soon
  const isOverdue = task.is_overdue
  const isDueSoon = daysUntilDue !== null && daysUntilDue <= 2 && daysUntilDue >= 0

  const handleClick = () => {
    if (onClick) {
      onClick(task)
    }
  }

  return (
    <Draggable draggableId={task.task_id} index={index}>
      {(provided, snapshot) => (
        <div
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          onClick={handleClick}
          className={`
            rounded-lg border-2 p-4 mb-3 cursor-pointer transition-all
            ${priorityColors.bg} ${priorityColors.border}
            ${snapshot.isDragging ? 'shadow-2xl rotate-2 opacity-90' : 'shadow-sm hover:shadow-md'}
          `}
        >
          {/* Header: Priority Badge + Type Icon */}
          <div className="flex items-start justify-between mb-2">
            {/* Priority Badge */}
            <span
              className={`
                inline-flex items-center px-2 py-1 rounded-full text-xs font-semibold
                ${priorityColors.badge}
              `}
            >
              {priorityLabel}
            </span>

            {/* Type Icon */}
            <span className="text-lg" title={task.task_type}>
              {typeIcon}
            </span>
          </div>

          {/* Title */}
          <h3 className={`font-semibold text-sm mb-2 line-clamp-2 ${priorityColors.text}`}>
            {task.title}
          </h3>

          {/* Description */}
          {task.description && (
            <p className="text-xs text-gray-600 mb-3 line-clamp-2">
              {task.description}
            </p>
          )}

          {/* Footer: Due Date + Alert Badge */}
          <div className="flex items-center justify-between text-xs">
            {/* Due Date */}
            {task.due_date && (
              <div
                className={`
                  flex items-center gap-1 font-medium
                  ${
                    isOverdue
                      ? 'text-red-600'
                      : isDueSoon
                      ? 'text-orange-600'
                      : 'text-gray-600'
                  }
                `}
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                  />
                </svg>
                <span>{dueText}</span>
              </div>
            )}

            {/* Alert Badge */}
            {task.related_alert_id && (
              <div
                className="flex items-center gap-1 text-orange-600"
                title="關聯警示"
              >
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"
                  />
                </svg>
                <span className="text-xs font-medium">警示</span>
              </div>
            )}
          </div>

          {/* Overdue Warning Banner (if applicable) */}
          {isOverdue && (
            <div className="mt-3 pt-3 border-t border-red-300">
              <div className="flex items-center gap-2 text-red-600">
                <svg
                  className="w-4 h-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
                <span className="text-xs font-bold">任務已逾期！</span>
              </div>
            </div>
          )}
        </div>
      )}
    </Draggable>
  )
}

# Task Board UI Implementation Plan

**Document Version**: v1.0
**Created**: 2025-10-27
**Sprint**: Sprint 5 - Week 1
**Status**: Planning Complete - Ready for Implementation

---

## 🎯 Overview

Implement a Kanban-style Task Board UI for therapists to manage clinical tasks for their patients. The Task Board provides drag-and-drop task management with real-time status updates.

---

## 📊 API Integration Summary

### Core Task API Endpoints

Based on `/backend/src/respira_ally/api/v1/routers/task.py`:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **GET** | `/api/v1/patients/{patient_id}/tasks` | List patient tasks with filters |
| **POST** | `/api/v1/tasks/{task_id}/start` | Move task to IN_PROGRESS |
| **POST** | `/api/v1/tasks/{task_id}/complete` | Move task to DONE |
| **PATCH** | `/api/v1/tasks/{task_id}` | Update task details |

### Task Data Model

From `/backend/src/respira_ally/core/schemas/task.py`:

```typescript
// Task Status (3 columns in Kanban)
enum TaskStatus {
  TODO = "TODO",
  IN_PROGRESS = "IN_PROGRESS",
  DONE = "DONE",
  CANCELLED = "CANCELLED"  // Hidden from board
}

// Task Priority (visual indicators)
enum TaskPriority {
  CRITICAL = "CRITICAL",  // Red
  HIGH = "HIGH",          // Orange
  MEDIUM = "MEDIUM",      // Yellow
  LOW = "LOW"             // Blue
}

// Task Type (filter option)
enum TaskType {
  ALERT_TRIGGERED = "ALERT_TRIGGERED",  // 🔔 Auto-generated
  MANUAL = "MANUAL",                    // ✏️ Manual
  SCHEDULED = "SCHEDULED"               // 📅 Scheduled
}

// Task Response Schema
interface Task {
  task_id: string           // UUID
  patient_id: string        // UUID
  title: string             // Task title (1-200 chars)
  description?: string      // Task description
  task_type: TaskType
  priority: TaskPriority
  status: TaskStatus
  assigned_to?: string      // Therapist UUID
  related_alert_id?: string // Alert UUID (if triggered by alert)
  task_metadata?: object    // GOLD group, scores, etc.
  due_date?: string         // ISO 8601
  completed_at?: string     // ISO 8601
  created_at: string        // ISO 8601
  updated_at: string        // ISO 8601
  is_overdue: boolean       // Computed field
}

// List Response (Pagination)
interface TaskListResponse {
  tasks: Task[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
```

---

## 🏗️ Component Architecture

### Component Hierarchy

```
TaskBoard (Main Kanban Board)
├── TaskBoardFilters (Filter controls)
│   ├── PriorityFilter (CRITICAL | HIGH | MEDIUM | LOW)
│   ├── TypeFilter (ALERT_TRIGGERED | MANUAL | SCHEDULED)
│   └── OverdueToggle (Show overdue only)
├── TaskColumn (TODO Column)
│   └── TaskCard[] (Draggable task cards)
├── TaskColumn (IN_PROGRESS Column)
│   └── TaskCard[] (Draggable task cards)
└── TaskColumn (DONE Column)
    └── TaskCard[] (Draggable task cards)

TaskCard (Individual Task Card)
├── PriorityBadge (Color-coded indicator)
├── TaskTitle (Clickable title)
├── TaskDescription (Truncated)
├── PatientLink (Link to patient detail)
├── DueDateIndicator (With overdue warning)
└── QuickActions (Start | Complete | Edit)
```

---

## 🎨 UI Design Specifications

### TaskBoard Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ 🎯 Task Board - 王小明 的任務                                     │
│                                                                   │
│ 🔽 篩選: [All Priorities ▼] [All Types ▼] [⚠️ Show Overdue Only]│
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│   ┌──────────┐   ┌──────────┐   ┌──────────┐                  │
│   │ TODO (3) │   │ PROGRESS │   │ DONE (5) │                  │
│   │          │   │   (2)    │   │          │                  │
│   ├──────────┤   ├──────────┤   ├──────────┤                  │
│   │ ┌──────┐ │   │ ┌──────┐ │   │ ┌──────┐ │                  │
│   │ │ CARD │ │   │ │ CARD │ │   │ │ CARD │ │                  │
│   │ └──────┘ │   │ └──────┘ │   │ └──────┘ │                  │
│   │ ┌──────┐ │   │ ┌──────┐ │   │ ┌──────┐ │                  │
│   │ │ CARD │ │   │ │ CARD │ │   │ │ CARD │ │                  │
│   │ └──────┘ │   │ └──────┘ │   │ └──────┘ │                  │
│   └──────────┘   └──────────┘   └──────────┘                  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### TaskCard Design

```
┌─────────────────────────────────────────────┐
│ 🔴 CRITICAL                     📅 2 天逾期 │ ← Priority Badge + Overdue
│ 追蹤病患血氧濃度                            │ ← Title
│ 病患血氧持續低於 85%，需立即追蹤...        │ ← Description (truncated)
│ ─────────────────────────────────────────   │
│ 👤 王小明 | 🔔 Alert #123 | 到期: 10/25    │ ← Patient + Alert + Due Date
│ ─────────────────────────────────────────   │
│ [▶️ 開始執行]  [✅ 標記完成]  [✏️ 編輯]     │ ← Quick Actions
└─────────────────────────────────────────────┘
```

### Priority Color Coding

```typescript
const PRIORITY_COLORS = {
  CRITICAL: {
    bg: 'bg-red-100',
    border: 'border-red-500',
    text: 'text-red-700',
    badge: 'bg-red-500 text-white'
  },
  HIGH: {
    bg: 'bg-orange-100',
    border: 'border-orange-500',
    text: 'text-orange-700',
    badge: 'bg-orange-500 text-white'
  },
  MEDIUM: {
    bg: 'bg-yellow-100',
    border: 'border-yellow-500',
    text: 'text-yellow-700',
    badge: 'bg-yellow-500 text-white'
  },
  LOW: {
    bg: 'bg-blue-100',
    border: 'border-blue-500',
    text: 'text-blue-700',
    badge: 'bg-blue-500 text-white'
  }
}
```

---

## 📂 File Structure

```
frontend/dashboard/
├── components/
│   └── task/
│       ├── TaskBoard.tsx           # Main Kanban board (600 lines)
│       ├── TaskColumn.tsx          # Single column with drop zone (200 lines)
│       ├── TaskCard.tsx            # Individual task card (300 lines)
│       ├── TaskBoardFilters.tsx    # Filter controls (150 lines)
│       └── index.ts                # Export barrel file
├── lib/
│   ├── api/
│   │   └── tasks.ts                # Task API client functions (200 lines)
│   └── types/
│       └── task.ts                 # TypeScript interfaces (100 lines)
└── app/
    └── patients/
        └── [id]/
            └── page.tsx            # Add TaskBoard to patient detail page
```

---

## 🔧 Implementation Steps

### Step 1: TypeScript Type Definitions (30 min)

**File**: `frontend/dashboard/lib/types/task.ts`

```typescript
/**
 * Task Type Definitions
 * Mirrors backend Pydantic schemas
 */

export enum TaskStatus {
  TODO = 'TODO',
  IN_PROGRESS = 'IN_PROGRESS',
  DONE = 'DONE',
  CANCELLED = 'CANCELLED',
}

export enum TaskPriority {
  CRITICAL = 'CRITICAL',
  HIGH = 'HIGH',
  MEDIUM = 'MEDIUM',
  LOW = 'LOW',
}

export enum TaskType {
  ALERT_TRIGGERED = 'ALERT_TRIGGERED',
  MANUAL = 'MANUAL',
  SCHEDULED = 'SCHEDULED',
}

export interface Task {
  task_id: string
  patient_id: string
  title: string
  description?: string
  task_type: TaskType
  priority: TaskPriority
  status: TaskStatus
  assigned_to?: string
  related_alert_id?: string
  task_metadata?: Record<string, any>
  due_date?: string
  completed_at?: string
  created_at: string
  updated_at: string
  is_overdue: boolean
}

export interface TaskListResponse {
  tasks: Task[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface TaskFilters {
  priority?: TaskPriority
  task_type?: TaskType
  show_overdue_only?: boolean
}
```

### Step 2: API Client Functions (45 min)

**File**: `frontend/dashboard/lib/api/tasks.ts`

```typescript
/**
 * Task API Client
 * REST API calls for Task Management
 */

import { Task, TaskListResponse, TaskStatus } from '@/lib/types/task'

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'

/**
 * Fetch tasks for a specific patient
 */
export async function fetchPatientTasks(
  patientId: string,
  params?: {
    page?: number
    page_size?: number
    task_status?: TaskStatus
    priority?: string
    task_type?: string
  }
): Promise<TaskListResponse> {
  const queryParams = new URLSearchParams()

  if (params?.page !== undefined) queryParams.append('page', params.page.toString())
  if (params?.page_size !== undefined) queryParams.append('page_size', params.page_size.toString())
  if (params?.task_status) queryParams.append('task_status', params.task_status)
  if (params?.priority) queryParams.append('priority', params.priority)
  if (params?.task_type) queryParams.append('task_type', params.task_type)

  const response = await fetch(
    `${API_BASE}/patients/${patientId}/tasks?${queryParams.toString()}`,
    {
      headers: {
        'Authorization': `Bearer ${getAccessToken()}`,
        'Content-Type': 'application/json',
      },
    }
  )

  if (!response.ok) {
    throw new Error(`Failed to fetch tasks: ${response.statusText}`)
  }

  return response.json()
}

/**
 * Start a task (TODO → IN_PROGRESS)
 */
export async function startTask(taskId: string): Promise<Task> {
  const response = await fetch(`${API_BASE}/tasks/${taskId}/start`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAccessToken()}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to start task: ${response.statusText}`)
  }

  return response.json()
}

/**
 * Complete a task (IN_PROGRESS → DONE)
 */
export async function completeTask(taskId: string): Promise<Task> {
  const response = await fetch(`${API_BASE}/tasks/${taskId}/complete`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${getAccessToken()}`,
      'Content-Type': 'application/json',
    },
  })

  if (!response.ok) {
    throw new Error(`Failed to complete task: ${response.statusText}`)
  }

  return response.json()
}

/**
 * Helper: Get access token from localStorage/cookies
 */
function getAccessToken(): string {
  // TODO: Implement based on your auth system
  return localStorage.getItem('access_token') || ''
}
```

### Step 3: TaskCard Component (1 hour)

**File**: `frontend/dashboard/components/task/TaskCard.tsx`

**Features**:
- Draggable with react-beautiful-dnd
- Priority color-coded border and badge
- Patient name link to detail page
- Alert indicator (🔔) if related_alert_id exists
- Due date with overdue warning (🚨)
- Quick action buttons (Start | Complete)
- Hover effects and animations

**Key Props**:
```typescript
interface TaskCardProps {
  task: Task
  onStart: (taskId: string) => Promise<void>
  onComplete: (taskId: string) => Promise<void>
  onClick?: (task: Task) => void
}
```

### Step 4: TaskColumn Component (45 min)

**File**: `frontend/dashboard/components/task/TaskColumn.tsx`

**Features**:
- Droppable zone with react-beautiful-dnd
- Column header with task count badge
- Empty state when no tasks
- Scrollable task list
- Loading skeleton

**Key Props**:
```typescript
interface TaskColumnProps {
  title: string
  status: TaskStatus
  tasks: Task[]
  onTaskStart: (taskId: string) => Promise<void>
  onTaskComplete: (taskId: string) => Promise<void>
}
```

### Step 5: TaskBoard Component (1.5 hours)

**File**: `frontend/dashboard/components/task/TaskBoard.tsx`

**Features**:
- 3-column Kanban layout (TODO | IN_PROGRESS | DONE)
- Drag-and-drop task status updates
- Real-time task filtering
- Auto-refresh on drag-drop success
- Error handling with toast notifications
- Optimistic UI updates

**Key Props**:
```typescript
interface TaskBoardProps {
  patientId: string
  initialFilters?: TaskFilters
}
```

### Step 6: Integration with Patient Detail Page (30 min)

**File**: `frontend/dashboard/app/patients/[id]/page.tsx`

Add TaskBoard as a new tab in PatientTabs:

```typescript
// Add to PatientTabs.tsx tabs array
{
  id: 'tasks' as TabId,
  label: '臨床任務',
  icon: '📋',
  count: null, // Count will be displayed by TaskBoard
}

// Add TasksTab component
function TasksTab({ patientId }: { patientId: string }) {
  return (
    <div>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900">
          臨床任務管理
        </h3>
        <p className="text-sm text-gray-600 mt-1">
          拖拽任務卡片以更新狀態 (TODO → 進行中 → 完成)
        </p>
      </div>

      <TaskBoard patientId={patientId} />
    </div>
  )
}
```

---

## 🎯 Drag-and-Drop Implementation

### react-beautiful-dnd Setup

```typescript
import { DragDropContext, Droppable, Draggable, DropResult } from 'react-beautiful-dnd'

function TaskBoard({ patientId }: TaskBoardProps) {
  const [tasks, setTasks] = useState<Task[]>([])

  const handleDragEnd = async (result: DropResult) => {
    if (!result.destination) return

    const { draggableId: taskId, destination } = result
    const newStatus = destination.droppableId as TaskStatus

    // Optimistic UI update
    setTasks(prev =>
      prev.map(task =>
        task.task_id === taskId ? { ...task, status: newStatus } : task
      )
    )

    try {
      // API call based on status transition
      if (newStatus === TaskStatus.IN_PROGRESS) {
        await startTask(taskId)
      } else if (newStatus === TaskStatus.DONE) {
        await completeTask(taskId)
      }

      // Refresh task list
      await refetchTasks()
    } catch (error) {
      // Revert on error
      await refetchTasks()
      toast.error('Failed to update task status')
    }
  }

  return (
    <DragDropContext onDragEnd={handleDragEnd}>
      {/* 3 columns: TODO, IN_PROGRESS, DONE */}
      {Object.values(TaskStatus)
        .filter(status => status !== TaskStatus.CANCELLED)
        .map(status => (
          <TaskColumn
            key={status}
            status={status}
            tasks={tasks.filter(task => task.status === status)}
          />
        ))}
    </DragDropContext>
  )
}
```

---

## ⚡ Performance Optimizations

1. **Virtual Scrolling**: If task count > 50 per column, use `react-virtual`
2. **Memoization**: Use `React.memo` for TaskCard to prevent re-renders
3. **Debounced Filtering**: Debounce filter changes by 300ms
4. **Optimistic Updates**: Update UI immediately, revert on API failure
5. **Pagination**: Load 20 tasks per page, infinite scroll for more

---

## ✅ Acceptance Criteria

### Must Have (P0)
- [ ] Display 3-column Kanban board (TODO | IN_PROGRESS | DONE)
- [ ] Drag-and-drop task status updates
- [ ] Priority color-coded badges (CRITICAL → LOW)
- [ ] Overdue task indicators (🚨 red badge)
- [ ] Click card to view task details
- [ ] Quick actions: Start task, Complete task
- [ ] Filter by priority, type, overdue status
- [ ] Real-time task count badges per column

### Nice to Have (P1)
- [ ] Task detail modal with full description
- [ ] Edit task inline
- [ ] Batch actions (Complete all, Reassign)
- [ ] Task history timeline
- [ ] Export task list to CSV

### Future Enhancements (P2)
- [ ] Real-time updates via WebSocket
- [ ] Task assignment to other therapists
- [ ] Task templates for common workflows
- [ ] Analytics dashboard (completion rate, avg time)

---

## 🧪 Testing Strategy

### Unit Tests
- [ ] TaskCard renders correctly with all priority levels
- [ ] TaskColumn filters tasks by status
- [ ] API client handles errors gracefully

### Integration Tests
- [ ] Drag-and-drop updates task status via API
- [ ] Filter controls correctly filter task list
- [ ] Overdue indicator shows for past due dates

### E2E Tests
- [ ] Therapist can drag task from TODO to IN_PROGRESS
- [ ] Therapist can complete task by dragging to DONE
- [ ] Filter by CRITICAL priority shows only critical tasks

---

## 📊 Estimated Timeline

| Task | Estimated Time | Priority |
|------|---------------|----------|
| TypeScript type definitions | 30 min | P0 |
| API client functions | 45 min | P0 |
| TaskCard component | 1 hour | P0 |
| TaskColumn component | 45 min | P0 |
| TaskBoard main component | 1.5 hours | P0 |
| Integration with patient page | 30 min | P0 |
| **Total MVP** | **4 hours 30 min** | **P0** |
| Task filters component | 30 min | P1 |
| Task detail modal | 1 hour | P1 |
| E2E testing | 1 hour | P1 |
| **Total with P1** | **7 hours** | - |

---

## 📝 Implementation Checklist

### Phase 1: Foundation (P0)
- [ ] Create `lib/types/task.ts` with TypeScript definitions
- [ ] Create `lib/api/tasks.ts` with API client functions
- [ ] Create `components/task/TaskCard.tsx` component
- [ ] Create `components/task/TaskColumn.tsx` component
- [ ] Create `components/task/TaskBoard.tsx` component
- [ ] Add TaskBoard to PatientTabs in patient detail page
- [ ] Test drag-and-drop functionality
- [ ] Commit and push to `feature/task-board-ui` branch

### Phase 2: Enhancements (P1)
- [ ] Create `components/task/TaskBoardFilters.tsx`
- [ ] Add task detail modal
- [ ] Add inline task editing
- [ ] Add E2E tests

### Phase 3: Quality & Polish (P2)
- [ ] Add loading skeletons
- [ ] Add error boundaries
- [ ] Add performance optimizations
- [ ] Add accessibility (ARIA labels, keyboard navigation)

---

## 🎯 Success Metrics

- ✅ Task status can be updated via drag-and-drop in < 500ms
- ✅ Task Board loads in < 2 seconds for 50 tasks
- ✅ Zero-downtime during status updates (optimistic UI)
- ✅ 100% API integration coverage
- ✅ Mobile responsive (works on iPad and above)

---

## 📚 References

- **Task API Router**: `backend/src/respira_ally/api/v1/routers/task.py`
- **Task Schemas**: `backend/src/respira_ally/core/schemas/task.py`
- **Alert UI Pattern**: `frontend/dashboard/components/alert/AlertList.tsx`
- **react-beautiful-dnd Docs**: https://github.com/atlassian/react-beautiful-dnd

---

**Ready for Implementation** ✅

**Next Step**: Start with Phase 1 - Foundation (TypeScript types + API client)

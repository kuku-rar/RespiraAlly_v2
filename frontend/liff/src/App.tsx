import { useState } from 'react'

function App() {
  const [count, setCount] = useState(0)

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-6">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-foreground mb-2">
            RespiraAlly LIFF
          </h1>
          <p className="text-xl text-muted-foreground">
            COPD 健康管理
          </p>
        </div>

        <div className="bg-card p-6 rounded-lg shadow-md space-y-4">
          <h2 className="text-2xl font-semibold">系統狀態</h2>
          <div className="space-y-2">
            <div className="flex items-center">
              <span className="text-green-500 mr-2">●</span>
              <span>Vite + React 18 - Ready</span>
            </div>
            <div className="flex items-center">
              <span className="text-green-500 mr-2">●</span>
              <span>Tailwind CSS - Ready</span>
            </div>
            <div className="flex items-center">
              <span className="text-green-500 mr-2">●</span>
              <span>TypeScript - Ready</span>
            </div>
            <div className="flex items-center">
              <span className="text-yellow-500 mr-2">●</span>
              <span>LIFF SDK - Pending</span>
            </div>
          </div>

          <div className="pt-4 border-t">
            <button
              onClick={() => setCount((count) => count + 1)}
              className="w-full bg-primary text-primary-foreground px-6 py-4 rounded-lg font-medium text-lg hover:opacity-90 transition-opacity"
            >
              測試按鈕 {count}
            </button>
            <p className="text-sm text-muted-foreground mt-2 text-center">
              Elder-First 設計：大按鈕 (44px)、大字體 (18px)
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

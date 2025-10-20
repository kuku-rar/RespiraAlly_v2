export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold mb-4">
          RespiraAlly Dashboard
        </h1>
        <p className="text-xl text-muted-foreground mb-8">
          呼吸治療管理系統
        </p>
        <div className="bg-card p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4">系統狀態</h2>
          <div className="space-y-2">
            <div className="flex items-center">
              <span className="text-green-500 mr-2">●</span>
              <span>Next.js 14 App Router - Ready</span>
            </div>
            <div className="flex items-center">
              <span className="text-green-500 mr-2">●</span>
              <span>Tailwind CSS - Ready</span>
            </div>
            <div className="flex items-center">
              <span className="text-green-500 mr-2">●</span>
              <span>TypeScript - Ready</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}

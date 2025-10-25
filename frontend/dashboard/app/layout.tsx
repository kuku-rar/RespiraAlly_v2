// app/layout.tsx
import type { Metadata } from 'next'
import { Inter, Noto_Sans_TC } from 'next/font/google'
import './globals.css'
import { QueryProvider } from '@/providers/QueryProvider'

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

const notoSansTC = Noto_Sans_TC({
  // ⬅️ CJK 字型沒有 subset，需要禁用 preload
  weight: ['300', '400', '500', '700'],
  variable: '--font-noto-sans-tc',
  display: 'swap',
  preload: false, // 禁用 preload 以支援 CJK 字型
})

export const metadata: Metadata = {
  title: 'RespiraAlly Dashboard - 呼吸治療管理系統',
  description: 'COPD 病患健康管理儀表板 - 為呼吸治療師提供專業的個案管理工具',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-TW">
      {/* 只把 CSS 變數掛在 body，用 Tailwind 把它們串到 font-family */}
      <body className={`${inter.variable} ${notoSansTC.variable}`}>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  )
}
import type { Metadata } from 'next'
import { Inter, Noto_Sans_TC } from 'next/font/google'
import './globals.css'
import { QueryProvider } from '@/providers/QueryProvider'

// Load Inter for Latin characters
const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
})

// Load Noto Sans TC for Traditional Chinese characters
const notoSansTC = Noto_Sans_TC({
  subsets: ['latin'],
  weight: ['300', '400', '500', '700'],
  variable: '--font-noto-sans-tc',
  display: 'swap',
})

export const metadata: Metadata = {
  title: 'RespiraAlly Dashboard - 呼吸治療管理系統',
  description: 'COPD 病患健康管理儀表板 - 為呼吸治療師提供專業的個案管理工具',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-TW">
      <body className={`${inter.variable} ${notoSansTC.variable} font-sans`}>
        <QueryProvider>{children}</QueryProvider>
      </body>
    </html>
  )
}

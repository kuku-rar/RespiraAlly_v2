/**
 * TanStack Query Provider Component
 * Wraps the app with QueryClientProvider and DevTools
 */

'use client'

import { QueryClientProvider } from '@tanstack/react-query'
import { queryClient } from '@/lib/query-client'
import dynamic from 'next/dynamic'

interface QueryProviderProps {
  children: React.ReactNode
}

// Dynamically import ReactQueryDevtools with SSR disabled
// This prevents the module from being included in the production bundle
const ReactQueryDevtools = dynamic(
  () =>
    import('@tanstack/react-query-devtools').then((d) => ({
      default: d.ReactQueryDevtools,
    })),
  {
    ssr: false,
    // Only load in development
    loading: () => null,
  }
)

export function QueryProvider({ children }: QueryProviderProps) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      {/* React Query DevTools - only shows in development */}
      {process.env.NODE_ENV === 'development' && (
        <ReactQueryDevtools initialIsOpen={false} buttonPosition="bottom-right" />
      )}
    </QueryClientProvider>
  )
}

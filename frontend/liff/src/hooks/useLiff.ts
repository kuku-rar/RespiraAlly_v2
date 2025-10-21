/**
 * useLiff Hook - LINE LIFF SDK Integration
 * Handles LIFF initialization and profile fetching
 */

import { useState, useEffect } from 'react'
import liff from '@line/liff'
import type { LiffProfile } from '../types/auth'

const LIFF_ID = import.meta.env.VITE_LIFF_ID || 'mock_liff_id_12345'
const IS_MOCK_MODE = import.meta.env.VITE_MOCK_MODE === 'true'

// Mock profile for development
const MOCK_PROFILE: LiffProfile = {
  userId: 'Umock1234567890abcdefghijklmnopqr',
  displayName: '測試病患',
  pictureUrl: 'https://via.placeholder.com/150',
  statusMessage: 'Hello from mock!',
}

export interface UseLiffReturn {
  isReady: boolean
  isLoggedIn: boolean
  profile: LiffProfile | null
  error: string | null
  login: () => void
  logout: () => void
}

export const useLiff = (): UseLiffReturn => {
  const [isReady, setIsReady] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [profile, setProfile] = useState<LiffProfile | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const initLiff = async () => {
      try {
        // Mock mode: skip LIFF initialization
        if (IS_MOCK_MODE) {
          console.log('[MOCK] LIFF initialized with mock data')
          setIsReady(true)
          setIsLoggedIn(true)
          setProfile(MOCK_PROFILE)
          return
        }

        // Real LIFF initialization
        await liff.init({ liffId: LIFF_ID })
        setIsReady(true)

        // Check if user is logged in
        if (liff.isLoggedIn()) {
          setIsLoggedIn(true)

          // Get user profile
          const userProfile = await liff.getProfile()
          setProfile({
            userId: userProfile.userId,
            displayName: userProfile.displayName,
            pictureUrl: userProfile.pictureUrl,
            statusMessage: userProfile.statusMessage,
          })
        } else {
          setIsLoggedIn(false)
        }
      } catch (err) {
        console.error('LIFF initialization failed:', err)
        setError(err instanceof Error ? err.message : 'LIFF 初始化失敗')
      }
    }

    initLiff()
  }, [])

  const login = () => {
    if (IS_MOCK_MODE) {
      console.log('[MOCK] LIFF login triggered')
      setIsLoggedIn(true)
      setProfile(MOCK_PROFILE)
      return
    }

    if (!liff.isLoggedIn()) {
      liff.login()
    }
  }

  const logout = () => {
    if (IS_MOCK_MODE) {
      console.log('[MOCK] LIFF logout triggered')
      setIsLoggedIn(false)
      setProfile(null)
      return
    }

    if (liff.isLoggedIn()) {
      liff.logout()
      window.location.reload()
    }
  }

  return {
    isReady,
    isLoggedIn,
    profile,
    error,
    login,
    logout,
  }
}

/**
 * useTTS Hook - Text-to-Speech using Web Speech API
 *
 * Simplified TTS solution for elderly-friendly accessibility
 * Based on ADR-011: TTS Implementation Simplification
 *
 * Features:
 * - ✅ Traditional Chinese (zh-TW) support
 * - ✅ Elderly-friendly speech rate (0.9x)
 * - ✅ Browser compatibility check
 * - ✅ Play, pause, stop controls
 * - ✅ Speaking state management
 *
 * Browser Support:
 * - iOS Safari 14+ ✅
 * - Android Chrome 90+ ✅
 * - Desktop Chrome/Edge ✅
 *
 * Sprint 3 Task 5.3.1.2 - Week 6 Day 1
 */

import { useState, useEffect, useCallback, useRef } from 'react'

export interface UseTTSOptions {
  /** Speech language (default: zh-TW) */
  lang?: string
  /** Speech rate (default: 0.9 for elderly-friendly) */
  rate?: number
  /** Pitch (default: 1.0) */
  pitch?: number
  /** Volume (default: 1.0) */
  volume?: number
}

export interface UseTTSReturn {
  /** Whether Web Speech API is supported */
  isSupported: boolean
  /** Whether TTS is currently speaking */
  isSpeaking: boolean
  /** Whether TTS is paused */
  isPaused: boolean
  /** Speak the provided text */
  speak: (text: string) => void
  /** Pause current speech */
  pause: () => void
  /** Resume paused speech */
  resume: () => void
  /** Stop current speech */
  stop: () => void
  /** Error message if any */
  error: string | null
}

export const useTTS = (options: UseTTSOptions = {}): UseTTSReturn => {
  const {
    lang = 'zh-TW',
    rate = 0.9, // Elderly-friendly: slower speech
    pitch = 1.0,
    volume = 1.0,
  } = options

  // State
  const [isSupported, setIsSupported] = useState<boolean>(false)
  const [isSpeaking, setIsSpeaking] = useState<boolean>(false)
  const [isPaused, setIsPaused] = useState<boolean>(false)
  const [error, setError] = useState<string | null>(null)

  // Refs to store SpeechSynthesisUtterance instances
  const currentUtteranceRef = useRef<SpeechSynthesisUtterance | null>(null)

  // Check browser support on mount
  useEffect(() => {
    const supported = 'speechSynthesis' in window && 'SpeechSynthesisUtterance' in window
    setIsSupported(supported)

    if (!supported) {
      setError('此瀏覽器不支援語音朗讀功能 (Web Speech API)')
      console.warn('[useTTS] Web Speech API not supported in this browser')
    } else {
      console.log('[useTTS] Web Speech API supported ✅')
    }

    // Cleanup on unmount
    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.cancel()
      }
    }
  }, [])

  /**
   * Speak the provided text
   */
  const speak = useCallback(
    (text: string) => {
      if (!isSupported) {
        console.warn('[useTTS] Cannot speak: Web Speech API not supported')
        setError('您的瀏覽器不支援語音朗讀，但仍可正常填寫問卷')
        return
      }

      if (!text || text.trim().length === 0) {
        console.warn('[useTTS] Cannot speak: Empty text provided')
        return
      }

      try {
        // Cancel any ongoing speech
        window.speechSynthesis.cancel()

        // Create new utterance
        const utterance = new SpeechSynthesisUtterance(text)

        // Configure utterance
        utterance.lang = lang
        utterance.rate = rate
        utterance.pitch = pitch
        utterance.volume = volume

        // Event handlers
        utterance.onstart = () => {
          console.log('[useTTS] Speech started')
          setIsSpeaking(true)
          setIsPaused(false)
          setError(null)
        }

        utterance.onend = () => {
          console.log('[useTTS] Speech ended')
          setIsSpeaking(false)
          setIsPaused(false)
          currentUtteranceRef.current = null
        }

        utterance.onpause = () => {
          console.log('[useTTS] Speech paused')
          setIsPaused(true)
        }

        utterance.onresume = () => {
          console.log('[useTTS] Speech resumed')
          setIsPaused(false)
        }

        utterance.onerror = (event) => {
          console.error('[useTTS] Speech error:', event.error)
          setError(`語音朗讀發生錯誤: ${event.error}`)
          setIsSpeaking(false)
          setIsPaused(false)
          currentUtteranceRef.current = null
        }

        // Store current utterance
        currentUtteranceRef.current = utterance

        // Start speaking
        window.speechSynthesis.speak(utterance)

      } catch (err) {
        console.error('[useTTS] Error creating speech:', err)
        setError(err instanceof Error ? err.message : '語音朗讀發生未知錯誤')
        setIsSpeaking(false)
        setIsPaused(false)
      }
    },
    [isSupported, lang, rate, pitch, volume]
  )

  /**
   * Pause current speech
   */
  const pause = useCallback(() => {
    if (!isSupported) return

    if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
      window.speechSynthesis.pause()
      console.log('[useTTS] Paused speech')
    }
  }, [isSupported])

  /**
   * Resume paused speech
   */
  const resume = useCallback(() => {
    if (!isSupported) return

    if (window.speechSynthesis.paused) {
      window.speechSynthesis.resume()
      console.log('[useTTS] Resumed speech')
    }
  }, [isSupported])

  /**
   * Stop current speech
   */
  const stop = useCallback(() => {
    if (!isSupported) return

    if (window.speechSynthesis.speaking || window.speechSynthesis.pending) {
      window.speechSynthesis.cancel()
      setIsSpeaking(false)
      setIsPaused(false)
      currentUtteranceRef.current = null
      console.log('[useTTS] Stopped speech')
    }
  }, [isSupported])

  return {
    isSupported,
    isSpeaking,
    isPaused,
    speak,
    pause,
    resume,
    stop,
    error,
  }
}

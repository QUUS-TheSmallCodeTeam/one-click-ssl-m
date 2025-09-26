'use client'

import Link from 'next/link'
import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'

export default function AuthCodeError() {
  const [isProcessing, setIsProcessing] = useState(true)
  const [isSuccess, setIsSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const processAuthFragment = async () => {
      try {
        // Check if there's an access token in the URL fragment
        const fragment = window.location.hash.substring(1)
        const params = new URLSearchParams(fragment)
        const accessToken = params.get('access_token')
        const refreshToken = params.get('refresh_token')

        console.log('=== AUTH FRAGMENT PROCESSING ===')
        console.log('fragment:', fragment)
        console.log('accessToken exists:', !!accessToken)

        if (accessToken) {
          console.log('Processing implicit OAuth flow tokens')
          const supabase = createClient()

          // Set session using the tokens from URL fragment
          const { error } = await supabase.auth.setSession({
            access_token: accessToken,
            refresh_token: refreshToken || ''
          })

          if (error) {
            console.error('Failed to set session:', error)
            setError('토큰 설정 중 오류가 발생했습니다.')
          } else {
            console.log('Session set successfully')
            setIsSuccess(true)

            // Check if opened from iframe
            const isFromIframe = window.opener && window.opener !== window
            if (isFromIframe) {
              console.log('Opened from iframe, notifying and closing')
              // Try to notify parent iframe (may not work due to cross-origin)
              try {
                if (window.opener) {
                  window.opener.location.reload()
                }
              } catch (e) {
                console.log('Could not reload opener:', e)
              }

              // Close this window immediately for iframe context
              setTimeout(() => {
                window.close()
              }, 1000)
            } else {
              // If not from iframe, auto-redirect to home after 2 seconds
              setTimeout(() => {
                window.location.href = '/'
              }, 2000)
            }
          }
        } else {
          console.log('No access token found in URL fragment')
          setError('Google 로그인 중 오류가 발생했습니다.')
        }
      } catch (err) {
        console.error('Error processing auth fragment:', err)
        setError('인증 처리 중 오류가 발생했습니다.')
      } finally {
        setIsProcessing(false)
      }
    }

    processAuthFragment()
  }, [])

  if (isProcessing) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="text-6xl mb-6">⏳</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">로그인 처리 중</h1>
          <p className="text-gray-600 mb-6">
            Google 로그인을 처리하고 있습니다...
          </p>
        </div>
      </div>
    )
  }

  if (isSuccess) {
    const isFromIframe = typeof window !== 'undefined' && window.opener && window.opener !== window

    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="text-6xl mb-6">✅</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-4">로그인 완료!</h1>
          <p className="text-gray-600 mb-6">
            성공적으로 로그인되었습니다.
            {isFromIframe
              ? ' 이 창은 1초 후 자동으로 닫힙니다.'
              : ' 2초 후 자동으로 홈으로 이동합니다.'}
          </p>
          <div className="text-sm text-gray-500">
            {isFromIframe
              ? '원본 탭에서 새로고침을 확인해주세요.'
              : '잠시만 기다려주세요...'}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-rose-100 flex items-center justify-center">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="text-6xl mb-6">⚠️</div>
        <h1 className="text-2xl font-bold text-gray-900 mb-4">로그인 오류</h1>
        <p className="text-gray-600 mb-6">
          {error || 'Google 로그인 중 오류가 발생했습니다. 다시 시도해 주세요.'}
        </p>
        <Link
          href="/"
          className="inline-block bg-red-600 text-white px-6 py-3 rounded-lg hover:bg-red-700 transition-colors"
        >
          홈으로 돌아가기
        </Link>
      </div>
    </div>
  )
}
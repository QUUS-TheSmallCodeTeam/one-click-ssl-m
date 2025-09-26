'use client'

import { createClient } from '@/lib/supabase/client'
import { type User } from '@supabase/supabase-js'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'

export default function AuthButton() {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const router = useRouter()
  const supabase = createClient()

  useEffect(() => {
    const getUser = async () => {
      const { data: { session } } = await supabase.auth.getSession()
      setUser(session?.user ?? null)
      setLoading(false)
    }

    getUser()

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null)
      setLoading(false)
    })

    // Listen for OAuth success from popup window
    const handleMessage = (event: MessageEvent) => {
      if (event.data?.type === 'OAUTH_SUCCESS') {
        console.log('Received OAuth success message from popup')
        // Refresh user session
        getUser()
      }
    }

    // Listen for localStorage changes (OAuth success from popup)
    const handleStorageChange = async (e: StorageEvent) => {
      if (e.key === 'oauth_success' && e.newValue === 'true') {
        console.log('OAuth success detected via localStorage, setting session in iframe')

        const accessToken = localStorage.getItem('supabase_access_token')
        const refreshToken = localStorage.getItem('supabase_refresh_token')

        if (accessToken) {
          try {
            // Set session in iframe using tokens from popup
            const { error } = await supabase.auth.setSession({
              access_token: accessToken,
              refresh_token: refreshToken || ''
            })

            if (error) {
              console.error('Failed to set session in iframe:', error)
            } else {
              console.log('Session successfully set in iframe')
              // Clean up stored tokens
              localStorage.removeItem('oauth_success')
              localStorage.removeItem('oauth_timestamp')
              localStorage.removeItem('supabase_access_token')
              localStorage.removeItem('supabase_refresh_token')

              // Refresh user state
              getUser()
            }
          } catch (err) {
            console.error('Error setting session in iframe:', err)
          }
        }
      }
    }

    window.addEventListener('message', handleMessage)
    window.addEventListener('storage', handleStorageChange)

    return () => {
      subscription.unsubscribe()
      window.removeEventListener('message', handleMessage)
      window.removeEventListener('storage', handleStorageChange)
    }
  }, [supabase.auth])

  const handleSignIn = async () => {
    console.log('=== OAUTH START DEBUG ===')
    console.log('window.location.origin:', window.location.origin)
    console.log('window.location.href:', window.location.href)
    console.log('window.parent === window:', window.parent === window)
    console.log('window.top === window:', window.top === window)

    // Check if we're in an iframe
    const isInIframe = window.parent !== window || window.top !== window

    if (isInIframe) {
      // If in iframe, open OAuth in new tab and set up listener for success
      const authUrl = `${process.env.NEXT_PUBLIC_SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to=${encodeURIComponent(window.location.origin + '/auth/callback?iframe=true')}`
      console.log('Opening OAuth URL in new window:', authUrl)

      const newWindow = window.open(authUrl, '_blank')
      if (newWindow) {
        newWindow.focus()

        // Listen for storage events to detect login success
        const handleStorageChange = (e: StorageEvent) => {
          if (e.key === 'supabase.auth.token' && e.newValue) {
            console.log('Auth token detected in storage, refreshing iframe')
            window.removeEventListener('storage', handleStorageChange)
            // Force refresh the current iframe content
            setTimeout(() => {
              window.location.reload()
            }, 1000)
          }
        }

        window.addEventListener('storage', handleStorageChange)

        // Clean up listener after 5 minutes
        setTimeout(() => {
          window.removeEventListener('storage', handleStorageChange)
        }, 300000)
      }
      return
    }

    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: `${window.location.origin}/auth/callback`,
      }
    })
    if (error) {
      console.error('Error signing in:', error.message)
    }
  }

  const handleSignOut = async () => {
    const { error } = await supabase.auth.signOut()
    if (error) {
      console.error('Error signing out:', error.message)
    } else {
      router.refresh()
    }
  }

  if (loading) {
    return (
      <div className="flex items-center space-x-2">
        <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <span className="text-sm text-gray-600">로딩 중...</span>
      </div>
    )
  }

  if (user) {
    return (
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          {user.user_metadata?.avatar_url && (
            // eslint-disable-next-line @next/next/no-img-element
            <img
              src={user.user_metadata.avatar_url}
              alt="Profile"
              className="w-8 h-8 rounded-full"
            />
          )}
          <span className="text-sm font-medium text-gray-700">
            {user.user_metadata?.full_name || user.email}
          </span>
        </div>
        <button
          onClick={handleSignOut}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          로그아웃
        </button>
      </div>
    )
  }

  // Check if we're in an iframe for button text
  const isInIframe = typeof window !== 'undefined' && (window.parent !== window || window.top !== window)

  return (
    <button
      onClick={handleSignIn}
      className="flex items-center space-x-2 px-4 py-2 bg-white border border-gray-300 rounded-lg shadow-sm hover:shadow-md transition-all duration-200 text-gray-700 hover:text-gray-900"
    >
      <svg className="w-5 h-5" viewBox="0 0 24 24">
        <path
          fill="currentColor"
          d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
        />
        <path
          fill="currentColor"
          d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
        />
        <path
          fill="currentColor"
          d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
        />
        <path
          fill="currentColor"
          d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
        />
      </svg>
      <span className="text-sm font-medium">
        {isInIframe ? '새 창에서 Google 로그인' : 'Google로 로그인'}
      </span>
    </button>
  )
}
'use client'

import { useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'

export default function PopupHandler() {
  useEffect(() => {
    // Check if this window was opened as a popup
    const isPopup = window.opener && window.opener !== window

    if (isPopup) {
      console.log('Detected popup window, checking auth status')

      const checkAuthAndNotify = async () => {
        const supabase = createClient()
        const { data: { session } } = await supabase.auth.getSession()

        if (session) {
          console.log('User is authenticated in popup, sending success message')

          // Send success message to opener (iframe)
          try {
            window.opener.postMessage({ type: 'AUTH_SUCCESS' }, '*')
            console.log('Sent AUTH_SUCCESS message to opener')
          } catch (e) {
            console.error('Failed to send postMessage:', e)
          }

          // Auto-close popup after delay
          setTimeout(() => {
            console.log('Auto-closing popup window')
            window.close()

            // If window.close() fails, show manual instruction
            setTimeout(() => {
              if (!window.closed) {
                alert('로그인이 완료되었습니다. 이 창을 닫고 원본 탭으로 돌아가세요.')
              }
            }, 500)
          }, 1500)
        } else {
          console.log('No session found in popup')
        }
      }

      // Check immediately and after a short delay
      checkAuthAndNotify()
      setTimeout(checkAuthAndNotify, 1000)
    }
  }, [])

  return null // This component has no UI
}
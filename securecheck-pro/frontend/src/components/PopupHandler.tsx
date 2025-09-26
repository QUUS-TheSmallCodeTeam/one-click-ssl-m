'use client'

import { useEffect } from 'react'
import { createClient } from '@/lib/supabase/client'

export default function PopupHandler() {
  useEffect(() => {
    // Check if this window was opened as a popup (multiple detection methods)
    const hasOpener = window.opener && window.opener !== window
    const hasReferrer = document.referrer && document.referrer.includes('huggingface.co')
    const isNewWindow = window.history.length === 1
    const hasAuthFragment = window.location.hash.includes('access_token')

    const isPopup = hasOpener || (hasReferrer && isNewWindow && hasAuthFragment)

    console.log('=== POPUP DETECTION ===')
    console.log('hasOpener:', hasOpener)
    console.log('hasReferrer:', hasReferrer)
    console.log('isNewWindow:', isNewWindow)
    console.log('isPopup:', isPopup)

    if (isPopup) {
      console.log('Detected popup window, checking auth status')

      const checkAuthAndNotify = async () => {
        try {
          // Request storage access to share cookies with iframe
          if ('requestStorageAccess' in document) {
            console.log('Popup requesting storage access')
            await document.requestStorageAccess()
            console.log('Popup storage access granted')
          }
        } catch (error) {
          console.log('Popup storage access denied:', error)
        }

        const supabase = createClient()
        const { data: { session } } = await supabase.auth.getSession()

        if (session) {
          console.log('User is authenticated in popup, sending success message')

          // Send auth tokens to opener (iframe) via postMessage
          try {
            const sessionData = {
              type: 'AUTH_SUCCESS',
              session: session
            }
            window.opener.postMessage(sessionData, '*')
            console.log('Sent AUTH_SUCCESS with session to opener')
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
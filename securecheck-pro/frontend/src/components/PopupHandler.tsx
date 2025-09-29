'use client'

import { useEffect } from 'react'

export default function PopupHandler() {
  useEffect(() => {
    // Simple popup detection - only for debugging now
    // The actual popup handling is done in the callback route
    const hasOpener = window.opener && window.opener !== window
    const hasReferrer = document.referrer && document.referrer.includes('huggingface.co')
    const hasAuthFragment = window.location.hash.includes('access_token')

    console.log('=== POPUP HANDLER DEBUG ===')
    console.log('hasOpener:', hasOpener)
    console.log('hasReferrer:', hasReferrer)
    console.log('hasAuthFragment:', hasAuthFragment)
    console.log('Current URL:', window.location.href)

    // Note: Actual popup auth handling is now done in /auth/callback route
    // This component is kept for debugging and future enhancements
  }, [])

  return null // This component has no UI
}
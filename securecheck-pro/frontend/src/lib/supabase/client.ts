import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  // If using placeholder values, throw error to prevent usage
  if (!supabaseUrl || !supabaseAnonKey ||
      supabaseUrl === 'https://placeholder.supabase.co' ||
      supabaseAnonKey === 'placeholder_key') {
    throw new Error('Supabase configuration not properly set up. Please configure secrets in Hugging Face Spaces settings.')
  }

  // Check if we're in an iframe (different domain context)
  const isInIframe = typeof window !== 'undefined' && (window.parent !== window || window.top !== window)

  if (isInIframe) {
    // For iframe environments, use localStorage for session persistence
    return createBrowserClient(supabaseUrl, supabaseAnonKey, {
      auth: {
        storageKey: 'supabase.auth.token.iframe',
        storage: {
          getItem: (key: string) => {
            if (typeof window === 'undefined') return null
            return localStorage.getItem(key)
          },
          setItem: (key: string, value: string) => {
            if (typeof window === 'undefined') return
            localStorage.setItem(key, value)
          },
          removeItem: (key: string) => {
            if (typeof window === 'undefined') return
            localStorage.removeItem(key)
          },
        },
      },
    })
  }

  return createBrowserClient(supabaseUrl, supabaseAnonKey)
}
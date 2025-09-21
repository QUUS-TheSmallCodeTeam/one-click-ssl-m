import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()

  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  // If using placeholder values (build-time), use actual values for production
  const actualUrl = supabaseUrl === 'https://placeholder.supabase.co' ?
    'https://lbuvfygrcosdzhgppqba.supabase.co' : supabaseUrl

  const actualKey = supabaseAnonKey === 'placeholder_key' ?
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxidXZmeWdyY29zZHpoZ3BwcWJhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyNjgyOTIsImV4cCI6MjA3Mzg0NDI5Mn0.f3lGUXsrXFoUd1HjmkbvpbRroqbIAxxi8ZVSRKLVg58' : supabaseAnonKey

  if (!actualUrl || !actualKey) {
    throw new Error('Missing Supabase environment variables')
  }

  return createServerClient(
    actualUrl,
    actualKey,
    {
      cookies: {
        getAll() {
          return cookieStore.getAll()
        },
        setAll(cookiesToSet) {
          try {
            cookiesToSet.forEach(({ name, value, options }) =>
              cookieStore.set(name, value, options)
            )
          } catch {
            // The `setAll` method was called from a Server Component.
            // This can be ignored if you have middleware refreshing
            // user sessions.
          }
        },
      },
    }
  )
}
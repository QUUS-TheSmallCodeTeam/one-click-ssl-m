import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  // Check if we're running with actual env vars or placeholders
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL
  const supabaseAnonKey = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY

  console.log('Supabase URL:', supabaseUrl)
  console.log('Supabase Key exists:', !!supabaseAnonKey)

  // If using placeholder values (build-time), use actual values for production
  const actualUrl = supabaseUrl === 'https://placeholder.supabase.co' ?
    'https://lbuvfygrcosdzhgppqba.supabase.co' : supabaseUrl

  const actualKey = supabaseAnonKey === 'placeholder_key' ?
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxidXZmeWdyY29zZHpoZ3BwcWJhIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgyNjgyOTIsImV4cCI6MjA3Mzg0NDI5Mn0.f3lGUXsrXFoUd1HjmkbvpbRroqbIAxxi8ZVSRKLVg58' : supabaseAnonKey

  if (!actualUrl || !actualKey) {
    throw new Error('Missing Supabase environment variables')
  }

  return createBrowserClient(actualUrl, actualKey)
}
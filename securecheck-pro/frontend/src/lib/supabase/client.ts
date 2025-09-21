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

  return createBrowserClient(supabaseUrl, supabaseAnonKey)
}
import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const code = searchParams.get('code')
  // if "next" is in param, use it as the redirect URL
  const next = searchParams.get('next') ?? '/'

  // Get the correct origin from headers instead of URL parsing
  const host = request.headers.get('host')
  const protocol = request.headers.get('x-forwarded-proto') || 'https'
  const correctOrigin = `${protocol}://${host}`

  // Debug logging
  console.log('=== AUTH CALLBACK DEBUG ===')
  console.log('request.url:', request.url)
  console.log('host header:', host)
  console.log('protocol:', protocol)
  console.log('correctOrigin:', correctOrigin)
  console.log('next:', next)
  console.log('NODE_ENV:', process.env.NODE_ENV)

  if (code) {
    const supabase = await createClient()
    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) {
      const redirectUrl = `${correctOrigin}${next}`
      console.log('SUCCESS - Redirecting to:', redirectUrl)
      return NextResponse.redirect(redirectUrl)
    } else {
      console.log('AUTH ERROR:', error)
    }
  } else {
    console.log('NO CODE PARAMETER')
  }

  // return the user to an error page with instructions
  const errorUrl = `${correctOrigin}/auth/auth-code-error`
  console.log('ERROR - Redirecting to:', errorUrl)
  return NextResponse.redirect(errorUrl)
}
import { createClient } from '@/lib/supabase/server'
import { NextResponse } from 'next/server'

export async function GET(request: Request) {
  // Get the correct origin from headers instead of URL parsing
  const host = request.headers.get('host')
  const protocol = request.headers.get('x-forwarded-proto') || 'https'
  const correctOrigin = `${protocol}://${host}`

  // Reconstruct the request URL with correct origin for Supabase
  const originalUrl = new URL(request.url)
  const correctedUrl = new URL(originalUrl.pathname + originalUrl.search, correctOrigin)

  const { searchParams } = correctedUrl
  const code = searchParams.get('code')
  // if "next" is in param, use it as the redirect URL
  const next = searchParams.get('next') ?? '/'

  // Debug logging
  console.log('=== AUTH CALLBACK DEBUG ===')
  console.log('original request.url:', request.url)
  console.log('corrected URL:', correctedUrl.toString())
  console.log('host header:', host)
  console.log('protocol:', protocol)
  console.log('correctOrigin:', correctOrigin)
  console.log('next:', next)
  console.log('NODE_ENV:', process.env.NODE_ENV)

  if (code) {
    // Create a new request with corrected URL for Supabase
    const correctedRequest = new Request(correctedUrl, {
      method: request.method,
      headers: request.headers,
      body: request.body,
    })

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
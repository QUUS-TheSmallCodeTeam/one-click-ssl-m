import { createServerClient } from '@supabase/ssr'
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
  console.log('cookies:', request.headers.get('cookie'))

  if (code) {
    const supabaseResponse = NextResponse.redirect(`${correctOrigin}${next}`)

    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL!,
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
      {
        cookies: {
          getAll() {
            return request.headers.get('cookie')
              ?.split(';')
              ?.map(c => c.trim().split('='))
              ?.map(([name, value]) => ({ name, value: decodeURIComponent(value || '') })) ?? []
          },
          setAll(cookiesToSet) {
            cookiesToSet.forEach(({ name, value, options }) => {
              supabaseResponse.cookies.set(name, value, options)
            })
          },
        },
      }
    )

    const { error } = await supabase.auth.exchangeCodeForSession(code)
    if (!error) {
      console.log('SUCCESS - Redirecting to:', `${correctOrigin}${next}`)
      return supabaseResponse
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
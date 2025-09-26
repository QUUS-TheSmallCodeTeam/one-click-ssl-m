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
  const isFromIframe = searchParams.get('iframe') === 'true'
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
      console.log('SUCCESS - Auth completed')

      if (isFromIframe) {
        // If from iframe, show a success page that closes the window
        const successHtml = `
          <!DOCTYPE html>
          <html>
          <head>
            <title>로그인 완료</title>
            <style>
              body { font-family: Arial, sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; background: #f5f5f5; }
              .success { background: white; padding: 40px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); text-align: center; }
              .success h1 { color: #10b981; margin-bottom: 16px; }
              .success p { color: #666; margin-bottom: 24px; }
              .btn { background: #3b82f6; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; }
            </style>
          </head>
          <body>
            <div class="success">
              <h1>✅ 로그인 완료!</h1>
              <p>성공적으로 로그인되었습니다.<br>원본 탭으로 돌아가서 새로고침해주세요.</p>
              <button class="btn" onclick="window.close()">이 창 닫기</button>
            </div>
            <script>
              // Try to close the window automatically
              setTimeout(() => {
                window.close();
              }, 3000);
            </script>
          </body>
          </html>
        `
        return new Response(successHtml, {
          headers: { 'Content-Type': 'text/html' },
        })
      }

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
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
  const isPopup = searchParams.get('popup') === 'true'
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

      if (isPopup) {
        // If popup mode, get session data and send via multiple channels
        const { data: { session } } = await supabase.auth.getSession()

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
              .log { background: #f8f9fa; border: 1px solid #e9ecef; padding: 16px; margin-top: 20px; border-radius: 4px; font-family: monospace; font-size: 12px; text-align: left; max-height: 200px; overflow-y: auto; }
            </style>
          </head>
          <body>
            <div class="success">
              <h1>✅ 로그인 완료!</h1>
              <p>iframe에 로그인 상태가 반영되었습니다.<br>이 창을 닫아주세요.</p>
              <button class="btn" onclick="window.close()">창 닫기</button>
              <div class="log" id="log"></div>
            </div>
            <script>
              const log = document.getElementById('log');
              const addLog = (message) => {
                const timestamp = new Date().toISOString().split('T')[1].split('.')[0];
                log.innerHTML += timestamp + ': ' + message + '\\n';
                log.scrollTop = log.scrollHeight;
                console.log(message);
              };

              addLog('=== POPUP CALLBACK SCRIPT START ===');

              // Get session data from server
              const sessionData = ${JSON.stringify(session)};
              addLog('Session data received: ' + (sessionData ? 'YES' : 'NO'));

              // Prepare message data
              const messageData = {
                type: 'AUTH_SUCCESS',
                session: sessionData,
                timestamp: Date.now(),
                origin: window.location.origin
              };

              let communicationSuccess = false;

              // Method 1: BroadcastChannel
              const sendViaBroadcastChannel = () => {
                try {
                  const authChannel = new BroadcastChannel('auth_channel');
                  authChannel.postMessage(messageData);
                  addLog('✓ BroadcastChannel message sent');
                  authChannel.close();
                  return true;
                } catch (e) {
                  addLog('✗ BroadcastChannel failed: ' + e.message);
                  return false;
                }
              };

              // Method 2: PostMessage to opener
              const sendViaPostMessage = () => {
                if (window.opener && !window.opener.closed) {
                  try {
                    // Try multiple target origins for iframe contexts
                    const targetOrigins = ['*', 'https://huggingface.co', window.location.origin];

                    targetOrigins.forEach(origin => {
                      window.opener.postMessage(messageData, origin);
                    });

                    addLog('✓ PostMessage sent to opener with multiple origins');
                    return true;
                  } catch (e) {
                    addLog('✗ PostMessage failed: ' + e.message);
                    return false;
                  }
                } else {
                  addLog('✗ No opener window available');
                  return false;
                }
              };

              // Method 3: localStorage as fallback
              const sendViaLocalStorage = () => {
                try {
                  if (sessionData) {
                    localStorage.setItem('oauth_success', 'true');
                    localStorage.setItem('oauth_timestamp', Date.now().toString());
                    localStorage.setItem('supabase_access_token', sessionData.access_token);
                    if (sessionData.refresh_token) {
                      localStorage.setItem('supabase_refresh_token', sessionData.refresh_token);
                    }
                    addLog('✓ Session data stored in localStorage');
                    return true;
                  } else {
                    addLog('✗ No session data to store');
                    return false;
                  }
                } catch (e) {
                  addLog('✗ localStorage failed: ' + e.message);
                  return false;
                }
              };

              // Send via all available methods
              const sendMessage = () => {
                addLog('Attempting to send auth success message...');

                const results = [
                  sendViaBroadcastChannel(),
                  sendViaPostMessage(),
                  sendViaLocalStorage()
                ];

                communicationSuccess = results.some(result => result);

                if (communicationSuccess) {
                  addLog('✓ At least one communication method succeeded');
                } else {
                  addLog('✗ All communication methods failed');
                }

                return communicationSuccess;
              };

              // Retry logic
              let attempts = 0;
              const maxAttempts = 3;
              const retryDelay = 1000;

              const tryMessage = () => {
                attempts++;
                addLog('Attempt ' + attempts + ' of ' + maxAttempts);

                if (sendMessage()) {
                  addLog('Communication successful, scheduling window close');
                  // Auto-close after successful communication
                  setTimeout(() => {
                    addLog('Closing popup window');
                    window.close();
                  }, 2000);
                } else if (attempts < maxAttempts) {
                  addLog('Retrying in ' + retryDelay + 'ms...');
                  setTimeout(tryMessage, retryDelay);
                } else {
                  addLog('Max attempts reached, giving up');
                  setTimeout(() => {
                    alert('로그인이 완료되었습니다. 이 창을 닫고 원본 탭으로 돌아가세요.');
                  }, 1000);
                }
              };

              // Start the process
              addLog('Starting authentication communication process');
              tryMessage();
            </script>
          </body>
          </html>
        `
        return new Response(successHtml, {
          headers: { 'Content-Type': 'text/html' },
        })
      }

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
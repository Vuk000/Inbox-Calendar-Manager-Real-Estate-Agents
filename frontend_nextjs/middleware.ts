import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

/**
 * Middleware for Next.js App Router
 * 
 * Note: Since we use localStorage for auth (client-side only), we cannot
 * check authentication in middleware. All auth checks are handled client-side
 * in the respective page components and layouts.
 * 
 * This middleware only handles route matching and allows all routes through.
 * Client-side components will handle redirects based on auth state.
 */
export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Allow all routes through - client-side handles auth redirects
  // Static files and API routes are automatically excluded by the matcher config
  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\..*|public).*)',
  ],
}


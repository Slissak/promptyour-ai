import createIntlMiddleware from 'next-intl/middleware';
import { routing } from './src/i18n/routing';
import { updateSession } from './src/lib/supabase/middleware';
import { type NextRequest } from 'next/server';

// Create the next-intl middleware
const intlMiddleware = createIntlMiddleware(routing);

export async function middleware(request: NextRequest) {
  // First, handle authentication with Supabase
  const supabaseResponse = await updateSession(request);

  // If Supabase middleware returns a redirect (e.g., to login page),
  // return that response immediately
  if (supabaseResponse.status === 307 || supabaseResponse.status === 308) {
    return supabaseResponse;
  }

  // Otherwise, continue with internationalization middleware
  return intlMiddleware(request);
}

export const config = {
  // Match all pathnames except for
  // - … if they start with `/api`, `/_next` or `/_vercel`
  // - … the ones containing a dot (e.g. `favicon.ico`)
  matcher: ['/((?!api|_next|_vercel|.*\\..*).*)']
};
// Follow this setup guide to integrate the Deno language server with your editor:
// https://deno.land/manual/getting_started/setup_your_environment
// This enables autocomplete, go to definition, etc.

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // 1. Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // 2. Validate Auth (Optional but recommended: Check for Supabase Anon Key)
    // For a more robust auth check, you can verify the JWT token here using `req.headers.get('Authorization')`
    // But since this is a proxy, we'll pass the auth header to the backend if needed,
    // OR relies on the fact that only our valid frontend calls this.
    // A basic check is verifying the API Key presence.
    const authHeader = req.headers.get('Authorization')
    if (!authHeader) {
        // return new Response(JSON.stringify({ error: 'Missing Authorization header' }), { status: 401, headers: { ...corsHeaders, 'Co
    }

    // 3. Get Backend Configuration
    const backendUrl = Deno.env.get('BACKEND_URL')
    const gatewaySecret = Deno.env.get('GATEWAY_SECRET')

    if (!backendUrl || !gatewaySecret) {
      console.error("Missing configuration: BACKEND_URL or GATEWAY_SECRET")
      return new Response(
        JSON.stringify({ error: 'Server misconfiguration' }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // 4. Prepare the Request to Azure Backend
    // We strip the '/functions/v1/chat-proxy' prefix if present and append the rest to the backend URL
    const url = new URL(req.url)
    // The path usually comes in as /functions/v1/chat-proxy/api/v1/chat/message...
    // We want to forward /api/v1/chat/message...
    // Let's construct the target URL carefully.
    
    // Simplification: We assume the client calls this function URL with the exact path needed by the backend appended?
    // Actually, usually clients call the function directly.
    // Let's assume the client sends the target path in a custom header OR we map specific function calls.
    
    // BETTER APPROACH for this specific app:
    // The frontend code calls specific endpoints like `/api/v1/chat/message`.
    // If we change the Base URL in the frontend to the Edge Function URL, the path will be appended.
    // Example: Edge Function URL is https://<project>.supabase.co/functions/v1/chat-proxy
    // Client calls: https://<project>.supabase.co/functions/v1/chat-proxy/api/v1/chat/message
    // We need to extract `/api/v1/chat/message` and append it to the Azure Base URL.

    // Extract path after /chat-proxy
    const path = url.pathname.replace(/.*\/chat-proxy/, '')
    const targetUrl = `${backendUrl}${path}${url.search}`

    console.log(`Proxying request to: ${targetUrl}`)

    // 5. Forward the Request
    const proxyRequest = new Request(targetUrl, {
      method: req.method,
      headers: new Headers(req.headers),
      body: req.body,
      // Important: Set 'duplex' to 'half' for streaming bodies if needed, though standard fetch might handle it.
      // Deno's fetch supports streaming.
    })

    // Add Gateway Secret for Security
    proxyRequest.headers.set('X-Gateway-Secret', gatewaySecret)
    
    // Clean up headers that might cause issues
    proxyRequest.headers.delete('host')

    const backendResponse = await fetch(proxyRequest)

    // 6. Return the Backend Response (Streaming)
    // We pass the body stream directly to support chat streaming
    return new Response(backendResponse.body, {
      status: backendResponse.status,
      statusText: backendResponse.statusText,
      headers: {
        ...corsHeaders,
        ...Object.fromEntries(backendResponse.headers.entries()),
        // Ensure Access-Control-Allow-Origin is strictly set to avoid conflicts if backend sets it too
        'Access-Control-Allow-Origin': '*' 
      }
    })

  } catch (error) {
    console.error('Proxy error:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})


// /supabase/functions/proxy/index.ts
import { serve } from "https://deno.land/std@0.203.0/http/server.ts";
import { corsHeaders } from "../_shared/cors.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

serve(async (req) => {
  // Handle CORS
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: corsHeaders() });
  }

  const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
  const supabaseAnonKey = Deno.env.get("SUPABASE_ANON_KEY")!;
  const backendUrl = Deno.env.get("BACKEND_URL")!;

  const supabaseClient = createClient(supabaseUrl, supabaseAnonKey, {
    global: { headers: { Authorization: req.headers.get("Authorization")! } },
  });

  // 1. Authenticate user
  const {
    data: { user },
    error,
  } = await supabaseClient.auth.getUser();

  if (error || !user) {
    return new Response(JSON.stringify({ error: "Unauthorized" }), {
      status: 401,
      headers: corsHeaders(),
    });
  }

  // 2. Construct backend URL
  const incomingPath = new URL(req.url).pathname.replace("/proxy", "");
  const targetUrl = `${backendUrl}${incomingPath}`;

  // 3. Build trusted headers (cannot be overridden by client)
  const trustedHeaders = {
    "x-user-id": user.id,
    "x-user-email": user.email ?? "",
    "x-role": user.role ?? "user",
    "x-provider": user.app_metadata?.provider ?? "unknown",
    "x-original-method": req.method,
    "x-api-key": Deno.env.get("BACKEND_API_KEY") ?? "",
  };

  // 4. Forward request to backend
  const body = ["GET", "HEAD"].includes(req.method)
    ? undefined
    : await req.text();

  const backendResponse = await fetch(targetUrl, {
    method: req.method,
    headers: {
      "Content-Type": req.headers.get("Content-Type") ?? "application/json",
      ...trustedHeaders,
    },
    body,
  });

  // 5. Return backend response to frontend
  const result = await backendResponse.text();

  return new Response(result, {
    status: backendResponse.status,
    headers: {
      ...corsHeaders(),
      "Content-Type":
        backendResponse.headers.get("Content-Type") ?? "application/json",
    },
  });
});

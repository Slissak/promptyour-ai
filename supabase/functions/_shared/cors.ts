// /supabase/functions/_shared/cors.ts
export function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": "*", // Replace with frontend origin in prod
    "Access-Control-Allow-Headers": "authorization, x-client-info, content-type",
    "Access-Control-Allow-Methods": "GET,POST,PUT,PATCH,DELETE,OPTIONS",
  };
}

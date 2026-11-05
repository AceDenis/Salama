// Optional AI guide for the Salama app (Supabase Edge Function, Deno).
// Deploy:  supabase functions deploy ai-guide --no-verify-jwt
// Secrets: supabase secrets set ANTHROPIC_API_KEY=...   (or swap the provider call below for any other model API)
// Then paste the function URL into AI_ENDPOINT in web/config.js.
//
// Safety design:
//  * The app checks for crisis or danger wording BEFORE calling this function and shows people and help numbers instead.
//    This function checks again and refuses to chat on those topics.
//  * Nothing is stored or logged here. Do not add logging of message text.
//  * The assistant is told it is not a clinician, must not diagnose, and must point to a nurse for anything serious.
//  * Rate-limited per IP in memory (best effort). Add a proper limiter before wide release.
//  * Text leaves the phone for an AI provider: needs ethics committee approval, a data-protection impact assessment and
//    a lawful basis for any cross-border transfer (Data Protection Act 2019, Regulation 26 of the 2021 Regulations).

const SYSTEM = `You are the Salama guide, a brief, kind, practical assistant for personnel, family members and students linked to the Kenya Defence Forces and the Defence College of Health Sciences.
You are an AI, not a nurse, counsellor or doctor. Never diagnose, never tell anyone to start or stop medicine, never promise confidentiality beyond saying the app does not store what is typed.
Keep replies under 120 words, in plain English (or Kiswahili if the person writes in it). Offer one or two small practical steps (sleep, stress reset, a one-page debt plan, talking to a buddy, a welfare officer or a chaplain).
For money problems: never advise hiding a held ID or falsely reporting a card lost; suggest the welfare officer, the nurse or the chaplain and keeping evidence of threats.
If the person mentions suicide, self-harm, violence, abuse or immediate danger, do not continue normal chat: say you are glad they said it, urge them to call 999 or 112 or the gender-violence line 1195 or go to the nearest health facility, and to use the Ask a nurse button.
Always end by reminding them that a nurse can contact them through the app. Do not ask for names, service numbers or lender details.`;

const CRISIS = /(kill myself|suicid|end my life|end it all|want to die|better off dead|hurt myself|harm myself|self[- ]harm|overdose|take my life|kujiua|nataka kufa|beat(s|ing)? me|rape|abus)/i;
const hits = new Map<string, number[]>();
const cors = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "content-type", "Content-Type": "application/json" };

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: cors });
  if (req.method !== "POST") return new Response("{}", { status: 405, headers: cors });
  const ip = req.headers.get("x-forwarded-for") ?? "x"; const now = Date.now();
  const recent = (hits.get(ip) ?? []).filter((t) => now - t < 60_000); recent.push(now); hits.set(ip, recent);
  if (recent.length > 12) return new Response(JSON.stringify({ reply: "Please slow down a little. You can also ask a nurse to contact you from the app." }), { headers: cors });
  let msgs: { role: string; content: string }[] = [];
  try { msgs = (await req.json()).messages ?? []; } catch { return new Response("{}", { status: 400, headers: cors }); }
  msgs = msgs.slice(-8).map((m) => ({ role: m.role === "assistant" ? "assistant" : "user", content: String(m.content).slice(0, 500) }));
  if (!msgs.length || msgs[msgs.length - 1].role !== "user") return new Response("{}", { status: 400, headers: cors });
  if (msgs.some((m) => m.role === "user" && CRISIS.test(m.content)))
    return new Response(JSON.stringify({ reply: "I am glad you said that. Please get help now: call 999 or 112, or the free gender-violence line 1195, or go to the nearest health facility, and use Ask a nurse in this app so someone contacts you today. Please stay with someone you trust." }), { headers: cors });
  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "x-api-key": Deno.env.get("ANTHROPIC_API_KEY") ?? "", "anthropic-version": "2023-06-01", "content-type": "application/json" },
    body: JSON.stringify({ model: Deno.env.get("AI_MODEL") ?? "claude-haiku-5-5", max_tokens: 300, system: SYSTEM, messages: msgs }),
  });
  if (!r.ok) return new Response("{}", { status: 502, headers: cors });
  const j = await r.json(); const text = (j.content ?? []).map((c: { text?: string }) => c.text ?? "").join("").trim();
  return new Response(JSON.stringify({ reply: text }), { headers: cors });
});

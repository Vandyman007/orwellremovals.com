/**
 * Cloudflare Pages Function — handles enquiry / quote / contact form submissions.
 * Route: POST /api/quote  (all three site forms post here).
 *
 * Emails the enquiry to the sales inbox via the Resend API and replies straight to the
 * customer. Works with a plain (no-JS) form POST: on success it 303-redirects to
 * /thank-you/; on a JSON/fetch request it returns JSON instead.
 *
 * Required environment variables (set in the Cloudflare Pages dashboard → Settings → Env vars):
 *   RESEND_API_KEY   — Resend API key (server-side secret)
 *   QUOTE_TO         — (optional) recipient; defaults to sales@orwellremovals.com
 *   QUOTE_FROM       — (optional) verified sender; defaults to website@orwellremovals.com
 *
 * The sending domain (orwellremovals.com) must be verified in Resend (SPF/DKIM DNS).
 */

const TO_DEFAULT = "sales@orwellremovals.com";
const FROM_DEFAULT = "Orwell Removals Website <website@orwellremovals.com>";

// Pretty labels for known fields (everything else falls back to the raw key).
const LABELS = {
  first_name: "First name", last_name: "Last name", email: "Email", phone: "Phone",
  enquiry: "Nature of enquiry", move_from: "Moving from", move_to: "Moving to",
  property: "Property size", move_date: "Preferred date", services: "Services needed",
  message: "Message",
};
const FIELD_ORDER = ["first_name", "last_name", "email", "phone", "enquiry", "move_from",
  "move_to", "property", "move_date", "services", "message"];

function esc(s) {
  return String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}

async function readFields(request) {
  const ct = (request.headers.get("content-type") || "").toLowerCase();
  if (ct.includes("application/json")) {
    const j = await request.json();
    const out = {};
    for (const [k, v] of Object.entries(j)) out[k] = Array.isArray(v) ? v.join(", ") : v;
    return { fields: out, wantsJson: true };
  }
  const fd = await request.formData();
  const out = {};
  for (const k of fd.keys()) {
    const vals = fd.getAll(k).filter(v => typeof v === "string" && v.trim() !== "");
    if (vals.length) out[k] = vals.join(", ");
  }
  const wantsJson = (request.headers.get("accept") || "").includes("application/json");
  return { fields: out, wantsJson };
}

export async function onRequestPost({ request, env }) {
  let fields, wantsJson;
  try {
    ({ fields, wantsJson } = await readFields(request));
  } catch {
    return new Response("Bad request", { status: 400 });
  }

  // Honeypot: real users never fill "company" (it's visually hidden). Silently accept & drop bots.
  if (fields.company && fields.company.trim() !== "") {
    return wantsJson
      ? Response.json({ ok: true })
      : Response.redirect(new URL("/thank-you/", request.url).toString(), 303);
  }
  delete fields.company;

  // Minimal validation.
  if (!fields.email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(fields.email)) {
    return wantsJson
      ? Response.json({ ok: false, error: "A valid email address is required." }, { status: 422 })
      : new Response("A valid email address is required.", { status: 422 });
  }

  const name = [fields.first_name, fields.last_name].filter(Boolean).join(" ").trim() || "Website enquiry";

  // Build the email body (ordered known fields first, then any extras).
  const seen = new Set();
  const rows = [];
  for (const k of FIELD_ORDER) {
    if (fields[k]) { rows.push([LABELS[k] || k, fields[k]]); seen.add(k); }
  }
  for (const [k, v] of Object.entries(fields)) {
    if (!seen.has(k) && v) rows.push([LABELS[k] || k, v]);
  }
  const textBody = rows.map(([l, v]) => `${l}: ${v}`).join("\n");
  const htmlBody =
    `<h2 style="font-family:Arial,sans-serif">New website enquiry</h2>` +
    `<table style="font-family:Arial,sans-serif;border-collapse:collapse">` +
    rows.map(([l, v]) =>
      `<tr><td style="padding:4px 12px 4px 0;vertical-align:top;color:#254063;font-weight:bold">${esc(l)}</td>` +
      `<td style="padding:4px 0">${esc(v).replace(/\n/g, "<br>")}</td></tr>`).join("") +
    `</table><p style="font-family:Arial,sans-serif;color:#777;font-size:12px">` +
    `Sent from orwellremovals.com</p>`;

  if (!env.RESEND_API_KEY) {
    return wantsJson
      ? Response.json({ ok: false, error: "Email service not configured." }, { status: 503 })
      : new Response("Email service not configured.", { status: 503 });
  }

  const payload = {
    from: env.QUOTE_FROM || FROM_DEFAULT,
    to: [env.QUOTE_TO || TO_DEFAULT],
    reply_to: fields.email,
    subject: `Website enquiry — ${name}`,
    text: textBody,
    html: htmlBody,
  };

  const res = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${env.RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    console.log("Resend error", res.status, detail);
    return wantsJson
      ? Response.json({ ok: false, error: "Sorry, we couldn't send your enquiry. Please call 01473 411531." }, { status: 502 })
      : new Response("Sorry, we couldn't send your enquiry. Please call 01473 411531.", { status: 502 });
  }

  return wantsJson
    ? Response.json({ ok: true })
    : Response.redirect(new URL("/thank-you/", request.url).toString(), 303);
}

// A direct GET (someone visiting /api/quote) → bounce to the quote page.
export async function onRequestGet({ request }) {
  return Response.redirect(new URL("/get-a-quote/", request.url).toString(), 303);
}

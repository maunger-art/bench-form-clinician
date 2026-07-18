// blog-feedback — one-click Approve / Skip / Edit endpoint for the weekly preview email.
//
// The preview email's buttons link here with ?token=&n=&a=approve|skip|edit&t=<title>.
// This validates the token and appends the instruction to feedback.json in the repo
// (via the GitHub Contents API). The existing "Process Feedback" workflow then applies
// it to queue.json and clears feedback.json. Approve is a no-op (posts publish by default).
//
// Env secrets required (set with `supabase secrets set`):
//   FEEDBACK_TOKEN  — must match the token in the email links (same value as the GH secret)
//   GH_TOKEN        — a fine-grained PAT with Contents: Read & Write on maunger-art/bench-form-clinician

const REPO = "maunger-art/bench-form-clinician";
const FILE = "feedback.json";
const GH_API = `https://api.github.com/repos/${REPO}/contents/${FILE}`;

const b64decode = (b: string) =>
  new TextDecoder().decode(Uint8Array.from(atob(b), (c) => c.charCodeAt(0)));
const b64encode = (s: string) => {
  const bytes = new TextEncoder().encode(s);
  let bin = "";
  for (const byte of bytes) bin += String.fromCharCode(byte);
  return btoa(bin);
};

const ghHeaders = () => ({
  "Authorization": `Bearer ${Deno.env.get("GH_TOKEN")}`,
  "Accept": "application/vnd.github+json",
  "X-GitHub-Api-Version": "2022-11-28",
  "User-Agent": "benchmark-blog-feedback", // GitHub API rejects requests with no UA
});

// Append an entry to feedback.json, retrying on a stale-sha 409.
async function appendFeedback(entry: Record<string, unknown>) {
  for (let attempt = 0; attempt < 4; attempt++) {
    const getRes = await fetch(`${GH_API}?ref=main`, { headers: ghHeaders() });
    if (!getRes.ok) throw new Error(`GET feedback.json failed: ${getRes.status}`);
    const cur = await getRes.json();
    let list: unknown[] = [];
    try { list = JSON.parse(b64decode(cur.content)); } catch { list = []; }
    if (!Array.isArray(list)) list = [];
    list.push(entry);
    const putRes = await fetch(GH_API, {
      method: "PUT",
      headers: { ...ghHeaders(), "Content-Type": "application/json" },
      body: JSON.stringify({
        message: `blog feedback: ${JSON.stringify(entry)}`,
        content: b64encode(JSON.stringify(list, null, 2) + "\n"),
        sha: cur.sha,
        branch: "main",
      }),
    });
    if (putRes.ok) return;
    if (putRes.status !== 409) throw new Error(`PUT feedback.json failed: ${putRes.status}`);
    // 409 = someone else wrote first; loop and retry with the fresh sha
  }
  throw new Error("feedback.json write conflict after retries");
}

function page(title: string, body: string, status = 200): Response {
  const html = `<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>${title}</title>
<style>body{margin:0;background:#f0f4f8;font:16px/1.6 -apple-system,Segoe UI,Roboto,Arial,sans-serif;color:#1e3a5f}
.card{max-width:520px;margin:12vh auto;background:#fff;border-radius:14px;padding:34px 32px;
box-shadow:0 8px 30px rgba(16,24,40,.08);text-align:center}
h1{font-size:22px;margin:0 0 10px}p{color:#475569;margin:0 0 8px}
.tick{font-size:44px;color:#16a34a;line-height:1}
input[type=text]{width:100%;box-sizing:border-box;padding:11px 13px;border:1px solid #cbd5e1;border-radius:9px;font-size:15px;margin:10px 0}
button{background:#1e3a5f;color:#fff;border:0;border-radius:9px;padding:11px 20px;font-size:15px;font-weight:700;cursor:pointer}
small{color:#94a3b8}</style></head><body><div class="card">${body}
<p style="margin-top:18px"><small>Benchmark PS Blog</small></p></div></body></html>`;
  return new Response(html, { status, headers: { "Content-Type": "text/html; charset=utf-8" } });
}

Deno.serve(async (req) => {
  const url = new URL(req.url);
  const q = url.searchParams;
  const token = q.get("token") || "";
  const n = parseInt(q.get("n") || "", 10);
  const a = (q.get("a") || "").toLowerCase();
  const title = q.get("t") || "";

  if (token !== Deno.env.get("FEEDBACK_TOKEN"))
    return page("Invalid link", `<h1>Link expired or invalid</h1><p>Please use the buttons from the latest preview email.</p>`, 403);
  if (!n || !["approve", "skip", "edit"].includes(a))
    return page("Bad request", `<h1>Something's off</h1><p>Missing post number or action.</p>`, 400);

  try {
    if (a === "approve")
      return page("Approved", `<div class="tick">✓</div><h1>Post #${n} approved</h1><p>It will publish as scheduled. Nothing else to do.</p>`);

    if (a === "edit") {
      if (req.method === "POST") {
        const form = await req.formData();
        const newTitle = String(form.get("new_title") || "").trim();
        if (!newTitle) return page("Edit", `<h1>Please enter a new title</h1>`, 400);
        await appendFeedback({ action: "EDIT", number: n, new_title: newTitle });
        return page("Edit saved", `<div class="tick">✓</div><h1>Edit saved for post #${n}</h1><p>New title:</p><p><b>${newTitle.replace(/</g, "&lt;")}</b></p><p>It's queued for the next processing run.</p>`);
      }
      // GET → show a small form to capture the new title
      const action = `${url.origin}${url.pathname}?token=${encodeURIComponent(token)}&n=${n}&a=edit`;
      return page("Edit post", `<h1>Edit post #${n}</h1><p>Current: <i>${title.replace(/</g, "&lt;")}</i></p>
        <form method="POST" action="${action}"><input type="text" name="new_title" placeholder="New title or instruction" autofocus>
        <button type="submit">Save edit</button></form>`);
    }

    // skip
    await appendFeedback({ action: "SKIP", number: n });
    return page("Skipped", `<div class="tick">✓</div><h1>Post #${n} skipped</h1><p>It won't publish. The queue updates on the next processing run.</p>`);
  } catch (e) {
    return page("Error", `<h1>Couldn't record that</h1><p>${String(e).replace(/</g, "&lt;")}</p><p>You can reply to the email instead.</p>`, 500);
  }
});

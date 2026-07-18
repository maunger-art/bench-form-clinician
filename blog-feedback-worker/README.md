# blog-feedback Worker

One-click Approve / Skip / Edit endpoint for the weekly blog preview email.
Served at **www.benchmarkps.org/blog-feedback** via Cloudflare Workers (the domain is
already on Cloudflare; the Worker only intercepts `/blog-feedback*`, everything else
still goes to Render). Writes the instruction to `feedback.json`; the Process Feedback
workflow applies it to the queue. No Supabase involved.

## Deploy (one-time)
From this folder:

```bash
cd blog-feedback-worker

# 1. Log in to Cloudflare (opens a browser)
npx wrangler login

# 2. Create a GitHub token for the Worker:
#    github.com/settings/tokens?type=beta  → Generate new token
#    Resource owner: maunger-art · Only select repo: bench-form-clinician
#    Permissions → Repository → Contents: Read and write · copy the github_pat_… value

# 3. Set the two secrets (each prompts you to paste the value)
npx wrangler secret put FEEDBACK_TOKEN   # paste: 5257a378053509df916460f886288850a89d69a4033c56d4
npx wrangler secret put GH_TOKEN         # paste: your github_pat_… from step 2

# 4. Deploy
npx wrangler deploy
```

That publishes the Worker and attaches the `www.benchmarkps.org/blog-feedback` route
(the zone `benchmarkps.org` must be in the Cloudflare account you logged into).

## Test
```
https://www.benchmarkps.org/blog-feedback?token=<FEEDBACK_TOKEN>&n=1&a=approve
```
should return a "Post #1 approved" page.

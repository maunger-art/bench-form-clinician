import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers":
    "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const SENDER_EMAIL = "info@benchmarkps.org";
const INTERNAL_NOTIFY_EMAIL = "info@benchmarkps.org";

function getConfirmationHtml(firstName: string): string {
  return `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<title>Benchmark PS — Thanks for your interest</title>
<style>
  body,table,td,a{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%;}
  table,td{mso-table-lspace:0pt;mso-table-rspace:0pt;}
  img{-ms-interpolation-mode:bicubic;border:0;height:auto;line-height:100%;outline:none;text-decoration:none;}
  body{margin:0!important;padding:0!important;background:#f0f4f8;}
  @media screen and (max-width:600px){
    .email-container{width:100%!important;margin:0!important;}
    .stack-col{display:block!important;width:100%!important;padding-left:0!important;padding-right:0!important;padding-bottom:10px!important;}
    .px-mobile{padding-left:20px!important;padding-right:20px!important;}
    .hero-title{font-size:26px!important;}
  }
</style>
</head>
<body>
<div style="display:none;max-height:0;overflow:hidden;mso-hide:all;">We've received your details and someone from the team will be in touch shortly.</div>
<center style="background:#f0f4f8;padding:24px 0;">
<table class="email-container" cellpadding="0" cellspacing="0" border="0" width="600" style="max-width:600px;margin:0 auto;">
  <tr>
    <td style="background:linear-gradient(160deg,#0d2744 0%,#1a4a7a 55%,#0f3360 100%);border-radius:12px 12px 0 0;overflow:hidden;">
      <table cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
          <td style="background:rgba(255,255,255,0.05);padding:14px 32px;border-bottom:1px solid rgba(255,255,255,.08);">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td style="vertical-align:middle;">
                  <table cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td style="vertical-align:middle;">
                        <div style="font-size:14px;font-weight:700;color:#fff;letter-spacing:.5px;text-transform:uppercase;line-height:1.2;">Benchmark</div>
                        <div style="font-size:14px;color:rgba(255,255,255,.4);letter-spacing:1.2px;text-transform:uppercase;margin-top:1px;">Performance Systems</div>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td class="px-mobile" style="padding:44px 36px 40px;text-align:center;">
            <div style="display:inline-block;background:rgba(74,200,120,.2);border:1px solid rgba(74,200,120,.4);border-radius:20px;padding:5px 18px;font-size:14px;color:#6ee79e;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:20px;font-weight:600;">&#10003;&nbsp; Message received</div>
            <h1 class="hero-title" style="font-size:32px;font-weight:800;color:#fff;line-height:1.15;margin:0 0 14px;letter-spacing:-0.5px;">Thanks for reaching out,<br><em style="color:#7dbff5;font-style:italic;">${firstName}</em></h1>
            <p style="font-size:15px;color:rgba(255,255,255,.6);max-width:420px;margin:0 auto;line-height:1.65;">We've received your details. Someone from the Benchmark PS team will be in touch with you shortly.</p>
          </td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td style="background:#fff;padding:0;">
      <table cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
          <td class="px-mobile" style="padding:36px 36px 24px;">
            <p style="font-size:15px;color:#374151;line-height:1.75;margin:0 0 16px;">Hi ${firstName},</p>
            <p style="font-size:15px;color:#374151;line-height:1.75;margin:0 0 16px;">We're glad you found us. Benchmark PS is built specifically for clinic owners and physiotherapists who want to move beyond subjective assessment — giving you validated protocols, population benchmarks, and a system that connects test data directly to treatment planning.</p>
            <p style="font-size:15px;color:#374151;line-height:1.75;margin:0;">We'll reach out soon to understand what you're working on and show you how the platform fits your practice.</p>
          </td>
        </tr>
        <tr>
          <td class="px-mobile" style="padding:0 36px 24px;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f0f7ff;border-left:4px solid #1a4a7a;border-radius:0 9px 9px 0;">
              <tr>
                <td style="padding:20px 22px;">
                  <div style="font-size:14px;font-weight:700;color:#1a4a7a;letter-spacing:1px;text-transform:uppercase;margin-bottom:14px;">What Benchmark PS gives you</div>
                  <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-bottom:12px;">
                    <tr>
                      <td style="vertical-align:top;width:28px;padding-right:12px;"><div style="width:26px;height:26px;border-radius:50%;background:#1a4a7a;font-size:14px;font-weight:700;color:#fff;text-align:center;line-height:26px;">1</div></td>
                      <td style="vertical-align:top;"><p style="font-size:14px;color:#1f2937;line-height:1.65;margin:0;"><strong>Objective benchmarking</strong> — validated protocols you can run with whatever equipment you have, measured against published population norms</p></td>
                    </tr>
                  </table>
                  <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-bottom:12px;">
                    <tr>
                      <td style="vertical-align:top;width:28px;padding-right:12px;"><div style="width:26px;height:26px;border-radius:50%;background:#1a4a7a;font-size:14px;font-weight:700;color:#fff;text-align:center;line-height:26px;">2</div></td>
                      <td style="vertical-align:top;"><p style="font-size:14px;color:#1f2937;line-height:1.65;margin:0;"><strong>Outcome tracking</strong> — monitor patient progress over time with data that builds a clear picture of clinical performance across your whole practice</p></td>
                    </tr>
                  </table>
                  <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    <tr>
                      <td style="vertical-align:top;width:28px;padding-right:12px;"><div style="width:26px;height:26px;border-radius:50%;background:#1a4a7a;font-size:14px;font-weight:700;color:#fff;text-align:center;line-height:26px;">3</div></td>
                      <td style="vertical-align:top;"><p style="font-size:14px;color:#1f2937;line-height:1.65;margin:0;"><strong>Integrated exercise prescription</strong> — test results automatically inform personalised rehab programmes, closing the loop from assessment to treatment</p></td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td class="px-mobile" style="padding:0 36px 26px;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f0f7ff;border:1px solid #d1e3f5;border-radius:8px;">
              <tr>
                <td style="padding:18px 20px;">
                  <div style="font-size:14px;font-weight:700;color:#1a4a7a;letter-spacing:1px;text-transform:uppercase;margin-bottom:14px;">Early results from Benchmark PS clinics</div>
                  <table cellpadding="0" cellspacing="0" border="0" width="100%" style="margin-bottom:14px;">
                    <tr>
                      <td class="stack-col" style="width:50%;padding-right:6px;vertical-align:top;">
                        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#fff;border:1px solid #d1e3f5;border-radius:8px;">
                          <tr><td style="padding:14px 16px;text-align:center;">
                            <div style="font-size:32px;font-weight:800;color:#0d2744;line-height:1;">39%</div>
                            <div style="font-size:14px;color:#6b7280;margin-top:4px;line-height:1.4;">improvement vs<br>standard physio</div>
                          </td></tr>
                        </table>
                      </td>
                      <td class="stack-col" style="width:50%;padding-left:6px;vertical-align:top;">
                        <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#fff;border:1px solid #d1e3f5;border-radius:8px;">
                          <tr><td style="padding:14px 16px;text-align:center;">
                            <div style="font-size:32px;font-weight:800;color:#0d2744;line-height:1;">83%</div>
                            <div style="font-size:14px;color:#6b7280;margin-top:4px;line-height:1.4;">of patients showed<br>measurable improvement</div>
                          </td></tr>
                        </table>
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td class="px-mobile" style="padding:0 36px 28px;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;">
              <tr>
                <td style="padding:16px 18px;">
                  <p style="font-size:14px;color:#374151;line-height:1.65;margin:0;"><strong style="color:#0d2744;">What happens next</strong> &nbsp;&#8250;&nbsp; A member of the team will reach out within 1&ndash;2 working days to arrange a short call. If you have questions in the meantime, reply to this email and we'll get back to you.</p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr>
          <td class="px-mobile" style="padding:0 36px 0;">
            <table cellpadding="0" cellspacing="0" border="0" width="100%">
              <tr>
                <td style="padding-top:20px;border-top:1px solid #f3f4f6;">
                  <p style="font-size:15px;color:#374151;line-height:1.75;margin:0 0 14px;">Speak soon.</p>
                  <p style="font-size:14px;color:#9ca3af;line-height:1.75;margin:0;">
                    <strong style="color:#374151;">The Benchmark PS Team</strong><br>
                    <a href="mailto:hello@benchmarkps.org" style="color:#9ca3af;">hello@benchmarkps.org</a>&nbsp;&middot;&nbsp;
                    <a href="https://benchmarkps.org" style="color:#9ca3af;">benchmarkps.org</a>
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
        <tr><td style="height:32px;"></td></tr>
      </table>
    </td>
  </tr>
  <tr>
    <td style="background:#f0f4f8;border-radius:0 0 12px 12px;padding:18px 32px;border-top:1px solid #e5e7eb;">
      <p style="font-size:12px;color:#9ca3af;text-align:center;line-height:1.7;margin:0;">
        You're receiving this because you submitted an enquiry at benchmarkps.org &middot;
        Benchmark Performance Systems Ltd
      </p>
    </td>
  </tr>
</table>
</center>
</body>
</html>`;
}

function getInternalNotificationHtml(data: {
  full_name: string;
  email: string;
  clinic_name?: string;
  role?: string;
  phone?: string;
  submitted_at: string;
}): string {
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8"></head>
<body style="font-family:Arial,sans-serif;background:#f5f5f5;padding:20px;">
<div style="max-width:560px;margin:0 auto;background:#fff;border-radius:8px;padding:32px;border:1px solid #e0e0e0;">
  <h2 style="color:#0d2744;margin:0 0 20px;font-size:20px;">🔔 New Early Access Request</h2>
  <table style="width:100%;font-size:14px;color:#333;border-collapse:collapse;">
    <tr><td style="padding:8px 0;font-weight:600;width:120px;vertical-align:top;">Name</td><td style="padding:8px 0;">${data.full_name}</td></tr>
    <tr><td style="padding:8px 0;font-weight:600;vertical-align:top;">Email</td><td style="padding:8px 0;"><a href="mailto:${data.email}">${data.email}</a></td></tr>
    ${data.clinic_name ? `<tr><td style="padding:8px 0;font-weight:600;vertical-align:top;">Clinic</td><td style="padding:8px 0;">${data.clinic_name}</td></tr>` : ""}
    ${data.role ? `<tr><td style="padding:8px 0;font-weight:600;vertical-align:top;">Role</td><td style="padding:8px 0;">${data.role}</td></tr>` : ""}
    ${data.phone ? `<tr><td style="padding:8px 0;font-weight:600;vertical-align:top;">Phone</td><td style="padding:8px 0;">${data.phone}</td></tr>` : ""}
    <tr><td style="padding:8px 0;font-weight:600;vertical-align:top;">Submitted</td><td style="padding:8px 0;">${data.submitted_at}</td></tr>
  </table>
  <hr style="border:none;border-top:1px solid #eee;margin:20px 0 12px;">
  <p style="font-size:12px;color:#999;margin:0;">Source: Early Access Form &middot; benchmarkps.org</p>
</div>
</body></html>`;
}

Deno.serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    const { full_name, email, clinic_name, role, phone } = await req.json();

    // Validate required fields
    if (!full_name || typeof full_name !== "string" || full_name.trim().length === 0) {
      return new Response(JSON.stringify({ error: "Full name is required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }
    if (!email || typeof email !== "string" || !EMAIL_REGEX.test(email.trim())) {
      return new Response(JSON.stringify({ error: "A valid email is required" }), {
        status: 400,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const cleanName = full_name.trim().substring(0, 200);
    const cleanEmail = email.trim().toLowerCase().substring(0, 255);
    const cleanClinic = clinic_name ? String(clinic_name).trim().substring(0, 200) : null;
    const cleanRole = role ? String(role).trim().substring(0, 100) : null;
    const cleanPhone = phone ? String(phone).trim().substring(0, 30) : null;

    // Create Supabase client with service role
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const supabaseKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, supabaseKey);

    // Upsert submission and return the row
    const { data: localRow, error: dbError } = await supabase
      .from("early_access_submissions")
      .upsert(
        {
          full_name: cleanName,
          email: cleanEmail,
          clinic_name: cleanClinic,
          role: cleanRole,
          phone: cleanPhone,
          source: "early_access_form",
          status: "new",
          sync_status: "pending",
          last_submitted_at: new Date().toISOString(),
        },
        { onConflict: "email" }
      )
      .select("id, created_at")
      .single();

    if (dbError || !localRow) {
      console.error("DB error:", dbError);
      return new Response(JSON.stringify({ error: "Failed to save submission" }), {
        status: 500,
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    // --- External Supabase sync ---
    const extUrl = Deno.env.get("EXTERNAL_SUPABASE_URL");
    const extKey = Deno.env.get("EXTERNAL_SUPABASE_SERVICE_ROLE_KEY");

    if (extUrl && extKey) {
      try {
        const extSupabase = createClient(extUrl, extKey);
        const { error: syncError } = await extSupabase
          .from("early_access_requests")
          .upsert(
            {
              source_submission_id: localRow.id,
              full_name: cleanName,
              email: cleanEmail,
              clinic_name: cleanClinic,
              role: cleanRole,
              phone: cleanPhone,
              source: "lovable_enquiry_form",
              created_at: localRow.created_at,
              raw_payload: { full_name: cleanName, email: cleanEmail, clinic_name: cleanClinic, role: cleanRole, phone: cleanPhone },
              synced_at: new Date().toISOString(),
            },
            { onConflict: "source_submission_id" }
          );

        if (syncError) {
          console.error("External sync error:", syncError);
          await supabase.from("early_access_submissions").update({ sync_status: "failed" }).eq("id", localRow.id);
        } else {
          console.log("External sync success for:", localRow.id);
          await supabase.from("early_access_submissions").update({ sync_status: "synced" }).eq("id", localRow.id);
        }
      } catch (syncErr) {
        console.error("External sync exception:", syncErr);
        await supabase.from("early_access_submissions").update({ sync_status: "failed" }).eq("id", localRow.id);
      }
    } else {
      console.warn("External Supabase credentials not configured — skipping sync");
      await supabase.from("early_access_submissions").update({ sync_status: "failed" }).eq("id", localRow.id);
    }

    // Send emails via Resend
    const resendKey = Deno.env.get("RESEND_API_KEY");
    if (!resendKey) {
      console.error("RESEND_API_KEY not configured");
      // Still return success since the data was saved
      return new Response(JSON.stringify({ success: true, email_sent: false }), {
        headers: { ...corsHeaders, "Content-Type": "application/json" },
      });
    }

    const firstName = cleanName.split(" ")[0];

    // Send confirmation email to clinician
    const confirmRes = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${resendKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: `Benchmark PS <${SENDER_EMAIL}>`,
        to: [cleanEmail],
        subject: "Thanks for your interest in Benchmark PS",
        html: getConfirmationHtml(firstName),
      }),
    });

    if (!confirmRes.ok) {
      const errBody = await confirmRes.text();
      console.error("Resend confirmation error:", errBody);
    }

    // Send internal notification
    const notifyRes = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${resendKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        from: `Benchmark PS <${SENDER_EMAIL}>`,
        to: [INTERNAL_NOTIFY_EMAIL],
        subject: `New Early Access Request: ${cleanName}`,
        html: getInternalNotificationHtml({
          full_name: cleanName,
          email: cleanEmail,
          clinic_name: cleanClinic ?? undefined,
          role: cleanRole ?? undefined,
          phone: cleanPhone ?? undefined,
          submitted_at: new Date().toISOString(),
        }),
      }),
    });

    if (!notifyRes.ok) {
      const errBody = await notifyRes.text();
      console.error("Resend notification error:", errBody);
    }

    return new Response(
      JSON.stringify({ success: true, email_sent: confirmRes.ok }),
      { headers: { ...corsHeaders, "Content-Type": "application/json" } }
    );
  } catch (err) {
    console.error("Unexpected error:", err);
    return new Response(JSON.stringify({ error: "Internal server error" }), {
      status: 500,
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});

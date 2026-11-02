import { useState } from "react";

const SIGNUP_URL = "https://platform.benchmarkps.org/login?signup=true";

type Billing = "monthly" | "annual";

interface Tier {
  name: string;
  monthly: string;
  annual: string;
  monthlyUnit: string;
  annualUnit: string;
  period: string;
  tagline: string;
  inheritLabel?: string;
  features: string[];
  cta: string;
  featured?: boolean;
}

// Prices per Mike's 1 Nov brief; feature bullets per the entitlements matrix
// in docs-claude/tier-trial-structure.scope.md. Per-practitioner, GBP,
// annual = 2 months free.
const TIERS: Tier[] = [
  {
    name: "Free",
    monthly: "£0",
    annual: "£0",
    monthlyUnit: "",
    annualUnit: "",
    period: "Free forever",
    tagline: "Patient-reported outcomes and the patient portal, at no cost.",
    features: [
      "PROMS — symptoms & PSFS tracking",
      "Patient web portal & companion apps",
    ],
    cta: "Get started",
  },
  {
    name: "Essentials",
    monthly: "£15",
    annual: "£150",
    monthlyUnit: "/practitioner/mo",
    annualUnit: "/practitioner/yr",
    period: "per practitioner · billed monthly",
    tagline: "Objective data capture, clinical resources and PDF reporting.",
    inheritLabel: "Everything in Free, plus",
    features: [
      "Objective testing & results — force, ROM, programmes",
      "Clinical resources — protocols, reference lists, exercise prescription",
      "PDF report builder",
      "Cliniko integration — patient import & report push",
    ],
    cta: "Start free trial",
  },
  {
    name: "Pro",
    monthly: "£25",
    annual: "£250",
    monthlyUnit: "/practitioner/mo",
    annualUnit: "/practitioner/yr",
    period: "per practitioner · billed monthly",
    tagline: "Adds AI clinical documentation from recorded consultations.",
    inheritLabel: "Everything in Essentials, plus",
    features: [
      "Session recording & transcription — 3,000 min / practitioner / month",
      "AI clinical notes — SOAP, summaries & referrals",
      "Cliniko SOAP push",
    ],
    cta: "Start free trial",
    featured: true,
  },
  {
    name: "Unlimited",
    monthly: "£35",
    annual: "£350",
    monthlyUnit: "/practitioner/mo",
    annualUnit: "/practitioner/yr",
    period: "per practitioner · billed monthly",
    tagline: "Every tool, with unlimited recording for high-volume clinics.",
    inheritLabel: "Everything in Pro, plus",
    features: [
      "Unlimited recording & transcription (fair use)",
      "Every Benchmark tool included",
    ],
    cta: "Start free trial",
  },
];

const Pricing = () => {
  const [billing, setBilling] = useState<Billing>("monthly");

  return (
    <section className="pricing" id="pricing">
      <div className="wrap">
        <div className="section-head reveal">
          <div className="eyebrow eyebrow--center">
            <span className="eyebrow__dash"></span>Pricing
          </div>
          <h2 className="section-title">
            Simple, <span className="ser">per-practitioner</span> pricing
          </h2>
          <p className="section-sub">
            Pay only for active practitioners — admin and reception staff are always free. Switch
            or cancel anytime.
          </p>
          <span className="pricing__seatnote">
            <svg viewBox="0 0 24 24" fill="none">
              <path
                d="M5 13l4 4L19 7"
                stroke="currentColor"
                strokeWidth="2.4"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            Admin &amp; reception staff included free
          </span>
        </div>

        <div className="bill-toggle reveal" role="group" aria-label="Billing period">
          <button
            type="button"
            className={billing === "monthly" ? "active" : ""}
            aria-pressed={billing === "monthly"}
            onClick={() => setBilling("monthly")}
          >
            Monthly
          </button>
          <button
            type="button"
            className={billing === "annual" ? "active" : ""}
            aria-pressed={billing === "annual"}
            onClick={() => setBilling("annual")}
          >
            Annual
          </button>
        </div>
        <span className="bill-save">Save two months with annual billing</span>

        <div className="price-grid">
          {TIERS.map((t) => {
            const isFree = t.name === "Free";
            const amount = billing === "monthly" ? t.monthly : t.annual;
            const unit = billing === "monthly" ? t.monthlyUnit : t.annualUnit;
            const period = isFree
              ? "Free forever"
              : `per practitioner · billed ${billing === "monthly" ? "monthly" : "annually"}`;
            return (
              <div
                className={`price-card reveal${t.featured ? " price-card--featured" : ""}`}
                key={t.name}
              >
                {t.featured && <div className="price-badge">Most popular</div>}
                <div className="price-card__name">{t.name}</div>
                <div className="price-card__amount">
                  {amount}
                  {unit && <small> {unit}</small>}
                </div>
                <div className="price-card__period">{period}</div>
                <p className="price-card__tag">{t.tagline}</p>
                <ul className="price-card__feats">
                  {t.inheritLabel && (
                    <li className="price-card__inherit">{t.inheritLabel}</li>
                  )}
                  {t.features.map((f) => (
                    <li key={f}>{f}</li>
                  ))}
                </ul>
                <a
                  className={`btn ${t.featured ? "btn--primary" : "btn--ghost"}`}
                  href={SIGNUP_URL}
                >
                  {t.cta}
                </a>
              </div>
            );
          })}
        </div>

        <div className="price-foot">
          <span className="price-trial">
            <svg viewBox="0 0 24 24" fill="none">
              <path
                d="M12 7v5l3 2"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
              <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.8" />
            </svg>
            Start with a 28-day free trial — no card required.
          </span>
          <p className="price-note">
            Prices are per practitioner. Annual billing is charged for ten months — two months free.
          </p>
        </div>
      </div>
    </section>
  );
};

export default Pricing;

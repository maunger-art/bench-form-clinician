import { useEffect, useState } from "react";
import screenshotResultsFull from "@/assets/screenshot-results-full.png";
import screenshotSoapNoteFull from "@/assets/screenshot-soap-note-full.png";
import screenshotSymptomsFull from "@/assets/screenshot-symptoms-full.png";

// Recording-card waveform pattern (percentage heights), mirrors the concept.
const REC_WAVE = [
  30, 55, 80, 45, 95, 60, 35, 70, 90, 50, 25, 65, 85, 40, 75, 55, 95, 45, 60, 30, 70, 88, 42, 58,
  92, 48, 33, 68, 80, 52, 28, 62, 86, 44, 72,
];

const RecTimer = () => {
  const [label, setLabel] = useState("02:17");
  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (reduce) return;
    let secs = 137;
    const id = window.setInterval(() => {
      secs++;
      const m = Math.floor(secs / 60);
      const s = secs % 60;
      setLabel(`${m < 10 ? "0" + m : m}:${s < 10 ? "0" + s : s}`);
    }, 1000);
    return () => window.clearInterval(id);
  }, []);
  return (
    <div className="rec-card__time" id="recTime">
      {label}
    </div>
  );
};

const Platform = () => {
  return (
    <section className="platform" id="platform">
      <div className="wrap">
        <div className="section-head reveal">
          <div className="eyebrow eyebrow--center">
            <span className="eyebrow__dash"></span>The Platform
          </div>
          <h2 className="section-title">
            Everything you need to{" "}
            <span className="ser">measure, document and prove</span> care
          </h2>
          <p className="section-sub">
            Real clinical tools designed by clinicians — objective data, clear visualisations,
            AI-powered documentation, and patient-reported outcomes, all in one place.
          </p>
        </div>

        {/* Feature 1 — Objective testing */}
        <div className="feature reveal">
          <div className="feature__media">
            <div className="browser tilt-sm">
              <div className="browser__bar">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="browser__url">Results · Patient benchmarking</span>
              </div>
              <div className="browser__body">
                <div className="shot shot--results">
                  <img
                    src={screenshotResultsFull}
                    alt="Objective testing results table comparing left and right measurements against expected normative values across strength, range of movement, endurance and power"
                  />
                </div>
              </div>
            </div>
            <div className="callout callout--tl">Left vs right · expected vs actual</div>
            <div className="callout callout--br accent-amber">Deficit flagged automatically</div>
          </div>
          <div className="feature__copy">
            <div className="ftag ftag--blue">Objective Testing</div>
            <h3>Benchmark every result against normative data</h3>
            <p>
              Capture range of movement, strength, endurance and power — then compare each
              measurement against age-, sex- and sport-matched norms. Asymmetries and deficits are
              surfaced instantly, in Newtons, degrees and repetitions clinicians trust.
            </p>
            <ul className="feature__list">
              <li>Expected vs actual for every test</li>
              <li>Left / right laterality comparison</li>
              <li>Absolute or percentage-of-expected views</li>
            </ul>
          </div>
        </div>

        {/* Feature 2 — AI reports + secure share */}
        <div className="feature feature--rev reveal">
          <div className="feature__media">
            <div className="browser tilt-sm">
              <div className="browser__bar">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="browser__url">Recording · AI clinical report</span>
              </div>
              <div className="browser__body">
                <div className="shot shot--soap">
                  <img
                    src={screenshotSoapNoteFull}
                    alt="AI-generated SOAP note from a consultation recording, with Transcription, SOAP Note, Patient Summary and Onward Referral tabs"
                  />
                </div>
              </div>
            </div>
            <div className="callout callout--tr">SOAP · Summary · Referral</div>
            <div className="callout callout--bl accent-green">
              <span className="dot-live"></span>Secure link to GP &amp; consultant
            </div>
          </div>
          <div className="feature__copy">
            <div className="ftag ftag--teal">
              AI Clinical Reports <span className="pill-new">New</span>
            </div>
            <h3>From consultation to shareable report in seconds</h3>
            <p>
              Turn a recorded consultation into a structured SOAP note, a plain-English patient
              summary, and an onward referral — generated automatically, reviewed by you. Share any
              report with a patient, GP or consultant through an encrypted, expiring link.
            </p>
            <ul className="feature__list">
              <li>SOAP note, patient summary &amp; referral from one recording</li>
              <li>Clinician reviews and edits before anything is sent</li>
              <li>Time-limited secure share links — no email attachments</li>
            </ul>
          </div>
        </div>

        {/* Feature 3 — Redesigned recording (CSS mock) */}
        <div className="feature reveal">
          <div className="feature__media">
            <div className="rec-card tilt-sm">
              <div className="rec-card__top">
                <div className="rec-card__status">
                  <span className="rec-dot"></span>Recording consultation
                </div>
                <RecTimer />
              </div>
              <div className="rec-card__wave" id="recWave" aria-hidden="true">
                {REC_WAVE.map((h, k) => (
                  <span
                    key={k}
                    style={{ height: `${h}%`, animationDelay: `${(k * 0.05).toFixed(2)}s` }}
                  />
                ))}
              </div>
              <div className="rec-card__meta">
                <span className="zdr-badge">
                  <svg viewBox="0 0 24 24">
                    <path
                      d="M12 2l8 4v6c0 5-3.4 8.5-8 10-4.6-1.5-8-5-8-10V6z"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.8"
                    />
                  </svg>
                  Zero data retention
                </span>
                <span className="rec-card__lang">Auto-transcribing · en-GB</span>
              </div>
              <div className="rec-card__out">
                <div className="rec-card__out-label">Structured note forming</div>
                <div className="skl skl--1"></div>
                <div className="skl skl--2"></div>
                <div className="skl skl--3"></div>
              </div>
            </div>
            <div className="callout callout--tr">Real-time waveform</div>
            <div className="callout callout--bl accent-amber">Note ready in seconds</div>
          </div>
          <div className="feature__copy">
            <div className="ftag ftag--blue">
              Redesigned Recording <span className="pill-new">New</span>
            </div>
            <h3>Dictate the consultation. Get a structured note.</h3>
            <p>
              A rebuilt recording experience with a live waveform so you always know it's listening.
              Speak naturally through the session and Benchmark transcribes it on a
              zero-data-retention basis — then drafts the clinical note for you to review.
            </p>
            <ul className="feature__list">
              <li>Real-time waveform &amp; clear recording state</li>
              <li>Zero-data-retention transcription pipeline</li>
              <li>Draft note ready the moment you stop</li>
            </ul>
          </div>
        </div>

        {/* Feature 4 — PROMS */}
        <div className="feature feature--rev reveal">
          <div className="feature__media">
            <div className="browser tilt-sm">
              <div className="browser__bar">
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="dot"></span>
                <span className="browser__url">Patient · Function &amp; pain over time</span>
              </div>
              <div className="browser__body">
                <div className="shot shot--symptoms">
                  <img
                    src={screenshotSymptomsFull}
                    alt="Activity and pain log with a symptoms graph tracking function score, pain score and projected function over time"
                  />
                </div>
              </div>
            </div>
            <div className="callout callout--tl">Function &amp; pain, over time</div>
            <div className="callout callout--br accent-green">Projected recovery line</div>
          </div>
          <div className="feature__copy">
            <div className="ftag ftag--teal">
              Patient-Reported Outcomes <span className="pill-new">New</span>
            </div>
            <h3>Capture how patients actually feel — and chart it</h3>
            <p>
              Patients log function and pain between visits. Benchmark plots the trend against a
              projected recovery line, so progress is visible to clinician and patient alike —
              turning subjective experience into a clear, shared picture of recovery.
            </p>
            <ul className="feature__list">
              <li>Function &amp; pain scores logged over time</li>
              <li>Projected recovery trajectory</li>
              <li>Shared view that keeps patients engaged</li>
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Platform;

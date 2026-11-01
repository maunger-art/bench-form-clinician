const PANEL_ROWS = [
  { key: "Encryption in transit", val: "TLS 1.2+" },
  { key: "Encryption at rest", val: "AES-256" },
  { key: "AI transcription retention", val: "Zero" },
  { key: "Two-factor authentication", val: "Enabled" },
  { key: "Audit trail", val: "Full" },
];

const Security = () => {
  return (
    <section className="security" id="security">
      <div className="security__mesh" aria-hidden="true"></div>
      <div className="security__grid-tex" aria-hidden="true"></div>
      <div className="wrap security__inner">
        <div className="security__head reveal">
          <div className="eyebrow eyebrow--center eyebrow--on-dark">
            <span className="eyebrow__dash"></span>Security &amp; Trust
          </div>
          <h2 className="section-title on-dark">
            Clinical data, <span className="ser">handled the way it should be</span>
          </h2>
          <p className="section-sub on-dark">
            Benchmark is built around patient confidentiality from the ground up. Every record is
            encrypted, every action is logged, and sensitive AI processing is designed to retain
            nothing.
          </p>
        </div>

        <div className="sec-layout">
          <div className="sec-panel reveal" data-delay="80">
            {PANEL_ROWS.map((r) => (
              <div className="sec-panel__row" key={r.key}>
                <span className="sec-panel__key">{r.key}</span>
                <span className="sec-panel__val on">
                  <span className="pulse"></span>
                  {r.val}
                </span>
              </div>
            ))}
            <div className="sec-panel__foot">
              <span className="sec-panel__flag">UK</span>
              <div>
                <div className="sec-panel__foot-title">GDPR-aligned UK data handling</div>
                <div className="sec-panel__foot-sub">Data processed under UK GDPR principles</div>
              </div>
            </div>
          </div>

          <div className="sec-cards">
            <div className="sec-card reveal" data-delay="60">
              <div className="sec-card__ic">
                <svg viewBox="0 0 24 24">
                  <rect x="4" y="10" width="16" height="10" rx="2" fill="none" stroke="currentColor" strokeWidth="1.8" />
                  <path d="M8 10V7a4 4 0 0 1 8 0v3" fill="none" stroke="currentColor" strokeWidth="1.8" />
                </svg>
              </div>
              <h4>Encrypted end to end</h4>
              <p>
                Patient data is encrypted in transit and at rest, so records stay protected on the
                wire and in storage.
              </p>
            </div>
            <div className="sec-card reveal" data-delay="120">
              <div className="sec-card__ic">
                <svg viewBox="0 0 24 24">
                  <path d="M12 3l7 3v5c0 4.5-3 7.6-7 9-4-1.4-7-4.5-7-9V6z" fill="none" stroke="currentColor" strokeWidth="1.8" />
                  <path d="M9.5 12l1.8 1.8L15 10" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <h4>Zero-retention AI</h4>
              <p>
                Transcription runs through a zero-data-retention pipeline — audio isn't kept or used
                to train models.
              </p>
            </div>
            <div className="sec-card reveal" data-delay="180">
              <div className="sec-card__ic">
                <svg viewBox="0 0 24 24">
                  <circle cx="12" cy="8" r="3.2" fill="none" stroke="currentColor" strokeWidth="1.8" />
                  <path d="M5 19c0-3.3 3.1-5 7-5s7 1.7 7 5" fill="none" stroke="currentColor" strokeWidth="1.8" />
                  <path d="M18 7l1.4 1.4L22 6" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <h4>Role-based access</h4>
              <p>
                Clinicians, admins and patients each see only what their role allows — access scoped
                by design.
              </p>
            </div>
            <div className="sec-card reveal" data-delay="240">
              <div className="sec-card__ic">
                <svg viewBox="0 0 24 24">
                  <path d="M6 3h9l3 3v15H6z" fill="none" stroke="currentColor" strokeWidth="1.8" />
                  <path d="M9 12h6M9 16h6M9 8h3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
                </svg>
              </div>
              <h4>Full audit trail</h4>
              <p>
                Every meaningful action is logged, giving your clinic a complete, reviewable record
                of data access.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Security;

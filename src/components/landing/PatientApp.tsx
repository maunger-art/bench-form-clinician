const Tick = () => (
  <span className="patient__ic">
    <svg viewBox="0 0 24 24">
      <path
        d="M5 13l4 4L19 7"
        fill="none"
        stroke="currentColor"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  </span>
);

const PatientApp = () => {
  return (
    <section className="patient" id="patient">
      <div className="wrap patient__inner">
        <div className="patient__copy reveal">
          <div className="eyebrow">
            <span className="eyebrow__dash"></span>For Your Patients
          </div>
          <h2 className="section-title">
            Your patients get <span className="ser">an app</span>, too
          </h2>
          <p className="section-sub section-sub--left">
            Progress doesn't stay locked in the clinic. Patients follow their prescribed exercises,
            log how they feel, and watch their own recovery take shape — through a patient web portal
            and companion mobile apps.
          </p>
          <ul className="patient__list">
            <li>
              <Tick />
              Prescribed exercises with clear guidance
            </li>
            <li>
              <Tick />
              Log function &amp; pain between appointments
            </li>
            <li>
              <Tick />
              See their own progress against the plan
            </li>
            <li>
              <Tick />
              Available on the web and as mobile apps
            </li>
          </ul>
        </div>

        <div className="patient__stage reveal" data-delay="150">
          <div className="phone float-slow">
            <div className="phone__notch"></div>
            <div className="phone__screen">
              <div className="pa__top">
                <div className="pa__hi">Hi, Sarah</div>
                <div className="pa__day">Week 6 · Knee rehab</div>
              </div>
              <div className="pa__ring">
                <svg viewBox="0 0 120 120">
                  <circle cx="60" cy="60" r="50" className="pa__ring-bg" />
                  <circle cx="60" cy="60" r="50" className="pa__ring-fg" id="paRing" />
                </svg>
                <div className="pa__ring-txt">
                  <span className="pa__pct">
                    78<small>%</small>
                  </span>
                  <span className="pa__lbl">of plan</span>
                </div>
              </div>
              <div className="pa__card">
                <div className="pa__ex">
                  <span className="pa__ex-ic"></span>
                  <div>
                    <div className="pa__ex-t">Single-leg sit to stand</div>
                    <div className="pa__ex-s">3 × 12 · done</div>
                  </div>
                  <span className="pa__ex-done">✓</span>
                </div>
                <div className="pa__ex">
                  <span className="pa__ex-ic pa__ex-ic--2"></span>
                  <div>
                    <div className="pa__ex-t">Knee flexion stretch</div>
                    <div className="pa__ex-s">2 × 30s · up next</div>
                  </div>
                  <span className="pa__ex-go">›</span>
                </div>
              </div>
              <div className="pa__trend">
                <div className="pa__trend-h">
                  <span>Function score</span>
                  <span className="pa__trend-v">
                    8.0 <small>▲</small>
                  </span>
                </div>
                <svg className="pa__trend-svg" viewBox="0 0 220 56" preserveAspectRatio="none">
                  <polyline
                    points="4,46 46,42 88,34 130,26 172,18 216,10"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="3"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
            </div>
          </div>
          <div className="chip chip--app float-b">
            <span className="chip__check sm">
              <svg viewBox="0 0 24 24">
                <path
                  d="M5 13l4 4L19 7"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.6"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </span>
            <div>
              <div className="chip__toast-title">Exercise logged</div>
              <div className="chip__toast-sub">Great work — keep it up</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PatientApp;

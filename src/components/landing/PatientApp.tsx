import patientPortalOverview from "@/assets/patient-portal-overview.png";

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
            Your patients see <span className="ser">their progress</span>, too
          </h2>
          <p className="section-sub section-sub--left">
            Progress doesn't stay locked in the clinic. Patients log in to their own secure web
            portal to check in on how they feel, see their results and recovery trajectory, and
            follow the exercises you've prescribed.
          </p>
          <ul className="patient__list">
            <li>
              <Tick />
              Guided PROMS check-ins — function &amp; pain
            </li>
            <li>
              <Tick />
              Their own results and recovery trajectory vs plan
            </li>
            <li>
              <Tick />
              Prescribed exercises with sets, reps and progressions
            </li>
            <li>
              <Tick />
              Works in any browser — no app install needed
            </li>
          </ul>
        </div>

        <div className="patient__stage reveal" data-delay="150">
          <div className="phone phone--shot float-slow">
            <div className="phone__screen">
              <div className="shot shot--patient">
                <img
                  src={patientPortalOverview}
                  alt="Benchmark patient portal overview: recovery phase and week, percentage of expected recovery with change since last session, a log-how-you-feel check-in prompt, assigned tests and today's exercises"
                />
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
              <div className="chip__toast-title">Check-in logged</div>
              <div className="chip__toast-sub">Function &amp; pain recorded</div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PatientApp;

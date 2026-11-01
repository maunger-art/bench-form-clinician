const WhoItsFor = () => {
  return (
    <section className="who" id="who">
      <div className="wrap">
        <div className="section-head reveal">
          <div className="eyebrow eyebrow--center">
            <span className="eyebrow__dash"></span>Who It's For
          </div>
          <h2 className="section-title">
            Built for <span className="ser">MSK professionals</span>
          </h2>
        </div>
        <div className="who__grid">
          <div className="who__card reveal" data-delay="0">
            <div className="who__ic">
              <svg viewBox="0 0 24 24">
                <path d="M4 21V6l7-3v18M14 21V10l6-2v13M3 21h18" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <h3>Private Clinics</h3>
            <p>Improve outcome transparency and clinical consistency across your practice.</p>
          </div>

          <div className="who__card reveal" data-delay="80">
            <div className="who__ic">
              <svg viewBox="0 0 24 24">
                <path d="M3 12h4l2 6 4-14 2 8h6" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <h3>Sports Medicine Teams</h3>
            <p>Monitor athlete recovery and performance benchmarks with objective data.</p>
          </div>

          <div className="who__card reveal" data-delay="160">
            <div className="who__ic">
              <svg viewBox="0 0 24 24">
                <path d="M6 3v6a6 6 0 0 0 12 0V3" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
                <path d="M12 15v3a3 3 0 0 0 6 0v-1" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
                <circle cx="18" cy="16" r="1.4" fill="currentColor" />
              </svg>
            </div>
            <h3>MSK Healthcare Providers</h3>
            <p>Standardise assessment and rehabilitation workflows across departments.</p>
          </div>

          <div className="who__card reveal" data-delay="240">
            <div className="who__ic">
              <svg viewBox="0 0 24 24">
                <path d="M6.5 9v6M17.5 9v6M4 10.5v3M20 10.5v3M6.5 12h11" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" />
              </svg>
            </div>
            <h3>Strength &amp; Conditioning Coaches</h3>
            <p>Objective testing and athlete monitoring to guide development and prevent injury.</p>
          </div>

          <div className="who__card reveal" data-delay="320">
            <div className="who__ic">
              <svg viewBox="0 0 24 24">
                <circle cx="12" cy="8" r="3.4" fill="none" stroke="currentColor" strokeWidth="1.7" />
                <path d="M5 20c0-3.5 3.1-5.5 7-5.5s7 2 7 5.5" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
                <path d="M16.5 8.5l1.3 1.3L20.5 7" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <h3>Personal Trainers</h3>
            <p>Track client progress using measurable, credible performance data.</p>
          </div>

          <div className="who__card who__card--cta reveal" data-delay="400">
            <h3>Not sure where you fit?</h3>
            <p>If you measure movement, strength or recovery, Benchmark was built for you.</p>
            <a href="#cta" className="who__link">
              Talk to us →
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhoItsFor;

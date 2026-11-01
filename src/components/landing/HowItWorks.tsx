const HowItWorks = () => {
  return (
    <section className="how" id="how">
      <div className="wrap">
        <div className="section-head reveal">
          <div className="eyebrow eyebrow--center">
            <span className="eyebrow__dash"></span>How It Works
          </div>
          <h2 className="section-title">
            Four steps to <span className="ser">measurable outcomes</span>
          </h2>
        </div>
        <div className="steps">
          <div className="steps__line" aria-hidden="true"></div>

          <div className="step reveal" data-delay="0">
            <div className="step__num">01</div>
            <div className="step__ic">
              <svg viewBox="0 0 24 24">
                <path d="M9 11l2 2 4-4" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
                <rect x="4" y="4" width="16" height="17" rx="2" fill="none" stroke="currentColor" strokeWidth="1.7" />
                <path d="M8 4V2.5M16 4V2.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
              </svg>
            </div>
            <h3>Assess</h3>
            <p>Collect objective patient data — range of movement, strength, endurance and power.</p>
          </div>

          <div className="step reveal" data-delay="120">
            <div className="step__num">02</div>
            <div className="step__ic">
              <svg viewBox="0 0 24 24">
                <path d="M5 20V10M12 20V4M19 20v-7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </div>
            <h3>Benchmark</h3>
            <p>Compare results against normative datasets matched for age, sex and sport.</p>
          </div>

          <div className="step reveal" data-delay="240">
            <div className="step__num">03</div>
            <div className="step__ic">
              <svg viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" strokeWidth="1.7" />
                <circle cx="12" cy="12" r="3.3" fill="none" stroke="currentColor" strokeWidth="1.7" />
                <circle cx="12" cy="12" r="0.6" fill="currentColor" stroke="currentColor" strokeWidth="1.4" />
              </svg>
            </div>
            <h3>Plan</h3>
            <p>Generate data-driven rehabilitation plans directly from the patient's results.</p>
          </div>

          <div className="step reveal" data-delay="360">
            <div className="step__num">04</div>
            <div className="step__ic">
              <svg viewBox="0 0 24 24">
                <path d="M4 16l5-5 3 3 7-7" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                <path d="M15 7h5v5" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            </div>
            <h3>Progress</h3>
            <p>Track patient improvement objectively across every stage of recovery.</p>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;

const FinalCTA = () => {
  return (
    <section className="cta" id="cta">
      <div className="wrap">
        <div className="cta__box reveal">
          <div className="cta__mesh" aria-hidden="true"></div>
          <div className="eyebrow eyebrow--center eyebrow--on-dark">
            <span className="eyebrow__dash"></span>Get Started
          </div>
          <h2 className="cta__title">
            Bring <span className="ser">measurable outcomes</span> to your clinic
          </h2>
          <p className="cta__sub">
            Join the growing number of MSK clinicians using objective data to improve patient care
            and demonstrate results. Free to get started in early access.
          </p>
          <div className="cta__btns">
            <a className="btn btn--primary" href="https://platform.benchmarkps.org/login?signup=true">
              Create Account
              <svg viewBox="0 0 24 24" className="ic">
                <path
                  d="M5 12h14M13 6l6 6-6 6"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </a>
            <a className="btn btn--ghost-light" href="https://calendly.com/benchmarkps-info/30min">
              Request a Demo
            </a>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FinalCTA;

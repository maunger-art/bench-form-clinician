const STATS = [
  { count: 100, suffix: "%", desc: "of clinicians would recommend Benchmark to a colleague" },
  { count: 83, suffix: "%", desc: "of patients showed measurable, objective improvement after treatment" },
  { count: 47, suffix: "%", desc: "achieved medium-to-large functional improvements vs baseline" },
  { count: 39, suffix: "%", desc: "more effective than standard physiotherapy in outcome comparison" },
];

const OutcomesSection = () => {
  return (
    <section className="outcomes" id="outcomes">
      <div className="wrap">
        <div className="section-head reveal">
          <div className="eyebrow eyebrow--center eyebrow--teal">
            <span className="eyebrow__dash"></span>Pilot Feedback
          </div>
          <h2 className="section-title">
            Early pilot feedback from <span className="ser">clinicians</span>
          </h2>
          <p className="section-sub">Results based on early pilot users of the Benchmark platform.</p>
          <p className="outcomes__note">
            Pilot data. Ongoing validation. Abbott 2014 criteria applied for effect size.
          </p>
        </div>

        <div className="stats">
          {STATS.map((s, i) => (
            <div className="stat reveal" data-delay={i * 100} key={i}>
              <div className="stat__num" data-count={s.count} data-suffix={s.suffix}>
                0{s.suffix}
              </div>
              <p>{s.desc}</p>
            </div>
          ))}
        </div>

        <figure className="quote reveal">
          <span className="quote__mark" aria-hidden="true">
            &ldquo;
          </span>
          <blockquote>
            I've been using the Benchmark system and have found it hugely beneficial to my own
            practice: maximising patient outcomes, patient buy-in to rehab and supporting my referral
            process onwards to consultants.
          </blockquote>
          <figcaption>
            <span className="quote__avatar">LT</span>
            <span>
              <strong>Lucas Taylor</strong>
              <small>Physiotherapist — Benchmark early adopter</small>
            </span>
          </figcaption>
        </figure>
      </div>
    </section>
  );
};

export default OutcomesSection;

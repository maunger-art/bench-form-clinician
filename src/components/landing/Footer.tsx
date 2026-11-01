import benchmarkIconNav from "@/assets/benchmark-icon-nav.png";

const Footer = () => {
  const year = new Date().getFullYear();
  return (
    <footer className="footer">
      <div className="wrap footer__inner">
        <div className="footer__brand">
          <a className="brand" href="#top" aria-label="Benchmark Performance Systems">
            <img className="brand__icon" src={benchmarkIconNav} alt="" />
            <span className="brand__text">
              <span className="brand__name">Benchmark</span>
              <span className="brand__sub">Performance Systems</span>
            </span>
          </a>
          <p className="footer__blurb">
            The clinical performance platform for measurable, provable musculoskeletal care.
          </p>
        </div>
        <div className="footer__cols">
          <div className="footer__col">
            <h5>Product</h5>
            <a href="#platform">Platform</a>
            <a href="#security">Security</a>
            <a href="#how">How It Works</a>
            <a href="#outcomes">Outcomes</a>
          </div>
          <div className="footer__col">
            <h5>Company</h5>
            <a href="#who">Who It's For</a>
            <a href="/blog">Blog</a>
            <a href="https://platform.benchmarkps.org/login">Login</a>
            <a href="#cta">Request Demo</a>
          </div>
          <div className="footer__col">
            <h5>Contact</h5>
            <a href="mailto:info@benchmarkps.org">info@benchmarkps.org</a>
            <a href="/privacy-policy">Privacy Policy</a>
            <a href="/terms-and-conditions">Terms &amp; Conditions</a>
          </div>
        </div>
      </div>
      <div className="wrap footer__bar">
        <span>© {year} Benchmark Performance Systems</span>
        <span className="footer__made">Built for clinicians, by clinicians</span>
      </div>
    </footer>
  );
};

export default Footer;

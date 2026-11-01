import { useState, useEffect } from "react";
import benchmarkIconNav from "@/assets/benchmark-icon-nav.png";

const NAV_LINKS = [
  { label: "Platform", href: "#platform" },
  { label: "Security", href: "#security" },
  { label: "How It Works", href: "#how" },
  { label: "Who It's For", href: "#who" },
  { label: "Outcomes", href: "#outcomes" },
];

const Brand = () => (
  <a className="brand" href="#top" aria-label="Benchmark Performance Systems">
    <img className="brand__icon" src={benchmarkIconNav} alt="" />
    <span className="brand__text">
      <span className="brand__name">Benchmark</span>
      <span className="brand__sub">Performance Systems</span>
    </span>
  </a>
);

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  const closeMobile = () => setMobileOpen(false);

  return (
    // Single sticky stack in normal flow: banner + nav. No fixed positioning,
    // so the nav always reserves its own space below the (wrap-able) banner.
    <header className="site-header" id="siteHeader">
      <div className="eab">
        <span>
          <strong>Now in early access — free to get started.</strong> Join physiotherapy clinics
          already measuring outcomes with Benchmark.
        </span>
        <a className="eab__btn" href="https://platform.benchmarkps.org/login?signup=true">
          Create Account &rarr;
        </a>
      </div>
      <nav className={`nav${scrolled ? " scrolled" : ""}`} id="nav">
        <div className="nav__inner">
          <Brand />
          <div className="nav__links">
            {NAV_LINKS.map((l) => (
              <a key={l.href} href={l.href}>
                {l.label}
              </a>
            ))}
            <a className="nav__login" href="https://platform.benchmarkps.org/login">
              Login
            </a>
            <a className="nav__cta" href="#cta">
              Request Demo
            </a>
          </div>
          <button
            className={`nav__toggle${mobileOpen ? " open" : ""}`}
            aria-label="Menu"
            aria-expanded={mobileOpen}
            onClick={() => setMobileOpen((o) => !o)}
          >
            <span></span>
            <span></span>
            <span></span>
          </button>
        </div>
        <div className={`nav__mobile${mobileOpen ? " open" : ""}`} id="navMobile">
          {NAV_LINKS.map((l) => (
            <a key={l.href} href={l.href} onClick={closeMobile}>
              {l.label}
            </a>
          ))}
          <a href="https://platform.benchmarkps.org/login" onClick={closeMobile}>
            Login
          </a>
          <a className="nav__mobile-cta" href="#cta" onClick={closeMobile}>
            Request Demo
          </a>
        </div>
      </nav>
    </header>
  );
};

export default Navbar;

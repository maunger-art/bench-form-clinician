import { useEffect, useRef, useState } from "react";
import screenshotAnalyticsFull from "@/assets/screenshot-analytics-full.png";

const TOUR_VIDEO_SRC = "/media/bps-platform-tour.mp4";

// Hero waveform chip — heights/delays mirror the approved concept (app.js).
const HERO_WAVE = [6, 12, 20, 14, 22, 9, 16, 11, 7];

const Hero = () => {
  const [videoOpen, setVideoOpen] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Autoplay on open, pause (and reset) on close.
  useEffect(() => {
    const v = videoRef.current;
    if (!v) return;
    if (videoOpen) {
      v.play().catch(() => {});
    } else {
      v.pause();
    }
  }, [videoOpen]);

  // Escape closes the modal.
  useEffect(() => {
    if (!videoOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setVideoOpen(false);
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [videoOpen]);

  return (
    <section className="hero">
      <div className="hero__mesh" aria-hidden="true"></div>
      <div className="hero__grid-tex" aria-hidden="true"></div>
      <div className="wrap hero__inner">
        <div className="hero__copy reveal">
          <div className="eyebrow">
            <span className="eyebrow__dash"></span>Clinical Performance Platform
          </div>
          <h1 className="hero__title">
            Progress You Can <span className="ser">Measure.</span>
            <br />
            Care You Can <span className="ser">Prove.</span>
          </h1>
          <p className="hero__lede">
            Benchmark is a clinical performance platform that lets physiotherapists objectively
            measure patient progress, benchmark results against normative data, and generate
            data-driven rehabilitation plans — with the evidence to prove every outcome.
          </p>
          <ul className="hero__ticks">
            <li>Objective strength &amp; performance benchmarking</li>
            <li>AI clinical reports with secure share links</li>
            <li>Structured, measurable progress tracking</li>
          </ul>
          <div className="hero__cta">
            <button
              type="button"
              className="btn btn--ghost"
              id="watchDemo"
              onClick={() => setVideoOpen(true)}
            >
              <svg viewBox="0 0 24 24" className="ic">
                <path d="M8 5v14l11-7z" />
              </svg>
              Watch Demo
            </button>
            <a className="btn btn--primary" href="#cta">
              <svg viewBox="0 0 24 24" className="ic">
                <path
                  d="M7 11h10M7 15h6M5 3h14a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H9l-4 4V5a2 2 0 0 1 2-2z"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
              Request Demo
            </a>
          </div>
        </div>

        <div className="hero__stage reveal" data-delay="150">
          <div className="browser hero__browser tilt">
            <div className="browser__bar">
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="dot"></span>
              <span className="browser__url">platform.benchmarkps.org</span>
            </div>
            <div className="browser__body">
              <div className="shot shot--analytics">
                <img
                  src={screenshotAnalyticsFull}
                  alt="Benchmark performance analytics dashboard: left vs right strength and range-of-movement benchmarked against expected scores"
                />
              </div>
            </div>
          </div>

          {/* floating chips */}
          <div className="chip chip--stat float-a">
            <div className="chip__label">Knee flexion · Right</div>
            <div className="chip__big">
              130°<span className="chip__delta up">+44%</span>
            </div>
            <div className="chip__spark">
              <svg viewBox="0 0 80 28" preserveAspectRatio="none">
                <polyline
                  points="0,24 16,20 32,18 48,10 64,8 80,3"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2.5"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </div>
          </div>

          <div className="chip chip--toast float-b">
            <span className="chip__check">
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
              <div className="chip__toast-title">Report shared with GP</div>
              <div className="chip__toast-sub">Secure link · expires in 7 days</div>
            </div>
          </div>

          <div className="chip chip--wave float-c">
            <span className="rec-dot"></span>
            <div className="wave" id="heroWave" aria-hidden="true">
              {HERO_WAVE.map((h, i) => (
                <span
                  key={i}
                  style={{ height: `${h}px`, animationDelay: `${(i * 0.07).toFixed(2)}s` }}
                />
              ))}
            </div>
            <span className="chip__time">01:48</span>
          </div>
        </div>
      </div>

      {/* demo video modal — native <video>, autoplay on open, pause on close */}
      <div className={`modal${videoOpen ? " open" : ""}`} id="demoModal" aria-hidden={!videoOpen}>
        <div className="modal__backdrop" onClick={() => setVideoOpen(false)}></div>
        <div className="modal__box" role="dialog" aria-label="Demo video">
          <button
            className="modal__close"
            aria-label="Close"
            onClick={() => setVideoOpen(false)}
          >
            ×
          </button>
          <div className="modal__inner">
            <video
              ref={videoRef}
              controls
              playsInline
              preload="metadata"
              style={{ width: "100%", height: "100%", display: "block", background: "#0A2C4F" }}
            >
              <source src={TOUR_VIDEO_SRC} type="video/mp4" />
            </video>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;

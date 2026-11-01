import { useEffect } from "react";

/**
 * Drives the facelift's scroll-reveal, stat count-up and patient-ring
 * animations by observing DOM nodes (class `.reveal`, attribute `[data-count]`,
 * id `paRing`). Mirrors the approved concept's app.js. Fully respects
 * prefers-reduced-motion: reveals show immediately and counters snap to their
 * final value with no animation.
 */
export function useFaceliftEffects() {
  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    // ---------- scroll reveal ----------
    const reveals = Array.from(document.querySelectorAll<HTMLElement>(".reveal"));
    let io: IntersectionObserver | null = null;
    if (reduce || !("IntersectionObserver" in window)) {
      reveals.forEach((el) => el.classList.add("in"));
    } else {
      io = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) {
              const el = e.target as HTMLElement;
              const d = parseInt(el.getAttribute("data-delay") || "0", 10);
              window.setTimeout(() => el.classList.add("in"), d);
              io!.unobserve(el);
            }
          });
        },
        { threshold: 0.12, rootMargin: "0px 0px -8% 0px" }
      );
      reveals.forEach((el) => io!.observe(el));
    }

    // ---------- count-up ----------
    const animateCount = (el: HTMLElement) => {
      const target = parseFloat(el.getAttribute("data-count") || "0") || 0;
      const suffix = el.getAttribute("data-suffix") || "";
      if (reduce) {
        el.textContent = target + suffix;
        return;
      }
      const dur = 1500;
      let start: number | null = null;
      const tick = (ts: number) => {
        if (start === null) start = ts;
        const p = Math.min((ts - start) / dur, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = Math.round(target * eased) + suffix;
        if (p < 1) requestAnimationFrame(tick);
        else el.textContent = target + suffix;
      };
      requestAnimationFrame(tick);
    };
    const counters = Array.from(document.querySelectorAll<HTMLElement>("[data-count]"));
    let cio: IntersectionObserver | null = null;
    if (!("IntersectionObserver" in window)) {
      counters.forEach(animateCount);
    } else {
      cio = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) {
              animateCount(e.target as HTMLElement);
              cio!.unobserve(e.target);
            }
          });
        },
        { threshold: 0.5 }
      );
      counters.forEach((el) => cio!.observe(el));
    }

    // ---------- patient progress ring ----------
    const ring = document.getElementById("paRing") as unknown as SVGCircleElement | null;
    let rio: IntersectionObserver | null = null;
    if (ring) {
      // 78% of circumference 314 -> offset 314 * (1 - .78)
      rio = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (e.isIntersecting) {
              ring.style.strokeDashoffset = String(314 * 0.22);
              rio!.unobserve(e.target);
            }
          });
        },
        { threshold: 0.4 }
      );
      rio.observe(ring);
    }

    return () => {
      io?.disconnect();
      cio?.disconnect();
      rio?.disconnect();
    };
  }, []);
}

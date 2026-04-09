import { motion, useInView } from "framer-motion";
import { useRef } from "react";

const stats = [
  { value: "100%", desc: "of clinicians would recommend Benchmark to a colleague" },
  { value: "83%", desc: "of patients showed measurable, objective improvement after treatment" },
  { value: "47%", desc: "achieved medium-to-large functional improvements vs baseline" },
  { value: "39%", desc: "more effective than standard physiotherapy in outcome comparison" },
];

const OutcomesSection = () => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="outcomes" className="bg-warm py-16 sm:py-24 md:py-32" ref={ref}>
      <div className="max-w-[1180px] mx-auto px-5 sm:px-6 md:px-12">
        {/* Part A — Intro */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center max-w-[760px] mx-auto mb-12 sm:mb-16"
        >
          <div className="flex items-center gap-2 justify-center mb-5">
            <div className="w-5 h-[2px] bg-teal rounded" />
            <span className="text-teal text-xs font-bold tracking-[0.14em] uppercase">
              Pilot Feedback
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-[44px] leading-[1.18] font-bold text-foreground mb-5">
            Early pilot feedback from{" "}
            <em className="font-editorial italic">clinicians</em>
          </h2>
          <p className="text-base sm:text-[17px] font-light text-mid leading-relaxed mb-3">
            Results based on early pilot users of the Benchmark platform.
          </p>
          <p className="text-xs italic text-mid/60 font-light">
            Pilot data. Ongoing validation. Abbott 2014 criteria applied for effect size.
          </p>
        </motion.div>

        {/* Part B — Four stat cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-12 sm:mb-16">
          {stats.map((s, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 24 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.15 * i, duration: 0.5 }}
              className="bg-card rounded-2xl shadow-sm hover:-translate-y-1 hover:shadow-md transition-all duration-300"
              style={{
                borderTop: "3px solid transparent",
                borderImage: "linear-gradient(90deg, hsl(var(--blue)), hsl(var(--blue-mid))) 1",
                borderImageSlice: 1,
                padding: "36px 28px",
              }}
            >
              <p className="font-editorial text-foreground mb-3" style={{ fontSize: "clamp(36px, 4vw, 48px)" }}>
                {s.value}
              </p>
              <p className="text-sm text-mid font-light leading-relaxed">{s.desc}</p>
            </motion.div>
          ))}
        </div>

        {/* Part C — Testimonial block */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="relative overflow-hidden"
          style={{
            background: "hsl(var(--navy))",
            borderRadius: "20px",
            borderLeft: "4px solid hsl(var(--blue-mid))",
            padding: "clamp(40px, 5vw, 64px) clamp(32px, 5vw, 72px)",
          }}
        >
          {/* Decorative quote mark */}
          <span
            className="absolute top-6 right-8 font-editorial pointer-events-none select-none"
            style={{ fontSize: "140px", color: "rgba(255,255,255,0.04)", lineHeight: 1 }}
            aria-hidden="true"
          >
            "
          </span>

          <p
            className="font-editorial italic text-primary-foreground relative z-10 mb-8"
            style={{
              fontSize: "clamp(20px, 2.2vw, 26px)",
              lineHeight: 1.55,
              maxWidth: "820px",
            }}
          >
            "I've been using the Benchmark system and have found it hugely beneficial to my own
            practice: maximising patient outcomes, patient buy-in to rehab and supporting my
            referral process onwards to consultants."
          </p>

          <div className="flex items-center gap-3 relative z-10">
            <div
              className="flex items-center justify-center rounded-full font-editorial text-primary-foreground font-bold"
              style={{
                width: "44px",
                height: "44px",
                background: "hsl(var(--blue-mid))",
                fontSize: "15px",
              }}
            >
              LT
            </div>
            <div>
              <p className="text-primary-foreground font-bold" style={{ fontSize: "15px" }}>
                Lucas Taylor
              </p>
              <p style={{ fontSize: "13px", color: "rgba(255,255,255,0.5)" }}>
                Physiotherapist — Benchmark early adopter
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default OutcomesSection;

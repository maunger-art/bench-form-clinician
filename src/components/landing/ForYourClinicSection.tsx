import { motion, useInView } from "framer-motion";
import { useRef } from "react";

const leftStats = [
  { value: "1 in 5", desc: "patients don't return after their first appointment" },
  { value: "DNA", desc: "rates cost UK clinics an estimated £1B+ annually" },
  { value: "39%", desc: "of patients disengage when they can't see progress" },
];

const ForYourClinicSection = () => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section className="bg-card py-16 sm:py-24 md:py-32" ref={ref}>
      <div className="max-w-[1180px] mx-auto px-5 sm:px-6 md:px-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center max-w-[760px] mx-auto mb-12 sm:mb-16"
        >
          <div className="flex items-center gap-2 justify-center mb-5">
            <div className="w-5 h-[2px] bg-teal rounded" />
            <span className="text-teal text-xs font-bold tracking-[0.14em] uppercase">
              For Your Clinic
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-[44px] leading-[1.18] font-bold text-foreground mb-5">
            Better outcomes, better retention
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8 md:gap-12 items-start">
          {/* Left — Stats */}
          <motion.div
            initial={{ opacity: 0, x: -32 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.1 }}
          >
            <p className="text-base sm:text-[17px] font-light text-mid leading-relaxed mb-8">
              Patient disengagement is the hidden cost of every physiotherapy clinic. When patients
              can't see where they're going, they stop showing up.
            </p>
            <div className="space-y-6">
              {leftStats.map((s, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -16 }}
                  animate={inView ? { opacity: 1, x: 0 } : {}}
                  transition={{ delay: 0.3 + i * 0.12, duration: 0.5 }}
                  className="flex items-start gap-4"
                >
                  <span className="font-editorial text-foreground font-semibold text-xl min-w-[60px]">
                    {s.value}
                  </span>
                  <span className="text-sm text-mid font-light leading-relaxed pt-1">{s.desc}</span>
                </motion.div>
              ))}
            </div>
          </motion.div>

          {/* Right — Retention visual (dark navy block) */}
          <motion.div
            initial={{ opacity: 0, x: 32 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="rounded-[20px] h-full"
            style={{ background: "hsl(var(--navy))", padding: "40px 44px" }}
          >
            {/* Title */}
            <p
              className="uppercase font-semibold mb-6"
              style={{
                color: "rgba(255,255,255,0.5)",
                fontSize: "12px",
                letterSpacing: "0.06em",
              }}
            >
              Patient Retention Comparison
            </p>

            {/* Without Benchmark bar */}
            <div className="mb-2">
              <div className="flex items-center justify-between mb-2">
                <span style={{ color: "rgba(255,255,255,0.5)", fontSize: "13px" }}>
                  Without Benchmark
                </span>
                <span className="font-editorial text-primary-foreground" style={{ fontSize: "22px" }}>
                  61%
                </span>
              </div>
              <div className="h-3 rounded-full" style={{ background: "rgba(255,255,255,0.1)" }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={inView ? { width: "61%" } : {}}
                  transition={{ delay: 0.5, duration: 1, ease: "easeOut" }}
                  className="h-full rounded-full"
                  style={{ background: "rgba(255,255,255,0.2)" }}
                />
              </div>
            </div>

            {/* Divider */}
            <div className="my-5" style={{ height: "1px", background: "rgba(255,255,255,0.08)" }} />

            {/* With Benchmark bar */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span style={{ color: "hsl(var(--blue-mid))", fontSize: "13px" }}>
                  With Benchmark
                </span>
                <span className="font-editorial text-primary-foreground" style={{ fontSize: "22px" }}>
                  89%
                </span>
              </div>
              <div className="h-3 rounded-full" style={{ background: "rgba(255,255,255,0.1)" }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={inView ? { width: "89%" } : {}}
                  transition={{ delay: 0.7, duration: 1, ease: "easeOut" }}
                  className="h-full rounded-full"
                  style={{
                    background: "linear-gradient(90deg, hsl(var(--blue)), hsl(var(--blue-mid)))",
                  }}
                />
              </div>
            </div>

            {/* Mini stat cards */}
            <div className="grid grid-cols-2 gap-3 mb-6">
              <div className="rounded-xl p-4" style={{ background: "rgba(255,255,255,0.08)" }}>
                <p className="font-editorial text-primary-foreground mb-1" style={{ fontSize: "22px" }}>
                  47%
                </p>
                <p className="text-primary-foreground text-xs font-light leading-relaxed">
                  fewer missed appointments
                </p>
              </div>
              <div className="rounded-xl p-4" style={{ background: "rgba(255,255,255,0.08)" }}>
                <p className="font-editorial text-primary-foreground mb-1" style={{ fontSize: "22px" }}>
                  100%
                </p>
                <p className="text-primary-foreground text-xs font-light leading-relaxed">
                  clinician recommendation rate
                </p>
              </div>
            </div>

            {/* Bottom block */}
            <div>
              <p className="font-semibold text-xs mb-1" style={{ color: "hsl(var(--blue-mid))" }}>
                The bottom line
              </p>
              <p className="text-primary-foreground text-sm font-medium leading-relaxed">
                Patients who can see their progress stay engaged longer
              </p>
              <p className="text-xs mt-1" style={{ color: "rgba(255,255,255,0.5)" }}>
                Based on pilot data from Benchmark-enabled clinics
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default ForYourClinicSection;

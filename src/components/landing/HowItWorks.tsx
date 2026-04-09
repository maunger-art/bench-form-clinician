import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { ClipboardCheck, BarChart, Target, TrendingUp } from "lucide-react";

const steps = [
  {
    icon: ClipboardCheck,
    num: "01",
    title: "Assess",
    desc: "Collect objective patient data including range of motion, strength, endurance and power.",
  },
  {
    icon: BarChart,
    num: "02",
    title: "Benchmark",
    desc: "Compare results against normative datasets matched for age, sex and sport.",
  },
  {
    icon: Target,
    num: "03",
    title: "Plan",
    desc: "Generate data-driven rehabilitation plans directly from the patient's test results.",
  },
  {
    icon: TrendingUp,
    num: "04",
    title: "Progress",
    desc: "Track patient improvement objectively across every stage of recovery.",
  },
];

const HowItWorks = () => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="how-it-works" className="bg-card py-16 sm:py-24 md:py-32" ref={ref}>
      <div className="max-w-[1180px] mx-auto px-5 sm:px-6 md:px-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center max-w-[720px] mx-auto mb-12 sm:mb-16"
        >
          <div className="flex items-center gap-2 justify-center mb-5">
            <div className="w-5 h-[2px] bg-brand-blue rounded" />
            <span className="text-brand-blue text-xs font-bold tracking-[0.14em] uppercase">
              How It Works
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-[44px] leading-[1.18] font-bold text-foreground">
            Four steps to measurable outcomes
          </h2>
        </motion.div>

        <div className="relative grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8">
          {/* Connecting line */}
          <div className="hidden md:block absolute top-[60px] left-[12.5%] right-[12.5%] h-[2px] border-t-2 border-dashed border-sand" />

          {steps.map((s, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.15 * i, duration: 0.5 }}
              className="relative text-center md:[&]:mt-[var(--stagger)]"
              style={{ "--stagger": `${i * 12}px` } as React.CSSProperties}
            >
              <div className="w-20 h-20 sm:w-[100px] sm:h-[100px] md:w-[120px] md:h-[120px] rounded-2xl bg-warm border border-sand/50 flex flex-col items-center justify-center mx-auto mb-4 sm:mb-6 relative z-10">
                <span className="text-xs font-bold text-brand-blue tracking-wider mb-1">{s.num}</span>
                <s.icon className="w-6 h-6 sm:w-7 sm:h-7 md:w-8 md:h-8 text-foreground" />
              </div>
              {/* Teal pulse dot */}
              <motion.div
                initial={{ scale: 0 }}
                animate={inView ? { scale: 1 } : {}}
                transition={{ delay: 0.3 + i * 0.2, duration: 0.3 }}
                className="hidden md:block absolute top-[59px] left-1/2 -translate-x-1/2 w-3 h-3 bg-teal rounded-full z-20 shadow-md shadow-teal/40"
              />
              <h3 className="text-base sm:text-lg font-semibold text-foreground mb-2">{s.title}</h3>
              <p className="text-xs sm:text-sm text-mid font-light leading-relaxed max-w-[220px] mx-auto">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;

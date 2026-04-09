import { motion, useInView } from "framer-motion";
import { useRef } from "react";

const ProblemSection = () => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  const stats = [
    { value: "1.7B", label: "people affected by MSK conditions globally" },
    { value: "60%", label: "of outcomes vary significantly between clinicians" },
    { value: "83%", label: "of rehabilitation based on subjective improvement" },
  ];

  return (
    <section className="bg-card py-16 sm:py-24 md:py-32" ref={ref}>
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
              The Challenge
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-[44px] leading-[1.18] font-bold text-foreground mb-5">
            Musculoskeletal care is rarely measured properly
          </h2>
          <p className="text-base sm:text-[17px] font-light text-mid leading-relaxed">
            Patients struggle to understand their progress. Clinicians lack objective tools
            to demonstrate improvement.
          </p>
        </motion.div>

        {/* Stats */}
        <div className="grid sm:grid-cols-3 gap-4 sm:gap-6 mb-12 sm:mb-16">
          {stats.map((s, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.15 * i, duration: 0.5 }}
              className="bg-warm rounded-2xl p-6 sm:p-8 text-center border border-sand/50"
            >
              <p className="text-3xl sm:text-4xl md:text-5xl font-bold text-foreground mb-3">{s.value}</p>
              <p className="text-sm text-mid font-light leading-relaxed">{s.label}</p>
            </motion.div>
          ))}
        </div>

        {/* Key message */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ delay: 0.5, duration: 0.6 }}
          className="text-center max-w-[700px] mx-auto"
        >
          <blockquote className="font-editorial italic text-lg sm:text-xl md:text-2xl text-foreground leading-relaxed">
            "Without objective benchmarking, clinicians cannot easily demonstrate improvement."
          </blockquote>
        </motion.div>
      </div>
    </section>
  );
};

export default ProblemSection;

import { motion, useInView } from "framer-motion";
import { useRef } from "react";

const TrustSection = () => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  const logos = [
    "Elite Sports Clinic",
    "PhysioFirst",
    "MSK Research Lab",
    "Performance Medicine",
    "National Sports Institute",
    "Rehab Sciences Group",
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
              Trusted By Clinicians
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-[40px] leading-[1.18] font-bold text-foreground mb-5">
            Built by clinicians working in elite sport, private practice, and performance medicine
          </h2>
        </motion.div>

        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
          {logos.map((name, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0 }}
              animate={inView ? { opacity: 1 } : {}}
              transition={{ delay: 0.08 * i, duration: 0.4 }}
              className="bg-warm rounded-xl p-4 sm:p-6 flex items-center justify-center border border-sand/30"
            >
              <span className="text-xs font-semibold text-mid tracking-wider text-center uppercase">
                {name}
              </span>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default TrustSection;

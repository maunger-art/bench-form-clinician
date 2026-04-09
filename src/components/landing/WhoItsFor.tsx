import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { Building2, Activity, Stethoscope, Dumbbell, UserCheck } from "lucide-react";

const segments = [
  {
    icon: Building2,
    title: "Private Clinics",
    desc: "Improve outcome transparency and clinical consistency across your practice.",
  },
  {
    icon: Activity,
    title: "Sports Medicine Teams",
    desc: "Monitor athlete recovery and performance benchmarks with objective data.",
  },
  {
    icon: Stethoscope,
    title: "MSK Healthcare Providers",
    desc: "Standardise assessment and rehabilitation workflows across departments.",
  },
  {
    icon: Dumbbell,
    title: "Strength & Conditioning Coaches",
    desc: "Objective testing and athlete monitoring tools to guide strength development and injury prevention.",
  },
  {
    icon: UserCheck,
    title: "Personal Trainers",
    desc: "Track client progress using measurable performance data.",
  },
];

const WhoItsFor = () => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="who" className="bg-warm py-16 sm:py-24 md:py-32" ref={ref}>
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
              Who It's For
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-[44px] leading-[1.18] font-bold text-foreground">
            Built for MSK professionals
          </h2>
        </motion.div>

        <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4 sm:gap-6">
          {segments.map((s, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.12 * i, duration: 0.5 }}
              className="bg-card rounded-2xl p-6 sm:p-8 border border-sand/50 shadow-sm text-center hover:shadow-md hover:-translate-y-1 transition-all duration-300"
            >
              <div className="w-14 h-14 rounded-2xl bg-navy flex items-center justify-center mx-auto mb-6">
                <s.icon className="w-7 h-7 text-primary-foreground" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-3">{s.title}</h3>
              <p className="text-sm text-mid font-light leading-relaxed">{s.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default WhoItsFor;

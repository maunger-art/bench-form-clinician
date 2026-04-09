import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { BarChart3, FileText, ClipboardList, TrendingUp } from "lucide-react";

const features = [
  {
    icon: BarChart3,
    title: "Clinical Benchmarking",
    desc: "Compare patient performance against validated normative datasets.",
  },
  {
    icon: FileText,
    title: "AI Clinical Notes",
    desc: "Generate structured SOAP notes and reports from consultation transcripts.",
  },
  {
    icon: ClipboardList,
    title: "Rehabilitation Planning",
    desc: "Evidence-informed exercise and progression planning.",
  },
  {
    icon: TrendingUp,
    title: "Patient Progress Tracking",
    desc: "Visual dashboards showing measurable improvement over time.",
  },
];

const SolutionSection = () => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="solution" className="bg-warm py-16 sm:py-24 md:py-32" ref={ref}>
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
              The Solution
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-[44px] leading-[1.18] font-bold text-foreground mb-5">
            Benchmarking brings clarity to rehabilitation
          </h2>
          <p className="text-base sm:text-[17px] font-light text-mid leading-relaxed max-w-[600px] mx-auto">
            Assess deficits, track progress objectively, compare to normative data,
            and guide rehabilitation decisions — all in one platform.
          </p>
        </motion.div>

        <div className="grid sm:grid-cols-2 gap-4 sm:gap-6">
          {features.map((f, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.1 * i, duration: 0.5 }}
              className="bg-card rounded-2xl p-6 sm:p-8 border border-sand/50 shadow-sm hover:shadow-md hover:-translate-y-1 transition-all duration-300"
            >
              <div className="w-12 h-12 rounded-xl bg-brand-blue/10 flex items-center justify-center mb-5">
                <f.icon className="w-6 h-6 text-brand-blue" />
              </div>
              <h3 className="text-lg font-semibold text-foreground mb-2">{f.title}</h3>
              <p className="text-sm text-mid font-light leading-relaxed">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default SolutionSection;

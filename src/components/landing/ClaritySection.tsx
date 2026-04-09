import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { BarChart3, Route, TrendingUp, CheckCircle2 } from "lucide-react";

const features = [
  {
    icon: BarChart3,
    title: "Objective Baselines",
    desc: "Capture measurable starting points from day one",
  },
  {
    icon: Route,
    title: "Rehabilitation Roadmap",
    desc: "Visual timelines grounded in clinical benchmarks",
  },
  {
    icon: TrendingUp,
    title: "Real-Time Progress",
    desc: "Track improvement against normative data",
  },
  {
    icon: CheckCircle2,
    title: "Clear Discharge Criteria",
    desc: "Evidence-based milestones everyone can see",
  },
];

const bullets = [
  "Objective, measurable baselines from day one",
  "Personalised rehabilitation roadmaps for every patient",
  "Real-time progress tracking against clinical benchmarks",
  "Clear discharge criteria everyone can see",
];

const ClaritySection = () => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section className="bg-card py-16 sm:py-24 md:py-32" ref={ref}>
      <div className="max-w-[1180px] mx-auto px-5 sm:px-6 md:px-12">
        {/* Section label */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center max-w-[760px] mx-auto mb-12 sm:mb-16"
        >
          <div className="flex items-center gap-2 justify-center mb-5">
            <div className="w-5 h-[2px] bg-teal rounded" />
            <span className="text-teal text-xs font-bold tracking-[0.14em] uppercase">
              What Clarity Looks Like
            </span>
          </div>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8 md:gap-12 items-start">
          {/* Left — Icon-driven feature grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {features.map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.15 + i * 0.1, duration: 0.5 }}
                className="bg-card rounded-2xl border border-sand/50 shadow-sm p-6 hover:shadow-md hover:-translate-y-0.5 transition-all duration-300"
              >
                <div className="w-11 h-11 rounded-full bg-teal/10 flex items-center justify-center mb-4">
                  <f.icon className="w-5 h-5 text-teal" />
                </div>
                <h3 className="text-[15px] font-semibold text-foreground mb-1">{f.title}</h3>
                <p className="text-[13px] font-light text-mid leading-relaxed">{f.desc}</p>
              </motion.div>
            ))}
          </div>

          {/* Right — Copy */}
          <motion.div
            initial={{ opacity: 0, x: 32 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="flex flex-col justify-center"
          >
            <h2 className="text-2xl sm:text-3xl md:text-[40px] leading-[1.18] font-bold text-foreground mb-5">
              Replace guesswork with a clear, measurable roadmap
            </h2>
            <p className="text-base sm:text-[17px] font-light text-mid leading-relaxed mb-8">
              Benchmark gives every patient a visual rehabilitation timeline — grounded in objective data,
              updated in real time, and shared between clinician and patient.
            </p>
            <ul className="space-y-4">
              {bullets.map((b, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, x: 16 }}
                  animate={inView ? { opacity: 1, x: 0 } : {}}
                  transition={{ delay: 0.4 + i * 0.1, duration: 0.5 }}
                  className="flex items-start gap-3"
                >
                  <div className="w-5 h-5 rounded-full bg-teal/10 flex items-center justify-center mt-0.5 flex-shrink-0">
                    <div className="w-2 h-2 rounded-full bg-teal" />
                  </div>
                  <span className="text-sm sm:text-[15px] text-foreground font-medium leading-relaxed">
                    {b}
                  </span>
                </motion.li>
              ))}
            </ul>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default ClaritySection;

import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { Smartphone, Settings, Layers, Scale } from "lucide-react";

const points = [
  {
    icon: Smartphone,
    title: "Low-Tech to High-Tech",
    desc: "Use simple clinical tests, handheld tools, or advanced performance equipment — all within one platform.",
  },
  {
    icon: Layers,
    title: "Standardised Across Setups",
    desc: "Consistent data capture whether you're a solo clinician, a private practice, or a sports medicine team.",
  },
  {
    icon: Scale,
    title: "Meaningful Without Expensive Equipment",
    desc: "Start collecting objective rehabilitation data with the tools you already have — no premium lab required.",
  },
  {
    icon: Settings,
    title: "Scalable Objective Care",
    desc: "Grow your measurement capabilities over time without overhauling your clinic setup or workflow.",
  },
];

const AccessibleTestingSection = () => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section className="bg-navy py-16 sm:py-24 md:py-32 relative overflow-hidden" ref={ref}>
      {/* Subtle background pattern */}
      <div
        className="absolute inset-0 opacity-[0.04] pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(circle at 1px 1px, hsl(var(--blue-mid)) 1px, transparent 0)",
          backgroundSize: "40px 40px",
        }}
      />

      <div className="max-w-[1180px] mx-auto px-5 sm:px-6 md:px-12 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          {/* Left — messaging */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
          >
            <div className="flex items-center gap-2 mb-5">
              <div className="w-5 h-[2px] bg-brand-blue-mid rounded" />
              <span className="text-brand-blue-mid text-xs font-bold tracking-[0.14em] uppercase">
                Accessible Data Collection
              </span>
            </div>

            <h2 className="text-2xl sm:text-3xl md:text-[40px] leading-[1.18] font-bold text-primary-foreground mb-5">
              Objective measurement without{" "}
              <span className="font-editorial italic font-normal text-brand-blue-mid">expensive hardware</span>
            </h2>

            <p className="text-base sm:text-[17px] font-light text-primary-foreground/60 leading-relaxed mb-6">
              Benchmark PS enables clinicians to collect and use meaningful rehabilitation data
              whether they work with simple clinical tests, handheld tools, or advanced performance
              equipment.
            </p>
            <p className="text-base sm:text-[17px] font-light text-primary-foreground/60 leading-relaxed">
              This makes objective assessment more accessible, more scalable, and more practical
              across real-world MSK care — from solo practitioners to elite sport environments.
            </p>
          </motion.div>

          {/* Right — feature points */}
          <div className="grid sm:grid-cols-2 gap-4">
            {points.map((p, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ delay: 0.1 + i * 0.1, duration: 0.5 }}
                className="bg-primary-foreground/[0.05] border border-primary-foreground/10 rounded-2xl p-5 sm:p-6 hover:bg-primary-foreground/[0.08] transition-colors duration-300"
              >
                <div className="w-10 h-10 rounded-xl bg-brand-blue-mid/20 flex items-center justify-center mb-4">
                  <p.icon className="w-5 h-5 text-brand-blue-mid" />
                </div>
                <h3 className="text-[15px] font-semibold text-primary-foreground mb-2">{p.title}</h3>
                <p className="text-sm font-light text-primary-foreground/50 leading-relaxed">{p.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default AccessibleTestingSection;

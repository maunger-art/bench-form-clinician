import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import screenshotResultsFull from "@/assets/screenshot-results-full.png";
import screenshotAnalyticsFull from "@/assets/screenshot-analytics-full.png";
import screenshotSymptomsFull from "@/assets/screenshot-symptoms-full.png";
import screenshotSoapNoteFull from "@/assets/screenshot-soap-note-full.png";

const screenshots = [
  {
    src: screenshotResultsFull,
    alt: "Patient testing results table showing strength, ROM, endurance and power measurements with expected vs actual values",
    caption: "Objective Testing Results",
    desc: "View patient performance data across strength, range of motion, endurance, and power — compared against expected normative values.",
  },
  {
    src: screenshotAnalyticsFull,
    alt: "Performance analytics bar chart showing left vs right comparison as percentage of expected score across all tests",
    caption: "Visual Performance Analytics",
    desc: "Identify deficits and asymmetries instantly with clear visual benchmarking against age- and sport-specific norms.",
  },
  {
    src: screenshotSymptomsFull,
    alt: "Symptoms graph tracking Function Score and Pain Score over time with projected function progression",
    caption: "Progress Tracking Over Time",
    desc: "Monitor patient recovery journey with visual trend analysis showing function improvement and pain reduction.",
  },
  {
    src: screenshotSoapNoteFull,
    alt: "AI-generated SOAP note from clinical recording session with subjective history and assessment details",
    caption: "AI-Generated Clinical Notes",
    desc: "Turn consultation recordings into structured SOAP notes, patient summaries, and onward referrals — automatically.",
  },
];

const ProductShowcase = () => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section className="bg-navy py-16 sm:py-24 md:py-32" ref={ref}>
      <div className="max-w-[1400px] mx-auto px-5 sm:px-6 md:px-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="text-center max-w-[720px] mx-auto mb-12 sm:mb-16"
        >
          <div className="flex items-center gap-2 justify-center mb-5">
            <div className="w-5 h-[2px] bg-brand-blue-mid rounded" />
            <span className="text-brand-blue-mid text-xs font-bold tracking-[0.14em] uppercase">
              The Platform
            </span>
          </div>
          <h2 className="text-2xl sm:text-3xl md:text-[44px] leading-[1.18] font-bold text-primary-foreground mb-5">
            See the platform in practice
          </h2>
          <p className="text-base sm:text-[17px] font-light text-primary-foreground/60 leading-relaxed">
            Real clinical tools designed by clinicians — objective data, clear visualisations, and AI-powered documentation.
          </p>
        </motion.div>

        {/* Full Screenshot Grid Layout */}
        <div className="grid sm:grid-cols-2 gap-6 sm:gap-8">
          {screenshots.map((s, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 30 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.1 * i, duration: 0.6 }}
              className="group"
            >
              {/* Screenshot Container - Full Image Visible */}
              <div className="rounded-xl overflow-hidden shadow-2xl shadow-black/20 border border-primary-foreground/10 bg-white mb-4 sm:mb-5">
                <img
                  src={s.src}
                  alt={s.alt}
                  className="w-full h-auto object-contain"
                  loading="lazy"
                />
              </div>

              {/* Caption */}
              <div className="text-center sm:text-left px-1 sm:px-2">
                <h3 className="text-lg sm:text-xl md:text-2xl font-bold text-primary-foreground mb-2">
                  {s.caption}
                </h3>
                <p className="text-sm sm:text-[15px] font-light text-primary-foreground/60 leading-relaxed">
                  {s.desc}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default ProductShowcase;

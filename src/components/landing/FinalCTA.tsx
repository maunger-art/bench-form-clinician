import { motion, useInView } from "framer-motion";
import { useRef } from "react";
import { Button } from "@/components/ui/button";
import { ArrowRight } from "lucide-react";

const FinalCTA = ({ onRequestAccess }: { onRequestAccess?: () => void }) => {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section id="cta" className="bg-warm py-16 sm:py-24 md:py-32" ref={ref}>
      <div className="max-w-[1180px] mx-auto px-5 sm:px-6 md:px-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={inView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.6 }}
          className="bg-navy rounded-2xl sm:rounded-3xl p-8 sm:p-12 lg:p-20 text-center"
        >
          <h2 className="text-2xl sm:text-3xl md:text-[44px] leading-[1.18] font-bold text-primary-foreground mb-5">
            Bring measurable outcomes to your clinic
          </h2>
          <p className="text-base sm:text-[17px] font-light text-primary-foreground/60 leading-relaxed max-w-[600px] mx-auto mb-8 sm:mb-10">
            Join the growing number of MSK clinicians using objective data to improve patient care
            and demonstrate results.
          </p>
          <div className="flex gap-3 sm:gap-4 justify-center flex-col sm:flex-row items-center">
            <Button
              onClick={onRequestAccess}
              className="w-full sm:w-auto bg-brand-blue hover:bg-brand-blue-mid text-primary-foreground px-8 py-6 text-[15px] font-semibold rounded-lg shadow-lg shadow-brand-blue/30 transition-all hover:-translate-y-0.5"
            >
              Request Access <ArrowRight className="ml-2 w-4 h-4" />
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default FinalCTA;

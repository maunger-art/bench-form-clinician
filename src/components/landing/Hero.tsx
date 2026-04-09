import { useState } from "react";
import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Play, CalendarDays } from "lucide-react";
import { Dialog, DialogContent } from "@/components/ui/dialog";
import screenshotAnalyticsFull from "@/assets/screenshot-analytics-full.png";

const LOOM_EMBED_URL = "https://www.loom.com/embed/64574912fc9f43ff9521d3819ca9cf0b";
const LOOM_SHARE_URL = "https://www.loom.com/share/64574912fc9f43ff9521d3819ca9cf0b";

const Hero = () => {
  const [videoOpen, setVideoOpen] = useState(false);
  const benefits = [
    "Objective strength and performance benchmarking",
    "Measurable patient progress tracking",
    "Structured rehabilitation planning",
    "AI-assisted clinical documentation",
  ];

  return (
    <section className="relative bg-warm pt-[66px] overflow-hidden">
      {/* Dot texture */}
      <div
        className="absolute inset-0 opacity-30 pointer-events-none"
        style={{
          backgroundImage: "radial-gradient(circle at 1px 1px, hsl(var(--sand)) 1px, transparent 0)",
          backgroundSize: "32px 32px",
        }}
      />

      <div className="max-w-[1180px] mx-auto px-5 sm:px-6 md:px-12 py-12 sm:py-20 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-10 lg:gap-16 items-center">
          {/* Left */}
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="relative z-10"
          >
            <div className="flex items-center gap-2 mb-6">
              <div className="w-5 h-[2px] bg-brand-blue rounded" />
              <span className="text-brand-blue text-xs font-bold tracking-[0.14em] uppercase">
                Clinical Performance Platform
              </span>
            </div>

            <h1 className="text-3xl sm:text-4xl lg:text-[52px] leading-[1.1] font-bold text-foreground mb-3">
              Progress You Can{" "}
              <span className="font-editorial italic font-normal text-brand-blue">Measure.</span>
            </h1>
            <p className="text-lg sm:text-xl lg:text-2xl font-editorial italic font-normal text-mid mb-7 leading-relaxed">
              Care You Can Prove.
            </p>

            <p className="text-base sm:text-[17px] font-light text-mid leading-relaxed mb-8 max-w-[500px]">
              Benchmark is a clinical performance platform that allows physiotherapists to objectively
              measure patient progress, benchmark results, and generate data-driven rehabilitation plans.
            </p>

            <ul className="space-y-3 mb-10">
              {benefits.map((b, i) => (
                <motion.li
                  key={i}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + i * 0.08, duration: 0.4 }}
                  className="text-[15px] font-medium text-foreground"
                >
                  {b}
                </motion.li>
              ))}
            </ul>

            <div className="flex gap-3 flex-col sm:flex-row">
              <Button
                variant="outline"
                className="w-full sm:w-auto border-foreground/20 text-foreground hover:border-brand-blue hover:text-brand-blue px-7 py-6 text-[15px] font-semibold rounded-lg bg-transparent"
                onClick={() => setVideoOpen(true)}
              >
                <Play className="mr-2 w-4 h-4" /> Watch Site Tour
              </Button>
              <Button
                onClick={() => window.open("https://calendly.com/benchmarkps-info/30min", "_blank", "noopener,noreferrer")}
                className="w-full sm:w-auto bg-brand-blue hover:bg-brand-blue-mid text-primary-foreground px-7 py-6 text-[15px] font-semibold rounded-lg shadow-lg shadow-brand-blue/25 transition-all hover:-translate-y-0.5"
              >
                <CalendarDays className="mr-2 w-4 h-4" /> Request Demo
              </Button>
            </div>
          </motion.div>

          {/* Right - Real Product Screenshot */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3, duration: 0.7 }}
            className="relative z-10"
          >
            <div className="rounded-xl overflow-hidden shadow-2xl shadow-navy/30 border border-sand/30 bg-white">
              <img
                src={screenshotAnalyticsFull}
                alt="Benchmark PS patient analytics dashboard showing performance benchmarking against expected scores with left vs right comparison"
                className="w-full h-auto"
                loading="eager"
              />
            </div>
          </motion.div>
        </div>
      </div>

      {/* Blue diagonal background accent */}
      <div
        className="absolute top-0 right-0 bottom-0 w-1/2 pointer-events-none hidden lg:block"
        style={{
          background: "linear-gradient(135deg, hsl(213 66% 16%) 0%, hsl(211 53% 23%) 100%)",
          clipPath: "polygon(30% 0, 100% 0, 100% 100%, 0% 100%)",
        }}
      />

      <Dialog open={videoOpen} onOpenChange={setVideoOpen}>
        <DialogContent className="max-w-[900px] p-0 border-none bg-transparent shadow-none">
          <div className="aspect-video w-full">
            <iframe
              src={videoOpen ? LOOM_EMBED_URL : undefined}
              className="w-full h-full rounded-lg"
              allowFullScreen
              onError={() => {
                setVideoOpen(false);
                window.open(LOOM_SHARE_URL, "_blank", "noopener,noreferrer");
              }}
            />
          </div>
        </DialogContent>
      </Dialog>
    </section>
  );
};

export default Hero;

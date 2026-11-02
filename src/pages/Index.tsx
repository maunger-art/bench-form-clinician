import Navbar from "@/components/landing/Navbar";
import Hero from "@/components/landing/Hero";
import Platform from "@/components/landing/Platform";
import Security from "@/components/landing/Security";
import PatientApp from "@/components/landing/PatientApp";
import HowItWorks from "@/components/landing/HowItWorks";
import WhoItsFor from "@/components/landing/WhoItsFor";
import Pricing from "@/components/landing/Pricing";
import OutcomesSection from "@/components/landing/OutcomesSection";
import FinalCTA from "@/components/landing/FinalCTA";
import Footer from "@/components/landing/Footer";
import { useFaceliftEffects } from "@/hooks/use-facelift-effects";

const Index = () => {
  useFaceliftEffects();

  return (
    <div className="facelift">
      <Navbar />
      <main id="top">
        <Hero />
        <Platform />
        <Security />
        <PatientApp />
        <HowItWorks />
        <WhoItsFor />
        <Pricing />
        <OutcomesSection />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
};

export default Index;

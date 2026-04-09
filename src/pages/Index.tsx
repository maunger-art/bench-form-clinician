import { useState } from "react";
import Navbar from "@/components/landing/Navbar";
import Hero from "@/components/landing/Hero";
import AccessibleTestingSection from "@/components/landing/AccessibleTestingSection";
import HowItWorks from "@/components/landing/HowItWorks";
import ProductShowcase from "@/components/landing/ProductShowcase";
import WhoItsFor from "@/components/landing/WhoItsFor";
import OutcomesSection from "@/components/landing/OutcomesSection";
import FinalCTA from "@/components/landing/FinalCTA";
import Footer from "@/components/landing/Footer";
import EarlyAccessModal from "@/components/landing/EarlyAccessModal";

const Index = () => {
  const [earlyAccessOpen, setEarlyAccessOpen] = useState(false);
  const openEarlyAccess = () => setEarlyAccessOpen(true);

  return (
    <div className="min-h-screen">
      <Navbar />
      <Hero />
      <AccessibleTestingSection />
      <HowItWorks />
      <ProductShowcase />
      <WhoItsFor />
      <OutcomesSection />
      <FinalCTA onRequestAccess={openEarlyAccess} />
      <Footer />
      <EarlyAccessModal open={earlyAccessOpen} onOpenChange={setEarlyAccessOpen} />
    </div>
  );
};

export default Index;

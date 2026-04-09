import BrandLogo from "@/components/BrandLogo";

const Footer = () => {
  return (
    <footer className="bg-navy py-8 sm:py-12 border-t border-primary-foreground/10">
      <div className="max-w-[1180px] mx-auto px-5 sm:px-6 md:px-12 flex flex-col md:flex-row items-center justify-between gap-4 sm:gap-6">
        <BrandLogo size="sm" linkTo="#" />
        <div className="flex gap-6">
          <a href="/privacy-policy" className="text-primary-foreground/50 hover:text-primary-foreground text-xs transition-colors">
            Privacy Policy
          </a>
          <a href="/terms-and-conditions" className="text-primary-foreground/50 hover:text-primary-foreground text-xs transition-colors">
            Terms
          </a>
          <a href="#" className="text-primary-foreground/50 hover:text-primary-foreground text-xs transition-colors">
            Contact
          </a>
        </div>
        <p className="text-primary-foreground/40 text-xs">
          © {new Date().getFullYear()} Benchmark Performance Systems
        </p>
      </div>
    </footer>
  );
};

export default Footer;

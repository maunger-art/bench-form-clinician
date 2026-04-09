import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Menu, X } from "lucide-react";
import benchmarkIconNav from "@/assets/benchmark-icon-nav.png";

const BrandLogoInline = ({ size = "md" }: { size?: "sm" | "md" }) => {
  const iconSize = size === "sm" ? "h-[38px] w-auto" : "h-[44px] sm:h-[48px] w-auto";
  const mainTextSize = size === "sm" ? "text-[16px]" : "text-[18px] sm:text-[20px]";
  const subTextSize = size === "sm" ? "text-[8px]" : "text-[8px] sm:text-[9px]";

  return (
    <span className="flex items-center gap-3 sm:gap-3">
      {/* Icon image */}
      <img src={benchmarkIconNav} alt="Benchmark PS" className={iconSize} />
      {/* Wordmark */}
      <span className="flex flex-col justify-center leading-none">
        <span
          className={`font-bold tracking-[0.12em] uppercase text-white ${mainTextSize}`}
          style={{ lineHeight: 1 }}
        >
          Benchmark
        </span>
        <span
          className={`font-semibold tracking-[0.22em] uppercase text-[#29AAE1] mt-[4px] ${subTextSize}`}
          style={{ lineHeight: 1 }}
        >
          Performance Systems
        </span>
      </span>
    </span>
  );
};

const Navbar = () => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [bannerVisible, setBannerVisible] = useState(true);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    if (!mobileOpen) return;
    const onScroll = () => setMobileOpen(false);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, [mobileOpen]);

  const links = [
    { label: "How It Works", href: "#how-it-works" },
    { label: "Who It's For", href: "#who" },
    { label: "Blog", href: "/blog" },
    { label: "Contact", href: "#cta" },
  ];

  return (
    <>
      {bannerVisible && (
        <div id="earlyAccessBanner" style={{background: 'hsl(199, 68%, 51%)', color: 'white', padding: '0.65rem 1.5rem', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1rem', fontSize: '0.85rem', fontWeight: 500, flexWrap: 'wrap', textAlign: 'center', position: 'fixed', top: 0, left: 0, right: 0, zIndex: 51}}>
          <span><strong>Now in early access — free to get started.</strong> Join physiotherapy clinics already measuring outcomes with Benchmark PS.</span>
          <a href="https://platform.benchmarkps.org/login?signup=true" style={{background: 'white', color: 'hsl(199, 68%, 51%)', padding: '0.3rem 1rem', borderRadius: '5px', fontWeight: 700, fontSize: '0.8rem', textDecoration: 'none', whiteSpace: 'nowrap'}}>Create Account &rarr;</a>
          <button onClick={() => setBannerVisible(false)} style={{position: 'absolute', right: '1rem', background: 'none', border: 'none', color: 'rgba(255,255,255,0.7)', cursor: 'pointer', fontSize: '1.1rem'}}>×</button>
        </div>
      )}
      <nav
        className={`fixed left-0 right-0 z-50 transition-all duration-300 ${
          scrolled
            ? "bg-navy/[0.97] backdrop-blur-xl shadow-lg"
            : "bg-navy/[0.97] backdrop-blur-xl"
        }`}
        style={{ top: bannerVisible ? '38px' : '0' }}
      >
        <div className="max-w-[1180px] mx-auto px-5 sm:px-6 md:px-12 h-[60px] sm:h-[66px] flex items-center justify-between">
          <a href="#" className="flex items-center">
            <BrandLogoInline size="md" />
          </a>

          <div className="hidden md:flex items-center gap-8">
            {links.map((l) => (
              <a
                key={l.label}
                href={l.href}
                className="text-primary-foreground/60 hover:text-primary-foreground text-[13px] font-medium transition-colors"
              >
                {l.label}
              </a>
            ))}
            <a
              href="https://platform.benchmarkps.org/login"
              className="text-primary-foreground/60 hover:text-primary-foreground text-[13px] font-medium transition-colors"
            >
              Login
            </a>
            <Button
              size="sm"
              asChild
              className="bg-brand-blue-mid hover:bg-brand-blue-mid/80 text-primary-foreground text-[13px] font-semibold px-5 rounded-md"
            >
              <a href="https://platform.benchmarkps.org/login?signup=true">Create Account</a>
            </Button>
          </div>

          <button
            className="md:hidden text-primary-foreground"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {mobileOpen && (
          <div className="md:hidden bg-navy border-t border-primary-foreground/10 px-5 py-6 flex flex-col gap-4">
            {links.map((l) => (
              <a
                key={l.label}
                href={l.href}
                className="text-primary-foreground/70 text-sm font-medium py-1"
                onClick={() => setMobileOpen(false)}
              >
                {l.label}
              </a>
            ))}
            <a href="https://platform.benchmarkps.org/login" className="text-primary-foreground/70 text-sm font-medium py-1">Login</a>
            <Button size="sm" asChild className="bg-brand-blue-mid text-primary-foreground w-full mt-2">
              <a href="https://platform.benchmarkps.org/login?signup=true">Create Account</a>
            </Button>
          </div>
        )}
      </nav>
    </>
  );
};

export default Navbar;

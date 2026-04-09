import { Link } from "react-router-dom";
import benchmarkIcon from "@/assets/benchmark-icon-logo.png";

interface BrandLogoProps {
  size?: "sm" | "md";
  linkTo?: string;
}

const BrandLogo = ({ size = "md", linkTo = "/" }: BrandLogoProps) => {
  const iconClass = size === "sm" ? "h-7 w-auto" : "h-8 sm:h-9 w-auto";
  const benchmarkClass = size === "sm"
    ? "text-[13px] sm:text-[15px] font-bold tracking-[0.08em]"
    : "text-[15px] sm:text-[17px] font-bold tracking-[0.08em]";
  const subtitleClass = size === "sm"
    ? "text-[9px] sm:text-[10px] font-normal tracking-[0.12em]"
    : "text-[10px] sm:text-[11.5px] font-normal tracking-[0.12em]";

  const content = (
    <span className="flex items-center gap-3 sm:gap-3.5">
      <img src={benchmarkIcon} alt="Benchmark PS" className={iconClass} />
      {/* Desktop: two-line wordmark */}
      <span className="hidden sm:flex flex-col leading-none gap-[2px]">
        <span className={`text-brand-blue-mid uppercase ${benchmarkClass}`}>
          Benchmark
        </span>
        <span className={`text-primary-foreground/60 uppercase ${subtitleClass}`}>
          Performance Systems
        </span>
      </span>
      {/* Mobile: single word */}
      <span className={`sm:hidden text-brand-blue-mid uppercase font-bold tracking-[0.08em] text-[14px]`}>
        Benchmark
      </span>
    </span>
  );

  if (linkTo.startsWith("/")) {
    return <Link to={linkTo} className="flex items-center">{content}</Link>;
  }
  return <a href={linkTo} className="flex items-center">{content}</a>;
};

export default BrandLogo;

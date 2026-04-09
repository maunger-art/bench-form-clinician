import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import BrandLogo from "@/components/BrandLogo";

const TermsAndConditions = () => {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <nav className="bg-navy py-4">
        <div className="max-w-[900px] mx-auto px-5 sm:px-6 md:px-12 flex items-center justify-between">
          <BrandLogo size="sm" />
          <Link to="/" className="text-primary-foreground/60 hover:text-primary-foreground text-sm flex items-center gap-1.5 transition-colors">
            <ArrowLeft size={16} />
            Back to Home
          </Link>
        </div>
      </nav>

      {/* Hero */}
      <section className="bg-navy py-12 sm:py-16 border-b border-primary-foreground/10">
        <div className="max-w-[900px] mx-auto px-5 sm:px-6 md:px-12">
          <p className="text-primary-foreground/70 text-sm font-medium mb-2">Benchmark Performance Systems</p>
          <h1 className="text-primary-foreground text-3xl sm:text-4xl font-bold tracking-tight">Terms and Conditions of Platform Use</h1>
          <div className="mt-4 space-y-1">
            <p className="text-primary-foreground/50 text-sm">Last Updated: 11th March 2026</p>
            <p className="text-primary-foreground/50 text-sm">Email: <a href="mailto:info@benchmarkps.org" className="text-primary-foreground/70 hover:text-primary-foreground transition-colors">info@benchmarkps.org</a></p>
          </div>
        </div>
      </section>

      {/* Content */}
      <article className="max-w-[900px] mx-auto px-5 sm:px-6 md:px-12 py-10 sm:py-16 prose prose-slate max-w-none
        prose-headings:font-sans prose-headings:tracking-tight
        prose-h2:text-xl prose-h2:sm:text-2xl prose-h2:mt-10 prose-h2:mb-4 prose-h2:text-foreground
        prose-h3:text-lg prose-h3:mt-6 prose-h3:mb-3 prose-h3:text-foreground
        prose-p:text-muted-foreground prose-p:leading-relaxed prose-p:mb-4
        prose-li:text-muted-foreground prose-li:leading-relaxed
        prose-a:text-brand-blue-mid prose-a:no-underline hover:prose-a:underline
        prose-strong:text-foreground
      ">
        <p>
          These Terms and Conditions ("Terms") govern access to and use of the Benchmark Performance Systems platform ("the Platform") operated by Benchmark Performance Systems Ltd ("Benchmark", "we", "us", or "our").
        </p>
        <p>
          By accessing or using the Platform you agree to be bound by these Terms.
        </p>
        <p>
          If you do not agree to these Terms, you must not access or use the Platform.
        </p>

        <h2>1. About Benchmark Performance Systems</h2>
        <p>
          Benchmark Performance Systems provides a digital platform designed to assist healthcare professionals in:
        </p>
        <ul>
          <li>collecting clinical performance data</li>
          <li>benchmarking patient outcomes</li>
          <li>analysing rehabilitation progress</li>
          <li>supporting clinical decision making</li>
          <li>managing musculoskeletal performance assessments</li>
        </ul>
        <p>
          The Platform is intended for use by qualified healthcare professionals and authorised clinical staff.
        </p>
        <p>
          Benchmark does not provide medical advice or clinical treatment.
        </p>

        <h2>2. Definitions</h2>
        <p>For the purposes of these Terms:</p>
        <p><strong>Platform</strong> — The Benchmark Performance Systems software platform, including web applications, dashboards, analytics tools, and associated services.</p>
        <p><strong>User</strong> — Any individual authorised to access the Platform, including clinicians, administrators, and authorised staff.</p>
        <p><strong>Organisation</strong> — A clinic, healthcare provider, institution, or entity subscribing to the Platform.</p>
        <p><strong>Account</strong> — A registered user profile providing access to the Platform.</p>
        <p><strong>Data</strong> — Any information entered, uploaded, or generated through the Platform including clinical metrics, performance data, and user information.</p>

        <h2>3. Eligibility</h2>
        <p>The Platform is intended for use by:</p>
        <ul>
          <li>physiotherapists</li>
          <li>sports therapists</li>
          <li>osteopaths</li>
          <li>chiropractors</li>
          <li>sports medicine practitioners</li>
          <li>rehabilitation professionals</li>
          <li>authorised clinical staff</li>
        </ul>
        <p>Users must:</p>
        <ul>
          <li>be at least 18 years of age</li>
          <li>be authorised by their organisation where applicable</li>
          <li>comply with relevant professional regulations and clinical governance standards</li>
        </ul>
        <p>Benchmark reserves the right to suspend or terminate accounts that do not meet these criteria.</p>

        <h2>4. Account Registration</h2>
        <p>To access certain features of the Platform you must create an account.</p>
        <p>You agree to:</p>
        <ul>
          <li>provide accurate and complete registration information</li>
          <li>keep login credentials confidential</li>
          <li>notify us immediately of any unauthorised access</li>
        </ul>
        <p>You are responsible for all activities conducted through your account.</p>
        <p>Benchmark is not responsible for losses arising from unauthorised use of your account where security obligations have not been followed.</p>

        <h2>5. Platform Licence</h2>
        <p>Subject to compliance with these Terms, Benchmark grants you a limited, non-exclusive, non-transferable licence to access and use the Platform for professional healthcare purposes.</p>
        <p>You may not:</p>
        <ul>
          <li>copy or redistribute the Platform</li>
          <li>reverse engineer or attempt to extract source code</li>
          <li>reproduce proprietary algorithms or benchmarking systems</li>
          <li>resell the Platform without written permission</li>
        </ul>
        <p>All intellectual property rights remain the property of Benchmark Performance Systems Ltd.</p>

        <h2>6. Clinical Use Disclaimer</h2>
        <p>The Platform is intended to support clinical decision-making, not replace professional judgment.</p>
        <p>Users remain responsible for:</p>
        <ul>
          <li>clinical assessments</li>
          <li>diagnosis</li>
          <li>treatment decisions</li>
          <li>patient care outcomes</li>
        </ul>
        <p>Benchmark does not guarantee:</p>
        <ul>
          <li>clinical outcomes</li>
          <li>diagnostic accuracy</li>
          <li>treatment effectiveness</li>
        </ul>
        <p>The Platform provides analytical tools and benchmarking data only.</p>

        <h2>7. Data Use and Ownership</h2>
        <p>Users retain ownership of any data they enter into the Platform.</p>
        <p>However, by using the Platform you grant Benchmark a licence to:</p>
        <ul>
          <li>process data for platform functionality</li>
          <li>generate aggregated benchmarking insights</li>
          <li>improve platform performance</li>
        </ul>
        <p>Benchmark may use anonymised and aggregated data for:</p>
        <ul>
          <li>research</li>
          <li>product development</li>
          <li>statistical analysis</li>
        </ul>
        <p>No personally identifiable patient information will be used for research without appropriate legal basis.</p>

        <h2>8. Patient Data and GDPR Compliance</h2>
        <p>Users are responsible for ensuring that:</p>
        <ul>
          <li>patient data is collected lawfully</li>
          <li>appropriate patient consent has been obtained where required</li>
          <li>data is processed in accordance with GDPR and relevant healthcare regulations</li>
        </ul>
        <p>Benchmark processes data in accordance with its Privacy Policy.</p>
        <p>Where applicable, Benchmark may act as a data processor and the healthcare organisation as the data controller.</p>

        <h2>9. Acceptable Use</h2>
        <p>Users agree not to:</p>
        <ul>
          <li>upload unlawful or harmful content</li>
          <li>attempt to breach platform security</li>
          <li>interfere with system performance</li>
          <li>access accounts belonging to other users without permission</li>
          <li>use the Platform for illegal or unethical purposes</li>
        </ul>
        <p>Benchmark reserves the right to suspend accounts that violate these terms.</p>

        <h2>10. Platform Availability</h2>
        <p>Benchmark aims to maintain reliable platform access but does not guarantee uninterrupted service.</p>
        <p>The Platform may occasionally be unavailable due to:</p>
        <ul>
          <li>system maintenance</li>
          <li>software updates</li>
          <li>technical issues</li>
          <li>security measures</li>
        </ul>
        <p>We will use reasonable efforts to minimise disruption.</p>

        <h2>11. Fees and Subscriptions</h2>
        <p>Where the Platform is provided through paid subscription:</p>
        <ul>
          <li>fees will be communicated during onboarding</li>
          <li>payment terms will be agreed with the subscribing organisation</li>
          <li>subscriptions may renew automatically unless cancelled</li>
        </ul>
        <p>Failure to pay subscription fees may result in suspension of access.</p>

        <h2>12. Intellectual Property</h2>
        <p>All intellectual property rights relating to the Platform, including:</p>
        <ul>
          <li>software architecture</li>
          <li>benchmarking algorithms</li>
          <li>databases</li>
          <li>visualisations</li>
          <li>documentation</li>
        </ul>
        <p>remain the property of Benchmark Performance Systems Ltd.</p>
        <p>Users may not reproduce or commercialise these materials without written consent.</p>

        <h2>13. Limitation of Liability</h2>
        <p>To the maximum extent permitted by law, Benchmark shall not be liable for:</p>
        <ul>
          <li>indirect or consequential losses</li>
          <li>loss of revenue or profits</li>
          <li>clinical outcomes resulting from platform use</li>
          <li>misuse of data by users</li>
        </ul>
        <p>Nothing in these Terms excludes liability for:</p>
        <ul>
          <li>fraud</li>
          <li>death or personal injury caused by negligence</li>
          <li>any liability that cannot be excluded under applicable law</li>
        </ul>

        <h2>14. Termination</h2>
        <p>Benchmark may suspend or terminate access if:</p>
        <ul>
          <li>these Terms are breached</li>
          <li>unlawful activity is suspected</li>
          <li>misuse of the Platform occurs</li>
        </ul>
        <p>Users may terminate their account at any time by contacting Benchmark.</p>
        <p>Upon termination:</p>
        <ul>
          <li>access to the Platform will cease</li>
          <li>data handling will follow applicable retention policies</li>
        </ul>

        <h2>15. Modifications to the Platform</h2>
        <p>Benchmark may update, improve, or modify the Platform at any time.</p>
        <p>This may include:</p>
        <ul>
          <li>new features</li>
          <li>security improvements</li>
          <li>interface changes</li>
          <li>performance enhancements</li>
        </ul>
        <p>Where changes materially affect service delivery, users will be notified where reasonably possible.</p>

        <h2>16. Governing Law</h2>
        <p>These Terms are governed by the laws of England and Wales.</p>
        <p>Any disputes arising in connection with these Terms shall be subject to the exclusive jurisdiction of the courts of England and Wales.</p>

        <h2>17. Contact Information</h2>
        <p>If you have any questions regarding these Terms, please contact:</p>
        <p><strong>Benchmark Performance Systems Ltd</strong></p>
        <p>Email: <a href="mailto:info@benchmarkps.org">info@benchmarkps.org</a></p>

        <h2>18. Entire Agreement</h2>
        <p>These Terms, together with the Privacy Policy, constitute the entire agreement governing the use of the Platform.</p>
      </article>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="max-w-[900px] mx-auto px-5 sm:px-6 md:px-12">
          <p className="text-muted-foreground text-sm text-center">
            © {new Date().getFullYear()} Benchmark Performance Systems. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default TermsAndConditions;

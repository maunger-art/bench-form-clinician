import { Link } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import BrandLogo from "@/components/BrandLogo";

const PrivacyPolicy = () => {
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
          <h1 className="text-primary-foreground text-3xl sm:text-4xl font-bold tracking-tight">Privacy Policy</h1>
          <p className="text-primary-foreground/50 mt-3 text-sm">Last updated: 11th March 2026</p>
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
        <p className="text-foreground font-medium text-lg leading-relaxed">
          Benchmark RPS Ltd (CN 13817021)
        </p>
        <p>
          This Privacy Policy applies to Benchmark RPS Ltd and relates to its operations. It explains how we handle personal information and comply with the requirements of applicable privacy laws and other related laws regulating the handling of personal information, including without limitation the General Data Protection Regulation EU 2016/269 ("GDPR") and applicable EU Member State laws (Privacy Laws). If you have further questions relating to this policy please contact Charles Woolhouse at{" "}
          <a href="mailto:DPO@benchmarkps.org">DPO@benchmarkps.org</a>. This Privacy Policy also serves as notification to individuals of the matters required to be notified on collection of their personal information. We recognise the importance of your privacy, and that you have a right to control how your personal information is collected and used.
        </p>

        <h2>1. Collection of personal information</h2>

        <h3>1.1</h3>
        <p>
          We collect personal information from clients (existing and prospective), as well as end users of the Benchmark PS website, Benchmark PS software and individuals who engage with us via our social media accounts. We also collect personal information from suppliers, contractors, investors, shareholders, prospective employees, and consumers and other individuals who interact with us or our clients for various business and other purposes further listed in section 2.2 below. In this section 1, we explain the kinds of personal information which we usually collect and hold as well as how we collect this information.
        </p>

        <h3>1.2</h3>
        <p>The kinds of personal information Benchmark PS will collect and hold about you will depend on the circumstances in which that information is collected. It may include:</p>
        <ul>
          <li>(a) contact details which may include your name, address, email and phone details;</li>
          <li>(b) age or date of birth information;</li>
          <li>(c) personal information that you include in any content that you enter into the Benchmark PS websites or the webapp, being any information relating to a natural person who can be identified, directly or indirectly, by reference to that information (e.g. name, identification number, location data, or one or more factors specific to the physical, physiological, genetic, mental, economic, cultural or social identity of a person);</li>
          <li>(d) information required for you to open a trading or subscription account with us or subscribe to any of the Benchmark PS websites or the webapp or to otherwise do business with us, including bank account details, and any other relevant financial information;</li>
          <li>(e) your device/s ID, device type, geo-location information, dates and times of visits, computer and connection information including browser type and operating system, statistics on page views, traffic to and from the sites and referring website addresses, ad data, IP address, standard web log information including online usage, and any other information or online analytics regarding the use of the Benchmark PS website and the webapp, unless you object to such processing pursuant to rights that exist under applicable Privacy Laws (including the GDPR);</li>
          <li>(f) information regarding the use of the Benchmark PS website and the webapps, including users' IP addresses and the dates, the country from which the user accessed the websites and the Apps, times and durations of visits, referring website address and device location, unless you object to such processing pursuant to rights that exist under applicable Privacy Laws (including the GDPR);</li>
          <li>(g) information on your dealings with Benchmark PS, including details of the products and services we have provided to you or that you have enquired about, including any additional information necessary to deliver those products and services and respond to your enquiries;</li>
          <li>(h) behavioural information and information on personal lifestyle preferences and past behaviours;</li>
          <li>(i) information regarding the use of the Benchmark PS website and the webapps, including users' IP addresses and the dates, the country from which the user accessed the websites and the webapp, times and durations of visits, referring website address and device location;</li>
          <li>(j) any additional information relating to you that you provide to us directly through our websites or the Apps or indirectly through your use of our website or the webapp or online presence or through other websites or accounts from which you permit us to collect information; and</li>
          <li>(k) information you provide to us through customer surveys.</li>
        </ul>

        <h3>1.3</h3>
        <p>If you are a healthcare professional, we may collect additional personal information including:</p>
        <ul>
          <li>(a) your medical specialty; and</li>
          <li>(b) your clinical interests.</li>
        </ul>

        <h3>1.4</h3>
        <p>If you are a patient, we may collect additional personal information including:</p>
        <ul>
          <li>(a) details of your healthcare professional; and</li>
          <li>(b) information about your health, including medical conditions.</li>
        </ul>

        <h3>1.5</h3>
        <p>We usually collect personal information either directly from you, someone acting on your behalf, or from third parties through:</p>
        <ul>
          <li>(a) your use of Benchmark PS website and the webapps, including when you register or subscribe for an account, create a profile, post or otherwise submit content or via our use of website analytics;</li>
          <li>(b) use of social media;</li>
          <li>(c) information that you communicate to us including through correspondence, chats, and other social media applications, services or websites, email, telephone, SMS, third party apps and any other forms of communication sent or given to us electronically or in hard copy;</li>
          <li>(d) interaction with our services, content and advertising;</li>
          <li>(e) orders for products or services;</li>
          <li>(f) third party service providers;</li>
          <li>(g) requests for brochures, to join a mailing list or to be contacted for further information about our products or services;</li>
          <li>(h) warranty claims;</li>
          <li>(i) provision of customer service and support;</li>
          <li>(j) our shareholder registry;</li>
          <li>(k) responses to surveys or research conducted by us or on our behalf; and</li>
          <li>(l) entries into competitions or trade promotions conducted by us or on our behalf.</li>
        </ul>

        <h3>1.6</h3>
        <p>If you do not provide us with the information we request, we may not be able to fulfil the applicable purpose of collection, such as to supply products or services to you or to assess your application for employment.</p>

        <h3>1.7</h3>
        <p>Where reasonable and practicable, we will collect personal information directly from you. If we collect information about you from someone else (for example, from someone who supplies goods or services to us), we will ensure you are aware that we have collected personal information about you and the circumstances of the collection and provide any additional disclosure required under applicable Privacy Laws (including the GDPR).</p>

        <h3>1.8 Sensitive Information (or special categories of personal information)</h3>
        <p>Given the nature of the Benchmark PS website and the webapps, it is possible that there could be instances where we collect sensitive information or special categories of personal data (as defined under relevant Privacy Laws) such as:</p>
        <ul>
          <li>(a) health information or data relating to health; and</li>
          <li>(b) other sensitive information or special categories of personal data (as defined under relevant Privacy Laws), but only where you choose to disclose it to us via the Benchmark PS website and the webapps.</li>
        </ul>

        <h3>1.9</h3>
        <p>Depending on the applicable Privacy Laws, we will only collect such information about you:</p>
        <ul>
          <li>(a) with your consent (or explicit consent, if the GDPR applies); or</li>
        </ul>

        <h2>2. Use and disclosure of personal information</h2>

        <h3>2.1</h3>
        <p>We will only use and disclose your personal information in accordance with Privacy Laws and in accordance with this Privacy Policy.</p>

        <h3>2.2</h3>
        <p>Our main purposes for collecting, holding, using and disclosing personal information are the following:</p>
        <ul>
          <li>(a) to supply products or services to our customers and end users of our websites and the Apps;<br /><em>Legal basis: we need to process your personal information in order to perform our contractual obligations to you as our customer or end user in relation to the supply of products or services.</em></li>
          <li>(b) to manage your account with us;<br /><em>Legal basis: it is in our legitimate business interests to collect and process your personal information to enable us to deliver our products and related services to you, our customers, and to manage your account with Benchmark PS.</em></li>
          <li>(c) to obtain products and services from our suppliers;<br /><em>Legal basis: it is in our legitimate business interest to process minimal amounts of business contact information in order to conduct business with our third party suppliers.</em></li>
          <li>(d) to respond to enquiries from existing or prospective customers seeking information about our products or services;<br /><em>Legal basis: it is in our legitimate business interests to collect and process personal information to provide quality customer service and assistance to our valued customers (existing or prospective).</em></li>
          <li>(e) to assess and process warranty claims;<br /><em>Legal basis: it is in our legitimate business interests to process your personal information in order to assess and process warranty claims.</em></li>
          <li>(f) to process and assess employment applications;<br /><em>Legal basis: it is in Benchmark PS's legitimate business interest to collect personal information relating to job applicants/candidates. This enables Benchmark PS to contact candidates and conduct other reasonable enquiries as part of the recruitment process.</em></li>
          <li>(g) to enforce agreements between you and Benchmark PS;<br /><em>Legal basis: we may process your personal data for the performance of an agreement between you and Benchmark PS (including enforcement of agreements).</em></li>
          <li>(h) to undertake research and surveys and analyse statistical information including the disclosure of de-identified, aggregated statistics created using your personal information (including health data) to third parties if you have given Benchmark PS express consent, in writing, to do so;<br /><em>Legal basis: it is in our legitimate business interests to collect and process personal information to monitor, evaluate and improve our products and service offerings and ensure they are tailored to our customers' needs and preferences. Further, personal data can be shared with approved third parties in circumstances where you have provided express written consent for Benchmark PS to do so.</em></li>
          <li>(i) to communicate updates or orders with you, including for competitions and trade promotions; and<br /><em>Legal basis: we will only process your data in this way if you have provided consent and have not unsubscribed from receiving such information.</em></li>
          <li>(j) to comply with applicable laws and with our policy requirements including in relation to occupational health and safety and environmental matters.<br /><em>Legal basis: we may need to process your personal information in order to comply with applicable laws.</em></li>
        </ul>

        <h3>2.3</h3>
        <p>We will only use or disclose personal information for a purpose other than for which it was collected or a related purpose if you have consented to such different use or disclosure or to the extent that such use or disclosure is permitted by applicable law.</p>

        <h3>2.4</h3>
        <p>In carrying out our business, it may be necessary to share information about you with and between our related bodies corporate and organisations that provide services to us. We would not otherwise routinely disclose personal information to an organisation other than as set out in this Privacy Policy unless:</p>
        <ul>
          <li>(a) required or permitted by law;</li>
          <li>(b) we believe it is necessary to provide you with a product or service which you have requested;</li>
          <li>(c) it is necessary to protect the rights, property or personal safety of any of our customers, any member of the public or our interests;</li>
          <li>(d) the assets and operations of our business are transferred to another party as a going concern; or</li>
          <li>(e) you have provided your consent.</li>
        </ul>

        <h2>3. Service Providers</h2>

        <h3>3.1</h3>
        <p>Like most organisations, we use a range of service providers to help us maximise the quality and efficiency of our products and services and our business operations. This means that individuals and organisations outside of Benchmark PS, such as cloud and web hosting service providers, software as a service providers, providers of IT support services, providers of analytics and marketing support services and online payment system providers, will sometimes have access to or be disclosed personal information held by us and may only use it on behalf of us to facilitate our services, provide services on our behalf, perform service-related services or assist us in analysing how our service is used. We require our service providers to adhere to strict privacy guidelines which require the service providers not to keep this information, nor to use it or disclose it for any unauthorised purposes.</p>

        <h2>4. Disclosure of personal information outside the jurisdiction of collection</h2>

        <h3>General disclosure</h3>
        <h3>4.1</h3>
        <p>We may disclose personal information outside of the jurisdiction from which it was collected. In the conduct of our business, we transfer to, hold or access personal information from various countries including the United Kingdom, as well as the United States of America and countries in the European Economic Area. The privacy laws of those countries may not provide the same level of protection as the privacy laws of the country from which the personal information was collected. However, this does not change our commitments to safeguard your privacy and we will comply with all applicable laws relating to the cross-border data disclosure.</p>

        <h3>Data transfers from the European Economic Area ("EEA")</h3>
        <h3>4.2</h3>
        <p>We will take all reasonable and necessary steps to ensure your personal information is treated securely and in accordance with this Privacy Policy and applicable Privacy Laws (including the GDPR, where applicable), and will not transfer personal information outside the EEA unless an appropriate safeguard is implemented (other than to a jurisdiction whose Privacy Laws have been deemed adequate by the European Commission), such as entering into the EU Standard Contractual Clauses (or equivalent measures) with the party outside the EEA receiving the personal information. You may obtain a copy of the appropriate safeguards implemented by us in relation to your personal information by contacting <a href="mailto:DPO@benchmarkps.org">DPO@benchmarkps.org</a>.</p>

        <h2>5. Direct marketing</h2>

        <h3>5.1</h3>
        <p>Like most businesses, marketing is important to our business' success. We therefore, from time to time, send marketing materials to current or prospective customers. We only do so in accordance with applicable laws (which may or may not require Benchmark PS to obtain your prior consent, depending on the country in which you are located and/or the applicable Privacy Laws).</p>

        <h3>5.2</h3>
        <p>If you are receiving promotional information from us and do not wish to receive this information any longer, please contact Benchmark PS directly at <a href="mailto:DPO@benchmarkps.org">DPO@benchmarkps.org</a> asking to be removed from our mailing lists, or use the unsubscribe facilities included in our marketing communications.</p>

        <h3>5.3</h3>
        <p>After you opt-out or update your marketing preferences, please allow us sufficient time to process your marketing preferences. Unless otherwise required to process your requests earlier by law, it may take up to 5 business days to process your opt-out requests in relation to receipt of electronic marketing materials such as emails and SMS, and up to 30 days for all other marketing-related requests.</p>

        <h2>6. Our website and webapps privacy practices</h2>

        <h3>6.1</h3>
        <p>We sometimes use cookie and similar tracking technology on Benchmark PS website and the webapp to provide information and services to site visitors and improve your experience on our website and the webapp. Cookies are pieces of information that a website transfers to your computer's hard disk for record keeping purposes and are a necessary part of facilitating online transactions, and include standard internet log information and visitor behaviour information. Most web browsers are set to accept cookies. Cookies are useful to keep you signed in, remember your preferences, estimate our number of users and determine overall traffic patterns through our sites.</p>

        <h3>6.2</h3>
        <p>If you do not wish to receive any cookies you may set your browser to refuse cookies. This may mean you will not be able to take full advantage of the services on the website and the webapp.</p>

        <h3>6.3</h3>
        <p>Google and other third parties collect data about traffic to this site. Google Analytics uses Cookies to monitor traffic to, and use of, the website. Google uses this information on our behalf to evaluate your Website usage, to compile reports on the Website activities, and to provide additional services connected with the Website. We will not identify you to Google, and will not merge personal and non-personal information collected through this service. You can prevent the use of Google Analytics Cookies by adjusting the settings on your browser software, however, you may not be able to fully use all of the functions of the Websites if you do so. If you would like to prevent Google's collection of data generated by your use of the Websites (including your IP address), please download and install a Browser Plugin available at <a href="https://tools.google.com/dlpage/gaoptout?hl=en" target="_blank" rel="noopener noreferrer">https://tools.google.com/dlpage/gaoptout?hl=en</a>. Alternatively, you can find out how Google Analytics uses data when you use our website, at <a href="https://www.google.com/policies/privacy/partners" target="_blank" rel="noopener noreferrer">www.google.com/policies/privacy/partners</a>.</p>

        <h2>7. Links to other websites and other third party collections</h2>

        <h3>7.1</h3>
        <p>Our website and the webapp may contain links to third party websites or references to third party apps. These linked sites and app are not under our control and we are not responsible for the content of those sites nor are those sites or apps subject to our Privacy Policy. Before disclosing your personal information on any other website or app we recommend that you examine the terms and conditions and Privacy Policy. Benchmark PS is not responsible for any practices on third party websites or apps that might breach your privacy.</p>

        <h3>7.2</h3>
        <p>You should also note that, if you are a patient, personal information you provide via the webapp will also be collected by your healthcare professional. Before disclosing your personal information we recommend that you examine the relevant healthcare practice's Privacy Policy. Benchmark PS is not responsible for the privacy practices of your healthcare professional that might breach your privacy.</p>

        <h2>8. Accessing and correcting the information we keep about you</h2>

        <h3>8.1</h3>
        <p>This section 8 applies unless the GDPR applies to processing of your personal information by Benchmark PS.</p>

        <h3>8.2</h3>
        <p>If at any time you want to know exactly what personal information we hold about you, you are welcome to request access to your record by contacting us at <a href="mailto:DPO@benchmarkps.org">DPO@benchmarkps.org</a>. We will make our file of your information available to you within a reasonable time from receipt of your request. We will only withhold access where permitted by law.</p>

        <h3>8.3</h3>
        <p>If at any time you wish to change personal information that we hold about you because it is inaccurate, incomplete or out of date, please contact us at <a href="mailto:DPO@benchmarkps.org">DPO@benchmarkps.org</a>. If you wish to have your personal information deleted, please let us know in the same manner as referred to above and we will take all reasonable steps to delete it unless we need to keep it for legal reasons. You should note that you may update certain content and account details directly within the Benchmark PS website and the webapp.</p>

        <h3>8.4</h3>
        <p>We may charge a small fee to cover our costs of supplying the information. If we do not grant you access to your personal information or do not agree to correct your personal information, we will tell you why.</p>

        <h2>9. Your rights (GDPR)</h2>

        <h3>9.1</h3>
        <p>If the GDPR applies to processing of your personal information by Benchmark PS, you have the right to:</p>
        <ul>
          <li>(a) <strong>Access.</strong> You have the right to request a copy of the personal information we are processing about you, which we will provide back to you in electronic form. For your own privacy and security, in our discretion we may require you to prove your identity before providing the requested information. If you require multiple copies of your personal information, we may charge a reasonable administration fee.</li>
          <li>(b) <strong>Rectification.</strong> You have the right to have incomplete or inaccurate personal information that we process about you corrected.</li>
          <li>(c) <strong>Deletion.</strong> You have the right to request that we delete personal information that we process about you, except we are not obligated to do so if we need to retain such information in order to comply with a legal obligation or to establish, exercise or defend legal claims.</li>
          <li>(d) <strong>Restriction.</strong> You have the right to restrict our processing of your personal information where you believe such information to be inaccurate, our processing is unlawful or that we no longer need to process such information for a particular purpose, but where we are not able to delete the information due to a legal or other obligation or because you do not wish for us to delete it.</li>
          <li>(e) <strong>Portability.</strong> You have the right to obtain personal information we hold about you, in a structured, electronic format, and to transmit such information to another data controller, where this is (a) personal information which you have provided to us, and (b) if we are processing that information on the basis of your consent (such as for direct marketing communications) or to perform a contract with you.</li>
          <li>(f) <strong>Objection.</strong> Where the legal justification for our processing of your personal information is our legitimate interest, you have the right to object to such processing on grounds relating to your particular situation. We will abide by your request unless we have compelling legitimate grounds for the processing which override your interests and rights, or if we need to continue to process the information for the establishment, exercise or defence of a legal claim.</li>
          <li>(g) <strong>Withdrawing Consent.</strong> If you have consented to our processing of your personal data, you have the right to withdraw your consent at any time, free of charge. This includes cases where you wish to opt out from marketing messages that you receive from us (see Section 5 above).</li>
        </ul>

        <h3>9.2</h3>
        <p>You can make any of these requests in relation to your personal data by sending the request to our Data Protection Officer by email at <a href="mailto:DPO@benchmarkps.org">DPO@benchmarkps.org</a>.</p>

        <h2>10. Storage and security of your personal information</h2>

        <h3>10.1</h3>
        <p>We will endeavour to implement appropriate technical and organisational measures to keep secure any information which we hold about you, and to keep this information accurate, up to date and complete, and to ensure a level of security appropriate to any risks which may be associated with the processing activities outlined in this Privacy Policy.</p>

        <h3>10.2</h3>
        <p>Your information is stored on secure servers that are protected in controlled facilities. These are third party data storage services, including cloud service providers.</p>

        <h3>10.3</h3>
        <p>We require our personnel to respect the confidentiality of any personal information held by us.</p>

        <h3>10.4</h3>
        <p>We take all reasonable physical, administrative, and technological precautions to store and transmit data securely. For example, personal data is encrypted and held with reputable data storage providers. Other measures include:</p>
        <ul>
          <li>(a) computer firewall protection; and</li>
          <li>(b) computer maintenance to prevent unauthorised access.</li>
        </ul>

        <h3>10.5</h3>
        <p>In addition to technological measures, Benchmark PS also places access controls on its employees and other partners. Our employees are subject to contractual confidentiality obligations that are consistent with this Privacy Policy. Despite these measures, Benchmark PS cannot guarantee that the information described in this Privacy Policy will be completely secure.</p>

        <h2>11. Retention of personal information</h2>

        <h3>11.1</h3>
        <p>We will retain and process your personal data only for as long as is necessary for the purposes for which the information is collected. In addition, we will retain and use your personal data to the extent necessary to comply with our legal obligations and exercise our legal rights (for example, if we are required to retain your data to comply with applicable laws), resolve disputes and enforce our legal agreements and policies.</p>

        <h3>11.2</h3>
        <p>When we no longer need to use your personal information or retain it pursuant to legal obligations in order to exercise our legal rights, we will remove it from our systems and records or take steps to anonymise it so that you can no longer be identified from it in accordance with relevant Privacy Laws.</p>

        <h2>12. Contacting Us</h2>

        <h3>12.1</h3>
        <p>If you have any concerns or complaints about how we handle your personal information, or if you have any questions about this policy, please contact us at <a href="mailto:DPO@benchmarkps.org">DPO@benchmarkps.org</a> or at the address below:</p>
        <p>
          Data Protection Officer<br />
          Benchmark RPS Ltd<br />
          82 Wandsworth Bridge Road<br />
          London SW6 2TF
        </p>

        <h3>12.2</h3>
        <p>In most cases we will ask that you put your request in writing to us. We will investigate your complaint and will use reasonable endeavours to respond to you in writing within 30 days of receiving the written complaint. If we fail to respond to your complaint or if you are dissatisfied with the response that you receive from us, you should be aware that you might also have the right to make a complaint to the applicable privacy authorities.</p>

        <h3>12.3</h3>
        <p>In Australia, this is the Office of the Australian Information Commissioner (<a href="https://www.oaic.gov.au" target="_blank" rel="noopener noreferrer">www.oaic.gov.au</a>) or, potentially in some instances, your applicable State or Territory privacy commissioner with regard to handling of health information.</p>
        <p>In the UK, this is The Information Commissioner's Office (<a href="https://www.ico.org.uk" target="_blank" rel="noopener noreferrer">www.ico.org.uk</a>), with regard to handling of health information.</p>

        <h3>12.4</h3>
        <p>If you are located in the EU and the GDPR applies to the processing of your personal data, you also have the right to lodge a complaint with a supervisory authority. A list of supervisory authorities for all EU Member States is available <a href="https://edpb.europa.eu/about-edpb/board/members_en" target="_blank" rel="noopener noreferrer">here</a>.</p>

        <h2>13. Future changes</h2>

        <h3>13.1</h3>
        <p>We operate in a dynamic business environment. Over time, aspects of our business may change as we respond to changing market conditions. This may require our policies to be reviewed and revised. We reserve the right to change this Privacy Policy at any time and notify you by posting an updated version of the policy on the Benchmark PS website and the webapp. If at any point we decide to use personal information in a manner materially different from that stated at the time it was collected we will notify users by email or via a prominent notice on our website.</p>
      </article>

      {/* Footer */}
      <footer className="bg-navy py-8 border-t border-primary-foreground/10">
        <div className="max-w-[900px] mx-auto px-5 sm:px-6 md:px-12 text-center">
          <p className="text-primary-foreground/40 text-xs">
            © {new Date().getFullYear()} Benchmark Performance Systems. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default PrivacyPolicy;

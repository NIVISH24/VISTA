"use client";
import Image from "next/image";
import Hack from "../public/hack.jpg";
import { ShieldCheck, Mic, Activity, Server, Eye } from "lucide-react";

const About = () => {
  return (
    <section
      id="about"
      className="bg-[#657120] text-white py-24 px-4 sm:px-6 lg:px-8 scroll-mt-24 min-h-screen"
    >
      <div className="max-w-7xl mx-auto grid md:grid-cols-2 gap-12 items-center">
        {/* Text Section */}
        <div>
          <h2 className="text-4xl font-bold mb-6">About VISTA</h2>
          <p className="text-lg mb-6 leading-relaxed">
            VISTA - Voice & Insider Surveillance for Threat Assessment is a cutting-edge endpoint monitoring and authentication platform
            designed for passive surveillance and real-time behavioral analysis to detect insider threats.
          </p>
          <p className="text-lg mb-6 leading-relaxed">
            By combining biometric voice authentication, behavioral profiling, and hardware event monitoring,
            VISTA empowers security teams with proactive alerts, forensic insights, and seamless
            multi-factor authentication on Linux systems.
          </p>

          {/* Icon List */}
          <ul className="space-y-4">
            <li className="flex items-start gap-3">
              <ShieldCheck className="text-[#FF5E5B] w-6 h-6" />
              <span>Enterprise-grade endpoint protection with real-time risk alerts</span>
            </li>
            <li className="flex items-start gap-3">
              <Mic className="text-[#FF5E5B] w-6 h-6" />
              <span>Voice-based biometric authentication for secure access control</span>
            </li>
            <li className="flex items-start gap-3">
              <Activity className="text-[#FF5E5B] w-6 h-6" />
              <span>Behavioral profiling and anomaly detection using AI</span>
            </li>
            <li className="flex items-start gap-3">
              <Server className="text-[#FF5E5B] w-6 h-6" />
              <span>Hardware-level event monitoring and forensic traceability</span>
            </li>
            <li className="flex items-start gap-3">
              <Eye className="text-[#FF5E5B] w-6 h-6" />
              <span>Zero-interruption passive surveillance with adaptive response</span>
            </li>
          </ul>
        </div>

        {/* Image Section */}
        <div className="relative w-full h-80 sm:h-96 md:h-[500px]">
          <Image
            src={Hack}
            alt="About VISTA"
            layout="fill"
            objectFit="cover"
            className="rounded-lg shadow-2xl"
          />
        </div>
      </div>
    </section>
  );
};

export default About;

"use client";
import {
  ShieldCheckIcon,
  MicrophoneIcon,
  CpuChipIcon,
  EyeIcon,
  BugAntIcon,
  CameraIcon,
} from "@heroicons/react/24/outline";

const services = [
  {
    title: "Insider Threat Protection",
    description:
      "Real-time behavioral profiling, keystroke dynamics, and USB forensics to detect suspicious user activity before it becomes a threat.",
    icon: ShieldCheckIcon,
  },
  {
    title: "Voice-Based Authentication",
    description:
      "Advanced voice biometrics using Wav2Vec2 for speaker recognition and stress detection—enabling seamless, secure authentication.",
    icon: MicrophoneIcon,
  },
  {
    title: "Hardware Event Monitoring",
    description:
      "Capture and analyze low-level hardware events like keystrokes, device insertions, and process changes for forensic traceability.",
    icon: CpuChipIcon,
  },
  {
    title: "Continuous Passive Surveillance",
    description:
      "Run silent monitoring in the background to observe behavior patterns and flag anomalies in real-time without interrupting workflows.",
    icon: EyeIcon,
  },
  {
    title: "Forensic Logging & Analysis",
    description:
      "Track endpoint activity logs securely for post-incident analysis, threat attribution, and regulatory compliance.",
    icon: BugAntIcon,
  },
  {
    title: "Camera-Based Intrusion Detection",
    description:
      "Integrate AI-powered feeds to identify unauthorized personnel, trigger alerts on unusual behavior, and enable visual forensics.",
    icon: CameraIcon,
  },
];

export default function Services() {
  return (
    <section
      id="services"
      className="relative bg-gradient-to-br from-black via-[#1a1f13] to-[#0d0f0b] py-28 text-white min-h-screen scroll-mt-24 overflow-hidden"
    >
      {/* Glowing background blob */}
      <div className="absolute top-[-100px] left-[-100px] w-[400px] h-[400px] bg-green-600 opacity-20 rounded-full blur-3xl animate-pulse" />
      <div className="absolute bottom-[-150px] right-[-150px] w-[400px] h-[400px] bg-red-500 opacity-20 rounded-full blur-3xl animate-pulse" />

      <div className="max-w-7xl mx-auto w-full px-6 lg:px-8 relative z-10">
        <h2 className="text-4xl font-bold text-khaki text-center mb-16">
          Our Capabilities
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
          {services.map((service, index) => {
            const Icon = service.icon;
            return (
              <div
                key={index}
                className="bg-[#4B5320] p-6 rounded-xl shadow-lg hover:shadow-khaki transition-all duration-300 hover:scale-105"
              >
                <Icon className="h-12 w-12 text-khaki mb-4" />
                <h3 className="text-xl font-semibold mb-3">{service.title}</h3>
                <p className="text-sm text-white leading-relaxed">
                  {service.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

"use client";

import Image from "next/image";
import { useRouter } from "next/navigation";
import SoldierImg from "../public/soldier.jpg";

export default function HeroSection() {
  const router = useRouter();

  return (
    <section className="flex flex-col md:flex-row w-full min-h-[calc(100vh-5rem)] pt-30 font-geist bg-[#1a1a1a]">
      {/* Left Image Section */}
      <div className="md:w-1/2 w-full relative min-h-[300px] md:min-h-0">
        <Image
          src={SoldierImg}
          alt="Soldier"
          layout="fill"
          objectFit="cover"
          className="brightness-110 saturate-150 contrast-125"
          priority
        />
      </div>

      {/* Right Text Section */}
      <div className="md:w-1/2 w-full bg-[#1a1a1a] text-white flex flex-col justify-center px-8 md:px-16 lg:px-20 py-10">
        <h1 className="text-4xl md:text-5xl lg:text-6xl font-extrabold text-[#FF5E5B] drop-shadow-md font-pg">
          Securing from Within
        </h1>
        <p className="mt-6 text-lg md:text-xl leading-relaxed text-gray-300 max-w-[90%] font-pg">
          Our next-generation threat detection system leverages biometric behavior, AI voice analysis, and adaptive defense algorithms to ensure mission-critical security in real-time.
        </p>
        <div className="mt-8">
          <button
            onClick={() => router.push("/dashboard")}
            className="px-6 py-3 bg-[#FF5E5B] text-white font-semibold rounded-lg hover:bg-red-600 transition duration-300 shadow-lg"
          >
            Get Started
          </button>
        </div>
      </div>
    </section>
  );
}

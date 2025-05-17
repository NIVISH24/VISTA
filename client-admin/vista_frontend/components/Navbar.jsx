"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import Link from "next/link";

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const pathname = usePathname();

  const handleScroll = (id) => {
    const section = document.getElementById(id);
    if (section) {
      section.scrollIntoView({ behavior: "smooth" });
      setMenuOpen(false);
    }
  };

  const isDashboard = pathname === "/dashboard";
  const isHome = pathname === "/";

  const headerClass = isDashboard
    ? "w-full fixed top-0 z-50 bg-[#adabab16] backdrop-blur-md text-white shadow-md"
    : isHome
    ? "w-full fixed top-0 z-50 bg-[#4B5320] text-white shadow-md"
    : "w-full fixed top-0 z-50 bg-black text-white shadow-md"; // fallback if needed

  return (
    <header className={headerClass}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center h-20">
        {/* Logo */}
        <Link href="/">
          <div className="text-2xl font-extrabold tracking-widest text-[#FF5E5B] cursor-pointer">
            VISTA
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex gap-8 text-sm font-medium">
          <button onClick={() => handleScroll("hero")} className="hover:text-khaki">
            Home
          </button>
          <button onClick={() => handleScroll("about")} className="hover:text-khaki">
            About
          </button>
          <button onClick={() => handleScroll("services")} className="hover:text-khaki">
            Services
          </button>
          <Link href="/dashboard" passHref>
    <button className="text-right">Dashboard</button>
  </Link>
          <button onClick={() => handleScroll("footer")} className="hover:text-khaki">
            Contact
          </button>
        </nav>

        {/* Mobile Menu Button */}
        <div className="md:hidden">
          {!menuOpen && (
            <button onClick={() => setMenuOpen(true)} aria-label="Open menu">
              <Menu className="w-6 h-6 text-highlightRed" />
            </button>
          )}
        </div>
      </div>

      {/* Slide-in Mobile Menu */}
      <div
        className={`fixed top-0 right-0 h-full w-64 bg-[#4B5320] text-white z-50 transform transition-transform duration-300 ease-in-out ${
          menuOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="flex justify-between items-center px-6 py-4 border-b border-[#6E6E3A]">
          <h2 className="text-xl font-bold">Menu</h2>
          <button onClick={() => setMenuOpen(false)} aria-label="Close menu">
            <X className="w-6 h-6 text-[#FF5E5B]" />
          </button>
        </div>
        <nav className="flex flex-col gap-6 px-6 py-6 text-lg font-medium">
  <button onClick={() => handleScroll("hero")}>Home</button>
  <button onClick={() => handleScroll("about")}>About</button>
  <button onClick={() => handleScroll("services")}>Services</button>
  <a className="text-center" href="/dashboard" passHref>
    <button className="text-right">Dashboard</button>
  </a>
  <button onClick={() => handleScroll("footer")}>Contact</button>
</nav>


      </div>
    </header>
  );
}

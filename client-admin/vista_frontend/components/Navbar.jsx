"use client";

import { useState } from "react";
import Link from "next/link";
import { Menu, X } from "lucide-react";

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);

  return (
    <header className="w-full fixed top-0 z-50 bg-[#4B5320] text-white shadow-md fon">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center h-20">
        {/* Logo */}
        <div className="text-2xl font-extrabold tracking-widest text-[#FF5E5B]">
          VISTA
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex gap-8 text-sm font-medium">
          <Link href="/">Home</Link>
          <Link href="/about">About</Link>
          <Link href="/verification">Verification</Link>
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/contact">Contact</Link>
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

      {/* Right Slide-in Mobile Menu */}
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
          <Link href="/" onClick={() => setMenuOpen(false)}>Home</Link>
          <Link href="/about" onClick={() => setMenuOpen(false)}>About</Link>
          <Link href="/verification" onClick={() => setMenuOpen(false)}>Verification</Link>
          <Link href="/contact" onClick={() => setMenuOpen(false)}>Contact</Link>
        </nav>
      </div>
    </header>
  );
}
    
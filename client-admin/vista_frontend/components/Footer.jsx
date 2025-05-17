"use client";
import { Mail, Phone, MapPin } from "lucide-react";

export default function Footer() {
  return (
    <footer id="contact" className="bg-[#0c0f0a] text-white py-12 px-6 md:px-12">
      <div className="max-w-7xl mx-auto grid md:mt-40 mt-28 md:grid-cols-2 gap-12 items-start">
        {/* Contact Info */}
        <div>
          <h2 className="text-3xl font-bold text-[#FF5E5B] mb-4">Get in Touch</h2>
          <p className="text-gray-300 mb-6">
            Have questions or want to work with us? We'd love to hear from you.
          </p>

          <div className="flex items-center mb-4 text-khaki">
            <Mail className="w-5 h-5 mr-3" />
            <span>contact@vista.com</span>
          </div>
          <div className="flex items-center mb-4 text-khaki">
            <Phone className="w-5 h-5 mr-3" />
            <span>+91 98765 43210</span>
          </div>
          <div className="flex items-center text-khaki">
            <MapPin className="w-5 h-5 mr-3" />
            <span>Bangalore, India</span>
          </div>
        </div>

        {/* Contact Form */}
        <form className="bg-[#4B5320] p-6 rounded-lg shadow-md space-y-4">
          <input
            type="text"
            placeholder="Your Name"
            className="w-full p-3 rounded bg-[#2f3320] text-white placeholder-gray-400 outline-none focus:ring-2 focus:ring-khaki"
          />
          <input
            type="email"
            placeholder="Your Email"
            className="w-full p-3 rounded bg-[#2f3320] text-white placeholder-gray-400 outline-none focus:ring-2 focus:ring-khaki"
          />
          <textarea
            placeholder="Your Message"
            rows="4"
            className="w-full p-3 rounded bg-[#2f3320] text-white placeholder-gray-400 outline-none focus:ring-2 focus:ring-khaki"
          />
          <button
            type="submit"
            className="w-full bg-[#FF5E5B] hover:bg-red-500 text-white font-semibold py-3 rounded transition-colors duration-300"
          >
            Send Message
          </button>
        </form>
      </div>

      {/* Bottom Bar */}
      <div className="mt-12 border-t border-gray-700 pt-6 text-center text-sm text-gray-400">
        © {new Date().getFullYear()} VISTA. All rights reserved.
      </div>
    </footer>
  );
}

"use client";

import { useEffect, useState } from "react";
import { ChevronDown, ChevronUp, CheckCircle, XCircle, Usb } from "lucide-react";
import Navbar from "@/components/Navbar";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";

// Utility for icons
const getStatusIcon = (status) =>
  status ? (
    <CheckCircle className="text-green-400 w-5 h-5" />
  ) : (
    <XCircle className="text-red-500 w-5 h-5" />
  );

export default function DashboardPage() {
  const [userData, setUserData] = useState([]);
  const [usbEvents, setUsbEvents] = useState([]);
  const [openIndex, setOpenIndex] = useState(null);
  const [viewMode, setViewMode] = useState("system");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [systemRes, usbRes] = await Promise.all([
          axios.get("https://ethnic-achievement-fits-clan.trycloudflare.com/system-info/"),
          axios.get("https://ethnic-achievement-fits-clan.trycloudflare.com/usb-events/"),
        ]);

        const systemInfo = systemRes.data?.system_info || [];
        const usbEvents = usbRes.data?.usb_events || [];

        // Augment each user with fixed score/threat values
        const augmentedUsers = systemInfo.map((info, idx) => {
          const score = Math.floor(Math.random() * 100);
          return {
            ...info,
            name: info.hostname || `User ${idx + 1}`,
            voice: true,
            mouse: true,
            keyboard: true,
            score,
            threat: score >= 60 ? "Below" : "Above",
          };
        });

        setUserData(augmentedUsers);
        setUsbEvents(usbEvents);
      } catch (err) {
        console.error("Error fetching data:", err);
      }
    };

    fetchData();
  }, []);

  const toggleAccordion = (index) => {
    setOpenIndex(openIndex === index ? null : index);
    setViewMode("system"); // Reset to system info when opening
  };

  const toggleViewMode = () => {
    setViewMode(viewMode === "system" ? "usb" : "system");
  };

  return (
    <>
      <Navbar />
      <motion.main
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="min-h-screen bg-[#1a1a1a] text-white px-4 py-20 md:px-16 lg:px-32 font-geist"
      >
        <h1 className="text-4xl md:text-5xl font-extrabold mb-12 text-[#FF5E5B] text-center font-pg drop-shadow-md backdrop-blur-sm bg-[#ffffff0a] px-4 py-2 rounded-xl border border-[#FF5E5B]/30">
          Behavioral Biometrics Dashboard
        </h1>

        <div className="space-y-6">
          {userData.map((user, idx) => {
            const userUsbEvents = usbEvents.filter(
              (event) => event.device_fingerprint === user.device_fingerprint
            );

            return (
              <div
                key={idx}
                className="rounded-xl overflow-hidden border border-[#3b3b3b] shadow-lg bg-[#2C2C2C] hover:bg-[#333] transition"
              >
                <button
                  onClick={() => toggleAccordion(idx)}
                  className="w-full flex justify-between items-center px-6 py-5 font-semibold text-left"
                >
                  <div>
                    <p className="text-xl font-bold text-white font-pg">
                      {user.name}
                    </p>
                    <p className="text-sm text-gray-400 mt-1 font-mono">
                      Timeline: {new Date(user.recorded_time).toLocaleString()}
                    </p>
                  </div>

                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1">{getStatusIcon(user.voice)} Voice</div>
                    <div className="flex items-center gap-1">{getStatusIcon(user.mouse)} Mouse</div>
                    <div className="flex items-center gap-1">{getStatusIcon(user.keyboard)} Keyboard</div>
                    <span
                      className={`font-bold ${
                        user.score >= 80
                          ? "text-green-400"
                          : user.score >= 60
                          ? "text-yellow-400"
                          : "text-red-500"
                      }`}
                    >
                      {user.score}%
                    </span>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-bold ${
                        user.threat === "Below"
                          ? "bg-green-700"
                          : "bg-red-600"
                      } text-white`}
                    >
                      {user.threat} Threat
                    </span>
                    {openIndex === idx ? <ChevronUp /> : <ChevronDown />}
                  </div>
                </button>

                <AnimatePresence>
                  {openIndex === idx && (
                    <motion.div
                      key="content"
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.4 }}
                      className="bg-[#1f1f1f] px-6 py-4 border-t border-[#333]"
                    >
                      <div className="flex justify-end mb-4">
                        <button
                          onClick={toggleViewMode}
                          className="flex items-center gap-2 px-4 py-2 bg-[#FF5E5B] text-white rounded hover:bg-[#e14e4b] transition"
                        >
                          <Usb className="w-4 h-4" />
                          {viewMode === "system" ? "View USB Events" : "View System Info"}
                        </button>
                      </div>

                      {viewMode === "system" ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-300 font-mono">
                          <div><strong>MAC Address:</strong> {user.mac_address}</div>
                          <div><strong>CPU Info:</strong> {user.cpu_info}</div>
                          <div><strong>Disk Info:</strong> {user.disk_info}</div>
                          <div><strong>Memory:</strong> {(user.memory_info / (1024 ** 3)).toFixed(2)} GB</div>
                          <div><strong>Hostname:</strong> {user.hostname}</div>
                          <div><strong>OS Info:</strong> {user.os_info}</div>
                          <div><strong>Fingerprint:</strong> {user.device_fingerprint}</div>
                          <div><strong>Recorded At:</strong> {new Date(user.recorded_at).toLocaleString()}</div>
                        </div>
                      ) : userUsbEvents.length > 0 ? (
                        <div className="overflow-x-auto">
                          <table className="min-w-full text-sm text-left text-gray-300 font-mono">
                            <thead className="bg-[#2C2C2C] text-gray-400">
                              <tr>
                                <th className="px-4 py-2">Time</th>
                                <th className="px-4 py-2">Action</th>
                                <th className="px-4 py-2">Vendor</th>
                                <th className="px-4 py-2">Product</th>
                                <th className="px-4 py-2">Serial</th>
                              </tr>
                            </thead>
                            <tbody>
                              {userUsbEvents.map((event) => (
                                <tr key={event.id} className="border-t border-[#333]">
                                  <td className="px-4 py-2">{new Date(event.event_time).toLocaleString()}</td>
                                  <td className="px-4 py-2 capitalize">{event.action}</td>
                                  <td className="px-4 py-2">{event.vendor_name}</td>
                                  <td className="px-4 py-2">{event.product_name}</td>
                                  <td className="px-4 py-2">{event.serial_number}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <p className="text-gray-400 text-sm">No USB events found for this device.</p>
                      )}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            );
          })}
        </div>
      </motion.main>
    </>
  );
}

"use client";

import { useEffect, useState, useRef } from "react";
import {
  ChevronDown,
  ChevronUp,
  CheckCircle,
  XCircle,
  Usb,
  Cpu,
} from "lucide-react";
import Navbar from "@/components/Navbar";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";

export default function DashboardPage() {
  const getStatusIcon = (status) => {
    return status ? (
      <CheckCircle className="w-4 h-4 text-green-400" />
    ) : (
      <XCircle className="w-4 h-4 text-red-500" />
    );
  };

  const [userData, setUserData] = useState([]);
  const [usbEvents, setUsbEvents] = useState([]);
  const [inputDriftData, setInputDriftData] = useState([]);
  const [openIndex, setOpenIndex] = useState(null);
  const [viewMode, setViewMode] = useState("system");
  const canvasRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const letters = "アァイィウヴエエェオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモラリルレロワン";
    const fontSize = 14;
    const columns = canvas.width / fontSize;
    const drops = Array.from({ length: columns }).fill(1);

    const draw = () => {
      ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      ctx.fillStyle = "#0F0";
      ctx.font = `${fontSize}px monospace`;

      for (let i = 0; i < drops.length; i++) {
        const text = letters[Math.floor(Math.random() * letters.length)];
        ctx.fillText(text, i * fontSize, drops[i] * fontSize);

        if (drops[i] * fontSize > canvas.height || Math.random() > 0.975) {
          drops[i] = 0;
        }

        drops[i]++;
      }
    };

    const interval = setInterval(draw, 33);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    // ✅ Commenting out actual data fetching
    // const fetchData = async () => {
    //   try {
    //     const [systemRes, usbRes, driftRes] = await Promise.all([
    //       axios.get("https://emphasis-unlock-factor-vehicles.trycloudflare.com/system-info/"),
    //       axios.get("https://emphasis-unlock-factor-vehicles.trycloudflare.com/usb-events/"),
    //       axios.get("https://services.vistaa.xyz/km/dashboard/km"),
    //     ]);

    //     const systemInfo = systemRes.data?.system_info || [];
    //     const usbEvents = usbRes.data?.usb_events || [];
    //     const inputDriftRaw = driftRes.data?.input_drift || [];

    //     const driftMap = {};
    //     inputDriftRaw.forEach((drift) => {
    //       driftMap[drift.device_fingerprint] = drift;
    //     });

    //     const augmentedUsers = systemInfo.map((info, idx) => ({
    //       ...info,
    //       name: info.hostname,
    //       voice: true,
    //       driftScore: 90,
    //       validated: true,
    //       threat: "Below",
    //     }));

    //     setUserData(augmentedUsers);
    //     setUsbEvents(usbEvents);
    //     setInputDriftData(inputDriftRaw);
    //   } catch (err) {
    //     console.error("Error fetching data:", err);
    //   }
    // };

    // fetchData();

    // ✅ Using dummy data instead
    setUserData([
      {
        name: "DESKTOP-123ABC",
        mac_address: "00:1B:44:11:3A:B7",
        cpu_info: "Intel Core i7-10700K",
        disk_info: "Samsung SSD 970 EVO 1TB",
        memory_info: 17179869184,
        hostname: "DESKTOP-123ABC",
        os_info: "Windows 10 Pro",
        device_fingerprint: "abcd1234",
        recorded_at: new Date().toISOString(),
        recorded_time: new Date().toISOString(),
        voice: true,
        validated: true,
        driftScore: 91,
        threat: "Below",
      },
      {
        name: "LAPTOP-XYZ987",
        mac_address: "00:1B:44:11:3A:C8",
        cpu_info: "AMD Ryzen 5 5600H",
        disk_info: "WD Blue 500GB SSD",
        memory_info: 8589934592,
        hostname: "LAPTOP-XYZ987",
        os_info: "Windows 11 Home",
        device_fingerprint: "efgh5678",
        recorded_at: new Date().toISOString(),
        recorded_time: new Date().toISOString(),
        voice: false,
        validated: true,
        driftScore: 72,
        threat: "Below",
      },
      {
        name: "WORKSTATION-55GHK",
        mac_address: "00:1B:44:11:3A:DD",
        cpu_info: "Intel Xeon E5-2670",
        disk_info: "Kingston SSD 240GB",
        memory_info: 34359738368,
        hostname: "WORKSTATION-55GHK",
        os_info: "Ubuntu 22.04",
        device_fingerprint: "ijkl9012",
        recorded_at: new Date().toISOString(),
        recorded_time: new Date().toISOString(),
        voice: true,
        validated: false,
        driftScore: 64,
        threat: "Above",
      },
      {
        name: "LAPTOP-789XYZ",
        mac_address: "00:1C:42:2E:60:4A",
        cpu_info: "AMD Ryzen 5 5600X",
        disk_info: "WD Blue SN550 1TB NVMe",
        memory_info: 8589934592,
        hostname: "LAPTOP-789XYZ",
        os_info: "Windows 11 Home",
        device_fingerprint: "efgh5678",
        recorded_at: new Date().toISOString(),
        recorded_time: new Date().toISOString(),
        voice: true,
        validated: true,
        driftScore: 87,
        threat: "Below",
      },
      {
        name: "WORKSTATION-456DEF",
        mac_address: "00:16:3E:7E:44:12",
        cpu_info: "Intel Xeon E5-2699 v4",
        disk_info: "Seagate FireCuda 2TB",
        memory_info: 34359738368,
        hostname: "WORKSTATION-456DEF",
        os_info: "Ubuntu 22.04 LTS",
        device_fingerprint: "ijkl9012",
        recorded_at: new Date().toISOString(),
        recorded_time: new Date().toISOString(),
        voice: true,
        validated: true,
        driftScore: 92,
        threat: "Below",
      },
    ]);
    

    setUsbEvents([
      {
        device_fingerprint: "abcd1234",
        timestamp: new Date().toISOString(),
        vendor_id: "0x1234",
        product_id: "0x5678",
        device_name: "SanDisk USB Drive",
        serial_number: "SN123456789",
      },
      {
        device_fingerprint: "efgh5678",
        timestamp: new Date().toISOString(),
        vendor_id: "0x1111",
        product_id: "0x2222",
        device_name: "Kingston DataTraveler",
        serial_number: "SN987654321",
      },
      {
        device_fingerprint: "ijkl9012",
        timestamp: new Date().toISOString(),
        vendor_id: "0x3333",
        product_id: "0x4444",
        device_name: "Transcend USB 3.0",
        serial_number: "SN5566778899",
      },
      {
        device_fingerprint: "abcd123",
        timestamp: new Date().toISOString(),
        vendor_id: "0x1234",
        product_id: "0x5678",
        device_name: "SanDisk USB Drive",
        serial_number: "SN123456789",
      },
      {
        device_fingerprint: "efgh567",
        timestamp: new Date().toISOString(),
        vendor_id: "0x1111",
        product_id: "0x2222",
        device_name: "Kingston DataTraveler",
        serial_number: "SN987654321",
      },
      {
        device_fingerprint: "ijkl901",
        timestamp: new Date().toISOString(),
        vendor_id: "0x3333",
        product_id: "0x4444",
        device_name: "Transcend USB 3.0",
        serial_number: "SN5566778899",
      },
    ]);
    
  }, []);

  const toggleAccordion = (index) => {
    setOpenIndex(openIndex === index ? null : index);
    setViewMode("system");
  };

  const toggleViewMode = () => {
    setViewMode(viewMode === "system" ? "usb" : "system");
  };

  return (
    <>
      <Navbar />
      <div className="relative">
        <canvas
          ref={canvasRef}
          className="fixed top-0 left-0 w-full h-full"
          style={{ zIndex: -1 }}
        />
        <motion.main
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="relative z-10 min-h-screen text-white px-4 py-20 md:px-16 lg:px-32 font-geist"
        >
          <h1 className="text-4xl md:text-5xl mt-6 font-extrabold mb-12 text-[#00FF41] text-center font-pg drop-shadow-md backdrop-blur-sm bg-[#ffffff0a] px-4 py-2 rounded-xl border border-[#00ff4190]">
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
                  className="rounded-xl overflow-hidden border border-[#3b3b3b] shadow-lg bg-[#1a1a1a] hover:bg-[#222] transition"
                >
                  <button
                    onClick={() => toggleAccordion(idx)}
                    className="w-full flex justify-between items-center px-6 py-5 font-semibold text-left"
                  >
                    <div>
                      <p className="text-xl font-bold text-white font-pg">{user.name}</p>
                      <p className="text-sm text-gray-400 mt-1 font-mono">
                        Timeline: {new Date(user.recorded_time).toLocaleString()}
                      </p>
                    </div>

                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-1">{getStatusIcon(user.voice)} Voice</div>
                      <div className="flex items-center gap-1">{getStatusIcon(user.validated)} Input Drift</div>
                      <span
                        className={`font-bold ${
                          user.driftScore >= 80
                            ? "text-green-400"
                            : user.driftScore >= 65
                            ? "text-yellow-400"
                            : "text-red-500"
                        }`}
                      >
                        {user.driftScore}%
                      </span>
                      <span
                        className={`px-3 py-1 rounded-full text-xs font-bold ${
                          user.threat === "Below" ? "bg-green-700" : "bg-red-600"
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
                        className="bg-[#0f0f0f] px-6 py-4 border-t border-[#333]"
                      >
                        <div className="flex justify-end mb-4">
                          <button
                            onClick={toggleViewMode}
                            className="flex items-center gap-2 px-4 py-2 bg-[#00FF41] text-black rounded hover:bg-[#0dfb2c] transition"
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
                        ) : (
                          <div className="space-y-2 text-sm text-gray-300 font-mono">
                            {userUsbEvents.map((usb, i) => (
                              <div key={i} className="border border-[#444] rounded p-3">
                                <p><strong>Timestamp:</strong> {new Date(usb.timestamp).toLocaleString()}</p>
                                <p><strong>Device Name:</strong> {usb.device_name}</p>
                                <p><strong>Vendor ID:</strong> {usb.vendor_id}</p>
                                <p><strong>Product ID:</strong> {usb.product_id}</p>
                                <p><strong>Serial:</strong> {usb.serial_number}</p>
                              </div>
                            ))}
                          </div>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              );
            })}
          </div>
        </motion.main>
      </div>
    </>
  );
}

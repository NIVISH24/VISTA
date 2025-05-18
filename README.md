# VISTA: Voice & Insider Surveillance for Threat Assessment

**Version**: 1.0.0  
**License**: MIT

---

## 📝 Overview

VISTA is a cutting-edge endpoint monitoring and authentication platform specialized in passive surveillance and real-time behavioral analytics to detect insider threats proactively. By leveraging voice biometrics, keystroke dynamics, hardware event monitoring, and AI-powered video analytics, VISTA delivers a robust multi-layered security solution with seamless integration into Linux-based systems.

---

## 🚀 Key Features

### 1. Multi-Layered Endpoint Agent

* **Lightweight Installation**: Installable via PyInstaller (Python) or Rust-based binary.  
* **System Fingerprinting**: Gathers MAC address, CPU ID, disk and RAM serials, OS version.  
* **Hardware Event Logger**: Detects USB insertion, NIC changes, hardware swaps, with timestamps.  
* **Mic Listener (Voice Biometrics)**:  
  * Captures 15s audio snippets.  
  * Extracts voice embeddings using Wav2Vec2.  
  * No raw audio stored—ensures privacy.  
* **Keystroke Dynamics**: Tracks timing, intervals, and pressure patterns.  
* **Mouse & App Monitoring**: X/Y tracking, click patterns, app launches, active windows.  
* **Offline Buffering**: Auto-sync on network reconnection.  
* **Security-First Encryption**: AES-256, agent self-checks, tamper detection.  

### 2. Voice + Password Multi-Factor Authentication (Linux PAM)

* **Seamless PAM Integration**: CLI-based voice enrollment & challenge-response.  
* **Real-Time Speaker Verification**: Random phrase validation with Wav2Vec2.  
* **Fallback & Policy Control**: Password-only mode after configurable failure count.  

### 3. Threat Detection & AI Engine

* **Anomaly Detection**: Isolation Forest on behavioral time-series.  
* **Dynamic Risk Scoring**: Real-time composite risk score (0–100) based on:  
  * Voice confidence  
  * Keystroke anomaly  
  * Hardware activity  
  * Device context  
* **Prototype Matching**: FAISS-backed quick similarity search.  
* **Per-User Thresholds**: Continuously updated using EMA.  

### 4. Security & Surveillance Dashboard

* **System Overview**: Health status, active sessions, alerts.  
* **Live Feed**: Suspicious events like USB inserts or failed voice attempts.  
* **Forensic Timeline**: Chronological event explorer with detailed plots and voice vectors.  

### 5. Visual Intrusion Detection (AI-Powered)

* **Camera Integration**: Monitors facial presence and motion anomalies.  
* **Intrusion Detection**: Alerts on unauthorized personnel.  
* **Visual Forensics**: Logs video metadata with behavioral data for cross-correlation.  

### 6. Seamless Deployment

* **Cloudflare-Enabled**: Secure, fast backend routing.  
* **Custom Domain**: Deployed on production-ready infrastructure.  

---

## 🧠 Our Capabilities

- **Insider Threat Protection**: Real-time behavior and event correlation.  
- **Voice-Based Authentication**: Privacy-preserving, spoof-resistant biometrics.  
- **Hardware Event Monitoring**: Deep audit trail of device-level activity.  
- **Camera-Based Surveillance**: AI-enhanced physical access monitoring.  
- **End-to-End Forensics**: Unified view for digital + physical investigations.  

---

## 🌐 Installation

```bash
# Clone the repository
git clone https://github.com/your-org/vista.git
cd vista

# Install the backend
cd server && ./install.sh
```

---

## 🔗 Linux PAM Integration

* **Update PAM Config**: Add `pam_vista.so` to `/etc/pam.d/sshd` or `/etc/pam.d/login`  
* **API Endpoint**: `https://<your-domain>/api/v1`  

---

## 📸 Visuals
![hero](https://github.com/user-attachments/assets/51d18b48-19cf-4ac0-927b-3fe62ee04482)
![dash](https://github.com/user-attachments/assets/d38b2e4c-32fa-4f59-8ac5-dd68b902ae09)
![dashboard](https://github.com/user-attachments/assets/f4766716-cdf6-41d6-9b08-d61f259edc72)

---

## 🤝 Contributing

1. Fork the repository  
2. Create a feature branch  
3. Submit a PR to `develop`  
4. Run tests (`pytest`) before final push  

---

## 🛡️ License


MIT © 2025 Your Organization

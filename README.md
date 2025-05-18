# VISTA: Voice & Insider Surveillance for Threat Assessment

**Version**: 1.0.0
**License**: MIT

---

## 📝 Overview

VISTA is a next-generation endpoint monitoring and authentication platform designed for passive surveillance and real-time behavioral analysis to detect insider threats. By combining biometric voice authentication, behavioral profiling, and hardware event monitoring, VISTA provides security teams with proactive alerts, forensic insights, and seamless multi-factor authentication on Linux systems.

---

## 🚀 Key Features

### 1. Endpoint Agent

* **Lightweight Installation**: Rust-based binary (\~30MB) or Python agent via PyInstaller.
* **System Fingerprinting**: Collects MAC address, CPU ID, disk serials, RAM serials, OS & patch level.
* **Hardware Event Logger**: Tracks USB insertions, new NIC attachments, RAM/SSD swaps, with timestamps.
* **Voice & Behavior Streamer**:

  * **Mic Listener**: Captures 15-second audio windows; extracts embeddings (no raw audio stored).
  * **Keystroke Dynamics**: Records key‑down/up durations, inter‑key intervals.
  * **Mouse Analytics**: Logs X/Y movements, velocity, click timing.
  * **Application Usage**: Monitors app launches, active window focus, login/logout times.
* **Offline Buffering**: Caches all captured data locally when offline; auto-syncs on network restoration.
* **Encryption & Integrity**: AES-256 wrapped data, agent self-integrity check, tamper alerts.

### 2. Voice & Password MFA Integration

* **PAM Module for Linux**: Seamless plug‑in using libpam.
* **Enrollment CLI**: Record voice samples; generate user voice profile.
* **Authentication Flow**:

  1. Password prompt
  2. Voice challenge (random phrase)
  3. Real‑time speaker verification
* **Failover**: Falls back to password-only after threshold failures; configurable policies.

### 3. Threat Detection & ML Engine

* **Anomaly Detection**: Isolation Forest on time-series behavior data.
* **Voice Stress Classifier**: Wav2Vec2 embeddings + XGBoost for stress/hesitation cues.
* **Risk Scoring**: Weighted fusion of hardware, behavior, and voice models into a 0–100 score.
* **Prototype Authentication**: Rapid nearest‑neighbor search via FAISS index on user prototypes.
* **Dynamic Thresholding**: Per-user & global thresholds, EMA-based prototype updates.

### 4. Security Dashboard

* **Overview Panel**: Active agents, health status, last check‑in, suspicion scores.
* **Heatmap View**: Org‑wide risk distribution by department & location.
* **Live Alerts Feed**: USB events, failed voice auth, high-risk behavior spikes.
* **Forensics Explorer**: Timeline view of events, raw feature plots, and audio embeddings.
* **Reporting**: Scheduled PDF/CSV exports with compliance-ready audit trails.
* **RBAC & SSO**: LDAP/Active Directory integration, JWT-based API auth.

### 5. Deployment Modes

* **On‑Premise**: Docker Compose & Helm charts available.
* **Hybrid**: Local data ingestion + optional cloud analytics module.
* **Air‑Gapped**: Model updates via signed USB packages.

---

## 🔧 Installation

```bash
# Clone repo
git clone https://github.com/your-org/vista.git
cd vista

# Install server components
cd server && ./install.sh

# Deploy agents via Ansible / SCCM
ansible-playbook -i inventory deploy-agents.yml
```

---

## 🔗 Integration

* **PAM Config**: Add `pam_vista.so` to `/etc/pam.d/sshd` and `/etc/pam.d/login`.
* **API Endpoint**: `https://<your-server>/api/v1`
* **MQTT Broker**: `mqtts://<broker-host>`
* **TLS Certs**: Place cert & key in `server/certs/`

---

## 📈 Performance & Sizing

* **Agent Footprint**: \~30MB RAM, \~5% CPU during voice capture.
* **Server**: Scales to 10k agents with Redis cluster & PostgreSQL replica set.

---

## 📚 Documentation

Detailed guides, API docs, and ML model specs are available in the `/docs` folder.

---

## 🤝 Contributing

1. Fork the repo
2. Create feature branch
3. Submit PR against `develop`
4. Ensure tests pass (`pytest`)

---

## 🛡️ License

MIT © 2025 Your Organization

# Voice-based PAM Authentication Setup

This guide walks through setting up voice-based authentication using PAM (Pluggable Authentication Modules) with a custom module that records audio and verifies it using an external API.

---

## 1. Install Required Dependencies

```bash
sudo apt update
sudo apt install libcurl4-openssl-dev libpam0g-dev alsa-utils
```

---

## 2. Create PAM Module Source File

```bash
nano pam_voice_auth.c
```

Paste the full C code provided for `pam_voice_auth.c` into the file.

> **Note**: Replace `https://your.server/api/voice-auth` with your actual voice authentication API URL.

---

## 3. Compile and Install the PAM Module

```bash
gcc -fPIC -shared -o pam_voice_auth.so pam_voice_auth.c -lcurl
sudo mv pam_voice_auth.so /lib/security/
```

---

## 4. Modify PAM Configuration for `sudo`

```bash
sudo nano /etc/pam.d/sudo
```

Add the following line at the top:

```text
auth    requisite    pam_voice_auth.so
```

---

## 5. Test the PAM Voice Authentication

Invalidate current sudo credentials and trigger a new authentication:

```bash
sudo -k
sudo echo test
```

You should be prompted for voice input. The recording will be sent to the API, and access will be granted/denied based on the result.

---

## Notes

* The module records a 3-second audio clip to `/tmp/voice.wav` using `arecord`.
* Ensure the server endpoint correctly returns a JSON result like:

  ```json
  {"result":"known"} // or "unknown"
  ```
* Logging is sent to system logs. Use `journalctl` or `syslog` tools to inspect PAM messages.
* You may extend this to other PAM-enabled programs beyond `sudo` (e.g., `login`, `ssh`, etc.).

---

This completes the setup for voice-based authentication via PAM using a custom C module and external API verification.

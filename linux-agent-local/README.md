# Linux Agent Setup and Management

This guide provides instructions for setting up, enabling, and managing the `linux-agent-local` service, including configuring logging and systemd.

---

## 1. Activate the Virtual Environment

```bash
source venv/bin/activate
```

---

## 2. Set Up Log Directory

```bash
sudo mkdir -p /var/log/linux-agent
sudo chown user:user /var/log/linux-agent
sudo chmod 755 /var/log/linux-agent
```

---

## 3. Install the Agent in Editable Mode

```bash
pip install -e .
```

---

## 4. Set Up the systemd Service

### Create/Edit Service File:

```bash
sudo nano /usr/lib/systemd/system/linux-agent-local.service
```

### Paste the following configuration:

```ini
[Service]
Type=simple
User=user
Group=user

# Environment
Environment="DISPLAY=:0"
Environment="XAUTHORITY=/home/user/.Xauthority"
Environment="LOG_DIR=/var/log/linux-agent"

# Working directory
WorkingDirectory=/home/user/Desktop/hackathon/linux-agent-local
ExecStart=/home/user/Desktop/hackathon/linux-agent-local/venv/bin/python -m agent.main

# Standard output logging
StandardOutput=append:/var/log/linux-agent/agent.log
StandardError=append:/var/log/linux-agent/agent.log

# Restart options
Restart=on-failure
RestartSec=5

# Logging directory
RuntimeDirectory=linux-agent
RuntimeDirectoryMode=0755
LogsDirectory=linux-agent
LogsDirectoryMode=0755

# Security restrictions
NoNewPrivileges=true
ProtectSystem=strict
ProtectHome=read-only
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

---

## 5. Reload and Enable Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable linux-agent-local.service
sudo systemctl start linux-agent-local.service
```

---

## 6. Monitor the Service

```bash
systemctl status linux-agent-local.service
journalctl -u linux-agent-local -b -f
tail -f /var/log/linux-agent/{module_name}.log
```

Replace `{module_name}` with the appropriate log module name.

---

## 7. Restart the Service

```bash
sudo systemctl daemon-reload
sudo systemctl restart linux-agent-local.service
sudo systemctl status linux-agent-local.service
journalctl -u linux-agent-local -b -f
tail -f /var/log/linux-agent/{module_name}.log
```

---

## 8. Stop and Disable the Service

```bash
sudo systemctl stop linux-agent-local.service
sudo systemctl disable linux-agent-local.service
```

---

## 9. To Stop Voice Recording from Root Directory

Run the following command from the root directory `/` as:

```bash
[user@user-arch /]$ sudo systemctl stop linux-agent-local.service
```

---

This completes the setup and management instructions for the Linux Agent.

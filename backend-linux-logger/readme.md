# PostgreSQL and Monitoring Utilities

This guide contains utilities for managing PostgreSQL tables, monitoring logs, and launching web interfaces.

---

## 1. Log Monitor Service Setup

### Create/Edit the Service File:

```bash
sudo nano /etc/systemd/system/log-monitor.service
```

> **Note**: Delete all entries in the file if necessary.

### Enable and Start the Service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable log-monitor.service
sudo systemctl start log-monitor.service
```

---

## 2. PostgreSQL: Delete All Data from All Tables

```bash
psql "postgres://url-here" -c "
DO \$\$
DECLARE
    tbl TEXT;
BEGIN
    FOR tbl IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        BEGIN
            EXECUTE format('DELETE FROM %I;', tbl);
        EXCEPTION WHEN others THEN
            RAISE NOTICE 'Skipping table % due to error: %', tbl, SQLERRM;
        END;
    END LOOP;
END
\$\$;"
```

---

## 3. PostgreSQL: Get Row Counts and Latest Timestamps

```bash
psql "postgres://url-here" <<EOF
SELECT 
    (SELECT COUNT(*) FROM mouse_events) AS mouse_events_count,
    (SELECT COUNT(*) FROM keystroke_events) AS keystroke_events_count,
    (SELECT COUNT(*) FROM system_info) AS system_info_count,
    (SELECT COUNT(*) FROM usb_events) AS usb_events_count,
    (SELECT COUNT(*) FROM voice_events) AS voice_events_count,
    (SELECT MAX(event_time) FROM mouse_events) AS latest_mouse_event,
    (SELECT MAX(event_time) FROM keystroke_events) AS latest_keystroke_event,
    (SELECT MAX(recorded_time) FROM system_info) AS latest_system_info,
    (SELECT MAX(event_time) FROM usb_events) AS latest_usb_event,
    (SELECT MAX(event_time) FROM voice_events) AS latest_voice_event;
EOF
```

---

## 4. PostgreSQL: View All Data

```bash
psql "postgres://url-here" <<EOF
-- Show all data from mouse_events
SELECT * FROM mouse_events;

-- Show all data from keystroke_events
SELECT * FROM keystroke_events;

-- Show all data from system_info
SELECT * FROM system_info;

-- Show all data from usb_events
SELECT * FROM usb_events;

-- Show all data from voice_events
SELECT * FROM voice_events;
EOF
```

---

## 5. Monitor Log File

```bash
tail -f ~/log-monitor-debug.log
```

---

## 6. Run FastAPI Server

```bash
uvicorn main:app --reload
```

---

## 7. Truncate Specific Table

```bash
psql "postgres://url-here" -c "TRUNCATE TABLE usb_events;"
```

---

## 8. Cloudflare Tunnel Setup

```bash
cloudflared tunnel --url http://localhost:8000
```

Then visit:

```
http://localhost:8000/docs
```

---

This guide supports PostgreSQL data management and service observation, complementing the Linux agent deployment.

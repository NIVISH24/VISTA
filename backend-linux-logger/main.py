import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["http://localhost:3000"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "sslmode": os.getenv("SSL_MODE")
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.expanduser('~/log-monitor-backend.log')
)
logger = logging.getLogger(__name__)

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

# Data Models
class MouseEvent(BaseModel):
    event_time: datetime
    event_type: str
    x: Optional[int] = None
    y: Optional[int] = None
    interval: Optional[float] = None
    device_fingerprint: str

class KeystrokeEvent(BaseModel):
    event_time: datetime
    key_pressed: str
    interval: float
    device_fingerprint: str

class SystemInfo(BaseModel):
    recorded_time: datetime
    mac_address: str
    cpu_info: str
    disk_info: str
    memory_info: int
    hostname: str
    os_info: str
    device_fingerprint: str

class USBEvent(BaseModel):
    event_time: datetime
    action: str
    vendor_id: str
    product_id: str
    vendor_name: str
    product_name: str
    serial_number: str
    device_fingerprint: str

class USBEventsRequest(BaseModel):
    events: List[USBEvent]

class VoiceEvent(BaseModel):
    event_time: datetime
    event_type: str
    file_path: Optional[str] = None
    duration: Optional[float] = None
    sample_rate: Optional[int] = None
    device_fingerprint: str

# API Endpoints
@app.post("/mouse-events/")
async def log_mouse_event(events: List[MouseEvent]):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            for event in events:
                cur.execute(
                    """
                    INSERT INTO mouse_events 
                    (event_time, event_type, x, y, interval, device_fingerprint)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (event.event_time, event.event_type, event.x, event.y, 
                     event.interval, event.device_fingerprint)
                )
            conn.commit()
            return {"status": "success", "count": len(events)}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting mouse events: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/keystroke-events/")
async def log_keystroke_event(events: List[KeystrokeEvent]):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            for event in events:
                cur.execute(
                    """
                    INSERT INTO keystroke_events 
                    (event_time, key_pressed, interval, device_fingerprint)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (event.event_time, event.key_pressed, 
                     event.interval, event.device_fingerprint)
                )
            conn.commit()
            return {"status": "success", "count": len(events)}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting keystroke events: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/system-info/")
async def log_system_info(info: SystemInfo):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO system_info 
                (recorded_time, mac_address, cpu_info, disk_info, memory_info, 
                 hostname, os_info, device_fingerprint)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (info.recorded_time, info.mac_address, info.cpu_info,
                 info.disk_info, info.memory_info, info.hostname,
                 info.os_info, info.device_fingerprint)
            )
            info_id = cur.fetchone()['id']
            conn.commit()
            return {"id": info_id, "status": "success"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/usb-events/")
async def log_usb_events(request: USBEventsRequest) -> dict:
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            values = [
                (
                    event.event_time, event.action, event.vendor_id,
                    event.product_id, event.vendor_name, event.product_name,
                    event.serial_number, event.device_fingerprint
                ) for event in request.events
            ]

            insert_query = """
                INSERT INTO usb_events 
                (event_time, action, vendor_id, product_id, vendor_name,
                 product_name, serial_number, device_fingerprint)
                VALUES %s
                RETURNING id
            """

            # Use psycopg2.extras.execute_values for efficient bulk insert
            from psycopg2.extras import execute_values
            execute_values(cur, insert_query, values)
            inserted_ids = [row["id"] for row in cur.fetchall()]
            conn.commit()
            return {"inserted_ids": inserted_ids, "status": "success"}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting USB events: {e}")
        raise HTTPException(status_code=500, detail="Failed to log USB events.")
    finally:
        conn.close()

from typing import List

@app.post("/voice-events/")
async def log_voice_events(events: List[VoiceEvent]):
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            inserted_ids = []
            for event in events:
                cur.execute(
                    """
                    INSERT INTO voice_events 
                    (event_time, event_type, file_path, duration, sample_rate, device_fingerprint)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (event.event_time, event.event_type, event.file_path,
                     event.duration, event.sample_rate, event.device_fingerprint)
                )
                event_id = cur.fetchone()['id']
                inserted_ids.append(event_id)
            conn.commit()
            return {"status": "success", "inserted_ids": inserted_ids, "count": len(inserted_ids)}
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting voice events: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()


@app.get("/health/")
async def health_check():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}

@app.get("/mouse-events/")
async def get_mouse_events():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM mouse_events ORDER BY event_time DESC")
            results = cur.fetchall()
            return {"mouse_events": results}
    except Exception as e:
        logger.error(f"Error fetching mouse events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch mouse events.")
    finally:
        conn.close()

@app.get("/keystroke-events/")
async def get_keystroke_events():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM keystroke_events ORDER BY event_time DESC")
            results = cur.fetchall()
            return {"keystroke_events": results}
    except Exception as e:
        logger.error(f"Error fetching keystroke events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch keystroke events.")
    finally:
        conn.close()

@app.get("/system-info/")
async def get_system_info():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM system_info ORDER BY recorded_time DESC")
            results = cur.fetchall()
            return {"system_info": results}
    except Exception as e:
        logger.error(f"Error fetching system info: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch system info.")
    finally:
        conn.close()

@app.get("/usb-events/")
async def get_usb_events():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM usb_events ORDER BY event_time DESC")
            results = cur.fetchall()
            return {"usb_events": results}
    except Exception as e:
        logger.error(f"Error fetching USB events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch USB events.")
    finally:
        conn.close()

@app.get("/voice-events/")
async def get_voice_events():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM voice_events ORDER BY event_time DESC")
            results = cur.fetchall()
            return {"voice_events": results}
    except Exception as e:
        logger.error(f"Error fetching voice events: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch voice events.")
    finally:
        conn.close()
import os
import time
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import requests
from typing import Optional, List, Dict, Any, DefaultDict, Union
from collections import defaultdict

# Configuration
LOG_DIR = "/var/log/linux-agent/"
LOG_FILES = {
    "mouse.log": "mouse",
    "keystroke.log": "keystroke",
    "system.log": "system",
    "usb.log": "usb",
    "voice_monitor.log": "voice"
}
API_BASE_URL = "http://localhost:8000"
CHECK_INTERVAL = 5  # seconds between file checks
BATCH_INTERVAL = 180  # 3 minutes in seconds
MAX_RETRIES = 3
API_TIMEOUT = 30  # Increased timeout for large batches
MAX_BATCH_SIZE = 100  # Maximum number of items per API call

# Robust logging setup
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.expanduser('~/log-monitor-debug.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BatchProcessor:
    def __init__(self):
        self.batches = defaultdict(list)
        self.last_flush_time = time.time()
    
    def add_to_batch(self, log_type: str, data: Any):
        """Add parsed data to the appropriate batch"""
        if isinstance(data, list):
            self.batches[log_type].extend(data)
        else:
            self.batches[log_type].append(data)
    
    def should_flush(self) -> bool:
        """Check if it's time to flush batches"""
        return time.time() - self.last_flush_time >= BATCH_INTERVAL
    
    def flush_all(self, sender) -> bool:
        """Flush all batches to their respective APIs"""
        success = True
        for log_type, batch in self.batches.items():
            if batch:
                if log_type == "system":
                    # System info must be sent individually
                    for item in batch:
                        logger.info(f"Flushing system info")
                        if not sender(log_type, [item]):  # Wrap in list for consistency
                            success = False
                else:
                    # Split large batches into smaller chunks
                    for i in range(0, len(batch), MAX_BATCH_SIZE):
                        chunk = batch[i:i + MAX_BATCH_SIZE]
                        logger.info(f"Flushing batch of {len(chunk)} {log_type} events")
                        if not sender(log_type, chunk):
                            success = False
                            break
        if success:
            self.batches.clear()
            self.last_flush_time = time.time()
        return success

class LogMonitor:
    def __init__(self):
        self.file_positions = {}
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        self.endpoint_mapping = {
            "mouse": "mouse-events/",
            "keystroke": "keystroke-events/",
            "system": "system-info/",
            "usb": "usb-events/",
            "voice": "voice-events/"
        }
        self.batch_processor = BatchProcessor()

    def parse_json_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """Improved JSON parser with timestamp handling"""
        try:
            # Handle both formats: with timestamp and pure JSON
            if line.startswith('20') and ' - ' in line:  # Has timestamp prefix
                json_part = line.split(' - ', 1)[1]
            else:
                json_part = line
            
            # Basic validation of JSON structure
            data = json.loads(json_part)
            if not isinstance(data, dict):
                logger.warning(f"Expected JSON object, got: {type(data)}")
                return None
            return data
        except json.JSONDecodeError as e:
            logger.debug(f"JSON parse error in line: {line[:100]}... Error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON: {str(e)}")
            return None

    def sanitize_event_data(self, event_data: Union[Dict, List]) -> Union[Dict, List, None]:
        """Ensure all required fields are present and properly formatted"""
        if isinstance(event_data, list):
            return [self._sanitize_single_event(e) for e in event_data if e]
        return self._sanitize_single_event(event_data)

    def _sanitize_single_event(self, event: Dict) -> Optional[Dict]:
        """Sanitize a single event"""
        if not event or not isinstance(event, dict):
            return None
            
        # Ensure required fields exist with proper types
        if 'event_time' not in event:
            event['event_time'] = datetime.now().isoformat()
            
        if 'device_fingerprint' not in event:
            event['device_fingerprint'] = 'unknown'
            
        # Type-specific sanitization
        if 'interval' in event and event['interval'] is None:
            event['interval'] = 0.0
            
        if 'memory_info' in event and event['memory_info'] is None:
            event['memory_info'] = 0
            
        if 'file_path' in event and event['file_path'] is None:
            event['file_path'] = ''
            
        if 'duration' in event and event['duration'] is None:
            event['duration'] = 0.0
            
        if 'sample_rate' in event and event['sample_rate'] is None:
            event['sample_rate'] = 0
            
        return event

    def parse_mouse_log(self, line: str) -> Optional[List[Dict[str, Any]]]:
        data = self.parse_json_log_line(line)
        if not data or not isinstance(data.get('data'), list):
            logger.warning(f"Invalid mouse data format: {data}")
            return None
        
        events = []
        for event in data['data']:
            try:
                if not isinstance(event, dict):
                    continue
                    
                # Required fields validation
                if 'time' not in event or 'type' not in event:
                    logger.warning(f"Missing required fields in mouse event: {event}")
                    continue
                    
                events.append({
                    'event_time': datetime.fromisoformat(event['time']).isoformat(),
                    'event_type': event['type'],
                    'x': event.get('x'),
                    'y': event.get('y'),
                    'interval': float(event.get('interval', 0.0)),
                    'device_fingerprint': data.get('device_fingerprint', 'unknown')
                })
            except ValueError as e:
                logger.warning(f"Invalid format in mouse event: {str(e)}")
            except Exception as e:
                logger.warning(f"Unexpected error parsing mouse event: {str(e)}")
        return events or None

    def parse_keystroke_log(self, line: str) -> Optional[List[Dict[str, Any]]]:
        data = self.parse_json_log_line(line)
        if not data or not isinstance(data.get('data'), list):
            logger.warning(f"Invalid keystroke data format: {data}")
            return None
        
        events = []
        previous_time = None
        
        for event in data['data']:
            try:
                if not isinstance(event, dict):
                    continue
                    
                # Required fields validation
                if 'time' not in event or 'key' not in event:
                    logger.warning(f"Missing required fields in keystroke event: {event}")
                    continue
                    
                current_time = datetime.fromisoformat(event['time'])
                
                # Calculate interval if this isn't the first event
                interval = 0.0  # Default value
                if previous_time is not None:
                    interval = (current_time - previous_time).total_seconds()
                
                events.append({
                    'event_time': current_time.isoformat(),
                    'key_pressed': event['key'],
                    'interval': interval,
                    'device_fingerprint': data.get('device_fingerprint', 'unknown')
                })
                
                previous_time = current_time
                
            except ValueError as e:
                logger.warning(f"Invalid timestamp format in keystroke event: {str(e)}")
            except Exception as e:
                logger.warning(f"Unexpected error parsing keystroke event: {str(e)}")
        
        return events or None

    def parse_system_log(self, line: str) -> Optional[Dict[str, Any]]:
        data = self.parse_json_log_line(line)
        if not data:
            return None
        
        try:
            # Validate required fields
            if 'timestamp' not in data or 'data' not in data:
                logger.warning(f"Missing required fields in system log: {data}")
                return None
                
            if not isinstance(data['data'], dict):
                logger.warning(f"System data should be an object: {data['data']}")
                return None
                
            return {
                'recorded_time': datetime.fromisoformat(data['timestamp']).isoformat(),
                'mac_address': data['data'].get('mac_address', 'unknown'),
                'cpu_info': data['data'].get('cpu_info', 'unknown'),
                'disk_info': data['data'].get('disk_info', 'unknown'),
                'memory_info': int(data['data'].get('memory_info', 0)),
                'hostname': data['data'].get('hostname', 'unknown'),
                'os_info': data['data'].get('os_info', 'unknown'),
                'device_fingerprint': data.get('fingerprint', '11d97794a37682881989d999a7ef03f95ead9ad8a7fc8f92b38f754524adb82f')
            }
        except ValueError as e:
            logger.warning(f"Invalid format in system log: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error parsing system log: {str(e)}")
            return None

    def parse_usb_log(self, line: str) -> Optional[Dict[str, Any]]:
        data = self.parse_json_log_line(line)
        if not data:
            return None
        
        try:
            # Validate required fields
            required_fields = ['timestamp', 'action', 'vendor_id', 'product_id', 'vendor', 'product', 'serial']
            for field in required_fields:
                if field not in data:
                    logger.warning(f"Missing required field '{field}' in USB event: {data}")
                    return None
                
            return {
                'event_time': datetime.fromisoformat(data['timestamp']).isoformat(),
                'action': data['action'],
                'vendor_id': data['vendor_id'],
                'product_id': data['product_id'],
                'vendor_name': data['vendor'],
                'product_name': data['product'],
                'serial_number': data['serial'],
                'device_fingerprint': data.get('device_fingerprint', 'unknown')
            }
        except ValueError as e:
            logger.warning(f"Invalid timestamp format in USB event: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error parsing USB event: {str(e)}")
            return None

    def parse_voice_log(self, line: str) -> Optional[Dict[str, Any]]:
        data = self.parse_json_log_line(line)
        if not data:
            return None
        
        try:
            # Validate required fields
            if 'timestamp' not in data or 'event' not in data:
                logger.warning(f"Missing required fields in voice event: {data}")
                return None
                
            return {
                'event_time': datetime.fromisoformat(data['timestamp']).isoformat(),
                'event_type': data['event'],
                'file_path': data.get('filepath', ''),
                'duration': float(data.get('duration', 0.0)),
                'sample_rate': int(data.get('sample_rate', 0)),
                'device_fingerprint': data.get('device_fingerprint', 'unknown')
            }
        except ValueError as e:
            logger.warning(f"Invalid format in voice event: {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Unexpected error parsing voice event: {str(e)}")
            return None

    def send_to_api(self, endpoint: str, data: Any) -> bool:
        """Robust API sender with retries and validation"""
        url = f"{API_BASE_URL}/{endpoint}"

        for attempt in range(MAX_RETRIES):
            try:
                logger.debug(f"Attempt {attempt+1} to {url} with {len(data) if isinstance(data, list) else 1} items")
                
                # Ensure data is properly formatted before sending
                sanitized_data = self.sanitize_event_data(data)
                if not sanitized_data:
                    logger.error("No valid data to send after sanitization")
                    return False

                # Special handling for system info (single item only)
                if endpoint == "system-info/":
                    if isinstance(sanitized_data, list):
                        if len(sanitized_data) != 1:
                            logger.error("system-info/ endpoint only accepts one record at a time")
                            return False
                        sanitized_data = sanitized_data[0]  # Unwrap list

                # Wrap list for usb-events endpoint
                if endpoint == "usb-events/" and isinstance(sanitized_data, list):
                    sanitized_data = {"events": sanitized_data}

                response = self.session.post(
                    url,
                    json=sanitized_data,
                    timeout=API_TIMEOUT
                )

                if response.status_code == 200:
                    count = (
                        len(sanitized_data["events"])
                        if endpoint == "usb-events/" and isinstance(sanitized_data, dict) and "events" in sanitized_data
                        else 1 if not isinstance(sanitized_data, list)
                        else len(sanitized_data)
                    )
                    logger.info(f"Successfully sent batch of {count} items to {endpoint}")
                    return True

                # Detailed error logging
                if response.status_code == 422:
                    error_detail = response.json().get('detail', 'No details')
                    logger.error(f"Validation error for {endpoint}: {error_detail}")

                    problem_item = (
                        sanitized_data["events"][0]
                        if endpoint == "usb-events/" and isinstance(sanitized_data, dict)
                        else sanitized_data[0]
                        if isinstance(sanitized_data, list)
                        else sanitized_data
                    )
                    logger.debug(f"First problematic item: {json.dumps(problem_item, indent=2)}")
                else:
                    logger.error(f"API error {response.status_code}: {response.text}")

                if response.status_code >= 500:
                    time.sleep(1)  # Wait before retrying server errors

            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {str(e)}")

            if attempt < MAX_RETRIES - 1:
                time.sleep(1)  # Wait before next retry

        logger.error(f"Failed after {MAX_RETRIES} attempts to send to {endpoint}")
        return False

    def monitor_file(self, log_path: str, log_type: str):
        """Robust file monitoring with position tracking"""
        try:
            current_size = os.path.getsize(log_path)
            last_position = self.file_positions.get(log_path, 0)
            
            # Handle log rotation
            if current_size < last_position:
                logger.info(f"Log rotation detected for {log_path}")
                last_position = 0
            
            if current_size == last_position:
                return  # No new data
            
            with open(log_path, 'r') as f:
                f.seek(last_position)
                new_lines = f.readlines()
                self.file_positions[log_path] = f.tell()
                
                for line in new_lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        parsed_data = None
                        
                        if log_type == "mouse":
                            parsed_data = self.parse_mouse_log(line)
                        elif log_type == "keystroke":
                            parsed_data = self.parse_keystroke_log(line)
                        elif log_type == "system":
                            parsed_data = self.parse_system_log(line)
                        elif log_type == "usb":
                            parsed_data = self.parse_usb_log(line)
                        elif log_type == "voice":
                            parsed_data = self.parse_voice_log(line)
                        
                        if parsed_data:
                            sanitized_data = self.sanitize_event_data(parsed_data)
                            if sanitized_data:
                                self.batch_processor.add_to_batch(log_type, sanitized_data)
                            
                    except Exception as e:
                        logger.error(f"Line processing failed: {str(e)}")
                        
        except FileNotFoundError:
            logger.warning(f"File not found: {log_path}")
        except Exception as e:
            logger.error(f"File monitoring error: {str(e)}")
            self.file_positions[log_path] = 0  # Reset on error

    def run(self):
        logger.info(f"Starting log monitor service with batch interval of {BATCH_INTERVAL} seconds")
        try:
            while True:
                start_time = time.time()
                
                # Check all log files for new data
                for log_file, log_type in LOG_FILES.items():
                    log_path = os.path.join(LOG_DIR, log_file)
                    if os.path.exists(log_path):
                        self.monitor_file(log_path, log_type)
                    else:
                        logger.debug(f"File not present: {log_path}")
                
                # Check if it's time to flush batches
                if self.batch_processor.should_flush():
                    logger.info("Batch interval reached, flushing all batches")
                    self.batch_processor.flush_all(
                        lambda log_type, data: self.send_to_api(
                            self.endpoint_mapping[log_type], 
                            data
                        )
                    )
                
                # Precise timing control
                elapsed = time.time() - start_time
                sleep_time = max(0, CHECK_INTERVAL - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    
        except KeyboardInterrupt:
            # Attempt to flush any remaining data before exiting
            logger.info("Received interrupt, attempting to flush remaining batches")
            self.batch_processor.flush_all(
                lambda log_type, data: self.send_to_api(
                    self.endpoint_mapping[log_type], 
                    data
                )
            )
            logger.info("Shutting down")
        except Exception as e:
            logger.error(f"Fatal error: {str(e)}")
        finally:
            logger.info("Log monitor stopped")

if __name__ == "__main__":
    # First verify API connectivity
    test_script = os.path.join(os.path.dirname(__file__), "test_api.py")
    if os.path.exists(test_script):
        os.system(f"python {test_script}")
    
    # Start the monitor
    monitor = LogMonitor()
    monitor.run()
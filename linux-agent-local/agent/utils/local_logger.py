
import json
import os
import logging
import tempfile
from datetime import datetime
from logging.handlers import RotatingFileHandler

class LocalLogger:
    def __init__(self, max_size_mb=10, backup_count=5):
        # Determine log directory from environment or default to /var/log/linux-agent
        self.log_dir = os.getenv("LOG_DIR", "/var/log/linux-agent")
        self.max_size_mb = max_size_mb
        self.backup_count = backup_count
        self.loggers = {}  # Dictionary to store module-specific loggers
        
        # Ensure log directory exists
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _get_logger(self, module_name):
        """Get or create a logger for a specific module"""
        if module_name in self.loggers:
            return self.loggers[module_name]
        
        # Create new logger
        logger = logging.getLogger(f'linux_agent.{module_name}')
        logger.setLevel(logging.INFO)
        
        # Create module-specific log file
        log_file = os.path.join(self.log_dir, f'{module_name}.log')
        
        try:
            handler = RotatingFileHandler(
                log_file,
                maxBytes=self.max_size_mb * 1024 * 1024,
                backupCount=self.backup_count,
                encoding='utf-8'
            )
            formatter = logging.Formatter('%(asctime)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
            self.loggers[module_name] = logger
            return logger
            
        except Exception as e:
            print(f"Failed to create logger for {module_name}: {str(e)}")
            # Fallback to system logger if module-specific logger fails
            return self._get_logger('system')

    def log_event(self, event_data):
        """Log event to module-specific log file"""
        try:
            if not isinstance(event_data, dict):
                event_data = {"data": event_data}
            
            # Determine module name (default to 'system' if not specified)
            module_name = event_data.get("module", "system")
            
            # Add timestamp if not present
            event_data.setdefault("timestamp", datetime.now().isoformat())
            
            # Get the appropriate logger
            logger = self._get_logger(module_name)
            
            # Log the event as JSON
            logger.info(json.dumps(event_data))
            
        except Exception as e:
            print(f"Error logging event: {str(e)}")
            print(f"Event data that failed to log: {str(event_data)}")

    def get_log_path(self, module_name='system'):
        """Return the current active log file path for a module"""
        return os.path.join(self.log_dir, f'{module_name}.log')

from pyudev import Context, Monitor, MonitorObserver
from datetime import datetime

class USBMonitor:
    def __init__(self, callback):
        self.callback = callback
        self.context = Context()
        self.monitor = Monitor.from_netlink(self.context)
        self.monitor.filter_by(subsystem='usb')
        self.observer = None
        self.running = False

    def _device_event(self, device):
        action = device.action
        if action in ('add', 'remove'):
            device_info = {
                "action": action,
                "time": datetime.now().isoformat(),
                "vendor_id": device.get('ID_VENDOR_ID', 'unknown'),
                "product_id": device.get('ID_MODEL_ID', 'unknown'),
                "vendor": device.get('ID_VENDOR_ENC', 'unknown'),
                "product": device.get('ID_MODEL_ENC', 'unknown'),
                "serial": device.get('ID_SERIAL_SHORT', 'unknown')
            }
            self.callback(device_info)

    def start(self):
        if not self.running:
                self.running = True
                self.observer = MonitorObserver(
                    self.monitor,
                    callback=lambda device: self._device_event(device),
                    name='usb-monitor'
                )
                self.observer.start()

    def stop(self):
        if self.running:
            self.running = False
            if self.observer:
                self.observer.stop()

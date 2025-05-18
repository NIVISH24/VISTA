
import psutil
import uuid
import hashlib
import platform
import socket
import netifaces

def get_real_mac():
    for iface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(iface)
        mac_info = addrs.get(netifaces.AF_LINK)
        if mac_info and len(mac_info) > 0:
            mac = mac_info[0]['addr']
            if mac and mac != '00:00:00:00:00:00':
                return mac
    return "00:00:00:00:00:00"

def get_device_fingerprint():
    try:
        mac = get_real_mac()

        cpu_info = platform.processor()
        if not cpu_info:
            cpu_info = platform.uname().machine or "unknown"

        partitions = psutil.disk_partitions(all=True)
        disk_info = partitions[0].device if partitions else "unknown"

        mem_info = psutil.virtual_memory().total

        fingerprint_str = f"{mac}-{cpu_info}-{disk_info}-{mem_info}"
        fingerprint = hashlib.sha256(fingerprint_str.encode()).hexdigest()

        return {
            "mac_address": mac,
            "cpu_info": cpu_info,
            "disk_info": disk_info,
            "memory_info": mem_info,
            "fingerprint": fingerprint,
            "hostname": socket.gethostname(),
            "os_info": f"{platform.system()} {platform.release()}"
        }
    except Exception as e:
        return {"error": str(e)}


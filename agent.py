import psutil
import time
import socketio
import platform
from datetime import datetime

sio = socketio.Client()

def get_system_metrics():
    # Get disk usage
    disk = psutil.disk_usage('/')
    disk_total = round(disk.total / (1024**3), 2)  # Convert to GB
    disk_used = round(disk.used / (1024**3), 2)
    disk_percent = disk.percent

    # Get RAM usage
    ram = psutil.virtual_memory()
    ram_total = round(ram.total / (1024**3), 2)  # Convert to GB
    ram_used = round(ram.used / (1024**3), 2)
    ram_percent = ram.percent

    # Get CPU usage and temperature
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_temp = None
    if hasattr(psutil, "sensors_temperatures"):
        temps = psutil.sensors_temperatures()
        if temps:
            for name, entries in temps.items():
                if entries:
                    cpu_temp = entries[0].current
                    break

    return {
        "hostname": platform.node(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "online": True,
        "disk_usage": {
            "total": disk_total,
            "used": disk_used,
            "percent": disk_percent
        },
        "ram": {
            "total": ram_total,
            "used": ram_used,
            "percent": ram_percent
        },
        "cpu": {
            "cores": psutil.cpu_count(),
            "usage": cpu_percent,
            "temperature": cpu_temp
        }
    }

@sio.event
def connect():
    print('Connected to server')

@sio.event
def disconnect():
    print('Disconnected from server')

def main():
    try:
        sio.connect('http://100.104.69.66:5001')
        while True:
            metrics = get_system_metrics()
            sio.emit('metrics_update', metrics)
            time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")
        if sio.connected:
            sio.disconnect()

if __name__ == '__main__':
    main()

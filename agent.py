import psutil
import time
import socketio
import platform
from datetime import datetime

sio = socketio.Client()

def get_system_metrics(online_status=None):
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
        "online": online_status if online_status is not None else connection_status.get('connected', False),
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

# Track connection status
connection_status = {'connected': False}

@sio.event
def connect():
    connection_status['connected'] = True
    print('Connected to server')
    # Send initial metrics with online status
    metrics = get_system_metrics()
    sio.emit('metrics_update', metrics)

@sio.event
def disconnect():
    connection_status['connected'] = False
    print('Disconnected from server')
    # Try to send offline status
    try:
        metrics = get_system_metrics()
        metrics['online'] = False
        sio.emit('metrics_update', metrics)
    except:
        pass

def get_server_url():
    # Get server URL from environment variable or use default
    return os.environ.get('SERVER_URL', 'http://100.104.69.66:5001')

def main():
    server_url = get_server_url()
    while True:
        try:
            print(f'Connecting to server at {server_url}...')
            sio.connect(server_url)
            
            # Main loop - send metrics every 5 seconds
            while True:
                try:
                    metrics = get_system_metrics()
                    sio.emit('metrics_update', metrics)
                    time.sleep(5)
                except Exception as e:
                    print(f"Error sending metrics: {e}")
                    break
                    
        except Exception as e:
            print(f"Connection error: {e}")
        
        finally:
            if sio.connected:
                try:
                    sio.disconnect()
                except:
                    pass
        
        print('Retrying in 5 seconds...')
        time.sleep(5)

if __name__ == '__main__':
    main()

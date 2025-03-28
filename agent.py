import psutil
import platform
import requests
import time
import socket
from datetime import datetime

class SystemMonitorAgent:
    def __init__(self, server_url):
        self.server_url = server_url
        self.hostname = socket.gethostname()
        
    def get_system_metrics(self):
        metrics = {
            'hostname': self.hostname,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'online': True,
            'disk_usage': {
                'total': round(psutil.disk_usage('/').total / (1024**3), 2),  # GB
                'used': round(psutil.disk_usage('/').used / (1024**3), 2),    # GB
                'free': round(psutil.disk_usage('/').free / (1024**3), 2),    # GB
                'percent': psutil.disk_usage('/').percent
            },
            'ram': {
                'total': round(psutil.virtual_memory().total / (1024**3), 2),  # GB
                'used': round(psutil.virtual_memory().used / (1024**3), 2),    # GB
                'free': round(psutil.virtual_memory().free / (1024**3), 2),    # GB
                'percent': psutil.virtual_memory().percent
            },
            'cpu': {
                'usage': psutil.cpu_percent(interval=1),
                'cores': psutil.cpu_count(),
                'temperature': None
            }
        }
        
        # Try to get CPU temperature
        try:
            temps = psutil.sensors_temperatures()
            if 'coretemp' in temps:
                metrics['cpu']['temperature'] = temps['coretemp'][0].current
            elif 'cpu_thermal' in temps:
                metrics['cpu']['temperature'] = temps['cpu_thermal'][0].current
        except:
            pass
            
        return metrics
    
    def send_metrics(self):
        try:
            metrics = self.get_system_metrics()
            response = requests.post(f"{self.server_url}/update_metrics", json=metrics)
            if response.status_code == 200:
                print(f"Successfully sent metrics for {self.hostname}")
            else:
                print(f"Failed to send metrics: {response.status_code}")
        except Exception as e:
            print(f"Error sending metrics: {str(e)}")

def main():
    # Replace with your server's IP address and port
    server_url = "http://SERVER_IP:5001"
    agent = SystemMonitorAgent(server_url)
    
    print(f"Starting monitoring agent for {agent.hostname}")
    print(f"Sending metrics to {server_url}")
    
    while True:
        agent.send_metrics()
        time.sleep(5)  # Send metrics every 5 seconds

if __name__ == "__main__":
    main()

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import psutil
import platform
import time
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

def get_system_metrics():
    metrics = {
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
            'temperature': None  # Will be updated if available
        }
    }
    
    # Try to get CPU temperature (not available on all systems)
    try:
        temps = psutil.sensors_temperatures()
        if 'coretemp' in temps:
            metrics['cpu']['temperature'] = temps['coretemp'][0].current
        elif 'cpu_thermal' in temps:
            metrics['cpu']['temperature'] = temps['cpu_thermal'][0].current
    except:
        pass
    
    return metrics

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/metrics')
def metrics():
    return jsonify(get_system_metrics())

def background_metrics():
    while True:
        metrics = get_system_metrics()
        socketio.emit('metrics_update', metrics)
        time.sleep(5)  # Update every 5 seconds

if __name__ == '__main__':
    from threading import Thread
    metrics_thread = Thread(target=background_metrics, daemon=True)
    metrics_thread.start()
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)

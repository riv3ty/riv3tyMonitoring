from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
from datetime import datetime
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# Store metrics from all agents
agents_metrics = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update_metrics', methods=['POST'])
def update_metrics():
    metrics = request.json
    hostname = metrics.get('hostname')
    if hostname:
        agents_metrics[hostname] = metrics
        socketio.emit('metrics_update', {'agents': list(agents_metrics.values())})
    return jsonify({'status': 'success'})

@app.route('/metrics')
def metrics():
    return jsonify({'agents': list(agents_metrics.values())})

def cleanup_old_agents():
    while True:
        current_time = datetime.now()
        to_remove = []
        for hostname, metrics in agents_metrics.items():
            try:
                last_update = datetime.strptime(metrics['timestamp'], '%Y-%m-%d %H:%M:%S')
                # Remove agents that haven't reported in 30 seconds
                if (current_time - last_update).seconds > 30:
                    to_remove.append(hostname)
            except:
                to_remove.append(hostname)
        
        for hostname in to_remove:
            del agents_metrics[hostname]
            
        time.sleep(10)

if __name__ == '__main__':
    from threading import Thread
    cleanup_thread = Thread(target=cleanup_old_agents, daemon=True)
    cleanup_thread.start()
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
import json
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

# Default settings
default_settings = {
    "display": {
        "show_disk": True,
        "show_ram": True,
        "show_cpu": True,
        "show_temp": True,
        "show_status": True
    },
    "theme": {
        "dark_mode": True,
        "accent_color": "#007bff"
    },
    "refresh_rate": 5
}

def save_settings(settings):
    with open('settings.json', 'w') as f:
        json.dump(settings, f, indent=4)

def load_settings():
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        save_settings(default_settings)
        return default_settings

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/settings', methods=['GET'])
def get_settings():
    return jsonify(load_settings())

@app.route('/settings', methods=['POST'])
def update_settings():
    settings = request.json
    save_settings(settings)
    socketio.emit('settings_update', settings)
    return jsonify({"status": "success"})

@socketio.on('metrics_update')
def handle_metrics_update(data):
    socketio.emit('metrics_update', {'agents': [data]})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)

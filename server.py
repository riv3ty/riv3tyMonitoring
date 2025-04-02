from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_socketio import SocketIO
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User
from notifications import TelegramNotifier
import json
import os
import time
from threading import Thread
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

socketio = SocketIO(app, cors_allowed_origins='*')
notifier = TelegramNotifier()

# Store last heartbeat time for each agent
agent_heartbeats = {}

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
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
    # Get hostname and status from the data
    hostname = data.get('hostname')
    timestamp = data.get('timestamp')
    
    # Update heartbeat time
    agent_heartbeats[hostname] = datetime.now()
    
    status = {
        'online': True,  # If we receive an update, the agent is online
        'timestamp': timestamp
    }
    
    # Extract metrics for resource monitoring
    metrics = {
        'ram': data.get('ram', {}),
        'cpu': data.get('cpu', {}),
        'disk_usage': data.get('disk_usage', {})
    }
    
    # Check for status changes and resource usage
    notifier.notify_status_change(hostname, status, timestamp, metrics)
    
    # Emit the update to all clients
    socketio.emit('metrics_update', {'agents': [data]})

def check_agent_status():
    while True:
        current_time = datetime.now()
        for hostname, last_heartbeat in list(agent_heartbeats.items()):
            # If no heartbeat for more than 15 seconds, consider agent offline
            if current_time - last_heartbeat > timedelta(seconds=15):
                # Mark agent as offline
                status = {
                    'online': False,
                    'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S')
                }
                notifier.notify_status_change(hostname, status, status['timestamp'])
                del agent_heartbeats[hostname]  # Remove from tracking
        time.sleep(5)  # Check every 5 seconds

def create_admin_user():
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin')
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()

if __name__ == '__main__':
    create_admin_user()
    # Start the agent status checker in a background thread
    status_checker = Thread(target=check_agent_status, daemon=True)
    status_checker.start()
    # Allow connections from any IP and disable debug mode in production
    socketio.run(app, host='0.0.0.0', port=5001, debug=False, allow_unsafe_werkzeug=True)

from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_socketio import SocketIO
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User
import json
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change this to a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

socketio = SocketIO(app, cors_allowed_origins='*')

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
    socketio.emit('metrics_update', {'agents': [data]})

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
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)

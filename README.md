# Riv3ty Monitoring

A system monitoring tool with real-time updates and Telegram notifications.

## Features
- Real-time system metrics monitoring (CPU, RAM, Disk)
- Multi-agent support
- Telegram notifications for system status changes
- User authentication
- Dark/Light mode support

## Installation

1. Clone the repository:
```bash
git clone https://github.com/riv3ty/riv3tyMonitoring.git
cd riv3tyMonitoring
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Telegram notifications:
```bash
cp telegram_config.example.py telegram_config.py
```
Then edit `telegram_config.py` with your Telegram bot token and chat ID.

4. Run the server:
```bash
python server.py
```

5. Run the agent on each machine you want to monitor:
```bash
python agent.py
```

## Default Login
- Username: admin
- Password: admin

## Configuration
- Server runs on port 5001 by default
- Agent automatically connects to the server
- System status is checked every 5 seconds
- Offline detection occurs after 15 seconds of no response

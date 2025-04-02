# Riv3ty Monitoring

A system monitoring tool with real-time updates and Telegram notifications.

## Features
- Real-time system metrics monitoring (CPU, RAM, Disk)
- Multi-agent support
- Telegram notifications for system status changes and resource usage
- User authentication
- Dark/Light mode support
- Docker support for server
- Installable agent package

## Server Installation (Docker)

1. Clone the repository:
```bash
git clone https://github.com/riv3ty/riv3tyMonitoring.git
cd riv3tyMonitoring
```

2. Configure Telegram notifications:
```bash
cp telegram_config.example.py telegram_config.py
```
Edit `telegram_config.py` with your Telegram bot token and chat ID.

3. Start the server using Docker Compose:
```bash
docker-compose up -d
```

The server will be available at `http://your-server:5001`

## Agent Installation

1. Install the agent package on each machine you want to monitor:
```bash
# From PyPI (recommended)
pip install riv3ty-monitoring-agent

# OR from source
git clone https://github.com/riv3ty/riv3tyMonitoring.git
cd riv3tyMonitoring
pip install .
```

2. Run the agent:
```bash
riv3ty-agent
```

## Default Login
- Username: admin
- Password: admin

## Configuration

### Server
- Runs on port 5001 by default
- Data is persisted in Docker volume
- Automatically restarts unless stopped

### Agent
- Automatically connects to the server
- System status is checked every 5 seconds
- Offline detection occurs after 15 seconds of no response

### Resource Monitoring
- RAM usage alerts at 80%
- CPU usage alerts at 80%
- Disk usage alerts at 80%
- Configurable alert thresholds

## Docker Commands

Start the server:
```bash
docker-compose up -d
```

View logs:
```bash
docker-compose logs -f
```

Stop the server:
```bash
docker-compose down
```

Update to latest version:
```bash
git pull
docker-compose up -d --build
```

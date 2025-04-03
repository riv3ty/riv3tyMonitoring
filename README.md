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

## Installation

### Option 1: Combined Server and Agent (Same Machine)

1. In Portainer, go to "Stacks" and click "Add stack"

2. Enter a name for your stack (e.g., "riv3ty-monitoring")

3. Copy and paste the following Docker Compose configuration:
```yaml
version: '3.8'

services:
  riv3ty-server:
    image: ghcr.io/riv3ty/riv3tymonitoring:latest
    container_name: riv3ty-monitoring
    ports:
      - "5001:5001"
    environment:
      - TELEGRAM_BOT_TOKEN=your_bot_token_here
      - TELEGRAM_CHAT_ID=your_chat_id_here
      - TZ=Europe/Berlin
      - PYTHONUNBUFFERED=1
    volumes:
      - riv3ty_data:/app/instance
    restart: unless-stopped
    networks:
      - riv3ty-net

  riv3ty-agent:
    image: ghcr.io/riv3ty/riv3tymonitoring-agent:latest
    container_name: riv3ty-agent
    environment:
      - SERVER_URL=http://riv3ty-server:5001
      - TZ=Europe/Berlin
      - HOSTNAME=docker-host
    restart: unless-stopped
    pid: host
    privileged: true
    depends_on:
      - riv3ty-server
    networks:
      - riv3ty-net

networks:
  riv3ty-net:
    driver: bridge

volumes:
  riv3ty_data:
    driver: local
```

4. Replace the environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID

5. Click "Deploy the stack"

This will start both the server and an agent to monitor the host system.

### Option 2: Server Only Installation (Recommended for Multiple Agents)

1. In Portainer, go to "Stacks" and click "Add stack"

2. Enter a name for your stack (e.g., "riv3ty-monitoring")

3. Copy and paste the following Docker Compose configuration:
```yaml
version: '3.8'

services:
  riv3ty-monitoring:
    image: ghcr.io/riv3ty/riv3tymonitoring:latest
    container_name: riv3ty-monitoring
    ports:
      - "5001:5001"
    environment:
      - TELEGRAM_BOT_TOKEN=your_bot_token_here
      - TELEGRAM_CHAT_ID=your_chat_id_here
      - TZ=Europe/Berlin
      - PYTHONUNBUFFERED=1
    volumes:
      - riv3ty_data:/app/instance
    restart: unless-stopped
    networks:
      - riv3ty-net

networks:
  riv3ty-net:
    driver: bridge

volumes:
  riv3ty_data:
    driver: local
```

4. Replace the environment variables:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
   - `TELEGRAM_CHAT_ID`: Your Telegram chat ID

5. Click "Deploy the stack"

The server will be available at `http://your-server:5001`

### Option 2: Manual Docker Installation

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

## Agent Installation

### Option 1: Using Portainer (Recommended)

1. In Portainer, go to "Stacks" and click "Add stack"

2. Enter a name for your stack (e.g., "riv3ty-agent")

3. Copy and paste the following Docker Compose configuration:
```yaml
version: '3.8'

services:
  riv3ty-agent:
    image: ghcr.io/riv3ty/riv3tymonitoring-agent:latest
    container_name: riv3ty-agent
    environment:
      - SERVER_URL=http://your_server_ip:5001  # Replace with your server IP
      - TZ=Europe/Berlin
      - HOSTNAME=${HOSTNAME:-unknown}
    restart: unless-stopped
    pid: host
    privileged: true
```

4. Replace `your_server_ip` with the IP address of your monitoring server

5. Click "Deploy the stack"

### Option 2: Using pip (Traditional)

1. Install the agent package:
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

# Network System Monitoring Tool

A web-based network monitoring tool that displays system metrics from multiple devices:
- Online status
- Disk usage
- RAM usage
- CPU usage and temperature (if available)

## Requirements
- Python 3.7+
- Required Python packages (install using requirements.txt)

## Installation

1. Install the required packages on all systems (server and agents):
```bash
pip install -r requirements.txt
```

## Usage

### 1. Start the Central Monitoring Server

On the machine that will act as the central monitoring server:

```bash
python server.py
```

The server will run on port 5001. You can access the web interface at:
```
http://SERVER_IP:5001
```

### 2. Start Monitoring Agents

On each machine you want to monitor:

1. Edit the `agent.py` file and update the `server_url` variable with your server's IP address:
```python
server_url = "http://SERVER_IP:5001"  # Replace SERVER_IP with your server's IP address
```

2. Run the agent:
```bash
python agent.py
```

## Features
- Real-time monitoring of multiple systems using WebSocket
- Modern, responsive web interface
- Visual indicators for resource usage levels
- Automatic updates every 5 seconds
- Automatic detection of offline systems
- Support for multiple operating systems

## Notes
- Make sure all machines can reach the server on port 5001
- Agents will automatically reconnect if the connection is lost
- Systems are considered offline if they haven't reported in 30 seconds

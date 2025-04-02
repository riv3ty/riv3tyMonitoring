#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Riv3ty Monitoring Server Installation...${NC}"

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Install Docker if not installed
if ! command_exists docker; then
    echo -e "${YELLOW}Docker not found. Installing Docker...${NC}"
    # Update package list
    apt-get update
    
    # Install prerequisites
    apt-get install -y \
        apt-transport-https \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker's official GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

    # Add Docker repository
    echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
    
    # Start and enable Docker service
    systemctl start docker
    systemctl enable docker
fi

# Install Docker Compose if not installed
if ! command_exists docker-compose; then
    echo -e "${YELLOW}Docker Compose not found. Installing Docker Compose...${NC}"
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
fi

# Create directory for monitoring server
echo -e "${GREEN}Creating directory for Riv3ty Monitoring...${NC}"
mkdir -p /opt/riv3ty-monitoring
cd /opt/riv3ty-monitoring

# Clone the repository
echo -e "${GREEN}Cloning repository...${NC}"
if [ -d ".git" ]; then
    git pull
else
    git clone https://github.com/riv3ty/riv3tyMonitoring.git .
fi

# Setup Telegram config if not exists
if [ ! -f "telegram_config.py" ]; then
    echo -e "${YELLOW}Setting up Telegram configuration...${NC}"
    cp telegram_config.example.py telegram_config.py
    echo -e "${RED}Please edit telegram_config.py with your Telegram bot token and chat ID${NC}"
    echo -e "You can edit it using: nano telegram_config.py"
fi

# Configure firewall if UFW is installed
if command_exists ufw; then
    echo -e "${YELLOW}Configuring firewall...${NC}"
    ufw allow 5001/tcp comment 'Riv3ty Monitoring'
    ufw reload
fi

# Start the server
echo -e "${GREEN}Starting Riv3ty Monitoring server...${NC}"
docker-compose down  # Stop any existing containers
docker-compose pull  # Pull latest images
docker-compose up -d # Start containers

# Create systemd service for auto-start
echo -e "${GREEN}Creating systemd service for auto-start...${NC}"
cat > /etc/systemd/system/riv3ty-monitoring.service << EOL
[Unit]
Description=Riv3ty Monitoring Server
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/riv3ty-monitoring
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down

[Install]
WantedBy=multi-user.target
EOL

# Enable and start the service
systemctl enable riv3ty-monitoring
systemctl start riv3ty-monitoring

# Show status
echo -e "${GREEN}Installation completed!${NC}"
echo -e "${YELLOW}Server Status:${NC}"
docker-compose ps

echo -e "\n${GREEN}Installation Summary:${NC}"
echo -e "1. Server installed at: /opt/riv3ty-monitoring"
echo -e "2. Service name: riv3ty-monitoring"
echo -e "3. Web interface: http://$(hostname -I | cut -d' ' -f1):5001"
echo -e "\n${YELLOW}Next steps:${NC}"
echo -e "1. Edit telegram_config.py with your bot token and chat ID:"
echo -e "   cd /opt/riv3ty-monitoring && nano telegram_config.py"
echo -e "2. Restart the server after editing:"
echo -e "   systemctl restart riv3ty-monitoring"
echo -e "3. Check logs if needed:"
echo -e "   docker-compose logs -f"

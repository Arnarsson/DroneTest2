#!/bin/bash

# DroneWatch Worker Installation Script
# Run with sudo

set -e

echo "Installing DroneWatch Ingestion Worker..."

# Create user if doesn't exist
if ! id "dronewatch" &>/dev/null; then
    echo "Creating dronewatch user..."
    useradd -r -s /usr/sbin/nologin dronewatch
fi

# Create directories
echo "Setting up directories..."
mkdir -p /opt/dronewatch/worker
mkdir -p /var/log

# Copy worker files
echo "Copying worker files..."
cp -r worker/* /opt/dronewatch/worker/

# Install Python dependencies
echo "Installing Python dependencies..."
cd /opt/dronewatch/worker
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# Setup environment file
if [ ! -f /opt/dronewatch/worker/.env ]; then
    echo "Creating .env file..."
    cp /opt/dronewatch/worker/.env.example /opt/dronewatch/worker/.env
    echo "⚠️  Please edit /opt/dronewatch/worker/.env with your configuration"
fi

# Set permissions
echo "Setting permissions..."
chown -R dronewatch:dronewatch /opt/dronewatch/worker
chmod 600 /opt/dronewatch/worker/.env

# Install systemd service
echo "Installing systemd service..."
cp ops/systemd/dronewatch-worker.service /etc/systemd/system/
systemctl daemon-reload

echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit /opt/dronewatch/worker/.env with your API credentials"
echo "2. Start the service: systemctl start dronewatch-worker"
echo "3. Enable on boot: systemctl enable dronewatch-worker"
echo "4. Check logs: journalctl -u dronewatch-worker -f"
#!/bin/bash

# UrVote Systemd Service Installation Script
# This script will set up the systemd service for UrVote

set -e

echo "🚀 Setting up UrVote systemd service..."

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   exit 1
fi

# Create urvote user and group (for secure version)
echo "👤 Creating urvote user and group..."
if ! id "urvote" &>/dev/null; then
    useradd --system --create-home --shell /bin/false urvote
    echo "✅ Created urvote user"
else
    echo "ℹ️  urvote user already exists"
fi

# Set proper ownership
echo "🔐 Setting file permissions..."
chown -R urvote:urvote /opt/urvote
chmod -R 755 /opt/urvote
chmod 755 /opt/urvote/uploads

# Copy service file to systemd directory
echo "📁 Installing systemd service..."
cp urvote-secure.service /etc/systemd/system/urvote.service

# Reload systemd daemon
echo "🔄 Reloading systemd daemon..."
systemctl daemon-reload

# Enable and start the service
echo "🚀 Enabling and starting UrVote service..."
systemctl enable urvote
systemctl start urvote

# Check service status
echo "📊 Service status:"
systemctl status urvote --no-pager -l

echo ""
echo "✅ UrVote systemd service has been installed and started!"
echo ""
echo "📋 Useful commands:"
echo "  View logs:     sudo journalctl -u urvote -f"
echo "  Stop service:  sudo systemctl stop urvote"
echo "  Start service: sudo systemctl start urvote"
echo "  Restart:       sudo systemctl restart urvote"
echo "  Status:        sudo systemctl status urvote"
echo ""
echo "🌐 The service should now be running on port 8002"
echo "📁 Logs are available via journalctl"

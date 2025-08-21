#!/bin/bash

# Jasper TG BULK - Update and Restart Script
# This script handles all updates and service restarts after code changes

set -e  # Exit on any error

echo "🚀 Jasper TG BULK - Update and Restart Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "main_bot.py" ] || [ ! -f "main_admin.py" ]; then
    print_error "This script must be run from the JasperTgBulk directory!"
    print_error "Current directory: $(pwd)"
    exit 1
fi

print_status "Current directory: $(pwd)"

# Step 1: Git operations
echo ""
print_status "Step 1: Updating from Git repository..."
print_status "Pulling latest changes from main branch..."

if git pull origin main; then
    print_success "Successfully pulled latest changes from main"
else
    print_warning "Git pull failed or no changes to pull"
fi

# Step 2: Check for new dependencies
echo ""
print_status "Step 2: Checking for new dependencies..."

if [ -f "requirements.txt" ]; then
    print_status "Installing/updating Python dependencies..."
    
    # Activate virtual environment
    if [ -d ".venv" ]; then
        print_status "Activating virtual environment..."
        source .venv/bin/activate
        
        # Upgrade pip first
        print_status "Upgrading pip..."
        pip install --upgrade pip
        
        # Install/update requirements
        print_status "Installing requirements..."
        pip install -r requirements.txt
        
        print_success "Dependencies updated successfully"
    else
        print_error "Virtual environment (.venv) not found!"
        print_status "Creating new virtual environment..."
        python3 -m venv .venv
        source .venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Virtual environment created and dependencies installed"
    fi
else
    print_warning "requirements.txt not found, skipping dependency update"
fi

# Step 3: Database operations
echo ""
print_status "Step 3: Checking database..."

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    print_status "Creating data directory..."
    mkdir -p data
    print_success "Data directory created"
fi

# Step 4: Restart services
echo ""
print_status "Step 4: Restarting services..."

# Function to restart a service
restart_service() {
    local service_name=$1
    local display_name=$2
    
    print_status "Restarting $display_name service..."
    
    if sudo systemctl is-active --quiet $service_name; then
        print_status "Stopping $display_name service..."
        sudo systemctl stop $service_name
        
        # Wait a moment
        sleep 2
        
        print_status "Starting $display_name service..."
        sudo systemctl start $service_name
        
        # Check status
        if sudo systemctl is-active --quiet $service_name; then
            print_success "$display_name service restarted successfully"
        else
            print_error "$display_name service failed to start"
            sudo systemctl status $service_name
        fi
    else
        print_warning "$display_name service is not running, starting it..."
        sudo systemctl start $service_name
        
        if sudo systemctl is-active --quiet $service_name; then
            print_success "$display_name service started successfully"
        else
            print_error "$display_name service failed to start"
            sudo systemctl status $service_name
        fi
    fi
}

# Reload systemd daemon
print_status "Reloading systemd daemon..."
sudo systemctl daemon-reload

# Restart bot service
restart_service "jaspertgbulk-bot" "Bot"

# Restart admin service
restart_service "jaspertgbulk-admin" "Admin Panel"

# Step 5: Check service status
echo ""
print_status "Step 5: Checking service status..."

echo ""
print_status "Bot service status:"
sudo systemctl status jaspertgbulk-bot --no-pager -l

echo ""
print_status "Admin service status:"
sudo systemctl status jaspertgbulk-admin --no-pager -l

# Step 6: Check if services are listening
echo ""
print_status "Step 6: Checking if services are listening..."

# Check admin panel port
if netstat -tlnp 2>/dev/null | grep -q ":8000"; then
    print_success "Admin panel is listening on port 8000"
else
    print_warning "Admin panel is not listening on port 8000"
fi

# Step 7: Final status
echo ""
print_status "Step 7: Final status check..."

# Check if both services are enabled
if sudo systemctl is-enabled jaspertgbulk-bot >/dev/null 2>&1; then
    print_success "Bot service is enabled (will start on boot)"
else
    print_warning "Bot service is not enabled (won't start on boot)"
fi

if sudo systemctl is-enabled jaspertgbulk-admin >/dev/null 2>&1; then
    print_success "Admin service is enabled (will start on boot)"
else
    print_warning "Admin service is not enabled (won't start on boot)"
fi

echo ""
print_success "🎉 Update and restart completed successfully!"
echo ""
print_status "Quick commands:"
echo "  • Check bot logs:    sudo journalctl -u jaspertgbulk-bot -f"
echo "  • Check admin logs:  sudo journalctl -u jaspertgbulk-admin -f"
echo "  • Restart bot:       sudo systemctl restart jaspertgbulk-bot"
echo "  • Restart admin:     sudo systemctl restart jaspertgbulk-admin"
echo "  • Check status:      sudo systemctl status jaspertgbulk-*"
echo ""
print_status "Your Jasper TG BULK system is now updated and running! 🚀"

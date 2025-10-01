#!/bin/bash

# School Management System - Smart Launcher (Linux/Mac)
# Colors for beautiful output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Set terminal title
echo -ne "\033]0;School Management System - Smart Launcher\007"

# Clear screen and show banner
clear
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗"
echo -e "║                                                              ║"
echo -e "║  ${BOLD}🎓 SCHOOL MANAGEMENT SYSTEM - SMART LAUNCHER${NC}${CYAN}              ║"
echo -e "║                                                              ║"
echo -e "║  ${GREEN}✨ Auto Network Detection  📱 Mobile Hotspot Support${NC}${CYAN}      ║"
echo -e "║  ${GREEN}🌐 Browser Auto-Launch     📊 Real-time Logs${NC}${CYAN}             ║"
echo -e "║  ${GREEN}📶 HTTP Only (Offline)     🚀 One-Click Startup${NC}${CYAN}           ║"
echo -e "║                                                              ║"
echo -e "╚══════════════════════════════════════════════════════════════╝${NC}"
echo

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}❌ Virtual environment not found!${NC}"
    echo -e "${YELLOW}💡 Please run: python3 -m venv venv${NC}"
    exit 1
fi

# Activate virtual environment
echo -e "${YELLOW}🔄 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ manage.py not found! Please run from Django project root.${NC}"
    exit 1
fi

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}❌ Python 3.8+ required. Current: $python_version${NC}"
    exit 1
fi

# Install required packages if not present
echo -e "${YELLOW}🔍 Checking dependencies...${NC}"
python3 -c "import psutil" 2>/dev/null || {
    echo -e "${YELLOW}📦 Installing psutil...${NC}"
    pip install psutil
}

# Check for production mode argument
PRODUCTION_MODE="false"
if [ "$1" = "--production" ] || [ "$1" = "-p" ]; then
    PRODUCTION_MODE="true"
fi

# Set environment variables for production
if [ "$PRODUCTION_MODE" = "true" ]; then
    echo -e "${RED}🚀 Starting in PRODUCTION mode...${NC}"
    export PRODUCTION=true
    export DEBUG=False
else
    echo -e "${GREEN}🚀 Starting in DEVELOPMENT mode...${NC}"
    export PRODUCTION=false
fi

# Make the Python script executable
chmod +x start_server.py

# Run the Python startup script
echo -e "${GREEN}🚀 Starting School Management System...${NC}"
python3 start_server.py

# Keep terminal open on error
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Server failed to start${NC}"
    read -p "Press Enter to exit..."
fi
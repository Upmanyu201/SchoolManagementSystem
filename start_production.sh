#!/bin/bash

# School Management System - Production Mode Launcher
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

clear
echo -e "${RED}========================================"
echo -e "   PRODUCTION MODE STARTUP"
echo -e "========================================${NC}"
echo

# Set production environment variables
export PRODUCTION=true
export DEBUG=False
export DJANGO_SETTINGS_MODULE=school_management.settings

# Call the main startup script with production flag
./start_server.sh --production
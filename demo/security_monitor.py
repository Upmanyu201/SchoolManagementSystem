"""
Anti-Piracy Security Monitor
============================

This module monitors and logs potential piracy attempts.
"""

import logging
import os
from datetime import datetime
from django.conf import settings

# Create security logger
def setup_security_logging():
    """Setup dedicated security logging for anti-piracy monitoring"""
    
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(settings.BASE_DIR, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Security log file
    security_log_file = os.path.join(logs_dir, 'security.log')
    
    # Configure security logger
    security_logger = logging.getLogger('demo.security')
    security_logger.setLevel(logging.INFO)
    
    # Create file handler
    handler = logging.FileHandler(security_log_file)
    handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - SECURITY - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    # Add handler to logger
    if not security_logger.handlers:
        security_logger.addHandler(handler)
    
    return security_logger

def log_piracy_attempt(attempt_type, details):
    """Log potential piracy attempts"""
    logger = setup_security_logging()
    
    log_message = f"PIRACY ATTEMPT - {attempt_type}: {details}"
    logger.critical(log_message)
    
    # Also log to console in debug mode
    if settings.DEBUG:
        print(f"🚨 SECURITY ALERT: {log_message}")

def log_license_activity(activity, details):
    """Log license-related activities"""
    logger = setup_security_logging()
    
    log_message = f"LICENSE ACTIVITY - {activity}: {details}"
    logger.info(log_message)

# Initialize security logging
setup_security_logging()
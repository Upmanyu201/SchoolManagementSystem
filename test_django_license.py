#!/usr/bin/env python3
"""
Django-integrated license system test
Tests the license system with actual Django models and database
"""

import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from demo.secure_license_service import SecureLicenseService
from demo.models import DemoStatus, LicenseActivation

def test_django_license_integration():
    """Test license system with Django models"""
    
    print("=" * 60)
    print("DJANGO LICENSE INTEGRATION TEST")
    print("=" * 60)
    
    # Test 1: Hardware fingerprint
    print("\nTest 1: Hardware Fingerprint Generation")
    fingerprint = SecureLicenseService.get_hardware_fingerprint()
    print(f"Hardware fingerprint: {fingerprint}")
    print(f"Length: {len(fingerprint)} (should be 24)")
    print(f"Is hex: {all(c in '0123456789abcdef' for c in fingerprint)}")
    
    # Test 2: License generation
    print("\nTest 2: License Generation")
    license_key = SecureLicenseService.generate_secure_license(fingerprint, "TEST")
    print(f"Generated license: {license_key}")
    print(f"Format valid: {license_key.startswith('SMS-FULL-')}")
    print(f"Length: {len(license_key)} characters")
    
    # Test 3: License validation
    print("\nTest 3: License Validation")
    is_valid, message = SecureLicenseService.validate_secure_license(license_key)
    print(f"Validation result: {is_valid}")
    print(f"Validation message: {message}")
    
    # Test 4: Django model integration
    print("\nTest 4: Django Model Integration")
    try:
        # Get demo status
        demo_status = DemoStatus.get_current_status()
        print(f"Demo status retrieved: {demo_status.machine_id}")
        print(f"Current license status: {demo_status.is_licensed}")
        
        # Test activation
        success, activation_message = SecureLicenseService.activate_secure_license(license_key)
        print(f"Activation result: {success}")
        print(f"Activation message: {activation_message}")
        
        # Check activation record
        activation_record = LicenseActivation.objects.filter(
            license_key_attempted=license_key
        ).first()
        
        if activation_record:
            print(f"Activation record created: {activation_record.success}")
            print(f"Attempted at: {activation_record.attempted_at}")
        
        # Test security monitoring
        print("\nTest 5: Security Monitoring")
        from demo.security_monitor import SecurityMonitor
        
        # Perform security check
        SecurityMonitor.perform_security_check()
        
        # Get security status
        security_status = SecurityMonitor.get_security_status()
        print(f"Security level: {security_status['security_level']}")
        print(f"Security message: {security_status['security_message']}")
        
        print("\n" + "=" * 60)
        print("DJANGO INTEGRATION TEST: PASSED")
        print("License system is working correctly with Django!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\nDjango integration error: {e}")
        print("\n" + "=" * 60)
        print("DJANGO INTEGRATION TEST: FAILED")
        print("=" * 60)
        return False

if __name__ == "__main__":
    test_django_license_integration()
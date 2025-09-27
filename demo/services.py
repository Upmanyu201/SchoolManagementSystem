import hashlib
import platform
from django.utils import timezone
from .models import DemoStatus, LicenseActivation

class LicenseService:
    """Centralized license validation and management"""
    
    SECRET_KEY = "SMS_2024_SECURE_KEY"  # Change in production
    
    @classmethod
    def get_machine_id(cls):
        """Generate unique machine identifier"""
        machine_info = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
        return hashlib.sha256(machine_info.encode()).hexdigest()[:16]
    
    @classmethod
    def generate_license_key(cls, machine_id=None):
        """Generate license key for machine"""
        if not machine_id:
            machine_id = cls.get_machine_id()
        
        hash_input = f"{machine_id}{cls.SECRET_KEY}"
        hash_output = hashlib.sha256(hash_input.encode()).hexdigest()[:12]
        
        return f"SMS-{hash_output[:4].upper()}-{hash_output[4:8].upper()}-{hash_output[8:12].upper()}"
    
    @classmethod
    def validate_license_key(cls, license_key, machine_id=None):
        """Validate license key for current machine"""
        if not license_key or len(license_key) != 17:
            return False, "Invalid license key format"
        
        parts = license_key.split('-')
        if len(parts) != 4 or parts[0] != 'SMS':
            return False, "Invalid license key format"
        
        expected_key = cls.generate_license_key(machine_id)
        if license_key.upper() != expected_key:
            return False, "License key does not match this machine"
        
        return True, "Valid license key"
    
    @classmethod
    def get_demo_status(cls):
        """Get current demo status"""
        return DemoStatus.get_current_status()
    
    @classmethod
    def activate_license(cls, license_key, user=None):
        """Activate license with validation"""
        demo_status = cls.get_demo_status()
        
        # Log activation attempt
        activation = LicenseActivation.objects.create(
            demo_status=demo_status,
            license_key_attempted=license_key,
            attempted_by=user
        )
        
        # Validate license key
        is_valid, message = cls.validate_license_key(license_key)
        
        if is_valid:
            demo_status.is_licensed = True
            demo_status.license_key = license_key.upper()
            demo_status.activated_by = user
            demo_status.activated_at = timezone.now()
            demo_status.save()
            
            activation.success = True
            activation.save()
            
            return True, "License activated successfully!"
        else:
            activation.error_message = message
            activation.save()
            
            return False, message
    
    @classmethod
    def check_demo_limits(cls, module_name, action_type):
        """Check if action is allowed under demo limitations"""
        demo_status = cls.get_demo_status()
        
        if demo_status.is_licensed:
            return True, "Licensed version - no limits"
        
        if not demo_status.is_active:
            return False, "Demo period has expired"
        
        # Module-specific limits
        if module_name == 'messaging':
            if action_type == 'bulk_sms':
                return False, "Bulk messaging requires licensed version"
            elif action_type == 'daily_sms_count':
                # This would be checked in the calling code
                return True, f"Demo: {demo_status.days_remaining} days remaining"
        
        return True, f"Demo: {demo_status.days_remaining} days remaining"
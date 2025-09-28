import hashlib
import platform
from django.utils import timezone
from .models import DemoStatus, LicenseActivation

class LicenseService:
    """Centralized license validation and management"""
    
    SECRET_KEY = "SMS_2024_SECURE_KEY"  # Change in production
    
    @classmethod
    def get_machine_id(cls):
        """Generate stable unique machine identifier"""
        import uuid
        
        # Use stable hardware identifiers only
        identifiers = [
            platform.node(),           # Computer name
            platform.machine(),        # CPU architecture  
            str(uuid.getnode()),       # MAC address (most stable)
        ]
        
        # Combine stable identifiers
        machine_info = '-'.join(filter(None, identifiers))
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
        if not license_key:
            return False, "License key is required"
        
        # Clean and validate format
        license_key = license_key.strip().upper()
        parts = license_key.split('-')
        
        if len(parts) != 4 or parts[0] != 'SMS':
            return False, "Invalid license key format. Expected: SMS-XXXX-XXXX-XXXX"
        
        # Validate each part length
        if len(parts[1]) != 4 or len(parts[2]) != 4 or len(parts[3]) != 4:
            return False, "Invalid license key format. Each section must be 4 characters"
        
        # Generate expected key for this machine
        expected_key = cls.generate_license_key(machine_id)
        
        if license_key != expected_key:
            return False, f"License key does not match this machine. Expected format: SMS-XXXX-XXXX-XXXX"
        
        return True, "Valid license key"
    
    @classmethod
    def get_demo_status(cls):
        """Get current demo status with anti-piracy validation"""
        status = DemoStatus.get_current_status()
        
        # Periodic validation: Check if machine ID still matches
        if status.is_licensed:
            current_machine_id = cls.get_machine_id()
            if status.machine_id != current_machine_id:
                # Machine changed - possible piracy attempt
                import logging
                logger = logging.getLogger('demo.security')
                logger.critical(f'PIRACY DETECTED: Machine ID changed from {status.machine_id} to {current_machine_id}')
                
                # Revoke license
                status.is_licensed = False
                status.license_key = None
                status.activated_by = None
                status.activated_at = None
                status.save()
                
        return status
    
    @classmethod
    def activate_license(cls, license_key, user=None):
        """Activate license with enhanced anti-piracy validation"""
        import logging
        
        demo_status = cls.get_demo_status()
        current_machine_id = cls.get_machine_id()
        
        # Enhanced logging for security monitoring
        logger = logging.getLogger('demo.security')
        logger.info(f'License activation attempt: {license_key[:8]}... on machine {current_machine_id}')
        
        # Log activation attempt with machine info
        activation = LicenseActivation.objects.create(
            demo_status=demo_status,
            license_key_attempted=license_key,
            attempted_by=user
        )
        
        # Validate license key
        is_valid, message = cls.validate_license_key(license_key)
        
        if is_valid:
            # Additional security: Check if license is already active on another machine
            existing_license = DemoStatus.objects.filter(
                license_key=license_key.upper(),
                is_licensed=True
            ).exclude(machine_id=current_machine_id).first()
            
            if existing_license:
                logger.warning(f'PIRACY ATTEMPT: License {license_key[:8]}... already active on machine {existing_license.machine_id}')
                activation.error_message = "License already active on another device"
                activation.save()
                return False, "This license is already active on another device. Each license works on one machine only."
            
            # Activate license
            demo_status.is_licensed = True
            demo_status.license_key = license_key.upper()
            demo_status.activated_by = user
            demo_status.activated_at = timezone.now()
            demo_status.save()
            
            activation.success = True
            activation.save()
            
            logger.info(f'License activated successfully on machine {current_machine_id}')
            return True, "License activated successfully!"
        else:
            logger.warning(f'License validation failed: {message}')
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
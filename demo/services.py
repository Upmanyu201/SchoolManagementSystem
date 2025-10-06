# DEPRECATED: This file is kept for backward compatibility only
# The secure license system is now in secure_license_service.py

import hashlib
import platform
from django.utils import timezone
from .models import DemoStatus, LicenseActivation

# Import secure service with fallback
try:
    from .secure_license_service import LicenseService
except ImportError:
    # Fallback to legacy implementation if secure service fails
    class LicenseService:
        """Centralized license validation and management"""
    
        SECRET_KEY = "SMS_2024_SECURE_KEY"  # Change in production
    
        @classmethod
        def get_machine_id(cls):
            """Generate stable unique machine identifier that never changes"""
            import uuid
            import subprocess
            import os
        
            # Check if we have a cached machine ID first
            cache_file = os.path.join(os.path.dirname(__file__), '.machine_id')
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r') as f:
                        cached_id = f.read().strip()
                        if len(cached_id) == 16:
                            return cached_id
                except:
                    pass
        
            # Generate stable hardware-based identifiers
            identifiers = []
        
            try:
                # 1. MAC Address (most stable)
                mac = uuid.getnode()
                identifiers.append(str(mac))
            
                # 2. CPU Architecture
                identifiers.append(platform.machine())
            
                # 3. Windows: Use WMIC for motherboard serial
                if platform.system() == 'Windows':
                    try:
                        result = subprocess.run(['wmic', 'baseboard', 'get', 'serialnumber'], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            lines = result.stdout.strip().split('\n')
                            if len(lines) > 1:
                                serial = lines[1].strip()
                                if serial and serial != 'SerialNumber':
                                    identifiers.append(serial)
                    except:
                        pass
                    
                    # Windows: CPU ID
                    try:
                        result = subprocess.run(['wmic', 'cpu', 'get', 'processorid'], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            lines = result.stdout.strip().split('\n')
                            if len(lines) > 1:
                                cpu_id = lines[1].strip()
                                if cpu_id and cpu_id != 'ProcessorId':
                                    identifiers.append(cpu_id)
                    except:
                        pass
                
                # 4. Linux/Mac: Use hardware info
                elif platform.system() in ['Linux', 'Darwin']:
                    try:
                        # Try to get machine ID from /etc/machine-id or /var/lib/dbus/machine-id
                        machine_id_files = ['/etc/machine-id', '/var/lib/dbus/machine-id']
                        for file_path in machine_id_files:
                            if os.path.exists(file_path):
                                with open(file_path, 'r') as f:
                                    machine_id = f.read().strip()
                                    if machine_id:
                                        identifiers.append(machine_id)
                                        break
                    except:
                        pass
                
                # 5. Fallback: Use system UUID if available
                try:
                    if platform.system() == 'Windows':
                        result = subprocess.run(['wmic', 'csproduct', 'get', 'uuid'], 
                                              capture_output=True, text=True, timeout=5)
                        if result.returncode == 0:
                            lines = result.stdout.strip().split('\n')
                            if len(lines) > 1:
                                system_uuid = lines[1].strip()
                                if system_uuid and system_uuid != 'UUID':
                                    identifiers.append(system_uuid)
                except:
                    pass
        
            except Exception:
                # Ultimate fallback
                identifiers = [str(uuid.getnode()), platform.machine()]
        
            # Ensure we have at least some identifiers
            if not identifiers:
                identifiers = [str(uuid.getnode()), 'fallback']
        
            # Combine all identifiers
            machine_info = '-'.join(filter(None, identifiers))
            machine_id = hashlib.sha256(machine_info.encode()).hexdigest()[:16]
        
            # Cache the machine ID for future use
            try:
                os.makedirs(os.path.dirname(cache_file), exist_ok=True)
                with open(cache_file, 'w') as f:
                    f.write(machine_id)
            except:
                pass
        
            return machine_id
    
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
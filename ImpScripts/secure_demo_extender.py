#!/usr/bin/env python3
"""
SECURE DEMO EXTENDER - Max 30 Days
Secure demo extension with username/password authentication
"""

import os
import sys
import hashlib
import getpass
import django
from datetime import timedelta
from django.utils import timezone

# Setup Django - Auto-detect if running from ImpScripts or project root
script_dir = os.path.dirname(__file__)
if 'ImpScripts' in script_dir:
    # Running from ImpScripts directory
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    sys.path.insert(0, project_root)
else:
    # Running from project root
    project_root = os.getcwd()
    sys.path.insert(0, project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'school_management.settings')
django.setup()

from demo.models import DemoStatus

class SecureDemoExtender:
    """Secure demo extension with authentication"""
    
    # AUTHORIZED USERS (hashed passwords)
    AUTHORIZED_USERS = {
        'admin': '8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918',  # admin123
        'support': 'ef92b778bafe771e89245b89ecbc08a44a4e166c06659911881f383d4473e94f',  # support456
        'developer': '2bb80d537b1da3e38bd30361aa855686bde0eacd7162fef6a25fe97bf527a25b'  # dev789
    }
    
    MAX_EXTENSION_DAYS = 30
    
    @classmethod
    def hash_password(cls, password):
        """Hash password with SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @classmethod
    def authenticate(cls):
        """Authenticate user with username/password"""
        print("🔐 AUTHENTICATION REQUIRED")
        print("-" * 30)
        
        max_attempts = 3
        for attempt in range(max_attempts):
            username = input("Username: ").strip().lower()
            password = getpass.getpass("Password: ")
            
            if username in cls.AUTHORIZED_USERS:
                password_hash = cls.hash_password(password)
                if password_hash == cls.AUTHORIZED_USERS[username]:
                    print(f"✅ Authentication successful for {username}")
                    return True, username
            
            remaining = max_attempts - attempt - 1
            if remaining > 0:
                print(f"❌ Invalid credentials. {remaining} attempts remaining.")
            else:
                print("❌ Authentication failed. Access denied.")
        
        return False, None
    
    @classmethod
    def get_demo_status(cls):
        """Get current demo status"""
        try:
            demo_status = DemoStatus.get_current_status()
            return demo_status
        except Exception as e:
            print(f"❌ Error getting demo status: {e}")
            return None
    
    @classmethod
    def extend_demo(cls, days, username):
        """Extend demo period with security checks"""
        if days > cls.MAX_EXTENSION_DAYS:
            print(f"❌ Maximum extension is {cls.MAX_EXTENSION_DAYS} days")
            return False
        
        try:
            demo_status = cls.get_demo_status()
            if not demo_status:
                return False
            
            if demo_status.is_licensed:
                print("✅ Already licensed - no extension needed")
                return True
            
            # Calculate new expiry
            current_expiry = demo_status.demo_expires
            new_expiry = max(timezone.now(), current_expiry) + timedelta(days=days)
            
            # Security: Limit total demo period
            max_total_days = 90  # Maximum 90 days total
            total_days = (new_expiry - demo_status.demo_started).days
            
            if total_days > max_total_days:
                print(f"❌ Total demo period cannot exceed {max_total_days} days")
                return False
            
            # Update demo status
            demo_status.demo_expires = new_expiry
            demo_status.save()
            
            # Log the extension
            cls.log_extension(username, days, demo_status)
            
            print(f"✅ Demo extended by {days} days")
            print(f"  New expiry: {new_expiry.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Days remaining: {demo_status.days_remaining}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error extending demo: {e}")
            return False
    
    @classmethod
    def log_extension(cls, username, days, demo_status):
        """Log demo extension for audit trail"""
        log_file = os.path.join(os.path.dirname(__file__), 'demo_extensions.log')
        
        try:
            with open(log_file, 'a', encoding='utf-8') as f:
                timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"{timestamp} | {username} | Extended {days} days | "
                       f"Machine: {demo_status.machine_id} | "
                       f"New expiry: {demo_status.demo_expires}\n")
        except Exception as e:
            print(f"⚠️ Could not log extension: {e}")

def main():
    """Main function"""
    print("🔒 SECURE DEMO EXTENDER")
    print("=" * 40)
    print("Maximum extension: 30 days per operation")
    print("Authentication required")
    print()
    
    # Authenticate user
    authenticated, username = SecureDemoExtender.authenticate()
    if not authenticated:
        sys.exit(1)
    
    print()
    
    while True:
        print("Options:")
        print("1. Check current demo status")
        print("2. Extend demo period")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == '1':
            demo_status = SecureDemoExtender.get_demo_status()
            if demo_status:
                print(f"\n📊 Current Demo Status:")
                print(f"  Machine ID: {demo_status.machine_id}")
                print(f"  Demo started: {demo_status.demo_started.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Demo expires: {demo_status.demo_expires.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"  Days remaining: {demo_status.days_remaining}")
                print(f"  Is active: {demo_status.is_active}")
                print(f"  Is licensed: {demo_status.is_licensed}")
                
                total_days = (demo_status.demo_expires - demo_status.demo_started).days
                print(f"  Total demo period: {total_days} days")
        
        elif choice == '2':
            try:
                days = int(input(f"Enter days to extend (1-{SecureDemoExtender.MAX_EXTENSION_DAYS}): "))
                
                if days < 1 or days > SecureDemoExtender.MAX_EXTENSION_DAYS:
                    print(f"❌ Days must be between 1 and {SecureDemoExtender.MAX_EXTENSION_DAYS}")
                    continue
                
                confirm = input(f"Extend demo by {days} days? (y/N): ").lower()
                if confirm == 'y':
                    SecureDemoExtender.extend_demo(days, username)
                
            except ValueError:
                print("❌ Invalid number")
        
        elif choice == '3':
            print(f"👋 Goodbye, {username}!")
            break
        
        else:
            print("❌ Invalid option")
        
        print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
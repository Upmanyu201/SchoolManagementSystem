#!/usr/bin/env python3
"""
🔍 System Requirements Checker
Validates Windows system for School Management System deployment
"""

import os
import sys
import platform
import subprocess
import winreg
import psutil
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class SystemChecker:
    def __init__(self):
        self.requirements = {
            'os': 'Windows 10/11',
            'python': '3.8+',
            'memory': '4GB',
            'disk': '2GB',
            'network': 'Required'
        }
        self.issues = []
        self.warnings = []
        
    def print_header(self):
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗")
        print(f"║                                                              ║")
        print(f"║  🔍 SYSTEM REQUIREMENTS CHECKER                             ║")
        print(f"║  📊 Validating Windows Environment                          ║")
        print(f"║                                                              ║")
        print(f"╚══════════════════════════════════════════════════════════════╝{Colors.END}")
        
    def check_windows_version(self):
        """Check Windows version compatibility"""
        print(f"\n{Colors.BOLD}🖥️  Operating System Check{Colors.END}")
        
        try:
            version = platform.version()
            release = platform.release()
            
            print(f"   OS: {Colors.GREEN}{platform.system()} {release}{Colors.END}")
            print(f"   Version: {Colors.GREEN}{version}{Colors.END}")
            
            # Check if Windows 10/11
            if platform.system() != 'Windows':
                self.issues.append("❌ This system is designed for Windows 10/11")
                return False
                
            # Check Windows version
            major_version = int(platform.version().split('.')[0])
            if major_version < 10:
                self.issues.append("❌ Windows 10 or later required")
                return False
                
            print(f"   {Colors.GREEN}✅ Windows version compatible{Colors.END}")
            return True
            
        except Exception as e:
            self.issues.append(f"❌ Could not detect Windows version: {e}")
            return False
    
    def check_python_installation(self):
        """Check Python installation and version"""
        print(f"\n{Colors.BOLD}🐍 Python Installation Check{Colors.END}")
        
        try:
            # Check current Python version
            version = sys.version_info
            version_str = f"{version.major}.{version.minor}.{version.micro}"
            
            print(f"   Current Python: {Colors.GREEN}{version_str}{Colors.END}")
            print(f"   Executable: {Colors.GREEN}{sys.executable}{Colors.END}")
            
            # Check version compatibility
            if version.major < 3 or (version.major == 3 and version.minor < 8):
                self.issues.append("❌ Python 3.8+ required")
                return False
                
            # Check pip availability
            try:
                import pip
                print(f"   {Colors.GREEN}✅ pip available{Colors.END}")
            except ImportError:
                self.warnings.append("⚠️  pip not found - will install")
                
            print(f"   {Colors.GREEN}✅ Python version compatible{Colors.END}")
            return True
            
        except Exception as e:
            self.issues.append(f"❌ Python check failed: {e}")
            return False
    
    def check_system_resources(self):
        """Check system memory and disk space"""
        print(f"\n{Colors.BOLD}💾 System Resources Check{Colors.END}")
        
        try:
            # Memory check
            memory = psutil.virtual_memory()
            memory_gb = memory.total / (1024**3)
            
            print(f"   RAM: {Colors.GREEN}{memory_gb:.1f} GB{Colors.END}")
            
            if memory_gb < 4:
                self.warnings.append("⚠️  Less than 4GB RAM - may affect performance")
            else:
                print(f"   {Colors.GREEN}✅ Sufficient RAM{Colors.END}")
            
            # Disk space check
            disk = psutil.disk_usage('.')
            free_gb = disk.free / (1024**3)
            
            print(f"   Free Disk: {Colors.GREEN}{free_gb:.1f} GB{Colors.END}")
            
            if free_gb < 2:
                self.issues.append("❌ Less than 2GB free disk space")
                return False
            else:
                print(f"   {Colors.GREEN}✅ Sufficient disk space{Colors.END}")
                
            return True
            
        except Exception as e:
            self.warnings.append(f"⚠️  Resource check failed: {e}")
            return True
    
    def check_network_connectivity(self):
        """Check network connectivity"""
        print(f"\n{Colors.BOLD}🌐 Network Connectivity Check{Colors.END}")
        
        try:
            # Check if connected to any network
            import socket
            
            # Try to connect to a reliable server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            
            try:
                result = sock.connect_ex(('8.8.8.8', 53))
                if result == 0:
                    print(f"   {Colors.GREEN}✅ Internet connectivity available{Colors.END}")
                    return True
                else:
                    self.warnings.append("⚠️  No internet - offline mode only")
                    return True
            finally:
                sock.close()
                
        except Exception as e:
            self.warnings.append(f"⚠️  Network check failed: {e}")
            return True
    
    def check_required_tools(self):
        """Check for required development tools"""
        print(f"\n{Colors.BOLD}🛠️  Development Tools Check{Colors.END}")
        
        tools_status = {}
        
        # Check Git
        try:
            result = subprocess.run(['git', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                tools_status['git'] = True
                print(f"   Git: {Colors.GREEN}✅ Available{Colors.END}")
            else:
                tools_status['git'] = False
        except:
            tools_status['git'] = False
            self.warnings.append("⚠️  Git not found - manual download may be needed")
        
        # Check Visual C++ Redistributable
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                               r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64")
            tools_status['vcredist'] = True
            print(f"   Visual C++ Redistributable: {Colors.GREEN}✅ Available{Colors.END}")
            winreg.CloseKey(key)
        except:
            tools_status['vcredist'] = False
            self.warnings.append("⚠️  Visual C++ Redistributable may be needed for some packages")
        
        return tools_status
    
    def check_project_structure(self):
        """Check if we're in the correct project directory"""
        print(f"\n{Colors.BOLD}📁 Project Structure Check{Colors.END}")
        
        required_files = [
            'manage.py',
            'requirements.txt',
            'config/settings.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"   {Colors.RED}❌ Missing files: {', '.join(missing_files)}{Colors.END}")
            self.issues.append("❌ Not in correct project directory")
            return False
        else:
            print(f"   {Colors.GREEN}✅ Project structure valid{Colors.END}")
            return True
    
    def generate_report(self):
        """Generate final system check report"""
        print(f"\n{Colors.BOLD}📊 SYSTEM CHECK REPORT{Colors.END}")
        print("=" * 60)
        
        if not self.issues and not self.warnings:
            print(f"{Colors.GREEN}🎉 EXCELLENT! Your system is ready for deployment{Colors.END}")
            print(f"{Colors.GREEN}✅ All requirements met{Colors.END}")
            return True
        
        if self.issues:
            print(f"{Colors.RED}❌ CRITICAL ISSUES FOUND:{Colors.END}")
            for issue in self.issues:
                print(f"   {Colors.RED}{issue}{Colors.END}")
            print()
        
        if self.warnings:
            print(f"{Colors.YELLOW}⚠️  WARNINGS:{Colors.END}")
            for warning in self.warnings:
                print(f"   {Colors.YELLOW}{warning}{Colors.END}")
            print()
        
        if self.issues:
            print(f"{Colors.RED}🚫 Please fix critical issues before proceeding{Colors.END}")
            return False
        else:
            print(f"{Colors.YELLOW}⚠️  System ready with warnings - proceed with caution{Colors.END}")
            return True
    
    def run_full_check(self):
        """Run complete system check"""
        self.print_header()
        
        checks = [
            self.check_windows_version,
            self.check_python_installation,
            self.check_system_resources,
            self.check_network_connectivity,
            self.check_required_tools,
            self.check_project_structure
        ]
        
        for check in checks:
            try:
                check()
            except Exception as e:
                self.issues.append(f"❌ Check failed: {e}")
        
        return self.generate_report()

def main():
    """Main execution function"""
    checker = SystemChecker()
    
    try:
        success = checker.run_full_check()
        
        if success:
            print(f"\n{Colors.GREEN}🚀 Ready to proceed with installation!{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}🛑 Please resolve issues before continuing{Colors.END}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  System check cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ System check failed: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
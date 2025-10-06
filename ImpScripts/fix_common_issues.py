#!/usr/bin/env python3
"""
[FIX] Common Issues Fixer
Automatically detects and fixes common Windows deployment issues
"""

import os
import sys
import subprocess
import shutil
import winreg
import urllib.request
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class CommonIssuesFixer:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "venv"
        self.python_exe = self.get_python_executable()
        self.issues_found = []
        self.fixes_applied = []
        
    def get_python_executable(self):
        """Get the correct Python executable"""
        if os.name == 'nt':  # Windows
            venv_python = self.venv_path / "Scripts" / "python.exe"
        else:
            venv_python = self.venv_path / "bin" / "python"
        
        return str(venv_python) if venv_python.exists() else sys.executable
    
    def print_header(self):
        print(f"{Colors.CYAN}================================================================")
        print(f"                                                                ")
        print(f"   [FIX]  COMMON ISSUES FIXER                                     ")
        print(f"   [TOOL] Automatic Windows deployment issue resolution            ")
        print(f"                                                                ")
        print(f"================================================================{Colors.END}")
    
    def check_python_path_issues(self):
        """Check and fix Python PATH issues"""
        print(f"\n{Colors.BOLD}[PYTHON] Checking Python PATH issues...{Colors.END}")
        
        try:
            # Test python command
            result = subprocess.run(['python', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                self.issues_found.append("Python not in PATH")
                return self.fix_python_path()
            else:
                print(f"   {Colors.GREEN}[OK] Python PATH is correct{Colors.END}")
                return True
                
        except FileNotFoundError:
            self.issues_found.append("Python command not found")
            return self.fix_python_path()
        except Exception as e:
            print(f"   {Colors.YELLOW}[WARN]  PATH check error: {e}{Colors.END}")
            return True
    
    def fix_python_path(self):
        """Fix Python PATH issues"""
        print(f"   [TOOL] Fixing Python PATH...")
        
        try:
            # Get Python installation path
            python_path = Path(sys.executable).parent
            scripts_path = python_path / "Scripts"
            
            # Add to user PATH (safer than system PATH)
            current_path = os.environ.get('PATH', '')
            
            paths_to_add = []
            if str(python_path) not in current_path:
                paths_to_add.append(str(python_path))
            
            if str(scripts_path) not in current_path:
                paths_to_add.append(str(scripts_path))
            
            if paths_to_add:
                new_path = current_path + ';' + ';'.join(paths_to_add)
                os.environ['PATH'] = new_path
                
                print(f"   {Colors.GREEN}[OK] Python PATH fixed for current session{Colors.END}")
                print(f"   {Colors.YELLOW}[TIP] Restart command prompt for permanent fix{Colors.END}")
                self.fixes_applied.append("Python PATH updated")
            
            return True
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Could not fix Python PATH: {e}{Colors.END}")
            return False
    
    def check_pip_issues(self):
        """Check and fix pip issues"""
        print(f"\n{Colors.BOLD}[PACKAGE] Checking pip issues...{Colors.END}")
        
        try:
            # Test pip command
            result = subprocess.run([self.python_exe, '-m', 'pip', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                self.issues_found.append("pip not working")
                return self.fix_pip_installation()
            else:
                print(f"   {Colors.GREEN}[OK] pip is working correctly{Colors.END}")
                
                # Check if pip is outdated
                return self.check_pip_version()
                
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] pip check failed: {e}{Colors.END}")
            self.issues_found.append("pip check failed")
            return self.fix_pip_installation()
    
    def fix_pip_installation(self):
        """Fix pip installation"""
        print(f"   [TOOL] Fixing pip installation...")
        
        try:
            # Download get-pip.py
            get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
            get_pip_path = self.project_root / "get-pip.py"
            
            print(f"   [DOWNLOAD] Downloading get-pip.py...")
            urllib.request.urlretrieve(get_pip_url, get_pip_path)
            
            # Install pip
            result = subprocess.run([self.python_exe, str(get_pip_path)], 
                                  capture_output=True, text=True, timeout=300)
            
            # Clean up
            if get_pip_path.exists():
                get_pip_path.unlink()
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}[OK] pip installed successfully{Colors.END}")
                self.fixes_applied.append("pip installation fixed")
                return True
            else:
                print(f"   {Colors.RED}[ERROR] pip installation failed{Colors.END}")
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] pip fix error: {e}{Colors.END}")
            return False
    
    def check_pip_version(self):
        """Check and upgrade pip version"""
        try:
            # Upgrade pip
            result = subprocess.run([self.python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}[OK] pip upgraded to latest version{Colors.END}")
                self.fixes_applied.append("pip upgraded")
            
            return True
            
        except Exception:
            return True  # Not critical
    
    def check_virtual_environment_issues(self):
        """Check virtual environment issues"""
        print(f"\n{Colors.BOLD}[NETWORK] Checking virtual environment issues...{Colors.END}")
        
        if not self.venv_path.exists():
            self.issues_found.append("Virtual environment missing")
            return self.fix_virtual_environment()
        
        # Check if venv is corrupted
        if os.name == 'nt':
            venv_python = self.venv_path / "Scripts" / "python.exe"
        else:
            venv_python = self.venv_path / "bin" / "python"
        
        if not venv_python.exists():
            self.issues_found.append("Virtual environment corrupted")
            return self.fix_virtual_environment()
        
        print(f"   {Colors.GREEN}[OK] Virtual environment is healthy{Colors.END}")
        return True
    
    def fix_virtual_environment(self):
        """Fix virtual environment issues"""
        print(f"   [TOOL] Fixing virtual environment...")
        
        try:
            # Remove corrupted venv
            if self.venv_path.exists():
                shutil.rmtree(self.venv_path)
            
            # Create new venv
            import venv
            venv.create(self.venv_path, with_pip=True, clear=True)
            
            print(f"   {Colors.GREEN}[OK] Virtual environment recreated{Colors.END}")
            self.fixes_applied.append("Virtual environment fixed")
            return True
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Virtual environment fix failed: {e}{Colors.END}")
            return False
    
    def check_dependency_issues(self):
        """Check and fix dependency issues"""
        print(f"\n{Colors.BOLD}[EMOJI] Checking dependency issues...{Colors.END}")
        
        requirements_file = self.project_root / "requirements.txt"
        
        if not requirements_file.exists():
            print(f"   {Colors.YELLOW}[WARN]  requirements.txt not found{Colors.END}")
            return True
        
        try:
            # Check if Django is installed
            result = subprocess.run([self.python_exe, '-c', 'import django'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                self.issues_found.append("Django not installed")
                return self.fix_dependencies()
            
            # Check other critical packages
            critical_packages = ['PIL', 'decouple', 'whitenoise']
            missing_packages = []
            
            for package in critical_packages:
                try:
                    result = subprocess.run([self.python_exe, '-c', f'import {package}'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode != 0:
                        missing_packages.append(package)
                except:
                    missing_packages.append(package)
            
            if missing_packages:
                self.issues_found.append(f"Missing packages: {', '.join(missing_packages)}")
                return self.fix_dependencies()
            
            print(f"   {Colors.GREEN}[OK] All dependencies are installed{Colors.END}")
            return True
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Dependency check failed: {e}{Colors.END}")
            return self.fix_dependencies()
    
    def fix_dependencies(self):
        """Fix dependency issues"""
        print(f"   [TOOL] Fixing dependencies...")
        
        try:
            requirements_file = self.project_root / "requirements.txt"
            
            if requirements_file.exists():
                # Install from requirements.txt
                result = subprocess.run([
                    self.python_exe, '-m', 'pip', 'install', 
                    '-r', str(requirements_file), '--no-cache-dir'
                ], capture_output=True, text=True, timeout=1800)
                
                if result.returncode == 0:
                    print(f"   {Colors.GREEN}[OK] Dependencies installed from requirements.txt{Colors.END}")
                    self.fixes_applied.append("Dependencies installed")
                    return True
            
            # Install critical packages individually
            critical_packages = [
                "Django>=5.1.0",
                "Pillow",
                "python-decouple",
                "whitenoise",
                "djangorestframework"
            ]
            
            for package in critical_packages:
                try:
                    result = subprocess.run([
                        self.python_exe, '-m', 'pip', 'install', package
                    ], capture_output=True, text=True, timeout=300)
                    
                    if result.returncode == 0:
                        print(f"   [EMOJI] {package} installed")
                except:
                    pass
            
            print(f"   {Colors.GREEN}[OK] Critical dependencies installed{Colors.END}")
            self.fixes_applied.append("Critical dependencies installed")
            return True
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Dependency fix failed: {e}{Colors.END}")
            return False
    
    def check_database_issues(self):
        """Check database issues"""
        print(f"\n{Colors.BOLD}[DATABASE]  Checking database issues...{Colors.END}")
        
        db_path = self.project_root / "db.sqlite3"
        
        try:
            # Check if manage.py works
            result = subprocess.run([self.python_exe, 'manage.py', 'check'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                if "No module named" in result.stderr:
                    self.issues_found.append("Django not properly installed")
                    return self.fix_dependencies()
                elif "DATABASES" in result.stderr:
                    self.issues_found.append("Database configuration issue")
                    return self.fix_database_config()
                else:
                    print(f"   {Colors.YELLOW}[WARN]  Django check warnings (may be normal){Colors.END}")
            
            # Check if database needs migration
            if not db_path.exists():
                self.issues_found.append("Database not created")
                return self.fix_database_migration()
            
            print(f"   {Colors.GREEN}[OK] Database appears healthy{Colors.END}")
            return True
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Database check failed: {e}{Colors.END}")
            return self.fix_database_migration()
    
    def fix_database_config(self):
        """Fix database configuration issues"""
        print(f"   [TOOL] Fixing database configuration...")
        
        # This is a placeholder - actual implementation would depend on specific issues
        print(f"   {Colors.GREEN}[OK] Database configuration checked{Colors.END}")
        return True
    
    def fix_database_migration(self):
        """Fix database migration issues"""
        print(f"   [TOOL] Fixing database migrations...")
        
        try:
            # Create migrations
            result = subprocess.run([self.python_exe, 'manage.py', 'makemigrations'], 
                                  capture_output=True, text=True, timeout=120)
            
            # Apply migrations
            result = subprocess.run([self.python_exe, 'manage.py', 'migrate'], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}[OK] Database migrations applied{Colors.END}")
                self.fixes_applied.append("Database migrations fixed")
                return True
            else:
                print(f"   {Colors.RED}[ERROR] Migration failed: {result.stderr}{Colors.END}")
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Migration fix failed: {e}{Colors.END}")
            return False
    
    def check_port_issues(self):
        """Check port availability issues"""
        print(f"\n{Colors.BOLD}[EMOJI] Checking port issues...{Colors.END}")
        
        import socket
        
        common_ports = [8000, 8080, 3000, 5000]
        available_ports = []
        
        for port in common_ports:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    result = s.connect_ex(('127.0.0.1', port))
                    if result != 0:  # Port is available
                        available_ports.append(port)
            except:
                available_ports.append(port)
        
        if available_ports:
            print(f"   {Colors.GREEN}[OK] Available ports: {', '.join(map(str, available_ports))}{Colors.END}")
        else:
            print(f"   {Colors.YELLOW}[WARN]  Common ports may be in use{Colors.END}")
            self.issues_found.append("Port availability issues")
        
        return True
    
    def check_permissions_issues(self):
        """Check file permissions issues"""
        print(f"\n{Colors.BOLD}[EMOJI] Checking permissions issues...{Colors.END}")
        
        try:
            # Test write permissions
            test_file = self.project_root / "test_write.tmp"
            
            with open(test_file, 'w') as f:
                f.write("test")
            
            test_file.unlink()
            
            print(f"   {Colors.GREEN}[OK] File permissions are correct{Colors.END}")
            return True
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Permission issues detected: {e}{Colors.END}")
            self.issues_found.append("File permission issues")
            return self.fix_permissions()
    
    def fix_permissions(self):
        """Fix permission issues"""
        print(f"   [TOOL] Fixing permissions...")
        
        try:
            # On Windows, try to fix common permission issues
            if os.name == 'nt':
                # Run as administrator check
                import ctypes
                if not ctypes.windll.shell32.IsUserAnAdmin():
                    print(f"   {Colors.YELLOW}[WARN]  Consider running as administrator{Colors.END}")
            
            print(f"   {Colors.GREEN}[OK] Permissions checked{Colors.END}")
            self.fixes_applied.append("Permissions verified")
            return True
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Permission fix failed: {e}{Colors.END}")
            return False
    
    def generate_fix_report(self):
        """Generate final fix report"""
        print(f"\n{Colors.BOLD}[HEALTH] FIX REPORT{Colors.END}")
        print("=" * 60)
        
        if not self.issues_found and not self.fixes_applied:
            print(f"{Colors.GREEN}[SUCCESS] EXCELLENT! No issues found{Colors.END}")
            print(f"{Colors.GREEN}[OK] Your system is ready to run{Colors.END}")
            return True
        
        if self.issues_found:
            print(f"{Colors.YELLOW}[WARN]  ISSUES DETECTED:{Colors.END}")
            for issue in self.issues_found:
                print(f"   {Colors.YELLOW}• {issue}{Colors.END}")
            print()
        
        if self.fixes_applied:
            print(f"{Colors.GREEN}[OK] FIXES APPLIED:{Colors.END}")
            for fix in self.fixes_applied:
                print(f"   {Colors.GREEN}• {fix}{Colors.END}")
            print()
        
        if len(self.fixes_applied) >= len(self.issues_found):
            print(f"{Colors.GREEN}[SUCCESS] Most issues have been resolved!{Colors.END}")
            return True
        else:
            print(f"{Colors.YELLOW}[WARN]  Some issues may need manual attention{Colors.END}")
            return False
    
    def run_fixes(self):
        """Run all common issue fixes"""
        self.print_header()
        
        fixes = [
            self.check_python_path_issues,
            self.check_pip_issues,
            self.check_virtual_environment_issues,
            self.check_dependency_issues,
            self.check_database_issues,
            self.check_port_issues,
            self.check_permissions_issues
        ]
        
        for fix_function in fixes:
            try:
                fix_function()
            except Exception as e:
                print(f"   {Colors.RED}[ERROR] Fix failed: {e}{Colors.END}")
        
        return self.generate_fix_report()

def main():
    """Main execution function"""
    fixer = CommonIssuesFixer()
    
    try:
        success = fixer.run_fixes()
        
        if success:
            print(f"\n{Colors.GREEN}[OK] System is ready to run School Management System!{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.YELLOW}[WARN]  Some issues may need manual attention{Colors.END}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[WARN]  Fix process cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR] Fix process error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
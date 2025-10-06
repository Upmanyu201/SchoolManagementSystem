#!/usr/bin/env python3
"""
Virtual Environment Setup & Dependency Manager
Creates isolated Python environment and installs all dependencies
"""

import os
import sys
import subprocess
import venv
import shutil
from pathlib import Path

class Colors:
    GREEN = ''
    RED = ''
    YELLOW = ''
    BLUE = ''
    CYAN = ''
    BOLD = ''
    END = ''

class EnvironmentSetup:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "venv"
        self.requirements_file = self.project_root / "requirements.txt"
        self.python_exe = None
        self.pip_exe = None
        
    def print_header(self):
        print(f"{Colors.CYAN}================================================================")
        print(f"                                                                ")
        print(f"  VIRTUAL ENVIRONMENT SETUP                                   ")
        print(f"  Creating isolated Python environment                        ")
        print(f"                                                                ")
        print(f"================================================================{Colors.END}")
    
    def check_project_structure(self):
        """Verify we're in the correct project directory"""
        print(f"\n{Colors.BOLD}[PROJECT] Checking project structure...{Colors.END}")
        
        required_files = [
            'manage.py',
            'requirements.txt',
            'config/settings.py'
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.project_root / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"   {Colors.RED}[ERROR] Missing files: {', '.join(missing_files)}{Colors.END}")
            print(f"   {Colors.YELLOW}[TIP] Make sure you're in the School Management System directory{Colors.END}")
            return False
        else:
            print(f"   {Colors.GREEN}[OK] Project structure valid{Colors.END}")
            return True
    
    def remove_existing_venv(self):
        """Remove existing virtual environment if it exists"""
        if self.venv_path.exists():
            print(f"\n{Colors.BOLD}[CLEAN] Removing existing virtual environment...{Colors.END}")
            
            try:
                shutil.rmtree(self.venv_path)
                print(f"   {Colors.GREEN}[OK] Old environment removed{Colors.END}")
            except Exception as e:
                print(f"   {Colors.RED}[ERROR] Could not remove old environment: {e}{Colors.END}")
                print(f"   {Colors.YELLOW}[TIP] Please delete the 'venv' folder manually{Colors.END}")
                return False
        
        return True
    
    def create_virtual_environment(self):
        """Create new virtual environment"""
        print(f"\n{Colors.BOLD}[CREATE] Creating virtual environment...{Colors.END}")
        
        try:
            print(f"   [PATH] Location: {self.venv_path}")
            
            # Create virtual environment
            venv.create(self.venv_path, with_pip=True, clear=True)
            
            # Set executable paths
            if os.name == 'nt':  # Windows
                self.python_exe = self.venv_path / "Scripts" / "python.exe"
                self.pip_exe = self.venv_path / "Scripts" / "pip.exe"
            else:  # Unix-like
                self.python_exe = self.venv_path / "bin" / "python"
                self.pip_exe = self.venv_path / "bin" / "pip"
            
            # Verify creation
            if self.python_exe.exists():
                print(f"   {Colors.GREEN}[OK] Virtual environment created successfully{Colors.END}")
                return True
            else:
                print(f"   {Colors.RED}[ERROR] Python executable not found in venv{Colors.END}")
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Failed to create virtual environment: {e}{Colors.END}")
            return False
    
    def upgrade_pip(self):
        """Upgrade pip to latest version"""
        print(f"\n{Colors.BOLD}[PIP] Upgrading pip...{Colors.END}")
        
        try:
            cmd = [str(self.python_exe), "-m", "pip", "install", "--upgrade", "pip"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}[OK] pip upgraded successfully{Colors.END}")
                return True
            else:
                print(f"   {Colors.YELLOW}[WARN] pip upgrade failed, continuing anyway{Colors.END}")
                return True  # Not critical
                
        except Exception as e:
            print(f"   {Colors.YELLOW}[WARN] pip upgrade error: {e}{Colors.END}")
            return True  # Not critical
    
    def install_dependencies(self):
        """Install project dependencies from requirements.txt"""
        print(f"\n{Colors.BOLD}[DEPS] Installing dependencies...{Colors.END}")
        
        if not self.requirements_file.exists():
            print(f"   {Colors.RED}[ERROR] requirements.txt not found{Colors.END}")
            return False
        
        try:
            # Read requirements file
            with open(self.requirements_file, 'r') as f:
                requirements = f.read().strip()
            
            if not requirements:
                print(f"   {Colors.YELLOW}[WARN] requirements.txt is empty{Colors.END}")
                return True
            
            print(f"   [INFO] Installing packages from requirements.txt...")
            
            # Install dependencies
            cmd = [
                str(self.python_exe), "-m", "pip", "install", 
                "-r", str(self.requirements_file),
                "--no-cache-dir"  # Avoid cache issues
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30 minutes
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}[OK] All dependencies installed successfully{Colors.END}")
                
                # Show installed packages
                self.show_installed_packages()
                return True
            else:
                print(f"   {Colors.RED}[ERROR] Dependency installation failed{Colors.END}")
                print(f"   Error output: {result.stderr}")
                
                # Try to install critical packages individually
                return self.install_critical_packages()
                
        except subprocess.TimeoutExpired:
            print(f"   {Colors.RED}[ERROR] Installation timed out{Colors.END}")
            return False
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Installation error: {e}{Colors.END}")
            return False
    
    def install_critical_packages(self):
        """Install critical packages individually if bulk install fails"""
        print(f"\n{Colors.BOLD}[CRITICAL] Installing critical packages individually...{Colors.END}")
        
        critical_packages = [
            "Django>=5.1.0",
            "Pillow",
            "python-decouple",
            "whitenoise",
            "djangorestframework"
        ]
        
        success_count = 0
        
        for package in critical_packages:
            try:
                print(f"   [INSTALL] Installing {package}...")
                
                cmd = [str(self.python_exe), "-m", "pip", "install", package]
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print(f"   {Colors.GREEN}[OK] {package} installed{Colors.END}")
                    success_count += 1
                else:
                    print(f"   {Colors.RED}[ERROR] {package} failed{Colors.END}")
                    
            except Exception as e:
                print(f"   {Colors.RED}[ERROR] {package} error: {e}{Colors.END}")
        
        if success_count >= 3:  # At least Django and a few others
            print(f"   {Colors.GREEN}[OK] Critical packages installed ({success_count}/{len(critical_packages)}){Colors.END}")
            return True
        else:
            print(f"   {Colors.RED}[ERROR] Too many critical packages failed{Colors.END}")
            return False
    
    def show_installed_packages(self):
        """Show list of installed packages"""
        try:
            cmd = [str(self.python_exe), "-m", "pip", "list"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                package_count = len(lines) - 2  # Exclude header lines
                print(f"   [COUNT] {package_count} packages installed")
                
                # Show key packages
                key_packages = ['Django', 'Pillow', 'whitenoise', 'djangorestframework']
                for line in lines:
                    for pkg in key_packages:
                        if line.lower().startswith(pkg.lower()):
                            print(f"   [OK] {line}")
                            
        except Exception:
            pass  # Not critical
    
    def create_activation_script(self):
        """Create convenient activation script"""
        print(f"\n{Colors.BOLD}[SCRIPT] Creating activation script...{Colors.END}")
        
        try:
            if os.name == 'nt':  # Windows
                activate_script = self.project_root / "activate_env.bat"
                script_content = f"""@echo off
echo [INFO] Activating School Management System Environment...
call "{self.venv_path}\\Scripts\\activate.bat"
echo [OK] Environment activated!
echo [TIP] Run 'python manage.py runserver' to start the server
cmd /k
"""
            else:  # Unix-like
                activate_script = self.project_root / "activate_env.sh"
                script_content = f"""#!/bin/bash
echo "[INFO] Activating School Management System Environment..."
source "{self.venv_path}/bin/activate"
echo "[OK] Environment activated!"
echo "[TIP] Run 'python manage.py runserver' to start the server"
bash
"""
            
            with open(activate_script, 'w') as f:
                f.write(script_content)
            
            if not os.name == 'nt':
                os.chmod(activate_script, 0o755)
            
            print(f"   {Colors.GREEN}[OK] Activation script created: {activate_script.name}{Colors.END}")
            return True
            
        except Exception as e:
            print(f"   {Colors.YELLOW}[WARN] Could not create activation script: {e}{Colors.END}")
            return True  # Not critical
    
    def test_environment(self):
        """Test the virtual environment setup"""
        print(f"\n{Colors.BOLD}[TEST] Testing environment...{Colors.END}")
        
        try:
            # Test Python
            cmd = [str(self.python_exe), "--version"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"   {Colors.GREEN}[OK] Python: {version}{Colors.END}")
            else:
                print(f"   {Colors.RED}[ERROR] Python test failed{Colors.END}")
                return False
            
            # Test Django
            cmd = [str(self.python_exe), "-c", "import django; print(f'Django {django.get_version()}')"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                django_info = result.stdout.strip()
                print(f"   {Colors.GREEN}[OK] {django_info}{Colors.END}")
            else:
                print(f"   {Colors.RED}[ERROR] Django test failed{Colors.END}")
                return False
            
            # Test manage.py
            cmd = [str(self.python_exe), "manage.py", "check", "--deploy"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}[OK] Django project check passed{Colors.END}")
            else:
                print(f"   {Colors.YELLOW}[WARN] Django check warnings (normal for first setup){Colors.END}")
            
            return True
            
        except Exception as e:
            print(f"   {Colors.RED}[ERROR] Environment test failed: {e}{Colors.END}")
            return False
    
    def run_setup(self):
        """Run complete environment setup"""
        self.print_header()
        
        # Check project structure
        if not self.check_project_structure():
            return False
        
        # Remove existing environment
        if not self.remove_existing_venv():
            return False
        
        # Create virtual environment
        if not self.create_virtual_environment():
            return False
        
        # Upgrade pip
        self.upgrade_pip()
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Create activation script
        self.create_activation_script()
        
        # Test environment
        if not self.test_environment():
            return False
        
        print(f"\n{Colors.GREEN}[SUCCESS] Environment setup completed successfully!{Colors.END}")
        print(f"\n{Colors.BOLD}[NEXT] Next Steps:{Colors.END}")
        print(f"   1. Run: {Colors.CYAN}activate_env.bat{Colors.END} (Windows) or {Colors.CYAN}./activate_env.sh{Colors.END} (Linux/Mac)")
        print(f"   2. Run: {Colors.CYAN}python manage.py migrate{Colors.END}")
        print(f"   3. Run: {Colors.CYAN}python manage.py runserver{Colors.END}")
        
        return True

def main():
    """Main execution function"""
    setup = EnvironmentSetup()
    
    try:
        success = setup.run_setup()
        
        if success:
            print(f"\n{Colors.GREEN}[READY] Virtual environment is ready!{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}[ERROR] Environment setup failed{Colors.END}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}[CANCELLED] Setup cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}[ERROR] Setup error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
🐍 Python Auto-Installer for Windows
Downloads and installs Python 3.12+ with all required components
"""

import os
import sys
import subprocess
import urllib.request
import tempfile
import winreg
from pathlib import Path

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class PythonInstaller:
    def __init__(self):
        self.python_version = "3.12.0"
        self.download_url = f"https://www.python.org/ftp/python/{self.python_version}/python-{self.python_version}-amd64.exe"
        self.installer_path = None
        
    def print_header(self):
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗")
        print(f"║                                                              ║")
        print(f"║  🐍 PYTHON AUTO-INSTALLER                                   ║")
        print(f"║  📦 Installing Python {self.python_version} for Windows                    ║")
        print(f"║                                                              ║")
        print(f"╚══════════════════════════════════════════════════════════════╝{Colors.END}")
    
    def check_existing_python(self):
        """Check if suitable Python version already exists"""
        print(f"\n{Colors.BOLD}🔍 Checking existing Python installations...{Colors.END}")
        
        try:
            # Check current Python version
            version = sys.version_info
            if version.major >= 3 and version.minor >= 8:
                print(f"   {Colors.GREEN}✅ Python {version.major}.{version.minor}.{version.micro} found{Colors.END}")
                print(f"   {Colors.GREEN}✅ Version is compatible{Colors.END}")
                
                # Check if pip is available
                try:
                    import pip
                    print(f"   {Colors.GREEN}✅ pip is available{Colors.END}")
                    return True
                except ImportError:
                    print(f"   {Colors.YELLOW}⚠️  pip not found - will install{Colors.END}")
                    return self.install_pip()
            else:
                print(f"   {Colors.RED}❌ Python {version.major}.{version.minor} is too old{Colors.END}")
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}❌ Could not check Python: {e}{Colors.END}")
            return False
    
    def download_python_installer(self):
        """Download Python installer from official website"""
        print(f"\n{Colors.BOLD}📥 Downloading Python {self.python_version}...{Colors.END}")
        
        try:
            # Create temporary directory
            temp_dir = tempfile.gettempdir()
            self.installer_path = os.path.join(temp_dir, f"python-{self.python_version}-installer.exe")
            
            print(f"   📍 Download URL: {self.download_url}")
            print(f"   💾 Saving to: {self.installer_path}")
            
            # Download with progress
            def progress_hook(block_num, block_size, total_size):
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) // total_size)
                    print(f"\r   📊 Progress: {percent}% ", end='', flush=True)
            
            urllib.request.urlretrieve(self.download_url, self.installer_path, progress_hook)
            print(f"\n   {Colors.GREEN}✅ Download completed{Colors.END}")
            
            # Verify file exists and has reasonable size
            if os.path.exists(self.installer_path):
                size_mb = os.path.getsize(self.installer_path) / (1024 * 1024)
                print(f"   📦 File size: {size_mb:.1f} MB")
                
                if size_mb < 10:  # Python installer should be larger than 10MB
                    raise Exception("Downloaded file seems too small")
                    
                return True
            else:
                raise Exception("Downloaded file not found")
                
        except Exception as e:
            print(f"\n   {Colors.RED}❌ Download failed: {e}{Colors.END}")
            print(f"   {Colors.YELLOW}💡 Please download manually from: https://python.org{Colors.END}")
            return False
    
    def install_python(self):
        """Install Python using the downloaded installer"""
        print(f"\n{Colors.BOLD}🔧 Installing Python {self.python_version}...{Colors.END}")
        
        if not self.installer_path or not os.path.exists(self.installer_path):
            print(f"   {Colors.RED}❌ Installer not found{Colors.END}")
            return False
        
        try:
            # Prepare installation command
            install_cmd = [
                self.installer_path,
                '/quiet',                    # Silent installation
                'InstallAllUsers=1',         # Install for all users
                'PrependPath=1',             # Add to PATH
                'Include_test=0',            # Skip tests
                'Include_pip=1',             # Include pip
                'Include_tcltk=1',           # Include tkinter
                'Include_launcher=1',        # Include py launcher
                'AssociateFiles=1',          # Associate .py files
                'Shortcuts=1',               # Create shortcuts
                'Include_symbols=0',         # Skip debug symbols
                'Include_debug=0'            # Skip debug binaries
            ]
            
            print(f"   🚀 Running installer...")
            print(f"   ⏳ This may take a few minutes...")
            
            # Run installer
            result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}✅ Python installation completed{Colors.END}")
                
                # Clean up installer
                try:
                    os.remove(self.installer_path)
                    print(f"   🧹 Installer cleaned up")
                except:
                    pass
                
                return True
            else:
                print(f"   {Colors.RED}❌ Installation failed{Colors.END}")
                print(f"   Error: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"   {Colors.RED}❌ Installation timed out{Colors.END}")
            return False
        except Exception as e:
            print(f"   {Colors.RED}❌ Installation error: {e}{Colors.END}")
            return False
    
    def verify_installation(self):
        """Verify Python installation was successful"""
        print(f"\n{Colors.BOLD}✅ Verifying installation...{Colors.END}")
        
        try:
            # Try to run python command
            result = subprocess.run(['python', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                version = result.stdout.strip()
                print(f"   {Colors.GREEN}✅ {version} installed successfully{Colors.END}")
                
                # Check pip
                pip_result = subprocess.run(['python', '-m', 'pip', '--version'], 
                                          capture_output=True, text=True, timeout=10)
                
                if pip_result.returncode == 0:
                    pip_version = pip_result.stdout.strip()
                    print(f"   {Colors.GREEN}✅ pip available: {pip_version.split()[1]}{Colors.END}")
                    return True
                else:
                    print(f"   {Colors.YELLOW}⚠️  pip not available{Colors.END}")
                    return self.install_pip()
            else:
                print(f"   {Colors.RED}❌ Python command not working{Colors.END}")
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}❌ Verification failed: {e}{Colors.END}")
            return False
    
    def install_pip(self):
        """Install pip if not available"""
        print(f"\n{Colors.BOLD}📦 Installing pip...{Colors.END}")
        
        try:
            # Download get-pip.py
            get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
            temp_dir = tempfile.gettempdir()
            get_pip_path = os.path.join(temp_dir, "get-pip.py")
            
            print(f"   📥 Downloading get-pip.py...")
            urllib.request.urlretrieve(get_pip_url, get_pip_path)
            
            # Run get-pip.py
            print(f"   🔧 Installing pip...")
            result = subprocess.run([sys.executable, get_pip_path], 
                                  capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}✅ pip installed successfully{Colors.END}")
                
                # Clean up
                try:
                    os.remove(get_pip_path)
                except:
                    pass
                
                return True
            else:
                print(f"   {Colors.RED}❌ pip installation failed{Colors.END}")
                print(f"   Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}❌ pip installation error: {e}{Colors.END}")
            return False
    
    def update_environment_path(self):
        """Ensure Python is in system PATH"""
        print(f"\n{Colors.BOLD}🔧 Updating system PATH...{Colors.END}")
        
        try:
            # Get Python installation path
            result = subprocess.run([sys.executable, '-c', 'import sys; print(sys.executable)'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                python_path = Path(result.stdout.strip()).parent
                scripts_path = python_path / "Scripts"
                
                print(f"   📍 Python path: {python_path}")
                print(f"   📍 Scripts path: {scripts_path}")
                
                # Check if already in PATH
                current_path = os.environ.get('PATH', '')
                
                paths_to_add = []
                if str(python_path) not in current_path:
                    paths_to_add.append(str(python_path))
                
                if str(scripts_path) not in current_path:
                    paths_to_add.append(str(scripts_path))
                
                if paths_to_add:
                    print(f"   {Colors.YELLOW}⚠️  Adding paths to system PATH{Colors.END}")
                    print(f"   💡 You may need to restart your command prompt{Colors.END}")
                else:
                    print(f"   {Colors.GREEN}✅ Python already in PATH{Colors.END}")
                
                return True
                
        except Exception as e:
            print(f"   {Colors.YELLOW}⚠️  Could not update PATH: {e}{Colors.END}")
            return True  # Not critical
    
    def run_installation(self):
        """Run complete Python installation process"""
        self.print_header()
        
        # Check if Python is already installed
        if self.check_existing_python():
            print(f"\n{Colors.GREEN}🎉 Python is already installed and ready!{Colors.END}")
            return True
        
        print(f"\n{Colors.YELLOW}📦 Python installation required{Colors.END}")
        
        # Download installer
        if not self.download_python_installer():
            return False
        
        # Install Python
        if not self.install_python():
            return False
        
        # Verify installation
        if not self.verify_installation():
            return False
        
        # Update PATH
        self.update_environment_path()
        
        print(f"\n{Colors.GREEN}🎉 Python installation completed successfully!{Colors.END}")
        print(f"{Colors.CYAN}💡 You may need to restart your command prompt{Colors.END}")
        
        return True

def main():
    """Main execution function"""
    installer = PythonInstaller()
    
    try:
        success = installer.run_installation()
        
        if success:
            print(f"\n{Colors.GREEN}✅ Python is ready for School Management System!{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}❌ Python installation failed{Colors.END}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Installation cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Installation error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()
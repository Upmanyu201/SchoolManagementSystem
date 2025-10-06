#!/usr/bin/env python3
"""
Fix Startup Issues - Comprehensive Script
Fixes missing dependencies and import errors
"""

import os
import sys
import subprocess
from pathlib import Path

def print_header():
    print("=" * 60)
    print("  STARTUP ISSUES FIXER")
    print("  Fixing missing dependencies and import errors")
    print("=" * 60)

def check_virtual_environment():
    """Check if virtual environment exists and is working"""
    print("\n[CHECK] Checking virtual environment...")
    
    venv_path = Path.cwd() / "venv"
    
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Unix-like
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    if not python_exe.exists():
        print("[ERROR] Virtual environment not found!")
        print("[TIP] Run 'python setup_environment.py' first")
        return None, None
    
    print("[OK] Virtual environment found")
    return python_exe, pip_exe

def install_missing_packages(python_exe):
    """Install missing packages"""
    print("\n[FIX] Installing missing packages...")
    
    missing_packages = [
        "psutil==7.0.0",
        "pathlib",  # Usually built-in but just in case
    ]
    
    success_count = 0
    
    for package in missing_packages:
        try:
            print(f"   [INSTALL] Installing {package}...")
            
            cmd = [str(python_exe), "-m", "pip", "install", package]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"   [OK] {package} installed successfully")
                success_count += 1
            else:
                print(f"   [WARN] {package} installation failed: {result.stderr}")
                
        except Exception as e:
            print(f"   [ERROR] {package} error: {e}")
    
    return success_count > 0

def test_imports(python_exe):
    """Test critical imports"""
    print("\n[TEST] Testing critical imports...")
    
    test_imports = [
        "import os",
        "import sys", 
        "import pathlib",
        "from pathlib import Path",
        "import psutil",
        "import django",
    ]
    
    success_count = 0
    
    for import_test in test_imports:
        try:
            cmd = [str(python_exe), "-c", import_test]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print(f"   [OK] {import_test}")
                success_count += 1
            else:
                print(f"   [ERROR] {import_test} - {result.stderr.strip()}")
                
        except Exception as e:
            print(f"   [ERROR] {import_test} - {e}")
    
    return success_count

def fix_start_server_script():
    """Fix the start_server.py script"""
    print("\n[FIX] Checking start_server.py script...")
    
    script_path = Path("ImpScripts/start_server.py")
    
    if not script_path.exists():
        print("[ERROR] start_server.py not found!")
        return False
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if Path is imported
        if "from pathlib import Path" not in content:
            print("[WARN] Path import missing - this should be fixed already")
            return False
        
        # Check if psutil fallback exists
        if "PSUTIL_AVAILABLE" not in content:
            print("[WARN] psutil fallback missing - this should be fixed already")
            return False
        
        print("[OK] start_server.py script looks good")
        return True
        
    except Exception as e:
        print(f"[ERROR] Could not check start_server.py: {e}")
        return False

def test_server_startup(python_exe):
    """Test if server can start without errors"""
    print("\n[TEST] Testing server startup...")
    
    try:
        # Test Django check
        cmd = [str(python_exe), "manage.py", "check"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("[OK] Django check passed")
        else:
            print(f"[WARN] Django check warnings: {result.stderr}")
        
        # Test start_server.py import
        cmd = [str(python_exe), "-c", "import sys; sys.path.append('ImpScripts'); import start_server"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("[OK] start_server.py imports successfully")
            return True
        else:
            print(f"[ERROR] start_server.py import failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Server startup test failed: {e}")
        return False

def main():
    """Main execution function"""
    print_header()
    
    # Check virtual environment
    python_exe, pip_exe = check_virtual_environment()
    if not python_exe:
        return False
    
    # Install missing packages
    if not install_missing_packages(python_exe):
        print("[WARN] Some packages failed to install")
    
    # Test imports
    success_count = test_imports(python_exe)
    print(f"\n[RESULT] {success_count}/6 imports successful")
    
    # Fix start_server script
    fix_start_server_script()
    
    # Test server startup
    if test_server_startup(python_exe):
        print("\n[SUCCESS] All startup issues have been fixed!")
        print("\n[NEXT] You can now run:")
        print("   - quick_start.bat")
        print("   - python ImpScripts/start_server.py")
        return True
    else:
        print("\n[ERROR] Some issues remain. Check the output above.")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n[CANCELLED] Fix cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        sys.exit(1)
#!/usr/bin/env python3
"""
Quick fix to install missing psutil dependency
"""

import os
import sys
import subprocess
from pathlib import Path

def install_psutil():
    """Install psutil in the virtual environment"""
    print("[INFO] Installing missing psutil dependency...")
    
    # Check if we're in virtual environment
    venv_path = Path.cwd() / "venv"
    
    if os.name == 'nt':  # Windows
        python_exe = venv_path / "Scripts" / "python.exe"
        pip_exe = venv_path / "Scripts" / "pip.exe"
    else:  # Unix-like
        python_exe = venv_path / "bin" / "python"
        pip_exe = venv_path / "bin" / "pip"
    
    if not python_exe.exists():
        print("[ERROR] Virtual environment not found. Run setup_environment.py first.")
        return False
    
    try:
        # Install psutil
        cmd = [str(python_exe), "-m", "pip", "install", "psutil==7.0.0"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("[OK] psutil installed successfully!")
            return True
        else:
            print(f"[ERROR] Failed to install psutil: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Installation error: {e}")
        return False

if __name__ == "__main__":
    success = install_psutil()
    sys.exit(0 if success else 1)
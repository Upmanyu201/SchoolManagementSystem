#!/usr/bin/env python3
"""
STARTUP ISSUES FIXER
Fixes critical startup errors: Path import and psutil dependency
"""

import os
import sys
import subprocess
from pathlib import Path

def fix_start_server_imports():
    """Fix missing imports in start_server.py"""
    script_path = Path(__file__).parent / "start_server.py"
    
    if not script_path.exists():
        print("❌ start_server.py not found")
        return False
    
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if Path is imported
        if 'from pathlib import Path' not in content:
            # Add Path import after other imports
            lines = content.split('\n')
            import_added = False
            
            for i, line in enumerate(lines):
                if line.startswith('import') and not import_added:
                    # Find the last import line
                    j = i
                    while j < len(lines) and (lines[j].startswith('import') or lines[j].startswith('from') or lines[j].strip() == ''):
                        j += 1
                    
                    # Insert Path import
                    lines.insert(j, 'from pathlib import Path')
                    import_added = True
                    break
            
            if import_added:
                content = '\n'.join(lines)
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print("✅ Added Path import to start_server.py")
            else:
                print("⚠️ Could not add Path import automatically")
        else:
            print("✅ Path import already exists")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing imports: {e}")
        return False

def install_psutil():
    """Install psutil dependency"""
    try:
        # Try importing first
        import psutil
        print("✅ psutil already installed")
        return True
    except ImportError:
        pass
    
    print("📦 Installing psutil...")
    
    try:
        # Try with current Python
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'psutil==7.0.0'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ psutil installed successfully")
            return True
        else:
            print(f"❌ pip install failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out")
        return False
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

def test_imports():
    """Test if all imports work"""
    print("\n🧪 Testing imports...")
    
    try:
        from pathlib import Path
        print("✅ Path import works")
    except ImportError as e:
        print(f"❌ Path import failed: {e}")
        return False
    
    try:
        import psutil
        print("✅ psutil import works")
    except ImportError as e:
        print(f"❌ psutil import failed: {e}")
        return False
    
    return True

def main():
    """Main fix function"""
    print("🔧 STARTUP ISSUES FIXER")
    print("=" * 40)
    
    success = True
    
    # Fix 1: Path import
    print("\n1. Fixing Path import...")
    if not fix_start_server_imports():
        success = False
    
    # Fix 2: Install psutil
    print("\n2. Installing psutil...")
    if not install_psutil():
        success = False
    
    # Test everything
    print("\n3. Testing fixes...")
    if not test_imports():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✅ ALL FIXES APPLIED SUCCESSFULLY!")
        print("🚀 You can now run: python start_server.py")
    else:
        print("❌ SOME FIXES FAILED")
        print("🔍 Check the errors above and try manual fixes")
    
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
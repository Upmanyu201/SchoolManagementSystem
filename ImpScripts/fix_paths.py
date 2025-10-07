#!/usr/bin/env python3
"""
PATH FIXER FOR IMPSCRIPTS
Updates all scripts to work from project root instead of ImpScripts directory
"""

import os
import re
from pathlib import Path

def fix_script_paths():
    """Fix paths in all ImpScripts to work from project root"""
    
    scripts_dir = Path(__file__).parent
    project_root = scripts_dir.parent
    
    print("🔧 FIXING SCRIPT PATHS")
    print("=" * 40)
    print(f"Scripts dir: {scripts_dir}")
    print(f"Project root: {project_root}")
    print()
    
    # Scripts that need path fixes
    scripts_to_fix = [
        'start_server.py',
        'secure_demo_extender.py',
        'database_setup.py',
        'reset_migrations.py',
        'system_health.py'
    ]
    
    fixes_applied = 0
    
    for script_name in scripts_to_fix:
        script_path = scripts_dir / script_name
        
        if not script_path.exists():
            print(f"⚠️ {script_name} not found, skipping...")
            continue
        
        print(f"🔧 Fixing {script_name}...")
        
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Fix 1: Add project root detection at the beginning
            if 'def __init__(self):' in content and 'script_dir = Path(__file__).parent' in content:
                # Already has path detection
                print(f"  ✅ {script_name} already has path detection")
            else:
                # Add path detection for scripts that don't have it
                if script_name in ['database_setup.py', 'reset_migrations.py', 'system_health.py']:
                    # Add Django setup with path detection
                    django_setup_pattern = r'(import django\s*\n)'
                    if re.search(django_setup_pattern, content):
                        replacement = '''import django

# Auto-detect project root
script_dir = os.path.dirname(__file__)
if 'ImpScripts' in script_dir:
    project_root = os.path.dirname(script_dir)
    os.chdir(project_root)
    sys.path.insert(0, project_root)

'''
                        content = re.sub(django_setup_pattern, replacement, content)
                        print(f"  ✅ Added path detection to {script_name}")
            
            # Fix 2: Update relative paths to work from project root
            # Fix manage.py references
            content = re.sub(r'["\']manage\.py["\']', '"manage.py"', content)
            
            # Fix 3: Update log file paths
            if 'demo_extensions.log' in content:
                content = re.sub(
                    r'os\.path\.join\(os\.path\.dirname\(__file__\), ["\']demo_extensions\.log["\']\)',
                    'os.path.join(os.getcwd(), "demo_extensions.log")',
                    content
                )
                print(f"  ✅ Fixed log path in {script_name}")
            
            # Fix 4: Ensure scripts work from both locations
            if script_name == 'start_server.py':
                # start_server.py already has good path detection
                print(f"  ✅ {script_name} path detection is good")
            
            # Write back if changes were made
            if content != original_content:
                with open(script_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixes_applied += 1
                print(f"  ✅ Updated {script_name}")
            else:
                print(f"  ℹ️ No changes needed for {script_name}")
                
        except Exception as e:
            print(f"  ❌ Error fixing {script_name}: {e}")
    
    print()
    print("=" * 40)
    print(f"✅ Path fixes completed!")
    print(f"📊 Scripts processed: {len(scripts_to_fix)}")
    print(f"🔧 Fixes applied: {fixes_applied}")
    print()
    print("📋 Usage Instructions:")
    print("  From project root: python ImpScripts/script_name.py")
    print("  From ImpScripts:   python script_name.py")
    print("  Both should work now!")

def create_wrapper_scripts():
    """Create wrapper scripts in project root for easy access"""
    
    scripts_dir = Path(__file__).parent
    project_root = scripts_dir.parent
    
    wrappers = {
        'start_server.py': 'ImpScripts/start_server.py',
        'extend_demo.py': 'ImpScripts/secure_demo_extender.py',
        'setup_db.py': 'ImpScripts/database_setup.py',
        'reset_db.py': 'ImpScripts/reset_migrations.py',
        'health_check.py': 'ImpScripts/system_health.py'
    }
    
    print("\n🔗 Creating wrapper scripts in project root...")
    
    for wrapper_name, target_script in wrappers.items():
        wrapper_path = project_root / wrapper_name
        
        wrapper_content = f'''#!/usr/bin/env python3
"""
Wrapper script for {target_script}
Automatically runs from project root
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    # Ensure we're in project root
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Run the actual script
    script_path = project_root / "{target_script}"
    
    if not script_path.exists():
        print(f"❌ Script not found: {{script_path}}")
        sys.exit(1)
    
    # Execute the script
    try:
        subprocess.run([sys.executable, str(script_path)] + sys.argv[1:], check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except KeyboardInterrupt:
        print("\\n👋 Operation cancelled")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        
        try:
            with open(wrapper_path, 'w', encoding='utf-8') as f:
                f.write(wrapper_content)
            print(f"  ✅ Created {wrapper_name}")
        except Exception as e:
            print(f"  ❌ Failed to create {wrapper_name}: {e}")

def main():
    """Main function"""
    fix_script_paths()
    create_wrapper_scripts()
    
    print("\n🎉 ALL FIXES COMPLETED!")
    print("\n📖 Quick Start Guide:")
    print("  python start_server.py      # Start server")
    print("  python extend_demo.py       # Extend demo")
    print("  python setup_db.py          # Setup database")
    print("  python health_check.py      # System health")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Operation cancelled")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
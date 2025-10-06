#!/usr/bin/env python3
"""
🔄 Migration Reset Tool
Safely resets Django migrations and rebuilds database schema
"""

import os
import sys
import subprocess
import shutil
import sqlite3
from pathlib import Path
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

class MigrationReset:
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "venv"
        self.db_path = self.project_root / "db.sqlite3"
        self.backup_dir = self.project_root / "backups"
        self.python_exe = self.get_python_executable()
        self.apps_with_migrations = []
        
    def get_python_executable(self):
        """Get the correct Python executable"""
        if os.name == 'nt':  # Windows
            venv_python = self.venv_path / "Scripts" / "python.exe"
        else:  # Unix-like
            venv_python = self.venv_path / "bin" / "python"
        
        return str(venv_python) if venv_python.exists() else sys.executable
    
    def print_header(self):
        print(f"{Colors.CYAN}╔══════════════════════════════════════════════════════════════╗")
        print(f"║                                                              ║")
        print(f"║  🔄 MIGRATION RESET TOOL                                    ║")
        print(f"║  🗄️  Safely reset Django migrations                         ║")
        print(f"║                                                              ║")
        print(f"╚══════════════════════════════════════════════════════════════╝{Colors.END}")
    
    def detect_django_apps(self):
        """Detect Django apps with migrations"""
        print(f"\n{Colors.BOLD}🔍 Detecting Django apps...{Colors.END}")
        
        self.apps_with_migrations = []
        
        # Common Django app directories
        potential_apps = [
            'students', 'teachers', 'fees', 'student_fees', 'attendance',
            'transport', 'messaging', 'dashboard', 'subjects', 'fines',
            'reports', 'promotion', 'backup', 'school_profile', 'users',
            'settings', 'core'
        ]
        
        for app_name in potential_apps:
            app_dir = self.project_root / app_name
            migrations_dir = app_dir / "migrations"
            
            if migrations_dir.exists():
                # Check if it has migration files (other than __init__.py)
                migration_files = [
                    f for f in migrations_dir.iterdir()
                    if f.is_file() and f.name.endswith('.py') and f.name != '__init__.py'
                ]
                
                if migration_files or app_dir.exists():
                    self.apps_with_migrations.append(app_name)
                    print(f"   📦 Found app: {Colors.GREEN}{app_name}{Colors.END} ({len(migration_files)} migrations)")
        
        if not self.apps_with_migrations:
            print(f"   {Colors.YELLOW}⚠️  No Django apps with migrations found{Colors.END}")
            return False
        
        print(f"   {Colors.GREEN}✅ Found {len(self.apps_with_migrations)} Django apps{Colors.END}")
        return True
    
    def backup_current_state(self):
        """Backup current database and migrations"""
        print(f"\n{Colors.BOLD}💾 Creating backup...{Colors.END}")
        
        try:
            # Create backup directory
            self.backup_dir.mkdir(exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Backup database if exists
            if self.db_path.exists():
                db_backup = self.backup_dir / f"db_before_reset_{timestamp}.sqlite3"
                shutil.copy2(self.db_path, db_backup)
                print(f"   {Colors.GREEN}✅ Database backed up: {db_backup.name}{Colors.END}")
            
            # Backup migration files
            migrations_backup_dir = self.backup_dir / f"migrations_backup_{timestamp}"
            migrations_backup_dir.mkdir(exist_ok=True)
            
            backed_up_count = 0
            for app_name in self.apps_with_migrations:
                app_migrations_dir = self.project_root / app_name / "migrations"
                if app_migrations_dir.exists():
                    app_backup_dir = migrations_backup_dir / app_name
                    shutil.copytree(app_migrations_dir, app_backup_dir)
                    backed_up_count += 1
            
            print(f"   {Colors.GREEN}✅ Migrations backed up: {backed_up_count} apps{Colors.END}")
            return True
            
        except Exception as e:
            print(f"   {Colors.RED}❌ Backup failed: {e}{Colors.END}")
            return False
    
    def show_reset_options(self):
        """Show reset options to user"""
        print(f"\n{Colors.BOLD}🎯 Reset Options:{Colors.END}")
        print(f"{Colors.GREEN}1.{Colors.END} 🔄 Soft Reset (Keep data, reset migrations only)")
        print(f"{Colors.GREEN}2.{Colors.END} 🗑️  Hard Reset (Delete database and migrations)")
        print(f"{Colors.GREEN}3.{Colors.END} 🧹 Clean Reset (Fresh start with sample data)")
        print(f"{Colors.GREEN}0.{Colors.END} ❌ Cancel")
        
        while True:
            try:
                choice = input(f"\n{Colors.YELLOW}Select reset type (0-3): {Colors.END}")
                
                if choice == "0":
                    return None
                elif choice in ["1", "2", "3"]:
                    return int(choice)
                else:
                    print(f"{Colors.RED}❌ Invalid choice. Please select 0-3{Colors.END}")
                    
            except KeyboardInterrupt:
                return None
    
    def export_data(self):
        """Export existing data before reset"""
        print(f"\n{Colors.BOLD}📤 Exporting existing data...{Colors.END}")
        
        if not self.db_path.exists():
            print(f"   {Colors.BLUE}ℹ️  No database to export{Colors.END}")
            return True
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_file = self.backup_dir / f"data_export_{timestamp}.json"
            
            cmd = [
                self.python_exe, "manage.py", "dumpdata",
                "--natural-foreign", "--natural-primary",
                "--exclude=contenttypes", "--exclude=auth.permission",
                "--exclude=sessions", "--exclude=admin.logentry",
                "--output", str(export_file)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}✅ Data exported: {export_file.name}{Colors.END}")
                return str(export_file)
            else:
                print(f"   {Colors.YELLOW}⚠️  Data export failed (may be empty database){Colors.END}")
                return None
                
        except Exception as e:
            print(f"   {Colors.YELLOW}⚠️  Export error: {e}{Colors.END}")
            return None
    
    def remove_migration_files(self):
        """Remove migration files from all apps"""
        print(f"\n{Colors.BOLD}🗑️  Removing migration files...{Colors.END}")
        
        removed_count = 0
        
        for app_name in self.apps_with_migrations:
            migrations_dir = self.project_root / app_name / "migrations"
            
            if migrations_dir.exists():
                try:
                    # Remove migration files (keep __init__.py)
                    for migration_file in migrations_dir.iterdir():
                        if (migration_file.is_file() and 
                            migration_file.name.endswith('.py') and 
                            migration_file.name != '__init__.py'):
                            
                            migration_file.unlink()
                            removed_count += 1
                    
                    # Remove __pycache__
                    pycache_dir = migrations_dir / "__pycache__"
                    if pycache_dir.exists():
                        shutil.rmtree(pycache_dir)
                    
                    print(f"   🧹 Cleaned {app_name} migrations")
                    
                except Exception as e:
                    print(f"   {Colors.YELLOW}⚠️  Could not clean {app_name}: {e}{Colors.END}")
        
        print(f"   {Colors.GREEN}✅ Removed {removed_count} migration files{Colors.END}")
        return True
    
    def remove_database(self):
        """Remove existing database"""
        if self.db_path.exists():
            print(f"\n{Colors.BOLD}🗑️  Removing database...{Colors.END}")
            
            try:
                os.remove(self.db_path)
                print(f"   {Colors.GREEN}✅ Database removed{Colors.END}")
            except Exception as e:
                print(f"   {Colors.RED}❌ Could not remove database: {e}{Colors.END}")
                return False
        
        return True
    
    def create_fresh_migrations(self):
        """Create fresh migration files"""
        print(f"\n{Colors.BOLD}📝 Creating fresh migrations...{Colors.END}")
        
        try:
            cmd = [self.python_exe, "manage.py", "makemigrations"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}✅ Fresh migrations created{Colors.END}")
                
                # Show created migrations
                if result.stdout:
                    lines = result.stdout.strip().split('\n')
                    for line in lines:
                        if 'Create model' in line or 'migrations for' in line:
                            print(f"   📄 {line}")
                
                return True
            else:
                print(f"   {Colors.RED}❌ Migration creation failed{Colors.END}")
                print(f"   Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}❌ Migration creation error: {e}{Colors.END}")
            return False
    
    def apply_migrations(self):
        """Apply fresh migrations"""
        print(f"\n{Colors.BOLD}🔧 Applying migrations...{Colors.END}")
        
        try:
            cmd = [self.python_exe, "manage.py", "migrate"]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}✅ Migrations applied successfully{Colors.END}")
                return True
            else:
                print(f"   {Colors.RED}❌ Migration application failed{Colors.END}")
                print(f"   Error: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   {Colors.RED}❌ Migration application error: {e}{Colors.END}")
            return False
    
    def restore_data(self, export_file):
        """Restore data from export file"""
        if not export_file or not Path(export_file).exists():
            return True
        
        print(f"\n{Colors.BOLD}📥 Restoring data...{Colors.END}")
        
        try:
            cmd = [self.python_exe, "manage.py", "loaddata", export_file]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                print(f"   {Colors.GREEN}✅ Data restored successfully{Colors.END}")
                return True
            else:
                print(f"   {Colors.YELLOW}⚠️  Data restoration failed{Colors.END}")
                print(f"   {Colors.CYAN}💡 You may need to recreate data manually{Colors.END}")
                return True  # Not critical
                
        except Exception as e:
            print(f"   {Colors.YELLOW}⚠️  Data restoration error: {e}{Colors.END}")
            return True  # Not critical
    
    def run_reset(self, reset_type):
        """Run the selected reset type"""
        export_file = None
        
        if reset_type == 1:  # Soft Reset
            print(f"\n{Colors.CYAN}🔄 Starting Soft Reset...{Colors.END}")
            export_file = self.export_data()
            
            if not self.remove_migration_files():
                return False
            if not self.create_fresh_migrations():
                return False
            if not self.apply_migrations():
                return False
            
            self.restore_data(export_file)
            
        elif reset_type == 2:  # Hard Reset
            print(f"\n{Colors.CYAN}🗑️  Starting Hard Reset...{Colors.END}")
            
            if not self.remove_migration_files():
                return False
            if not self.remove_database():
                return False
            if not self.create_fresh_migrations():
                return False
            if not self.apply_migrations():
                return False
            
        elif reset_type == 3:  # Clean Reset
            print(f"\n{Colors.CYAN}🧹 Starting Clean Reset...{Colors.END}")
            
            if not self.remove_migration_files():
                return False
            if not self.remove_database():
                return False
            if not self.create_fresh_migrations():
                return False
            if not self.apply_migrations():
                return False
            
            # Load sample data if available
            self.load_sample_data()
        
        return True
    
    def load_sample_data(self):
        """Load sample data for clean reset"""
        print(f"\n{Colors.BOLD}📊 Loading sample data...{Colors.END}")
        
        # Look for sample data fixtures
        sample_dirs = [
            self.project_root / "fixtures" / "sample",
            self.project_root / "sample_data",
            self.project_root / "initial_data"
        ]
        
        loaded_count = 0
        for sample_dir in sample_dirs:
            if sample_dir.exists():
                for fixture_file in sample_dir.glob("*.json"):
                    try:
                        cmd = [self.python_exe, "manage.py", "loaddata", str(fixture_file)]
                        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                        
                        if result.returncode == 0:
                            print(f"   {Colors.GREEN}✅ Loaded {fixture_file.name}{Colors.END}")
                            loaded_count += 1
                        
                    except Exception:
                        pass
        
        if loaded_count == 0:
            print(f"   {Colors.BLUE}ℹ️  No sample data found{Colors.END}")
        else:
            print(f"   {Colors.GREEN}✅ {loaded_count} sample data files loaded{Colors.END}")
    
    def run_migration_reset(self):
        """Run complete migration reset process"""
        self.print_header()
        
        # Detect Django apps
        if not self.detect_django_apps():
            return False
        
        # Show reset options
        reset_type = self.show_reset_options()
        
        if reset_type is None:
            print(f"\n{Colors.YELLOW}⚠️  Reset cancelled by user{Colors.END}")
            return False
        
        # Create backup
        if not self.backup_current_state():
            return False
        
        # Run selected reset
        if not self.run_reset(reset_type):
            return False
        
        print(f"\n{Colors.GREEN}🎉 Migration reset completed successfully!{Colors.END}")
        
        reset_names = {1: "Soft Reset", 2: "Hard Reset", 3: "Clean Reset"}
        print(f"\n{Colors.BOLD}📋 Reset Summary:{Colors.END}")
        print(f"   🔄 Type: {reset_names[reset_type]}")
        print(f"   📦 Apps: {len(self.apps_with_migrations)} Django apps")
        print(f"   💾 Backups: {self.backup_dir}")
        
        return True

def main():
    """Main execution function"""
    reset_tool = MigrationReset()
    
    try:
        success = reset_tool.run_migration_reset()
        
        if success:
            print(f"\n{Colors.GREEN}✅ Migrations reset successfully!{Colors.END}")
            sys.exit(0)
        else:
            print(f"\n{Colors.RED}❌ Migration reset failed{Colors.END}")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⚠️  Reset cancelled by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Reset error: {e}{Colors.END}")
        sys.exit(1)

if __name__ == "__main__":
    main()